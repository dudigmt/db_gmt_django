from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Dataset
from .forms import DatasetUploadForm
from .services.validator import ExcelValidator
from accounts.decorators import role_required
from audit.utils import log_action

@login_required
@role_required(['SuperAdmin', 'Admin', 'Manager'])
def upload_dataset(request):
    """View untuk upload file Excel"""
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Simpan dataset sementara
            dataset = form.save(commit=False)
            dataset.uploaded_by = request.user
            dataset.original_filename = request.FILES['file'].name
            dataset.file_size = request.FILES['file'].size
            dataset.status = 'uploaded'
            dataset.save()
            
            # Log upload
            log_action(request, 'UPLOAD', 
                      f"Uploaded file: {dataset.original_filename}", 
                      {'dataset_id': dataset.pk, 'filename': dataset.original_filename})
            
            # Validasi file
            validator = ExcelValidator(request.FILES['file'])
            validation_result = validator.validate()
            
            # Update dengan hasil validasi
            dataset.row_count = validation_result['row_count']
            dataset.column_count = validation_result['column_count']
            dataset.columns_json = {
                'columns': validation_result['columns'],
                'dtypes': {k: str(v) for k, v in validation_result['dtypes'].items()}  # Pastikan semua string
            }
            # dataset.summary_stats = validation_result['summary']
            dataset.summary_stats = {}  # Simpan object kosong dulu
            
            if validation_result['valid']:
                dataset.status = 'validated'
                messages.success(request, 'File uploaded and validated successfully!')
            else:
                dataset.status = 'rejected'
                dataset.validation_report = '\n'.join(validation_result['errors'])
                messages.error(request, 'File validation failed. Check the report.')
            
            dataset.save()
            
            return redirect('dataset_detail', pk=dataset.pk)
    else:
        form = DatasetUploadForm()
    
    return render(request, 'datasets/upload.html', {'form': form})

@login_required
def dataset_list(request):
    """List all datasets"""
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'datasets/list.html', {'datasets': datasets})

@login_required
def dataset_detail(request, pk):
    """Detail view for a dataset"""
    dataset = get_object_or_404(Dataset, pk=pk)
    return render(request, 'datasets/detail.html', {'dataset': dataset})

@login_required
@role_required(['SuperAdmin', 'Admin'])
def activate_dataset(request, pk):
    """Activate a dataset (only one can be active)"""
    dataset = get_object_or_404(Dataset, pk=pk)
    
    if dataset.status != 'validated':
        messages.error(request, 'Only validated datasets can be activated.')
        return redirect('dataset_detail', pk=pk)
    
    # Log before activation
    old_active = Dataset.objects.filter(status='active').first()
    if old_active:
        log_action(request, 'DEACTIVATE', 
                  f"Deactivated dataset: {old_active.name}", 
                  {'dataset_id': old_active.pk, 'name': old_active.name})
    
    # Deactivate all other datasets
    Dataset.objects.filter(status='active').update(status='validated')
    
    # Activate this one
    dataset.status = 'active'
    dataset.save()
    
    # Log activation
    log_action(request, 'ACTIVATE', 
              f"Activated dataset: {dataset.name}", 
              {'dataset_id': dataset.pk, 'name': dataset.name, 'rows': dataset.row_count})
    
    messages.success(request, f'Dataset "{dataset.name}" is now active.')
    return redirect('dataset_detail', pk=dataset.pk)