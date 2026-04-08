# clinical/models.py
from django.db import models
from django.conf import settings

class Clinic(models.Model):
    clinic_id = models.CharField(max_length=10, primary_key=True)
    clinic_name = models.CharField(max_length=255)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=20)
    clinic_type = models.CharField(max_length=100)
    bed_capacity = models.IntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    established_year = models.IntegerField()

    def __str__(self):
        return f"{self.clinic_name} - {self.city}"

class Doctor(models.Model):
    doctor_id = models.CharField(max_length=10, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    experience_years = models.IntegerField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1)
    availability_status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} ({self.specialization})"

class Patient(models.Model):
    patient_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    occupation_type = models.CharField(max_length=100)
    chronic_conditions_flag = models.BooleanField(default=False)
    registration_date = models.DateField()

    def __str__(self):
        return self.name

class Disease(models.Model):
    SEASONALITY_CHOICES = [
        ('Monsoon', 'Monsoon'),
        ('Summer', 'Summer'),
        ('Winter', 'Winter'),
        ('All-Year', 'All-Year')
    ]
    
    disease_id = models.CharField(max_length=10, primary_key=True)
    icd_10_code = models.CharField(max_length=20)
    disease_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    seasonality_flag = models.CharField(max_length=20, choices=SEASONALITY_CHOICES)
    severity_level = models.CharField(max_length=20)
    avg_recovery_days = models.IntegerField()

    def __str__(self):
        return f"{self.disease_name} ({self.icd_10_code})"

class Appointment(models.Model):
    appointment_id = models.CharField(max_length=10, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateField()
    vitals_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=50) # e.g., 'Completed', 'Cancelled'
    visit_type = models.CharField(max_length=50) # e.g., 'First Visit', 'Follow-up'

    def __str__(self):
        return f"Apt: {self.appointment_id} - {self.patient.name}"