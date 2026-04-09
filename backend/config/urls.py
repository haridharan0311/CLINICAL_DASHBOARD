from django.contrib import admin
from django.urls import include, path
from api.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # This automatically prefixes all URLs from api.urls with /api/
    # E.g., 'disease-trends/' becomes '/api/disease-trends/'
    path('api/', include('api.urls')),
    
    # JWT Authentication Endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
