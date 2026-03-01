from ..models import Employee
from django.db.models import Q
from django.core.paginator import Paginator

def get_dashboard_stats():
    """Return dashboard statistics for HR"""
    return {
        'total_employees': Employee.objects.count(),
        'active_employees': Employee.objects.filter(status_kerja='Aktif').count(),
        'contract_employees': Employee.objects.filter(status_karyawan='Kontrak').count(),
        'permanent_employees': Employee.objects.filter(status_karyawan='Tetap').count(),
        'active_count': Employee.objects.filter(status_kerja='Aktif').count(),
        'contract_count': Employee.objects.filter(status_karyawan='Kontrak').count(),
        'permanent_count': Employee.objects.filter(status_karyawan='Tetap').count(),
    }

def get_employee_list(request):
    """Return paginated employee list based on search query"""
    search_query = request.GET.get('search', '')
    employees = Employee.objects.all()
    
    if search_query:
        employees = employees.filter(
            Q(nama__icontains=search_query) |
            Q(nik__icontains=search_query) |
            Q(jabatan__icontains=search_query)
        )
    
    paginator = Paginator(employees, 25)
    page_number = request.GET.get('page', 1)
    return paginator.get_page(page_number)

def get_employee_by_nik(nik):
    """Get employee by NIK"""
    try:
        return Employee.objects.get(nik=nik)
    except Employee.DoesNotExist:
        return None