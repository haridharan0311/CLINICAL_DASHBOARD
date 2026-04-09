import csv
from django.http import HttpResponse
from django.db.models import F
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# Import our custom logic and models
from analytics.services import get_disease_trends, detect_spikes, predict_medicine_demand
from analytics.models import AnalyticsAlert
from pharmacy.models import DrugMaster
from .serializers import DiseaseTrendSerializer, RestockSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


# Helper function for RBAC
# api/views.py

def get_user_clinic(user, request):
    """
    Super_Admin can pass ?clinic_id=C001 in the URL.
    Other roles are locked to their assigned clinic.
    """
    if user.role_type == 'Super_Admin':
        return request.query_params.get('clinic_id', None)    
    return user.clinic_id


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ---------------------------------------------------------
# 1. Disease Trend Endpoint
# ---------------------------------------------------------
class DiseaseTrendView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access disease trends

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        clinic_id = get_user_clinic(request.user, request)

        # Call the Service Layer
        raw_data = get_disease_trends(days=days, clinic_id=clinic_id)
        
        # Serialize the output
        serializer = DiseaseTrendSerializer(data=raw_data, many=True)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# ---------------------------------------------------------
# 2. Spike Detection & Alert History Endpoint
# ---------------------------------------------------------
class SpikeDetectionView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can trigger or view alerts

    def post(self, request):
        """ Manually trigger the spike detection ML service. """
        clinic_id = get_user_clinic(request.user, request)
        
        if not clinic_id:
             return Response(
                 {"error": "A clinic_id is required to run spike detection."}, 
                 status=status.HTTP_400_BAD_REQUEST
             )

        # Call the Service Layer
        result_message = detect_spikes(clinic_id)
        return Response({"message": result_message}, status=status.HTTP_200_OK)

    # 2. Live Updates: We use @never_cache to prevent browser/proxy caching
    @method_decorator(never_cache)
    def get(self, request):
        """ Fetch recent outbreak alerts (Optimized ORM) """
        clinic_id = get_user_clinic(request.user, request)
        
        # 1. ORM Optimization: Only fetch the columns we are actually returning.
        # This prevents the DB from pulling heavy text fields or unused data.
        alerts = AnalyticsAlert.objects.only(
            'alert_id', 'alert_type', 'severity', 'trigger_metric', 'triggered_date'
        ).filter(is_resolved=False).order_by('-triggered_date')

        if clinic_id:
            alerts = alerts.filter(clinic_id=clinic_id)

        data = [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "trigger_metric": a.trigger_metric,
                "triggered_date": a.triggered_date
            } for a in alerts
        ]
        return Response(data, status=status.HTTP_200_OK)

# ---------------------------------------------------------
# 3. Restock Suggestion Endpoint (With N+1 Optimization)
# ---------------------------------------------------------
class RestockSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clinic_id = get_user_clinic(request.user, request)
        
        # We only want to analyze drugs that are currently below their safety buffer
        low_stock_drugs = DrugMaster.objects.filter(
            current_stock_level__lt=F('minimum_safety_buffer')
        )

        # Iterate and attach the predicted demand dynamically (as expected by our Serializer)
        for drug in low_stock_drugs:
            prediction_data = predict_medicine_demand(
                drug_id=drug.drug_id, 
                days_to_predict=30, 
                clinic_id=clinic_id
            )
            # Attach the dynamic value directly to the model instance in memory
            drug.annotated_predicted_demand = prediction_data.get('predicted_demand', 0)

        # Serialize using the ModelSerializer created in Step 4
        serializer = RestockSerializer(low_stock_drugs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ---------------------------------------------------------
# 4. CSV Export Endpoint
# ---------------------------------------------------------
class ExportCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        export_type = request.query_params.get('type', 'trends')
        clinic_id = get_user_clinic(request.user, request)

        # Setup the HTTP response for file download
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_type}_export.csv"'
        
        writer = csv.writer(response)

        if export_type == 'trends':
            data = get_disease_trends(days=30, clinic_id=clinic_id)
            # Write Header
            writer.writerow(['Date', 'Disease Name', 'Cases'])
            # Write Data Rows
            for row in data:
                writer.writerow([row['date'], row['disease_name'], row['cases']])

        elif export_type == 'restock':
            drugs = DrugMaster.objects.filter(current_stock_level__lt=F('minimum_safety_buffer'))
            writer.writerow(['Drug ID', 'Brand Name', 'Current Stock', 'Safety Buffer', 'Predicted Demand'])
            
            for drug in drugs:
                pred = predict_medicine_demand(drug.drug_id, clinic_id=clinic_id)
                writer.writerow([
                    drug.drug_id, 
                    drug.brand_name, 
                    drug.current_stock_level, 
                    drug.minimum_safety_buffer, 
                    pred.get('predicted_demand', 0)
                ])
        else:
            return Response({"error": "Invalid export type"}, status=status.HTTP_400_BAD_REQUEST)

        return response
