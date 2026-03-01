PHASE 2: AUTHENTICATION & ROLES - Complete Step by Step
📁 Struktur Akhir Proyek (Tambahan dari Phase 1)
text
/home/adung/projects/company_system/
├── accounts/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── accounts/
│   │       ├── login.html
│   │       └── dashboard.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── core/
│   ├── static/
│   │   └── core/
│   │       ├── css/
│   │       │   └── output.css
│   │       ├── js/
│   │       │   └── theme.js
│   │       └── src/
│   │           └── input.css
│   └── templates/
│       └── base.html
├── company_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── package.json
├── tailwind.config.js
└── tailwindcss (binary)
🚀 Step 1: Buat Superuser
bash
python manage.py createsuperuser
# Username: admin
# Email: dudi.gmtrangkas@gmail.com
# Password: GMTrangkas1207
🧪 Step 2: Test Admin Login
bash
python manage.py runserver
# Buka http://127.0.0.1:8000/admin
# Login dengan superuser
📦 Step 3: Buat App Accounts
bash
python manage.py startapp accounts
⚙️ Step 4: Daftarkan App Accounts di settings.py
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
    'accounts',   # <-- tambah ini
]
👤 Step 5: Buat Model Profile (Extend User)
Edit accounts/models.py:

python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('SuperAdmin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Viewer', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Viewer')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
🔄 Step 6: Migrasi Model Profile
bash
python manage.py makemigrations accounts
python manage.py migrate accounts
python manage.py migrate
🎛️ Step 7: Register Profile di Admin
Edit accounts/admin.py:

python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    
    def get_role(self, obj):
        return obj.profile.role
    get_role.short_description = 'Role'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
🔐 Step 8: Buat Decorators untuk Role-Based Access
Buat file accounts/decorators.py:

python
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # SuperAdmin bisa akses semua
            if request.user.profile.role == 'SuperAdmin':
                return view_func(request, *args, **kwargs)
            
            # Cek role lain
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You are not authorized to view this page.')
                return redirect('dashboard')
        return wrapper
    return decorator

def admin_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.profile.role in ['SuperAdmin', 'Admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
    return wrapper
👁️ Step 9: Buat Views (Login/Logout/Dashboard)
Edit accounts/views.py:

python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')
🎨 Step 10: Buat Template Login
Buat folder templates:

bash
mkdir -p accounts/templates/accounts
Buat file accounts/templates/accounts/login.html:

html
{% extends 'base.html' %}

{% block title %}Login{% endblock %}

{% block content %}
<div class="max-w-md mx-auto bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
    <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
    
    {% if messages %}
        {% for message in messages %}
            <div class="mb-4 p-3 bg-red-100 text-red-700 rounded">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    
    <form method="post">
        {% csrf_token %}
        <div class="mb-4">
            <label class="block text-gray-700 dark:text-gray-300 mb-2">Username</label>
            <input type="text" name="username" required 
                   class="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600">
        </div>
        
        <div class="mb-6">
            <label class="block text-gray-700 dark:text-gray-300 mb-2">Password</label>
            <input type="password" name="password" required 
                   class="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600">
        </div>
        
        <button type="submit" 
                class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
            Login
        </button>
    </form>
</div>
{% endblock %}
📊 Step 11: Buat Template Dashboard
Buat file accounts/templates/accounts/dashboard.html:

html
{% extends 'base.html' %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
    <h1 class="text-2xl font-bold mb-4">Welcome, {{ user.username }}!</h1>
    
    <div class="mb-4 p-4 bg-blue-50 dark:bg-gray-700 rounded">
        <p class="text-lg">Your Role: 
            <span class="font-semibold">{{ user.profile.role }}</span>
        </p>
        <p class="text-lg">Department: 
            <span class="font-semibold">{{ user.profile.department|default:'Not set' }}</span>
        </p>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded shadow">
            <h3 class="font-bold">Quick Stats</h3>
            <p class="mt-2">This is your dashboard. More features coming in Phase 3 & 4.</p>
        </div>
    </div>
    
    <div class="mt-6">
        <a href="{% url 'logout' %}" 
           class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
            Logout
        </a>
    </div>
</div>
{% endblock %}
🔗 Step 12: Setup URLs untuk Accounts
Buat file accounts/urls.py:

python
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
Edit company_system/urls.py:

python
from django.contrib import admin
from django.urls import path, include
from core.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('accounts.urls')),  # <-- tambah ini
]
🧭 Step 13: Update Base Template dengan Auth Links
Edit core/templates/base.html, ganti bagian navbar dengan ini:

html
<div class="flex justify-between items-center h-16">
    <span class="text-xl font-semibold">Company System</span>
    
    <div class="flex items-center space-x-4">
        {% if user.is_authenticated %}
            <span class="text-sm">Hi, {{ user.username }}</span>
            <a href="{% url 'dashboard' %}" 
               class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700">
                Dashboard
            </a>
            <a href="{% url 'logout' %}" 
               class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700">
                Logout
            </a>
        {% else %}
            <a href="{% url 'login' %}" 
               class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700">
                Login
            </a>
        {% endif %}
        
        <!-- Dark mode toggle button -->
        <button id="theme-toggle" class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700">
            Toggle Dark Mode
        </button>
    </div>
</div>
🌓 Step 14: Implement Dark Mode Toggle
Buat folder js:

bash
mkdir -p core/static/core/js
Buat file core/static/core/js/theme.js:

javascript
// Theme toggle functionality
(function() {
    // Get theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference or system preference
    function getInitialTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
    
    // Apply theme
    function setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('theme', theme);
    }
    
    // Initial theme setup
    const initialTheme = getInitialTheme();
    setTheme(initialTheme);
    
    // Toggle theme on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
})();
Edit core/templates/base.html, tambahkan di dalam <head>:

html
<script src="{% static 'core/js/theme.js' %}" defer></script>
🎯 Step 15: Update Tailwind Config untuk Dark Mode
Edit tailwind.config.js:

javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './**/*.py',
  ],
  darkMode: 'class',  // <-- tambah baris ini
  theme: {
    extend: {},
  },
  plugins: [],
}
🎨 Step 16: Fix Dark Mode dengan CSS Manual (karena Tailwind v4)
Edit core/static/core/src/input.css, tambahkan di bagian bawah:

css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Dark mode manual */
.dark body {
    background-color: #1a1a1a !important;
    color: #e5e5e5 !important;
}

.dark .bg-white {
    background-color: #2d2d2d !important;
}

.dark .bg-gray-50 {
    background-color: #1a1a1a !important;
}

.dark .text-gray-900 {
    color: #e5e5e5 !important;
}
Build CSS:

bash
./tailwindcss -i ./core/static/core/src/input.css -o ./core/static/core/css/output.css --minify
✅ Checkpoint 2: Authentication & Roles Complete
No	Item	Status
1	Superuser created	✅
2	App accounts dibuat	✅
3	Model Profile dengan roles	✅
4	Migrasi sukses	✅
5	Profile muncul di Admin	✅
6	Decorators role-based	✅
7	Login view	✅
8	Logout view	✅
9	Dashboard view	✅
10	Template login	✅
11	Template dashboard	✅
12	URLs routing	✅
13	Base template dengan auth links	✅
14	Dark mode toggle (JavaScript)	✅
15	Dark mode berfungsi	✅
📌 Catatan Penting
Virtual env: Selalu aktifkan dengan source .venv/bin/activate

Run server: python manage.py runserver

Build CSS (setiap kali ubah input.css): ./tailwindcss -i ./core/static/core/src/input.css -o ./core/static/core/css/output.css --minify

Role hierarchy: SuperAdmin > Admin > Manager > Viewer

Decorators siap digunakan di view mana pun

🔜 Next: Phase 3 - Dataset Engine
Upload Excel

Store metadata

Validate file structure

Generate validation report

Activate dataset

Cache active dataset