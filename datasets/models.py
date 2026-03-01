import os
import json
import pandas as pd
from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Dataset(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('validated', 'Validated'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    row_count = models.IntegerField(null=True, blank=True)
    column_count = models.IntegerField(null=True, blank=True)
    columns_json = models.JSONField(null=True, blank=True)
    summary_stats = models.JSONField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['status', 'uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        if self.status == 'active':
            Dataset.objects.filter(status='active').exclude(pk=self.pk).update(status='validated')
        super().save(*args, **kwargs)
    
    def calculate_summary_stats(self):
        if not self.file:
            return False
        
        try:
            file_path = self.file.path
            df = pd.read_excel(file_path)
            
            # Simpan columns ke columns_json
            self.columns_json = {
                'columns': list(df.columns),
                'dtypes': df.dtypes.astype(str).to_dict()
            }
            
            # Hitung stats dasar
            stats = {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'memory_usage': float(df.memory_usage(deep=True).sum() / 1024**2),
                'missing_values': int(df.isna().sum().sum()),
            }
            
            # Kategori stats
            categorical_stats = {}
            for col in df.select_dtypes(include=['object']).columns:
                value_counts = df[col].value_counts().head(20).to_dict()
                value_counts = {str(k): int(v) for k, v in value_counts.items()}
                categorical_stats[col] = {
                    'unique_count': int(df[col].nunique()),
                    'value_counts': value_counts
                }
            stats['categorical'] = categorical_stats
            
            # Numeric stats
            numeric_stats = {}
            for col in df.select_dtypes(include=['number']).columns:
                numeric_stats[col] = {
                    'min': float(df[col].min()) if pd.notna(df[col].min()) else None,
                    'max': float(df[col].max()) if pd.notna(df[col].max()) else None,
                    'mean': float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                    'median': float(df[col].median()) if pd.notna(df[col].median()) else None,
                }
            stats['numeric'] = numeric_stats
            
            # Sample data - CONVERSION FIX
            sample = df.head(5).to_dict('records')
            
            # DEBUG: lihat sebelum konversi
            print("\n=== DEBUG: SAMPLE BEFORE CONVERSION ===")
            for i, row in enumerate(sample):
                print(f"Row {i}:")
                for key, value in row.items():
                    print(f"  {key}: {value} (type: {type(value)})")
            
            # Konversi semua nilai ke tipe yang JSON serializable
            for row in sample:
                for key, value in row.items():
                    if pd.isna(value):
                        row[key] = None
                    elif isinstance(value, (datetime, pd.Timestamp)):
                        row[key] = value.strftime('%Y-%m-%d %H:%M:%S')  # Pakai string format
                        print(f"  Converted datetime: {key} -> {row[key]}")
                    elif hasattr(value, 'item'):  # numpy types
                        try:
                            row[key] = value.item()
                        except:
                            row[key] = str(value)
                    elif isinstance(value, (pd.Int64Dtype, pd.Float64Dtype)):
                        row[key] = float(value)
                    elif not isinstance(value, (str, int, float, bool, type(None), list, dict)):
                        row[key] = str(value)
                        print(f"  Converted other: {key} -> {row[key]}")
            
            # DEBUG: lihat setelah konversi
            print("\n=== DEBUG: SAMPLE AFTER CONVERSION ===")
            for i, row in enumerate(sample):
                print(f"Row {i}:")
                for key, value in row.items():
                    print(f"  {key}: {value} (type: {type(value)})")
            
            stats['sample'] = sample
            
            # Simpan summary_stats
            self.summary_stats = stats
            
            # Update counts
            self.row_count = int(len(df))
            self.column_count = int(len(df.columns))
            
            self.save()
            print("=== DEBUG: SAVE SUCCESS ===")
            return True
            
        except Exception as e:
            print(f"Error calculating stats: {e}")
            import traceback
            traceback.print_exc()
            return False