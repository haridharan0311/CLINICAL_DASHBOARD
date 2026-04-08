from django.contrib import admin

from .models import Appointment, Clinic, Disease, Doctor, Patient

admin.site.register(Clinic)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Disease)
admin.site.register(Appointment)