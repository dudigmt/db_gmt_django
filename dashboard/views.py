from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datasets.models import Dataset
import json
import random
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from audit.services import audit_utils

@login_required
def dashboard_home(request):
    # Ambil dataset yang active
    active_dataset = Dataset.objects.filter(status='active').first()
    
    # Inisialisasi variabel
    columns_list = []
    dept_data = []
    upload_date = None
    last_update = None
    
    if active_dataset:
        # Ambil columns dari columns_json
        if active_dataset.columns_json:
            columns_list = active_dataset.columns_json.get('columns', [])
        
        # Ambil summary_stats
        summary_stats = active_dataset.summary_stats or {}
        
        # Coba ambil data department dari summary_stats
        # Struktur yang benar: summary_stats['categorical']['dept']['value_counts']
        if 'categorical' in summary_stats and 'dept' in summary_stats['categorical']:
            dept_counts = summary_stats['categorical']['dept'].get('value_counts', {})
            dept_data = [{'name': k, 'count': v} for k, v in dept_counts.items()]
            dept_data.sort(key=lambda x: x['count'], reverse=True)
        # Fallback ke struktur lama (kalau suatu saat berubah)
        elif 'dept' in summary_stats and 'value_counts' in summary_stats['dept']:
            dept_counts = summary_stats['dept']['value_counts']
            dept_data = [{'name': k, 'count': v} for k, v in dept_counts.items()]
            dept_data.sort(key=lambda x: x['count'], reverse=True)
        
        # Metadata
        upload_date = active_dataset.uploaded_at
        last_update = active_dataset.updated_at
    
    # Sample data untuk chart (sementara)
    months = []
    counts = []
    end_date = datetime.now()
    for i in range(11, -1, -1):
        date = end_date - timedelta(days=30*i)
        months.append(date.strftime('%b %Y'))
        counts.append(random.randint(50, 200))
    
    context = {
        'active_dataset': active_dataset,
        'columns_list': columns_list,
        'upload_date': upload_date,
        'last_update': last_update,
        'dept_data': dept_data[:10],  # Top 10 aja
        'chart_months': json.dumps(months),
        'chart_counts': json.dumps(counts),
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def get_department_data(request):
    """API endpoint untuk ambil data department berdasarkan filter"""
    department = request.GET.get('dept', '')
    
    active_dataset = Dataset.objects.filter(status='active').first()
    if not active_dataset or not active_dataset.summary_stats:
        return JsonResponse({'error': 'No active dataset'}, status=404)
    
    summary_stats = active_dataset.summary_stats
    
    # Ambil data department
    if 'categorical' in summary_stats and 'dept' in summary_stats['categorical']:
        dept_counts = summary_stats['categorical']['dept'].get('value_counts', {})
        
        # Filter kalau ada parameter department
        if department and department in dept_counts:
            # Return single department
            return JsonResponse({
                'name': department,
                'count': dept_counts[department]
            })
        else:
            # Return all departments (top 10)
            dept_data = [{'name': k, 'count': v} for k, v in dept_counts.items()]
            dept_data.sort(key=lambda x: x['count'], reverse=True)
            return JsonResponse(dept_data[:10], safe=False)
    
    return JsonResponse({'error': 'No department data'}, status=404)

@login_required
def export_dataset_csv(request):
    """Export active dataset sebagai CSV"""
    active_dataset = Dataset.objects.filter(status='active').first()
    
    if not active_dataset:
        return HttpResponse("No active dataset", status=404)
    
    # Log export
    audit_utils.log_action(request, 'EXPORT', 
              f"Exported dataset: {active_dataset.name} to CSV", 
              {'dataset_id': active_dataset.pk, 'name': active_dataset.name, 'rows': active_dataset.row_count})
    
    # Kita perlu akses file aslinya
    if not active_dataset.file:
        return HttpResponse("Dataset file not found", status=404)
    
    import pandas as pd
    
    # Baca file Excel
    try:
        df = pd.read_excel(active_dataset.file.path)
    except Exception as e:
        return HttpResponse(f"Error reading file: {e}", status=500)
    
    # Buat response CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{active_dataset.name}.csv"'
    
    # Write CSV
    df.to_csv(response, index=False)
    
    return response