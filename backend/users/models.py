from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Super_Admin', 'Super Admin'),
        ('Clinic_Admin', 'Clinic Admin'),
        ('Doctor', 'Doctor'),
        ('Pharmacist', 'Pharmacist')
    ]

    # Matching the 'U001' format from users_user.csv
    id = models.CharField(max_length=10, primary_key=True, db_column='user_id') 
    
    # Lazy reference to Clinic to avoid circular imports
    clinic = models.ForeignKey(
        'clinical.Clinic', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)
    failed_login_attempts = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} - {self.role_type}"
