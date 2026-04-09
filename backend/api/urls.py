from django.urls import path
from .views import (
    DashboardSummaryView,
    DiseaseTrendView, 
    SpikeDetectionView, 
    RestockSuggestionView,
    ExportCSVView,
)

urlpatterns = [
    # Endpoint: /api/disease-trends/
    path('disease-trends/', DiseaseTrendView.as_view(), name='disease-trends'),
    
    # Endpoint: /api/spike-detection/
    path('spike-detection/', SpikeDetectionView.as_view(), name='spike-detection'),
    
    # Endpoint: /api/restock-suggestions/
    path('restock-suggestions/', RestockSuggestionView.as_view(), name='restock-suggestions'),

    # Endpoint: /api/dashboard-summary/
    path('dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    
    # Endpoint: /api/export/ (Adding this since we built it in Step 5!)
    path('export/', ExportCSVView.as_view(), name='export-csv'),
]