import csv
import os
import random
import re
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone

from users.models import User
from clinical.models import Clinic, Doctor, Patient, Disease, Appointment
from pharmacy.models import DrugMaster, Prescription, PrescriptionLine
from analytics.models import AnalyticsAlert

class Command(BaseCommand):
    help = 'Seeds the database with Tamil Nadu healthcare data from CSV files'

    def handle(self, *args, **kwargs):
        self.data_dir = os.path.join(os.getcwd(), '..', 'data')
        self.stdout.write(self.style.WARNING('Starting the database seeding process...'))

        self.seed_clinics()          # 1. Clinics
        self.seed_users()            # 2. Users 
        self.seed_doctors()          # 3. Doctors 
        self.seed_patients()         # 4. Patients
        self.seed_diseases()         # 5. Diseases
        self.seed_drugmaster()       # 6. Drugs
        self.seed_appointments()     # 7. Appointments
        self.seed_prescriptions()    # 8. Prescriptions
        self.seed_prescription_lines() # 9. Lines
        self.seed_alerts()           # 10. Alerts
        
        self.stdout.write(self.style.SUCCESS('🎉 All data successfully seeded!'))

    def parse_bool(self, value):
        return str(value).strip().lower() in ['true', '1', 't', 'y', 'yes']

    def seed_clinics(self):
        file_path = os.path.join(self.data_dir, 'clinical_clinic.csv')
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Clinic.objects.get_or_create(
                    clinic_id=row['clinic_id'],
                    defaults={
                        'clinic_name': row['clinic_name'],
                        'address_line': row['address_line'],
                        'city': row['city'],
                        'district': row['district'],
                        'pincode': row['pincode'],
                        'contact_number': row['contact_number'],
                        'clinic_type': row['clinic_type'],
                        'bed_capacity': int(row['bed_capacity']) if row['bed_capacity'] else 0,
                        'latitude': row['latitude'] if row['latitude'] else None,
                        'longitude': row['longitude'] if row['longitude'] else None,
                        'established_year': int(row['established_year']) if row['established_year'] else None,
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Clinics'))

    def seed_users(self):
        file_path = os.path.join(self.data_dir, 'users_user.csv')
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                created_dt = parse_datetime(row['created_at'])
                if created_dt and timezone.is_naive(created_dt):
                    created_dt = timezone.make_aware(created_dt)
                
                last_login_dt = parse_datetime(row['last_login']) if row['last_login'] else None
                if last_login_dt and timezone.is_naive(last_login_dt):
                    last_login_dt = timezone.make_aware(last_login_dt)

                # Identify if this user is a Super Admin
                is_super_admin = (row['role_type'] == 'Super_Admin')
                
                # Apply exact password hash for super admins, else use CSV hash
                if is_super_admin:
                    pwd_hash = "pbkdf2_sha256$1200000$ZIZKAGahQBneoyAgVmAJfS$W9ZCq3dtc2gyBeo2UVD5Z8SnELV+APRIec5FCtDzNUc="
                else:
                    pwd_hash = row['password_hash']

                User.objects.get_or_create(
                    id=row['user_id'], 
                    defaults={
                        'username': row['user_id'], 
                        'clinic_id': row['clinic_id'] if row['clinic_id'] else None, 
                        'role_type': row['role_type'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'email': row['email'],
                        'password': pwd_hash, 
                        'date_joined': created_dt, 
                        'last_login': last_login_dt,
                        'is_active': self.parse_bool(row['is_active']),
                        'failed_login_attempts': int(row['failed_login_attempts']) if row['failed_login_attempts'] else 0,
                        
                        # Fix for Admin Login
                        'is_staff': is_super_admin,
                        'is_superuser': is_super_admin,
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Users'))

    def seed_doctors(self):
        file_path = os.path.join(self.data_dir, 'clinical_doctor.csv')
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Doctor.objects.get_or_create(
                    doctor_id=row['doctor_id'],
                    defaults={
                        'user_id': row['user_id'],
                        'clinic_id': row['clinic_id'],
                        'specialization': row['specialization'],
                        'experience_years': int(row['experience_years']) if row['experience_years'] else 0,
                        'consultation_fee': row['consultation_fee'] if row['consultation_fee'] else 0.0,
                        'average_rating': row['average_rating'] if row['average_rating'] else 0.0,
                        'availability_status': row['availability_status'],
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Doctors'))

    def seed_patients(self):
        file_path = os.path.join(self.data_dir, 'clinical_patient.csv')
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Patient.objects.get_or_create(
                    patient_id=row['patient_id'],
                    defaults={
                        'name': row['name'],
                        'dob': parse_date(row['dob']),
                        'gender': row['gender'],
                        'blood_group': row['blood_group'],
                        'city': row['city'],
                        'district': row['district'],
                        'pincode': row['pincode'],
                        'occupation_type': row['occupation_type'],
                        'chronic_conditions_flag': self.parse_bool(row['chronic_conditions_flag']),
                        'registration_date': parse_date(row['registration_date']),
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Patients'))

    def seed_diseases(self):
        file_path = os.path.join(self.data_dir, 'clinical_disease.csv')
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Disease.objects.get_or_create(
                    disease_id=row['disease_id'],
                    defaults={
                        'icd_10_code': row['icd_10_code'],
                        'disease_name': row['disease_name'],
                        'category': row['category'],
                        'seasonality_flag': row['seasonality_flag'],
                        'severity_level': row['severity_level'],
                        'avg_recovery_days': int(row['avg_recovery_days']) if row['avg_recovery_days'] else 0,
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Diseases'))

    def seed_drugmaster(self):
        file_path = os.path.join(self.data_dir, 'pharmacy_drugmaster.csv')
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                DrugMaster.objects.get_or_create(
                    drug_id=row['drug_id'],
                    defaults={
                        'generic_name': row['generic_name'],
                        'brand_name': row['brand_name'],
                        'category': row['category'],
                        'current_stock_level': int(row['current_stock_level']) if row['current_stock_level'] else 0,
                        'minimum_safety_buffer': int(row['minimum_safety_buffer']) if row['minimum_safety_buffer'] else 0,
                        'unit_cost_inr': row['unit_cost_inr'] if row['unit_cost_inr'] else 0.0,
                        'lead_time_days': int(row['lead_time_days']) if row['lead_time_days'] else 0,
                        'requires_prescription': self.parse_bool(row['requires_prescription']),
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Drug Master'))

    def seed_appointments(self):
        file_path = os.path.join(self.data_dir, 'clinical_appointment.csv')
        batch_size = 5000
        objs = []
        
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                objs.append(Appointment(
                    appointment_id=row['appointment_id'],
                    patient_id=row['patient_id'],
                    doctor_id=row['doctor_id'],
                    clinic_id=row['clinic_id'],
                    disease_id=row['disease_id'] if row['disease_id'] else None,
                    appointment_date=parse_date(row['appointment_date']),
                    vitals_temperature=row['vitals_temperature'] if row['vitals_temperature'] else 0.0,
                    status=row['status'],
                    visit_type=row['visit_type']
                ))
                
                if len(objs) >= batch_size:
                    Appointment.objects.bulk_create(objs, ignore_conflicts=True)
                    objs = []
                    
            if objs:
                Appointment.objects.bulk_create(objs, ignore_conflicts=True)
                
        self.stdout.write(self.style.SUCCESS('✅ Appointments (Batch)'))

    def seed_prescriptions(self):
        file_path = os.path.join(self.data_dir, 'pharmacy_prescription.csv')
        batch_size = 5000
        objs = []
        
        valid_appts = list(Appointment.objects.values_list('appointment_id', flat=True))
        if not valid_appts:
            return
        valid_app_set = set(valid_appts)
        
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                appt_id = row['appointment_id'].replace('AP', 'A')
                if appt_id not in valid_app_set:
                    appt_id = random.choice(valid_appts)

                objs.append(Prescription(
                    prescription_id=row['prescription_id'],
                    appointment_id=appt_id,
                    date_issued=parse_date(row['date_issued']),
                    duration_days=int(row['duration_days']) if row['duration_days'] else 0,
                    digital_signature_flag=self.parse_bool(row['digital_signature_flag'])
                ))
                
                if len(objs) >= batch_size:
                    Prescription.objects.bulk_create(objs, ignore_conflicts=True)
                    objs = []
                    
            if objs:
                Prescription.objects.bulk_create(objs, ignore_conflicts=True)
                
        self.stdout.write(self.style.SUCCESS('✅ Prescriptions (Batch)'))

    def seed_prescription_lines(self):
        file_path = os.path.join(self.data_dir, 'pharmacy_prescriptionline.csv')
        batch_size = 5000
        objs = []
        
        valid_rxs = list(Prescription.objects.values_list('prescription_id', flat=True))
        valid_drugs = list(DrugMaster.objects.values_list('drug_id', flat=True))
        
        if not valid_rxs or not valid_drugs:
            return
            
        valid_rx_set = set(valid_rxs)
        valid_drug_set = set(valid_drugs)
        
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rx_id = row['prescription_id'].replace('RX-', 'PR')
                drug_id = row['drug_id'].replace('D-', 'DR')
                
                if rx_id not in valid_rx_set:
                    rx_id = random.choice(valid_rxs)
                if drug_id not in valid_drug_set:
                    drug_id = random.choice(valid_drugs)

                objs.append(PrescriptionLine(
                    line_id=row['line_id'],
                    prescription_id=rx_id,
                    drug_id=drug_id,
                    dosage_frequency=row['dosage_frequency'],
                    quantity_dispensed=int(row['quantity_dispensed']) if row['quantity_dispensed'] else 0
                ))
                
                if len(objs) >= batch_size:
                    PrescriptionLine.objects.bulk_create(objs, ignore_conflicts=True)
                    objs = []
                    
            if objs:
                PrescriptionLine.objects.bulk_create(objs, ignore_conflicts=True)
                
        self.stdout.write(self.style.SUCCESS('✅ Prescription Lines (Batch)'))

    def seed_alerts(self):
        file_path = os.path.join(self.data_dir, 'analytics_alert.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'❌ Cannot find file at: {file_path}'))
            return
            
        valid_clinics = list(Clinic.objects.values_list('clinic_id', flat=True))
        valid_clinic_set = set(valid_clinics)
            
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nums = re.findall(r'\d+', row['clinic_id'])
                if nums:
                    clinic_id = f"C{str(int(nums[0])).zfill(3)}"
                else:
                    clinic_id = row['clinic_id']
                    
                if clinic_id not in valid_clinic_set:
                    clinic_id = random.choice(valid_clinics)

                AnalyticsAlert.objects.get_or_create(
                    alert_id=row['alert_id'],
                    defaults={
                        'clinic_id': clinic_id,
                        'alert_type': row['alert_type'],
                        'reference_id': row['reference_id'],
                        'severity': row['severity'],
                        'trigger_metric': row['trigger_metric'],
                        'triggered_date': parse_date(row['triggered_date']),
                        'is_resolved': self.parse_bool(row['is_resolved']),
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Analytics Alerts'))