from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('api/dept-data/', views.get_department_data, name='dept_api'),
    path('export-csv/', views.export_dataset_csv, name='export_csv'),
]