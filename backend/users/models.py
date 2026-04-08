# users/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
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

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
        related_name='custom_user_set'  # Avoid clashes with default User model
    )

    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_user_permissions_set',  # Avoid clashes with default User model
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} - {self.role_type}"
