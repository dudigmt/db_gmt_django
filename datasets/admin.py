from django.contrib import admin
from .models import Dataset

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'row_count', 'column_count', 'uploaded_by', 'uploaded_at')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('name',)
    readonly_fields = ('row_count', 'column_count', 'uploaded_at', 'updated_at', 'columns_json', 'summary_stats')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'file', 'status')
        }),
        ('File Details', {
            'fields': ('row_count', 'column_count')
        }),
        ('Metadata', {
            'fields': ('columns_json', 'summary_stats')
        }),
        ('Audit', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at')
        }),
    )