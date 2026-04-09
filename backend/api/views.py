import re
import csv
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.db import models, transaction
from django.db.models import F, Q, Count
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from clinical.models import Appointment
from analytics.models import AnalyticsAlert
from pharmacy.models import DrugMaster, DrugBatch
from users.models import User, AuditLog

# Import our custom logic and models
from analytics.services import get_disease_trends, detect_spikes, predict_medicine_demand
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


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clinic_id = request.user.clinic_id if request.user.role_type != 'Super_Admin' else request.query_params.get('clinic_id')
        today = timezone.now().date()
        
        # 1. Appointments/Cases Filter
        apt_filter = Q(disease__isnull=False)
        alert_filter = Q()
        if clinic_id:
            apt_filter &= Q(clinic_id=clinic_id)
            alert_filter &= Q(clinic_id=clinic_id)

        # Cases Calculations
        cases_today = Appointment.objects.filter(apt_filter, appointment_date=today).count()
        cases_week = Appointment.objects.filter(apt_filter, appointment_date__gte=today - timedelta(days=7)).count()
        cases_month = Appointment.objects.filter(apt_filter, appointment_date__gte=today - timedelta(days=30)).count()

        # Top Disease (Last 30 days)
        top_disease = Appointment.objects.filter(apt_filter, appointment_date__gte=today - timedelta(days=30)) \
            .values('disease__disease_name').annotate(count=Count('appointment_id')).order_by('-count').first()

        # 2. Alerts/Spikes Calculations
        active_spikes = AnalyticsAlert.objects.filter(alert_filter, is_resolved=False, alert_type__in=['Disease_Spike', 'Outbreak_Warning'])
        resolved_spikes = AnalyticsAlert.objects.filter(alert_filter, is_resolved=True, alert_type__in=['Disease_Spike', 'Outbreak_Warning']).count()
        
        spike_breakdown = active_spikes.values('severity').annotate(count=Count('alert_id'))

        # 3. Inventory Calculations (Global or Clinic level depending on your DrugMaster setup)
        low_stock_drugs = DrugMaster.objects.filter(current_stock_level__lt=models.F('minimum_safety_buffer'))
        total_low_stock = low_stock_drugs.count()

        return Response({
            "cases": {
                "today": cases_today,
                "this_week": cases_week,
                "this_month": cases_month,
                "top_disease_30d": top_disease['disease__disease_name'] if top_disease else "None"
            },
            "spikes": {
                "active_total": active_spikes.count(),
                "resolved_total": resolved_spikes,
                "breakdown": {item['severity']: item['count'] for item in spike_breakdown}
            },
            "inventory": {
                "low_stock_total": total_low_stock,
                # Example rough logic for severity grouping
                "critical": low_stock_drugs.filter(current_stock_level__lte=10).count(),
                "medium": low_stock_drugs.filter(current_stock_level__gt=10).count()
            }
        })


class GetNextBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        drug_id = request.query_params.get('drug_id')
        if not drug_id:
            return Response({"error": "No drug_id provided"}, status=400)

        # 1. Look for the last batch for THIS drug to find the number
        last_batch = DrugBatch.objects.filter(drug_id=drug_id).order_by('-id').first()
        
        next_no = 1001 # Default starting number
        if last_batch:
            # Extract number from the end of any string (e.g., '1201' from 'TN-BN-1201')
            match = re.search(r'(\d+)$', last_batch.batch_number)
            if match:
                next_no = int(match.group(1)) + 1

        # 2. Format it into your new desired format: BAT-DR147-4756
        candidate_id = f"BAT-{drug_id}-{next_no}"

        # 3. UNIQUENESS CHECK: If this ID already exists (maybe for another drug), 
        # keep incrementing until we find a truly empty slot.
        while DrugBatch.objects.filter(batch_number=candidate_id).exists():
            next_no += 1
            candidate_id = f"BAT-{drug_id}-{next_no}"

        return Response({"next_batch": candidate_id})


class RestockBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        drug_id = request.data.get('drug_id')
        batch_no = request.data.get('batch_number')
        qty = int(request.data.get('quantity'))
        expiry = request.data.get('expiry_date')

        try:
            with transaction.atomic():
                # select_for_update() prevents other users from changing stock 
                # at the exact same millisecond as you.
                drug = DrugMaster.objects.select_for_update().get(drug_id=drug_id)

                # 1. Create the unique Batch record
                DrugBatch.objects.create(
                    drug=drug,
                    batch_number=batch_no,
                    expiry_date=expiry,
                    quantity_received=qty,
                    current_quantity=qty
                )

                # 2. Update Master Stock Level (CRITICAL FIX)
                drug.current_stock_level += qty
                drug.save()

                client_ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    
                # 3. Audit Log with the CORRECT resulting stock value
                AuditLog.objects.create(
                    user=request.user,
                    action=f"RESTOCK SUCCESS: {drug.brand_name}. Added {qty}. New Total: {drug.current_stock_level}",
                    ip_address=client_ip,
                    resource_accessed="Inventory System"
                )

            return Response({"message": "Stock and Batch synced successfully", "new_total": drug.current_stock_level})
        except Exception as e:
            return Response({"error": f"Database Error: {str(e)}"}, status=400)


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
