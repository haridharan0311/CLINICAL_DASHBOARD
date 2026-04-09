import statistics
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from collections import defaultdict

# Importing from the clinical app
from clinical.models import Appointment, Clinic
from pharmacy.models import DrugMaster, PrescriptionLine
from analytics.models import AnalyticsAlert


def get_disease_trends(days=30, clinic_id=None):
    """
    Aggregates disease case counts over the past 'N' days.
    If clinic_id is provided, scopes data to that specific clinic.
    Returns a list of dictionaries suitable for JSON serialization and frontend charting.
    """
    start_date = timezone.now().date() - timedelta(days=days)

    # Start with the base query
    queryset = Appointment.objects.filter(
        appointment_date__gte=start_date, 
        disease__isnull=False
    )

    # Apply Clinic scope if requested
    if clinic_id:
        queryset = queryset.filter(clinic_id=clinic_id)

    # THE FIX: Remove TruncDate and group by appointment_date directly
    trends = (
        queryset
        .values('appointment_date', 'disease__disease_name')
        .annotate(case_count=Count('appointment_id'))
        .order_by('appointment_date', 'disease__disease_name')
    )

    # Format the output for the React frontend
    formatted_trends = [
        {
            # str() safely handles both actual Date objects and SQLite strings
            "date": str(item["appointment_date"]), 
            "disease_name": item["disease__disease_name"],
            "cases": item["case_count"]
        }
        for item in trends
    ]

    return formatted_trends


def calculate_moving_average(disease_id, clinic_id=None):
    """
    Calculates a weighted moving average for disease cases.
    Formula: (last_3_days_avg * 0.6) + (last_7_days_avg * 0.4)
    If clinic_id is provided, it strictly scopes the math to that clinic.
    """
    # 1. Define the time windows
    today = timezone.now().date()
    three_days_ago = today - timedelta(days=3)
    seven_days_ago = today - timedelta(days=7)

    # 1. Build the base queries (Global by default)
    queryset_7_days = Appointment.objects.filter(
        disease_id=disease_id,
        appointment_date__gt=seven_days_ago,
        appointment_date__lte=today
    )

    queryset_3_days = Appointment.objects.filter(
        disease_id=disease_id,
        appointment_date__gt=three_days_ago,
        appointment_date__lte=today
    )

    # 2. RBAC FILTERING LOGIC: Apply Clinic scope if requested
    if clinic_id:
        queryset_7_days = queryset_7_days.filter(clinic_id=clinic_id)
        queryset_3_days = queryset_3_days.filter(clinic_id=clinic_id)

    # 3. Execute the count queries
    last_7_days_total = queryset_7_days.count()
    last_3_days_total = queryset_3_days.count()

    # 4. Calculate averages and apply formula
    last_3_days_avg = last_3_days_total / 3.0
    last_7_days_avg = last_7_days_total / 7.0

    # 4. Apply the custom weighted formula
    weighted_moving_average = (last_3_days_avg * 0.6) + (last_7_days_avg * 0.4)

    return round(weighted_moving_average, 2)


def detect_spikes(clinic_id):
    """
    Detects disease outbreaks using Z-score anomaly detection.
    Logic: Today_Count > (Mean_Last_7_Days + 2 * Std_Dev)
    """
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # 1. Get Today's Counts (We only care about diseases that actually have cases today)
    today_appointments = (
        Appointment.objects.filter(
            clinic_id=clinic_id,
            appointment_date=today,
            disease__isnull=False
        )
        .values('disease_id', 'disease__disease_name')
        .annotate(today_count=Count('appointment_id'))
    )

    if not today_appointments.exists():
        return "No cases today. No spikes detected."

    # 2. Fetch Baseline Data (The past 7 days, strictly excluding today)
    baseline_appointments = (
        Appointment.objects.filter(
            clinic_id=clinic_id,
            appointment_date__gte=seven_days_ago,
            appointment_date__lt=today, # Exclude today from baseline
            disease__isnull=False
        )
        .annotate(date=TruncDate('appointment_date'))
        .values('disease_id', 'date')
        .annotate(daily_count=Count('appointment_id'))
    )

    # 3. Organize baseline data into a fast lookup dictionary: data[disease_id][date] = count
    baseline_data = defaultdict(lambda: defaultdict(int))
    for item in baseline_appointments:
        baseline_data[item['disease_id']][item['date']] = item['daily_count']

    # 4. Fetch the clinic object once for alert creation
    clinic = Clinic.objects.get(clinic_id=clinic_id)
    alerts_created = []

    # 5. Evaluate each disease seen today against its 7-day history
    for item in today_appointments:
        disease_id = item['disease_id']
        disease_name = item['disease__disease_name']
        today_count = item['today_count']

        # Reconstruct the exact 7-day array, padding missing days with 0
        past_7_days_counts = []
        for d in range(1, 8):
            date_to_check = today - timedelta(days=d)
            # Will append 0 if the date doesn't exist in the database for this disease
            past_7_days_counts.append(baseline_data[disease_id][date_to_check])

        # Calculate Statistics
        mean_7_days = statistics.mean(past_7_days_counts)
        std_dev = statistics.stdev(past_7_days_counts) 
        
        # Calculate the anomaly threshold (Mean + 2 * Std Dev)
        threshold = mean_7_days + (2 * std_dev)

        # 6. Spike Logic + Noise Reduction
        # We add `today_count >= 3` to prevent statistical noise. 
        # (e.g., If a disease had 0 cases all week, Mean=0, StdDev=0. 
        # 1 single case today would technically trigger an alert without this safety check).
        if today_count > threshold and today_count >= 3:
            
            # Create the AI Alert in the database
            alert = AnalyticsAlert.objects.create(
                alert_id=f"AL-{timezone.now().strftime('%Y%m%d%H%M%S')}-{disease_id[-3:]}",
                clinic=clinic,
                alert_type="Disease_Spike",
                reference_id=disease_id,
                severity="Critical" if today_count > (mean_7_days + 3 * std_dev) else "High",
                trigger_metric=f"Spike in {disease_name}: {today_count} cases today (Threshold: {round(threshold, 1)}).",
                triggered_date=today,
                is_resolved=False
            )
            alerts_created.append(alert.alert_id)

    return f"Spike detection complete. Alerts generated: {len(alerts_created)}"


def predict_medicine_demand(drug_id, days_to_predict=30, clinic_id=None):
    """
    Predicts future demand for a specific drug.
    Formula: trend_count * avg_usage * safety_buffer_multiplier
    If clinic_id is provided, scopes the prediction to that specific branch.
    """
    start_date = timezone.now().date() - timedelta(days=days_to_predict)

    try:
        drug = DrugMaster.objects.get(drug_id=drug_id)
    except DrugMaster.DoesNotExist:
        return {"error": "Drug not found"}

    # 1. Base Query: Get recent prescription lines for this drug
    recent_prescriptions = PrescriptionLine.objects.filter(
        drug_id=drug_id,
        prescription__date_issued__gte=start_date
    )

    # 2. RBAC FILTERING LOGIC: Span relationships to find the clinic
    if clinic_id:
        # Reaches across 3 tables instantly: Line -> Prescription -> Appointment -> Clinic
        recent_prescriptions = recent_prescriptions.filter(
            prescription__appointment__clinic_id=clinic_id
        )

    # 3. Calculate Trend and Usage
    trend_count = recent_prescriptions.count()

    if trend_count == 0:
        return {"predicted_demand": 0, "message": "No recent usage data available."}

    avg_usage_dict = recent_prescriptions.aggregate(Avg('quantity_dispensed'))
    avg_usage = avg_usage_dict['quantity_dispensed__avg'] or 0.0

    # 4. Apply formula
    safety_buffer_multiplier = 1.20 
    predicted_demand = trend_count * avg_usage * safety_buffer_multiplier

    # 5. Alert Logic (Only create an alert if we are analyzing a specific clinic)
    needs_restock = predicted_demand > drug.current_stock_level
    
    if needs_restock and clinic_id:
        AnalyticsAlert.objects.create(
            alert_id=f"AL-{timezone.now().strftime('%Y%m%d%H%M')}-{drug_id[-3:]}",
            clinic_id=clinic_id, 
            alert_type="Low_Stock_Prediction",
            reference_id=drug_id,
            severity="High",
            trigger_metric=f"Predicted demand ({int(predicted_demand)}) exceeds current stock ({drug.current_stock_level}).",
            triggered_date=timezone.now().date(),
            is_resolved=False
        )

    return {
        "drug_name": drug.brand_name,
        "clinic_analyzed": clinic_id if clinic_id else "Global Data",
        "trend_count": trend_count,
        "avg_usage_per_prescription": round(avg_usage, 2),
        "predicted_demand": int(predicted_demand),
        "current_stock": drug.current_stock_level,
        "needs_restock": needs_restock
    }

