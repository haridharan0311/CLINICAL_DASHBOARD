from rest_framework import serializers
from pharmacy.models import DrugMaster
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add our custom user data to the JWT payload!
        token['role_type'] = user.role_type
        token['clinic_id'] = user.clinic_id
        token['name'] = f"{user.first_name} {user.last_name}"
        
        return token

# ---------------------------------------------------------
# 1. Disease Trend Serializer (Standard Serializer)
# ---------------------------------------------------------
class DiseaseTrendSerializer(serializers.Serializer):
    """
    Since our get_disease_trends() service function returns a list of 
    dictionaries (not raw ORM models), we use a standard Serializer 
    instead of a ModelSerializer.
    """
    date = serializers.CharField()
    disease_name = serializers.CharField()
    cases = serializers.IntegerField()


# ---------------------------------------------------------
# 2. Restock Serializer (Model Serializer with Custom Logic)
# ---------------------------------------------------------
class RestockSerializer(serializers.ModelSerializer):
    """
    Serializes the DrugMaster inventory and calculates restock needs.
    """
    # We use SerializerMethodFields to dynamically calculate values on the fly
    predicted_demand = serializers.SerializerMethodField()
    suggested_restock_quantity = serializers.SerializerMethodField()
    needs_urgent_restock = serializers.SerializerMethodField()

    class Meta:
        model = DrugMaster
        fields = [
            'drug_id', 
            'brand_name', 
            'category', 
            'current_stock_level', 
            'minimum_safety_buffer',
            'predicted_demand',
            'suggested_restock_quantity',
            'needs_urgent_restock'
        ]

    def get_predicted_demand(self, obj):
        # We expect the View to calculate the demand and pass it dynamically
        # using Django's annotation or context to avoid triggering an N+1 
        # problem by running the prediction service for every single row.
        return getattr(obj, 'annotated_predicted_demand', 0)

    def get_suggested_restock_quantity(self, obj):
        demand = self.get_predicted_demand(obj)
        # If predicted demand is higher than current stock, suggest the difference
        if demand > obj.current_stock_level:
            return demand - obj.current_stock_level
        return 0

    def get_needs_urgent_restock(self, obj):
        # Flag as urgent if current stock is below the absolute safety buffer
        return obj.current_stock_level < obj.minimum_safety_buffer
