from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee
from .services import import_service
from datasets.models import Dataset
from .services import employee_service

@login_required
def dashboard(request):
    context = employee_service.get_dashboard_stats()
    return render(request, 'hr/dashboard.html', context)

@login_required
def employee_list(request):
    page_obj = employee_service.get_employee_list(request)
    context = {
        'page_obj': page_obj,
        'search_query': request.GET.get('search', ''),
    }
    return render(request, 'hr/employee_list.html', context)

@login_required
def employee_detail(request, nik):
    employee = employee_service.get_employee_by_nik(nik)
    if not employee:
        messages.error(request, 'Employee not found')
        return redirect('hr:employee_list')
    return render(request, 'hr/employee_detail.html', {'employee': employee})

@login_required
def employee_edit(request, nik):
    return HttpResponse(f"Edit employee {nik}")

@login_required
def employee_add(request):
    return HttpResponse("Add new employee")

@login_required
def import_preview(request):
    """Preview data dari active dataset sebelum import"""
    
    active_dataset = import_service.get_active_dataset()
    
    if not active_dataset:
        messages.warning(request, "Tidak ada dataset dengan status 'active'.")
        return render(request, 'hr/import_preview.html', {'no_dataset': True})
    
    preview_data = import_service.preview_import(active_dataset)
    
    if preview_data and 'error' in preview_data:
        messages.error(request, f"Error reading dataset: {preview_data['error']}")
        return render(request, 'hr/import_preview.html', {'no_dataset': True})
    
    context = {
        'dataset': active_dataset,
        'columns': preview_data.get('columns', []),
        'sample_rows': preview_data.get('sample', []),
        'total_rows': preview_data.get('total_rows', 0),
    }
    
    return render(request, 'hr/import_preview.html', context)

@login_required
def import_execute(request):
    if request.method != 'POST':
        return redirect('hr:import_preview')
    
    update_duplicate = request.POST.get('update_duplicate') == 'on'
    active_dataset = import_service.get_active_dataset()
    
    if not active_dataset:
        messages.error(request, "No active dataset found")
        return redirect('hr:import_preview')
    
    stats, errors = import_service.import_from_dataset(
        dataset=active_dataset,
        update_duplicate=update_duplicate,
        user=request.user
    )
    
    if stats:
        messages.success(
            request, 
            f"Import completed: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped"
        )
    else:
        messages.error(request, f"Import failed: {errors}")
    
    return redirect('hr:employee_list')

@login_required
def api_employee_list(request):
    return HttpResponse("API endpoint for employees")