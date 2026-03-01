from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['nik', 'nama', 'dept', 'jabatan', 'status_kerja']
    list_filter = ['dept', 'status_karyawan', 'status_kerja']
    search_fields = ['nik', 'nama', 'no_ktp']
    readonly_fields = ['imported_at', 'updated_at']