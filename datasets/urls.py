from django.urls import path
from . import views

urlpatterns = [
    path('', views.dataset_list, name='dataset_list'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('<int:pk>/activate/', views.activate_dataset, name='activate_dataset'),
]