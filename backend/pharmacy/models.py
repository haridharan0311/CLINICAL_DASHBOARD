# pharmacy/models.py
from django.db import models

class DrugMaster(models.Model):
    drug_id = models.CharField(max_length=10, primary_key=True)
    generic_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    current_stock_level = models.IntegerField()
    minimum_safety_buffer = models.IntegerField()
    unit_cost_inr = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField()
    requires_prescription = models.BooleanField(default=True)

    def __str__(self):
        return self.brand_name

class Prescription(models.Model):
    prescription_id = models.CharField(max_length=15, primary_key=True)
    # Lazy relationship to the Clinical App
    appointment = models.ForeignKey('clinical.Appointment', on_delete=models.CASCADE)
    date_issued = models.DateField()
    duration_days = models.IntegerField()
    digital_signature_flag = models.BooleanField(default=True)

    def __str__(self):
        return f"Rx: {self.prescription_id}"

class PrescriptionLine(models.Model):
    line_id = models.CharField(max_length=15, primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='lines')
    drug = models.ForeignKey(DrugMaster, on_delete=models.PROTECT)
    dosage_frequency = models.CharField(max_length=20) # e.g., '1-0-1'
    quantity_dispensed = models.IntegerField()

    def __str__(self):
        return f"{self.prescription.prescription_id} - {self.drug.brand_name}"

class DrugBatch(models.Model):
    drug = models.ForeignKey('DrugMaster', on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50, unique=True)
    expiry_date = models.DateField()
    quantity_received = models.IntegerField()
    current_quantity = models.IntegerField()
    procurement_date = models.DateField(auto_now_add=True)

    def is_expired(self):
        return self.expiry_date <= timezone.now().date()
