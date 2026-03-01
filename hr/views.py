from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee
from .services import import_service
from datasets.models import Dataset

@login_required
def dashboard(request):
    context = {
        'total_employees': Employee.objects.count(),
        'active_employees': Employee.objects.filter(status_kerja='Aktif').count(),
        'contract_employees': Employee.objects.filter(status_karyawan='Kontrak').count(),
        'permanent_employees': Employee.objects.filter(status_karyawan='Tetap').count(),
        'active_count': Employee.objects.filter(status_kerja='Aktif').count(),
        'contract_count': Employee.objects.filter(status_karyawan='Kontrak').count(),
        'permanent_count': Employee.objects.filter(status_karyawan='Tetap').count(),
    }
    return render(request, 'hr/dashboard.html', context)

@login_required
def employee_list(request):
    # Ambil semua employee
    employees = Employee.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(nik__icontains=search_query) |
            Q(nama__icontains=search_query) |
            Q(dept__icontains=search_query)
        )
    
    # Filter
    dept = request.GET.get('dept', '')
    if dept:
        employees = employees.filter(dept=dept)
    
    status_karyawan = request.GET.get('status_karyawan', '')
    if status_karyawan:
        employees = employees.filter(status_karyawan=status_karyawan)
    
    status_kerja = request.GET.get('status_kerja', '')
    if status_kerja:
        employees = employees.filter(status_kerja=status_kerja)
    
    # Pagination
    paginator = Paginator(employees, 20)  # 20 per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Ambil list unique untuk filter dropdown
    dept_list = Employee.objects.values_list('dept', flat=True).distinct().order_by('dept')
    status_karyawan_list = Employee.objects.values_list('status_karyawan', flat=True).distinct()
    status_kerja_list = Employee.objects.values_list('status_kerja', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'dept_list': dept_list,
        'status_karyawan_list': status_karyawan_list,
        'status_kerja_list': status_kerja_list,
        'selected_dept': dept,
        'selected_status_karyawan': status_karyawan,
        'selected_status_kerja': status_kerja,
    }
    return render(request, 'hr/employee_list.html', context)

@login_required
def employee_detail(request, nik):
    return HttpResponse(f"Detail for employee {nik}")

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