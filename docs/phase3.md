PHASE 3: DATASET ENGINE - Complete Step by Step
📁 Struktur Akhir Proyek (Tambahan dari Phase 2)
text
/home/adung/projects/company_system/
├── datasets/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── services/
│   │   └── validator.py
│   ├── templates/
│   │   └── datasets/
│   │       ├── upload.html
│   │       ├── list.html
│   │       └── detail.html
│   ├── templatetags/
│   │   └── dataset_filters.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── media/
│   └── datasets/              # Folder untuk file upload
├── company_system/
│   ├── settings.py             # + MEDIA_URL & MEDIA_ROOT
│   └── urls.py                 # + datasets URLs + media serving
└── requirements.txt            # + pandas, openpyxl
🚀 Step 1: Buat App Datasets
bash
python manage.py startapp datasets
⚙️ Step 2: Daftarkan App Datasets di settings.py
Edit company_system/settings.py:

python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'datasets',   # <-- tambah ini
]
📦 Step 3: Install Library untuk Excel
bash
pip install pandas openpyxl
pip freeze > requirements.txt
🗃️ Step 4: Buat Model Dataset
Edit datasets/models.py:

python
from django.db import models
from django.contrib.auth.models import User
import pandas as pd
import os

class Dataset(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('validated', 'Validated'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='datasets/')
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='File size in bytes')
    row_count = models.IntegerField(null=True, blank=True)
    column_count = models.IntegerField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    validation_report = models.TextField(blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    columns_json = models.JSONField(default=dict, help_text='Column names and types')
    summary_stats = models.JSONField(default=dict, help_text='Basic statistics')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def get_file_extension(self):
        return os.path.splitext(self.original_filename)[1].lower()
    
    def is_active(self):
        return self.status == 'active'
🔄 Step 5: Migrasi Model Dataset
bash
python manage.py makemigrations datasets
python manage.py migrate datasets
🎛️ Step 6: Register Dataset di Admin
Edit datasets/admin.py:

python
from django.contrib import admin
from .models import Dataset

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'row_count', 'column_count', 'uploaded_by', 'uploaded_at')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('name', 'description')
    readonly_fields = ('file_size', 'row_count', 'column_count', 'uploaded_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'file', 'status')
        }),
        ('File Details', {
            'fields': ('original_filename', 'file_size', 'row_count', 'column_count')
        }),
        ('Metadata', {
            'fields': ('columns_json', 'summary_stats', 'validation_report')
        }),
        ('Audit', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at')
        }),
    )
📁 Step 7: Setup Media Files
Edit company_system/settings.py (tambah di bagian bawah):

python
# Media files (user uploads)
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
Edit company_system/urls.py:

python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('accounts.urls')),
    path('datasets/', include('datasets.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
📝 Step 8: Buat Form Upload
Buat file datasets/forms.py:

python
from django import forms
from .models import Dataset

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Cek ekstensi file
            ext = file.name.split('.')[-1].lower()
            if ext not in ['xlsx', 'xls']:
                raise forms.ValidationError('Only Excel files (.xlsx, .xls) are allowed.')
            
            # Cek ukuran file (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
        
        return file
🔧 Step 9: Buat Service Validator
Buat folder dan file:

bash
mkdir -p datasets/services
Buat file datasets/services/validator.py:

python
import pandas as pd
import os
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

class ExcelValidator:
    """Service untuk validasi file Excel"""
    
    def __init__(self, file):
        self.file = file
        self.df = None
        self.errors = []
        self.warnings = []
    
    def _convert_to_serializable(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        return obj
    
    def _make_serializable(self, data):
        """Recursively convert data to JSON serializable format"""
        if isinstance(data, dict):
            return {key: self._make_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(self._make_serializable(item) for item in data)
        else:
            return self._convert_to_serializable(data)
        
    def validate(self):
        """Main validation method"""
        try:
            # Baca file Excel
            if isinstance(self.file, (InMemoryUploadedFile, TemporaryUploadedFile)):
                temp_path = f'/tmp/{self.file.name}'
                with open(temp_path, 'wb+') as destination:
                    for chunk in self.file.chunks():
                        destination.write(chunk)
                self.df = pd.read_excel(temp_path)
                os.remove(temp_path)
            else:
                self.df = pd.read_excel(self.file)
            
            # Validasi dasar
            self._validate_basic()
            
            # Validasi struktur
            self._validate_structure()
            
            # Konversi dtypes ke string (JSON friendly)
            dtypes = {}
            for col in self.df.columns:
                dtypes[col] = str(self.df[col].dtype)
            
            result = {
                'valid': len(self.errors) == 0,
                'errors': self.errors,
                'warnings': self.warnings,
                'row_count': int(len(self.df)),
                'column_count': int(len(self.df.columns)),
                'columns': list(self.df.columns),
                'dtypes': dtypes,
                'summary': self._make_serializable(self._get_summary())
            }
            
            return result
            
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return {
                'valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'dtypes': {},
                'summary': {}
            }
    
    def _validate_basic(self):
        if self.df is None or self.df.empty:
            self.errors.append("File is empty or could not be read")
            return
        
        if len(self.df) > 100000:
            self.warnings.append(f"Large file: {len(self.df)} rows. Performance may be affected.")
        
        if len(self.df.columns) > 100:
            self.warnings.append(f"Many columns: {len(self.df.columns)} columns.")
    
    def _validate_structure(self):
        empty_cols = self.df.columns[self.df.isnull().all()].tolist()
        if empty_cols:
            self.warnings.append(f"Empty columns detected: {', '.join(empty_cols)}")
        
        if len(self.df.columns) != len(set(self.df.columns)):
            self.errors.append("Duplicate column names found")
    
    def _get_summary(self):
        if self.df is None or self.df.empty:
            return {}
        
        summary = {
            'total_rows': int(len(self.df)),
            'total_columns': int(len(self.df.columns)),
            'missing_values': int(self.df.isnull().sum().sum()),
            'memory_usage': float(self.df.memory_usage(deep=True).sum() / (1024 * 1024)),
        }
        
        sample = self.df.head(5).to_dict('records')
        summary['sample'] = self._make_serializable(sample)
        
        return summary
👁️ Step 10: Buat Views
Edit datasets/views.py:

python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Dataset
from .forms import DatasetUploadForm
from .services.validator import ExcelValidator
from accounts.decorators import role_required

@login_required
@role_required(['SuperAdmin', 'Admin', 'Manager'])
def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.uploaded_by = request.user
            dataset.original_filename = request.FILES['file'].name
            dataset.file_size = request.FILES['file'].size
            dataset.status = 'uploaded'
            dataset.save()
            
            validator = ExcelValidator(request.FILES['file'])
            validation_result = validator.validate()
            
            dataset.row_count = validation_result['row_count']
            dataset.column_count = validation_result['column_count']
            dataset.columns_json = {
                'columns': validation_result['columns'],
                'dtypes': validation_result['dtypes']
            }
            dataset.summary_stats = validation_result['summary']
            
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
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'datasets/list.html', {'datasets': datasets})

@login_required
def dataset_detail(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    return render(request, 'datasets/detail.html', {'dataset': dataset})

@login_required
@role_required(['SuperAdmin', 'Admin'])
def activate_dataset(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    
    if dataset.status != 'validated':
        messages.error(request, 'Only validated datasets can be activated.')
        return redirect('dataset_detail', pk=pk)
    
    Dataset.objects.filter(status='active').update(status='validated')
    
    dataset.status = 'active'
    dataset.save()
    
    messages.success(request, f'Dataset "{dataset.name}" is now active.')
    return redirect('dataset_detail', pk=pk)
🎨 Step 11: Buat Template Upload
Buat folder templates:

bash
mkdir -p datasets/templates/datasets
Buat file datasets/templates/datasets/upload.html:

html
{% extends 'base.html' %}

{% block title %}Upload Dataset{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h1 class="text-2xl font-bold mb-6">Upload Dataset</h1>
        
        {% if messages %}
            {% for message in messages %}
                <div class="mb-4 p-3 {% if message.tags == 'error' %}bg-red-100 text-red-700{% else %}bg-green-100 text-green-700{% endif %} rounded">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
        
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            
            <div class="mb-4">
                <label class="block text-gray-700 dark:text-gray-300 mb-2">Dataset Name</label>
                {{ form.name }}
                {% if form.name.errors %}
                    <p class="text-red-600 text-sm mt-1">{{ form.name.errors.0 }}</p>
                {% endif %}
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 dark:text-gray-300 mb-2">Description</label>
                {{ form.description }}
                {% if form.description.errors %}
                    <p class="text-red-600 text-sm mt-1">{{ form.description.errors.0 }}</p>
                {% endif %}
            </div>
            
            <div class="mb-6">
                <label class="block text-gray-700 dark:text-gray-300 mb-2">Excel File</label>
                {{ form.file }}
                <p class="text-sm text-gray-500 mt-1">Accepted formats: .xlsx, .xls (max 10MB)</p>
                {% if form.file.errors %}
                    <p class="text-red-600 text-sm mt-1">{{ form.file.errors.0 }}</p>
                {% endif %}
            </div>
            
            <div class="flex items-center space-x-4">
                <button type="submit" 
                        class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                    Upload & Validate
                </button>
                <a href="{% url 'dataset_list' %}" 
                   class="text-gray-600 dark:text-gray-400 hover:underline">
                    Cancel
                </a>
            </div>
        </form>
        
        <div class="mt-6 p-4 bg-blue-50 dark:bg-gray-700 rounded">
            <h3 class="font-semibold mb-2">File Requirements:</h3>
            <ul class="list-disc list-inside text-sm space-y-1">
                <li>Excel files only (.xlsx, .xls)</li>
                <li>Maximum file size: 10MB</li>
                <li>Maximum rows: 100,000</li>
                <li>Maximum columns: 100</li>
                <li>First row should contain column headers</li>
            </ul>
        </div>
    </div>
</div>
{% endblock %}
📋 Step 12: Buat Template List
Buat file datasets/templates/datasets/list.html:

html
{% extends 'base.html' %}

{% block title %}Datasets{% endblock %}

{% block content %}
<div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Datasets</h1>
        <a href="{% url 'upload_dataset' %}" 
           class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            + Upload New
        </a>
    </div>
    
    {% if messages %}
        {% for message in messages %}
            <div class="mb-4 p-3 {% if message.tags == 'error' %}bg-red-100 text-red-700{% else %}bg-green-100 text-green-700{% endif %} rounded">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    
    <div class="overflow-x-auto">
        <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                    <th class="px-4 py-2 text-left">Name</th>
                    <th class="px-4 py-2 text-left">Status</th>
                    <th class="px-4 py-2 text-left">Rows</th>
                    <th class="px-4 py-2 text-left">Columns</th>
                    <th class="px-4 py-2 text-left">Uploaded By</th>
                    <th class="px-4 py-2 text-left">Date</th>
                    <th class="px-4 py-2 text-left">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for dataset in datasets %}
                <tr class="border-t dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td class="px-4 py-3">{{ dataset.name }}</td>
                    <td class="px-4 py-3">
                        <span class="px-2 py-1 text-xs rounded-full 
                            {% if dataset.status == 'active' %}bg-green-100 text-green-800
                            {% elif dataset.status == 'validated' %}bg-blue-100 text-blue-800
                            {% elif dataset.status == 'uploaded' %}bg-yellow-100 text-yellow-800
                            {% elif dataset.status == 'rejected' %}bg-red-100 text-red-800
                            {% endif %}">
                            {{ dataset.get_status_display }}
                        </span>
                    </td>
                    <td class="px-4 py-3">{{ dataset.row_count|default:'-' }}</td>
                    <td class="px-4 py-3">{{ dataset.column_count|default:'-' }}</td>
                    <td class="px-4 py-3">{{ dataset.uploaded_by.username }}</td>
                    <td class="px-4 py-3">{{ dataset.uploaded_at|date:'Y-m-d H:i' }}</td>
                    <td class="px-4 py-3">
                        <a href="{% url 'dataset_detail' dataset.pk %}" 
                           class="text-blue-600 hover:underline">View</a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                        No datasets yet. 
                        <a href="{% url 'upload_dataset' %}" class="text-blue-600 hover:underline">
                            Upload your first dataset
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
🔍 Step 13: Buat Template Detail
Buat file datasets/templates/datasets/detail.html:

html
{% extends 'base.html' %}
{% load dataset_filters %}

{% block title %}Dataset: {{ dataset.name }}{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <!-- Header with actions -->
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">{{ dataset.name }}</h1>
        <div class="space-x-2">
            <a href="{% url 'dataset_list' %}" 
               class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
                Back to List
            </a>
            {% if dataset.status == 'validated' and user.profile.role in 'SuperAdmin,Admin' %}
            <a href="{% url 'activate_dataset' dataset.pk %}" 
               class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
               onclick="return confirm('Activate this dataset? This will deactivate any currently active dataset.')">
                Activate Dataset
            </a>
            {% endif %}
        </div>
    </div>
    
    {% if messages %}
        {% for message in messages %}
            <div class="mb-4 p-3 {% if message.tags == 'error' %}bg-red-100 text-red-700{% else %}bg-green-100 text-green-700{% endif %} rounded">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    
    <!-- Status Banner -->
    <div class="mb-6 p-4 rounded-lg 
        {% if dataset.status == 'active' %}bg-green-100 text-green-800
        {% elif dataset.status == 'validated' %}bg-blue-100 text-blue-800
        {% elif dataset.status == 'uploaded' %}bg-yellow-100 text-yellow-800
        {% elif dataset.status == 'rejected' %}bg-red-100 text-red-800
        {% endif %}">
        <div class="flex items-center">
            <span class="font-semibold mr-2">Status:</span>
            <span class="px-2 py-1 rounded-full text-sm font-medium 
                {% if dataset.status == 'active' %}bg-green-200 text-green-800
                {% elif dataset.status == 'validated' %}bg-blue-200 text-blue-800
                {% elif dataset.status == 'uploaded' %}bg-yellow-200 text-yellow-800
                {% elif dataset.status == 'rejected' %}bg-red-200 text-red-800
                {% endif %}">
                {{ dataset.get_status_display }}
            </span>
        </div>
        {% if dataset.validation_report %}
        <div class="mt-2 text-sm">
            <strong>Validation Report:</strong>
            <pre class="mt-1 whitespace-pre-wrap">{{ dataset.validation_report }}</pre>
        </div>
        {% endif %}
    </div>
    
    <!-- Main Info -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Dataset Information</h2>
            <dl class="space-y-2">
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Description:</dt>
                    <dd class="w-2/3">{{ dataset.description|default:'No description' }}</dd>
                </div>
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Filename:</dt>
                    <dd class="w-2/3">{{ dataset.original_filename }}</dd>
                </div>
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">File Size:</dt>
                    <dd class="w-2/3">{{ dataset.file_size|filesizeformat }}</dd>
                </div>
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Uploaded:</dt>
                    <dd class="w-2/3">{{ dataset.uploaded_at|date:'Y-m-d H:i:s' }}</dd>
                </div>
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Uploaded By:</dt>
                    <dd class="w-2/3">{{ dataset.uploaded_by.username }}</dd>
                </div>
            </dl>
        </div>
        
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Statistics</h2>
            <dl class="space-y-2">
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Rows:</dt>
                    <dd class="w-2/3">{{ dataset.row_count|default:'-' }}</dd>
                </div>
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Columns:</dt>
                    <dd class="w-2/3">{{ dataset.column_count|default:'-' }}</dd>
                </div>
                {% if dataset.summary_stats.missing_values %}
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Missing Values:</dt>
                    <dd class="w-2/3">{{ dataset.summary_stats.missing_values }}</dd>
                </div>
                {% endif %}
                {% if dataset.summary_stats.memory_usage %}
                <div class="flex">
                    <dt class="w-1/3 text-gray-600 dark:text-gray-400">Memory Usage:</dt>
                    <dd class="w-2/3">{{ dataset.summary_stats.memory_usage|floatformat:2 }} MB</dd>
                </div>
                {% endif %}
            </dl>
        </div>
    </div>
    
    <!-- Columns Info -->
    {% if dataset.columns_json.columns %}
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-6">
        <h2 class="text-lg font-semibold mb-4">Columns</h2>
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-50 dark:bg-gray-700">
                    <tr>
                        <th class="px-4 py-2 text-left">Column Name</th>
                        <th class="px-4 py-2 text-left">Data Type</th>
                    </tr>
                </thead>
                <tbody>
                    {% for column in dataset.columns_json.columns %}
                    <tr class="border-t dark:border-gray-700">
                        <td class="px-4 py-2">{{ column }}</td>
                        <td class="px-4 py-2">
                            {{ dataset.columns_json.dtypes|get_item:column|default:'unknown' }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
    
    <!-- Sample Data -->
    {% if dataset.summary_stats.sample %}
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 class="text-lg font-semibold mb-4">Sample Data (First 5 rows)</h2>
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-50 dark:bg-gray-700">
                    <tr>
                        {% for col in dataset.columns_json.columns|slice:":5" %}
                        <th class="px-4 py-2 text-left">{{ col|truncatechars:20 }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in dataset.summary_stats.sample %}
                    <tr class="border-t dark:border-gray-700">
                        {% for col in dataset.columns_json.columns|slice:":5" %}
                        <td class="px-4 py-2">{{ row|get_item:col|default:'-'|truncatechars:30 }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
🧩 Step 14: Buat Template Filter
Buat folder dan file:

bash
mkdir -p datasets/templatetags
Buat file datasets/templatetags/dataset_filters.py:

python
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key"""
    if dictionary and key:
        return dictionary.get(key)
    return None
🔗 Step 15: Setup URLs
Buat file datasets/urls.py:

python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dataset_list, name='dataset_list'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('<int:pk>/activate/', views.activate_dataset, name='activate_dataset'),
]
🧭 Step 16: Update Base Template dengan Link Datasets
Edit core/templates/base.html, tambahkan di navbar:

html
<a href="{% url 'dataset_list' %}" 
   class="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700">
    Datasets
</a>
✅ Checkpoint 3: Dataset Engine Complete
No	Item	Status
1	App datasets dibuat	✅
2	Model Dataset dengan JSONField	✅
3	Upload Excel (pandas)	✅
4	Validasi struktur file	✅
5	Metadata tersimpan (rows, columns, dtypes)	✅
6	Status management (uploaded → validated → active)	✅
7	Hanya satu dataset yang bisa active	✅
8	Role-based access untuk aktivasi	✅
9	Template upload, list, detail	✅
10	Custom template filter	✅
📌 Catatan Penting
Upload path: File tersimpan di media/datasets/

Validasi: Pandas membaca file, hasil disimpan di columns_json dan summary_stats

Aktivasi: Hanya SuperAdmin/Admin yang bisa mengaktifkan dataset

JSON serializable: Semua data numpy/pandas dikonversi ke tipe Python standar

🔜 Next: Phase 4 - Dashboard Layer
Summary metrics dari dataset active

Trend chart (Chart.js)

Division breakdown

Filter system

CSV export