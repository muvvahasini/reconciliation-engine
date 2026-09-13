from django.urls import path
from .views import discrepancy_list, tenant_list, health

urlpatterns = [
    path('health/', health),
    path('tenants/', tenant_list),
    path('discrepancies/', discrepancy_list),
]
