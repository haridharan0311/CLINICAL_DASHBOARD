import csv
import os
from django.core.management.base import BaseCommand
from django.apps import apps

# Model Imports
from users.models import User, AuditLog
from clinical.models import Clinic, Doctor, Patient, Disease, Appointment
from pharmacy.models import DrugMaster, Prescription, PrescriptionLine, DrugBatch
from analytics.models import AnalyticsAlert

class Command(BaseCommand):
    help = 'Exports all 12 tables from the database to CSV files for backup'

    def handle(self, *args, **kwargs):
        # Define output directory
        export_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data',))
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {export_dir}'))

        self.stdout.write(self.style.WARNING('Starting the data export process...'))

        # List of export tasks: (Model, Filename, Field_Mapping_List)
        # Note: Field names match your seed_data logic for easy re-import
        tasks = [
            (Clinic, 'clinical_clinic.csv', 
                ['clinic_id', 'clinic_name', 'address_line', 'city', 'district', 'pincode', 'contact_number', 'clinic_type', 'bed_capacity', 'latitude', 'longitude', 'established_year']),
            
            (User, 'users_user.csv', 
                ['id', 'clinic_id', 'role_type', 'first_name', 'last_name', 'email', 'password', 'date_joined', 'last_login', 'is_active', 'failed_login_attempts']),
            
            (AuditLog, 'users_auditlog.csv', 
                ['user_id', 'action', 'ip_address', 'timestamp', 'resource_accessed']),
            
            (Doctor, 'clinical_doctor.csv', 
                ['doctor_id', 'user_id', 'clinic_id', 'specialization', 'experience_years', 'consultation_fee', 'average_rating', 'availability_status']),
            
            (Patient, 'clinical_patient.csv', 
                ['patient_id', 'name', 'dob', 'gender', 'blood_group', 'city', 'district', 'pincode', 'occupation_type', 'chronic_conditions_flag', 'registration_date']),
            
            (Disease, 'clinical_disease.csv', 
                ['disease_id', 'icd_10_code', 'disease_name', 'category', 'seasonality_flag', 'severity_level', 'avg_recovery_days']),
            
            (DrugMaster, 'pharmacy_drugmaster.csv', 
                ['drug_id', 'generic_name', 'brand_name', 'category', 'current_stock_level', 'minimum_safety_buffer', 'unit_cost_inr', 'lead_time_days', 'requires_prescription']),
            
            (DrugBatch, 'pharmacy_drugbatch.csv', 
                ['drug_id', 'batch_number', 'expiry_date', 'quantity_received', 'current_quantity']),
            
            (Appointment, 'clinical_appointment.csv', 
                ['appointment_id', 'patient_id', 'doctor_id', 'clinic_id', 'disease_id', 'appointment_date', 'vitals_temperature', 'status', 'visit_type']),
            
            (Prescription, 'pharmacy_prescription.csv', 
                ['prescription_id', 'appointment_id', 'date_issued', 'duration_days', 'digital_signature_flag']),
            
            (PrescriptionLine, 'pharmacy_prescriptionline.csv', 
                ['line_id', 'prescription_id', 'drug_id', 'dosage_frequency', 'quantity_dispensed']),
            
            (AnalyticsAlert, 'analytics_alert.csv', 
                ['alert_id', 'clinic_id', 'alert_type', 'reference_id', 'severity', 'trigger_metric', 'triggered_date', 'is_resolved']),
        ]

        for model, filename, fields in tasks:
            self.export_to_csv(model, filename, fields, export_dir)

        self.stdout.write(self.style.SUCCESS(f'🎉 Export complete! Files saved in: {export_dir}'))

    def export_to_csv(self, model, filename, fields, export_dir):
        file_path = os.path.join(export_dir, filename)
        queryset = model.objects.all()

        with open(file_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write Header (We rename 'id' to 'user_id' for the User table to match your CSV needs)
            header = [f.replace('id', 'user_id') if model == User and f == 'id' else f for f in fields]
            header = [f.replace('password', 'password_hash') if f == 'password' else f for f in header]
            header = [f.replace('date_joined', 'created_at') if f == 'date_joined' else f for f in header]
            writer.writerow(header)

            for obj in queryset:
                row = []
                for field in fields:
                    val = getattr(obj, field)
                    
                    # Handle ForeignKeys (get the ID instead of the object)
                    if hasattr(val, 'pk'):
                        val = val.pk
                    
                    row.append(val)
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f'✅ Exported {model.__name__} ({queryset.count()} rows)'))