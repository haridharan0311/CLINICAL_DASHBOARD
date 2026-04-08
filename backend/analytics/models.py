from django.db import models

class AnalyticsAlert(models.Model):
    alert_id = models.CharField(max_length=10, primary_key=True)
    # Lazy relation back to Clinical 
    clinic = models.ForeignKey('clinical.Clinic', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=100) # e.g., 'Disease_Spike', 'Low_Stock'
    reference_id = models.CharField(max_length=20) # Stores 'DIS001' or 'DRG052'
    severity = models.CharField(max_length=20) # 'Medium', 'Critical', etc.
    trigger_metric = models.TextField() # e.g., "Cases increased 376% in 48 hours"
    triggered_date = models.DateField()
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert {self.alert_id} ({self.alert_type}) - {self.severity}"
