PHASE 1: FOUNDATION - Complete Step by Step
📁 Struktur Akhir Proyek
text
/home/adung/projects/company_system/
├── .venv/
├── company_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── migrations/
│   ├── static/
│   │   └── core/
│   │       ├── css/
│   │       │   └── output.css
│   │       └── src/
│   │           └── input.css
│   ├── templates/
│   │   └── base.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── manage.py
├── requirements.txt
├── package.json
├── tailwind.config.js
├── tailwindcss (binary)
└── db.sqlite3 (optional, bisa dihapus)
🚀 Step 1: Inisialisasi Proyek Django
bash
# 1.1 Buat folder proyek
cd ~
mkdir -p projects
cd projects
mkdir company_system
cd company_system

# 1.2 Buat virtual environment
python3.11 -m venv .venv

# 1.3 Aktivasi virtual environment
source .venv/bin/activate

# 1.4 Upgrade pip dan install Django
pip install --upgrade pip
pip install django

# 1.5 Buat proyek Django
django-admin startproject company_system .

# 1.6 Buat app core
python manage.py startapp core

# 1.7 Test run server
python manage.py runserver
# Buka http://127.0.0.1:8000 - Harusnya roket Django
# Ctrl+C untuk stop
🐘 Step 2: Setup PostgreSQL di WSL
bash
# 2.1 Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev -y

# 2.2 Cek status PostgreSQL
sudo service postgresql status

# 2.3 Masuk sebagai user postgres
sudo -i -u postgres

# 2.4 Buat database user (di dalam postgres user)
createuser --interactive
# Enter name of role: adung
# Shall the new role be a superuser? y

# 2.5 Buat database
createdb gmt_db

# 2.6 Masuk ke psql console
psql

# 2.7 Set password (di dalam psql)
ALTER USER adung WITH PASSWORD 'GMTrangkas1207';

# 2.8 Keluar dari psql
\q

# 2.9 Keluar dari user postgres
exit

# 2.10 Tes koneksi dari user biasa
psql -h localhost -U adung -d gmt_db -W
# Masukkan password, jika bisa masuk berarti sukses
# Keluar dengan \q
🔌 Step 3: Konfigurasi Django ke PostgreSQL
bash
# 3.1 Install psycopg2
pip install psycopg2-binary

# 3.2 Buat requirements.txt
cat > requirements.txt << EOF
Django==5.1.6
psycopg2-binary==2.9.10
python-dotenv==1.0.0
EOF

# 3.3 Edit company_system/settings.py
# Ganti konfigurasi DATABASES
Isi settings.py (bagian DATABASES):

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gmt_db',
        'USER': 'adung',
        'PASSWORD': 'GMTrangkas1207',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
bash
# 3.4 Jalankan migrasi pertama
python manage.py migrate

# 3.5 Test run server
python manage.py runserver
# Buka http://127.0.0.1:8000 - Harusnya masih muncul roket
🎨 Step 4: Setup Tailwind CSS (Versi Binary)
bash
# 4.1 Bersihkan file npm sebelumnya (jika ada)
rm -rf node_modules package-lock.json package.json tailwind.config.js

# 4.2 Inisialisasi package.json
npm init -y

# 4.3 Install Tailwind CSS
npm install -D tailwindcss

# 4.4 Buat file konfigurasi manual
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# 4.5 Buat struktur folder CSS
mkdir -p core/static/core/src
mkdir -p core/static/core/css

# 4.6 Buat file input.css
cat > core/static/core/src/input.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# 4.7 Install Tailwind sebagai binary (solusi UNC path error)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
mv tailwindcss-linux-x64 tailwindcss

# 4.8 Build CSS
./tailwindcss -i ./core/static/core/src/input.css -o ./core/static/core/css/output.css --minify

# 4.9 Cek hasil build
ls -la core/static/core/css/
# Harusnya ada file output.css
📄 Step 5: Base Template dengan Tailwind
bash
# 5.1 Buat folder templates
mkdir -p core/templates
5.2 Buat file core/templates/base.html:

html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company System - {% block title %}Home{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'core/css/output.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <nav class="bg-white dark:bg-gray-800 shadow">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center h-16">
                <span class="text-xl font-semibold">Company System</span>
                <button id="theme-toggle" class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700">
                    Toggle Dark Mode
                </button>
            </div>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8">
        {% block content %}
        {% endblock %}
    </main>

    {% block extra_js %}{% endblock %}
</body>
</html>
5.3 Edit core/views.py:

python
from django.shortcuts import render

def index(request):
    return render(request, 'base.html')
5.4 Edit company_system/settings.py (tambah 'core' ke INSTALLED_APPS):

python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # <-- tambah ini
]
5.5 Edit company_system/urls.py:

python
from django.contrib import admin
from django.urls import path
from core.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
]
5.6 Run server dan test:

bash
python manage.py runserver
# Buka http://127.0.0.1:8000
# Harusnya muncul navbar dengan tombol "Toggle Dark Mode"
✅ Checkpoint 1: Foundation Complete
No	Item	Status
1	Project runs	✅
2	DB connected (PostgreSQL)	✅
3	Superuser created (opsional)	⏳ (bisa nanti)
4	Base template renders	✅
5	Dark mode ready	✅ (toggle placeholder)
📌 Catatan Penting
Virtual env: Selalu aktifkan dengan source .venv/bin/activate

Run server: python manage.py runserver

Build CSS (setiap kali ubah input.css): ./tailwindcss -i ./core/static/core/src/input.css -o ./core/static/core/css/output.css --minify

Dark mode: Masih placeholder, akan diimplementasi di Phase 2

Environment variables: Masih hardcoded, akan dipindah ke .env nanti

🔜 Next: Phase 2 - Authentication & Roles
Extend user model

Setup Groups (SuperAdmin, Admin, Manager, Viewer)

Login/logout

Admin customization

Dark mode toggle functionality