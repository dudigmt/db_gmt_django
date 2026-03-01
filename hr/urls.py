from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Employee list & detail
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<str:nik>/', views.employee_detail, name='employee_detail'),
    path('employees/<str:nik>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/add/', views.employee_add, name='employee_add'),
    
    # Import
    path('import/', views.import_preview, name='import_preview'),
    path('import/execute/', views.import_execute, name='import_execute'),
    
    # API endpoints (for HTMX)
    path('api/employees/', views.api_employee_list, name='api_employee_list'),
]