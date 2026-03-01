import pandas as pd
from datetime import datetime, timedelta
from django.db import transaction
from datasets.models import Dataset
from hr.models import Employee
from audit.models import AuditLog

def get_active_dataset():
    """Ambil dataset dengan status 'active'"""
    return Dataset.objects.filter(status='active').first()

def parse_excel_date(val):
    """Handle Excel serial date (numeric) or string date"""
    if pd.isna(val) or val == '' or val is None:
        return None
    
    # Kalau sudah berupa string datetime (isoformat)
    if isinstance(val, str):
        try:
            # Coba parse string format ISO
            if 'T' in val:
                return datetime.fromisoformat(val.split('T')[0]).date()
            else:
                return datetime.strptime(val, '%Y-%m-%d').date()
        except:
            return None
    
    # Kalau angka (Excel serial)
    if isinstance(val, (int, float)):
        try:
            # Excel serial date: 45270 -> 2023-12-07
            base = datetime(1899, 12, 30)
            return (base + timedelta(days=float(val))).date()
        except:
            return None
    
    # Kalau sudah datetime object
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    
    return None

def get_val(row, key, default=''):
    """Safe get value from row, handle NaN"""
    val = row.get(key)
    if pd.isna(val):
        return default
    
    # Handle numeric values that should be strings (NIK, KTP, etc)
    if key in ['nik', 'no_ktp', 'no_kk', 'no_npwp', 'no_rek_bank', 'no_hp', 'kode_pos', 'bpjs_tk_no', 'bpjs_kes_no']:
        if isinstance(val, (int, float)):
            # Kalau angka bulat, convert ke integer dulu baru string (biar ga ada .0)
            if val == int(val):
                return str(int(val))
            return str(val)
    
    return val

def map_row_to_employee(row, dataset):
    """Mapping dari struktur Excel ke Employee model"""
    
    # Debug: print tipe data tgl_rekrut
    tgl_rekrut_val = get_val(row, 'tgl_rekrut')
    print(f"Row {row.get('nik')}: tgl_rekrut = {tgl_rekrut_val} (type: {type(tgl_rekrut_val)})")
    
    return Employee(
        # Basic
        nik=get_val(row, 'nik'),
        nama=get_val(row, 'nama'),
        
        # Personal
        sex=get_val(row, 'sex'),
        tgl_lahir=parse_excel_date(get_val(row, 'tgl_lahir')),
        tempat_lahir=get_val(row, 'tempat_lahir'),
        no_ktp=get_val(row, 'no_ktp'),
        no_kk=get_val(row, 'no_kk'),
        no_hp=get_val(row, 'no_hp'),
        alamat=get_val(row, 'alamat'),
        kelurahan=get_val(row, 'kelurahan'),
        kecamatan=get_val(row, 'kecamatan'),
        kabupaten=get_val(row, 'kabupaten_kota'),  # Mapping dari kolom Excel
        provinsi=get_val(row, 'provinsi'),
        kode_pos=get_val(row, 'kode_pos'),
        
        # Employment
        dept=get_val(row, 'dept'),
        jabatan=get_val(row, 'jabatan'),
        tgl_rekrut=parse_excel_date(tgl_rekrut_val),
        status_karyawan=get_val(row, 'status_karyawan'),
        tgl_kartetap=parse_excel_date(get_val(row, 'tgl_kartetap')),
        kontrak_ke=int(get_val(row, 'kontrak_ke', 0) or 0),
        kontrak_berakhir=parse_excel_date(get_val(row, 'kontrak_berakhir')),
        
        # Financial
        kode_gaji=get_val(row, 'kode_gaji'),
        no_rek_bank=get_val(row, 'no_rek_bank'),
        kode_bank=get_val(row, 'kode_bank'),
        nama_bank=get_val(row, 'nama_bank'),
        status_ptkp=get_val(row, 'status_ptkp'),
        no_npwp=get_val(row, 'no_npwp'),
        
        # BPJS
        bpjs_tk=True if get_val(row, 'bpjs_tk') == 'Ya' else False,
        bpjs_tk_no=get_val(row, 'bpjs_tk_no'),
        bpjs_tk_ditanggung=get_val(row, 'bpjs_tk_ditanggung'),
        bpjs_kes=True if get_val(row, 'bpjs_kes') == 'Ya' else False,
        bpjs_kes_no=get_val(row, 'bpjs_kes_no'),
        bpjs_kes_ditanggung=get_val(row, 'bpjs_kes_ditanggung'),
        
        # Status
        status_kerja=get_val(row, 'status_kerja', 'Aktif'),
        tgl_out=parse_excel_date(get_val(row, 'tgl_out')),
        
        # Metadata
        imported_from=dataset
    )

@transaction.atomic
def import_from_dataset(dataset=None, update_duplicate=False, user=None):
    """
    Import data dari dataset ke Employee
    Returns: (stats, errors)
    """
    if not dataset:
        dataset = get_active_dataset()
    
    if not dataset:
        return None, "No active dataset found"
    
    try:
        # Baca file Excel
        file_path = dataset.file.path
        df = pd.read_excel(file_path)
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'total': len(df)}
        errors = []
        
        print(f"\n=== Starting import from {dataset.name} ===")
        
        for idx, row in df.iterrows():
            try:
                nik = get_val(row, 'nik', '')
                if not nik:
                    print(f"Row {idx+2}: No NIK, skipped")
                    stats['skipped'] += 1
                    continue
                
                # Cek existing
                existing = Employee.objects.filter(nik=nik).first()
                
                if existing and not update_duplicate:
                    print(f"Row {idx+2}: NIK {nik} exists, skipped")
                    stats['skipped'] += 1
                    continue
                
                # Mapping data
                employee_data = map_row_to_employee(row.to_dict(), dataset)
                
                if existing and update_duplicate:
                    # Update existing
                    for field, value in employee_data.__dict__.items():
                        if field not in ['_state', 'id', 'nik', 'imported_at']:
                            setattr(existing, field, value)
                    existing.imported_from = dataset
                    existing.save()
                    stats['updated'] += 1
                    print(f"Row {idx+2}: NIK {nik} updated")
                else:
                    # Create new
                    employee_data.save()
                    stats['created'] += 1
                    print(f"Row {idx+2}: NIK {nik} created")
                    
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
                stats['skipped'] += 1
                print(f"Row {idx+2}: ERROR - {str(e)}")
        
        # Log ke audit - sesuaikan dengan model AuditLog
        try:
            AuditLog.objects.create(
                user=user,
                action='UPLOAD',  # Pakai action yang sudah ada
                description=f"Imported {stats['created']} employees, {stats['updated']} updated, {stats['skipped']} skipped from dataset {dataset.name}",
                data={
                    'dataset_id': dataset.id,
                    'dataset_name': dataset.name,
                    'stats': stats,
                    'errors': errors[:5] if errors else []
                }
            )
        except Exception as e:
            # Kalau audit log gagal, tetep lanjut tapi catat error
            errors.append(f"Audit log failed: {str(e)}")
        
        print(f"\n=== Import completed: {stats} ===")
        return stats, errors
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, str(e)

def preview_import(dataset=None, limit=10):
    """
    Preview data sebelum import
    Returns: dict with columns, total_rows, and sample rows
    """
    if not dataset:
        dataset = get_active_dataset()
    
    if not dataset:
        return None
    
    try:
        file_path = dataset.file.path
        df = pd.read_excel(file_path)
        
        # Ambil sample
        sample = df.head(limit).to_dict('records')
        
        # Clean NaN values for JSON serialization
        for row in sample:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
                elif isinstance(value, (datetime, pd.Timestamp)):
                    row[key] = value.isoformat()
                elif isinstance(value, (int, float)) and key in ['nik', 'no_ktp', 'no_kk', 'no_npwp', 'no_rek_bank']:
                    # Convert large numbers to string to avoid scientific notation
                    if value == int(value):
                        row[key] = str(int(value))
        
        return {
            'columns': list(df.columns),
            'total_rows': len(df),
            'sample': sample,
            'dataset_name': dataset.name,
            'dataset_id': dataset.id
        }
        
    except Exception as e:
        return {'error': str(e)}