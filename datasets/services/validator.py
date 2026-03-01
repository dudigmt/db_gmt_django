import pandas as pd
import os
import json
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
                # Simpan sementara ke disk
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
                'row_count': int(len(self.df)),  # konversi ke int
                'column_count': int(len(self.df.columns)),  # konversi ke int
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
        """Basic validation checks"""
        if self.df is None or self.df.empty:
            self.errors.append("File is empty or could not be read")
            return
        
        if len(self.df) > 100000:  # Max 100k rows
            self.warnings.append(f"Large file: {len(self.df)} rows. Performance may be affected.")
        
        if len(self.df.columns) > 100:  # Max 100 columns
            self.warnings.append(f"Many columns: {len(self.df.columns)} columns.")
    
    def _validate_structure(self):
        """Validate column structure and data types"""
        # Cek untuk kolom yang benar-benar kosong
        empty_cols = self.df.columns[self.df.isnull().all()].tolist()
        if empty_cols:
            self.warnings.append(f"Empty columns detected: {', '.join(empty_cols)}")
        
        # Cek duplicate column names
        if len(self.df.columns) != len(set(self.df.columns)):
            self.errors.append("Duplicate column names found")
    
    def _get_summary(self):
        """Get basic summary statistics"""
        if self.df is None or self.df.empty:
            return {}
        
        summary = {
            'total_rows': int(len(self.df)),
            'total_columns': int(len(self.df.columns)),
            'missing_values': int(self.df.isnull().sum().sum()),
            'memory_usage': float(self.df.memory_usage(deep=True).sum() / (1024 * 1024)),  # MB
        }
        
        # Sample data (first 5 rows) - konversi semua ke serializable
        sample = self.df.head(5).to_dict('records')
        summary['sample'] = self._make_serializable(sample)
        
        return summary