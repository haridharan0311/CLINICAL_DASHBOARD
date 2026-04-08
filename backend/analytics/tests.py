from django.test import TestCase

# Create your tests here.
# analytics/tests.py
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from clinical.models import Clinic, Disease, Appointment, Doctor, Patient
from analytics.models import AnalyticsAlert
from analytics.services import calculate_moving_average, detect_spikes

class AnalyticsServicesTestCase(TestCase):
    def setUp(self):
        """
        Creates synthetic master data (Clinic, Disease, etc.) 
        needed before we can log appointments.
        """
        self.clinic = Clinic.objects.create(
            clinic_id="C001",
            clinic_name="Test Health Centre",
            established_year=2010
        )
        self.disease = Disease.objects.create(
            disease_id="DS01",
            disease_name="Dengue Fever",
            avg_recovery_days=10
        )
        
        # Create minimal required foreign keys for an Appointment
        from users.models import User
        self.user = User.objects.create(id="U001", username="testdoc", role_type="Doctor")
        self.doctor = Doctor.objects.create(
            doctor_id="D001", user=self.user, clinic=self.clinic, 
            experience_years=5, consultation_fee=500, average_rating=4.5
        )
        self.patient = Patient.objects.create(
            patient_id="P001", name="Test Patient", dob="1990-01-01", registration_date="2021-01-01"
        )

        self.today = timezone.now().date()
        self.two_days_ago = self.today - timedelta(days=2)
        self.five_days_ago = self.today - timedelta(days=5)

    def create_appointment(self, apt_id, date):
        """ Helper function to quickly spawn synthetic appointments """
        return Appointment.objects.create(
            appointment_id=apt_id,
            patient=self.patient,
            doctor=self.doctor,
            clinic=self.clinic,
            disease=self.disease,
            appointment_date=date,
            vitals_temperature=98.6
        )

    def test_calculate_moving_average(self):
        """
        Tests the formula: (last_3_days_avg * 0.6) + (last_7_days_avg * 0.4)
        """
        # Create 3 cases in the last 3 days (Avg = 3/3 = 1.0)
        self.create_appointment("A01", self.two_days_ago)
        self.create_appointment("A02", self.two_days_ago)
        self.create_appointment("A03", self.today)

        # Create 4 cases between 4-7 days ago 
        # Total 7 day cases = 3 (recent) + 4 (older) = 7 (Avg = 7/7 = 1.0)
        self.create_appointment("A04", self.five_days_ago)
        self.create_appointment("A05", self.five_days_ago)
        self.create_appointment("A06", self.five_days_ago)
        self.create_appointment("A07", self.five_days_ago)

        wma = calculate_moving_average(self.disease.disease_id, self.clinic.clinic_id)
        
        # Math: (1.0 * 0.6) + (1.0 * 0.4) = 1.0
        self.assertEqual(wma, 1.0)

    def test_detect_spikes_triggers_alert(self):
        """
        Tests the Z-Score Outbreak logic: Today_Count > (Mean_Last_7_Days + 2 * Std_Dev)
        """
        # Baseline: 1 case per day for the last 7 days (Mean = 1, StdDev = 0)
        for i in range(1, 8):
            past_date = self.today - timedelta(days=i)
            self.create_appointment(f"B{i}", past_date)

        # Spike: 5 cases today (Threshold is Mean(1) + 2*StdDev(0) = 1)
        # 5 cases is well over the threshold, and > 3 (our safety noise limit)
        for i in range(5):
            self.create_appointment(f"S{i}", self.today)

        # Run the detection service
        result = detect_spikes(self.clinic.clinic_id)

        # Verify an alert was actually written to the database
        alerts = AnalyticsAlert.objects.filter(
            clinic=self.clinic, 
            alert_type="Disease_Spike",
            reference_id=self.disease.disease_id
        )
        
        self.assertTrue(alerts.exists())
        self.assertEqual(alerts.first().severity, "Critical")
        self.assertIn("Spike detection complete", result)

    def test_detect_spikes_ignores_noise(self):
        """
        Ensures the system doesn't trigger fake alerts for 1 or 2 isolated cases.
        """
        # No history. Just 2 cases today.
        self.create_appointment("N1", self.today)
        self.create_appointment("N2", self.today)

        detect_spikes(self.clinic.clinic_id)

        # Verify NO alert was created because today_count < 3
        alerts = AnalyticsAlert.objects.filter(clinic=self.clinic)
        self.assertFalse(alerts.exists())

