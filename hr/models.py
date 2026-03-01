from django.db import models
from django.contrib.auth.models import User
from datasets.models import Dataset

class Employee(models.Model):
    # Basic Info
    nik = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Personal Data
    nama = models.CharField(max_length=255)
    sex = models.CharField(max_length=10)
    tgl_lahir = models.DateField()
    tempat_lahir = models.CharField(max_length=100)
    no_ktp = models.CharField(max_length=30, unique=True)
    no_kk = models.CharField(max_length=30)
    no_hp = models.CharField(max_length=20)
    alamat = models.TextField()
    kelurahan = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    kabupaten = models.CharField(max_length=100)
    provinsi = models.CharField(max_length=100)
    kode_pos = models.CharField(max_length=10, blank=True)

    # Employment
    dept = models.CharField(max_length=100)
    jabatan = models.CharField(max_length=100)
    tgl_rekrut = models.DateField()
    status_karyawan = models.CharField(max_length=50)  # Tetap/Kontrak/OS
    tgl_kartetap = models.DateField(null=True, blank=True)
    kontrak_ke = models.IntegerField(default=0)
    kontrak_berakhir = models.DateField(null=True, blank=True)

    # Financial
    kode_gaji = models.CharField(max_length=50, blank=True)
    no_rek_bank = models.CharField(max_length=50, blank=True)
    kode_bank = models.CharField(max_length=10, blank=True)
    nama_bank = models.CharField(max_length=100, blank=True)
    status_ptkp = models.CharField(max_length=20, blank=True)
    no_npwp = models.CharField(max_length=30, blank=True)

    # BPJS
    bpjs_tk = models.BooleanField(default=False)
    bpjs_tk_no = models.CharField(max_length=50, blank=True)
    bpjs_tk_ditanggung = models.CharField(max_length=20, blank=True)
    bpjs_kes = models.BooleanField(default=False)
    bpjs_kes_no = models.CharField(max_length=50, blank=True)
    bpjs_kes_ditanggung = models.CharField(max_length=20, blank=True)

    # Status
    status_kerja = models.CharField(max_length=20)  # Aktif/Non-Aktif
    tgl_out = models.DateField(null=True, blank=True)

    # Metadata
    imported_from = models.ForeignKey(
        Dataset, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['nik']),
            models.Index(fields=['no_ktp']),
            models.Index(fields=['dept']),
            models.Index(fields=['status_kerja']),
            models.Index(fields=['tgl_rekrut']),
        ]
        ordering = ['nik']

    def __str__(self):
        return f"{self.nik} - {self.nama}"