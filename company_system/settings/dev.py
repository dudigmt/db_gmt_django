from .base import *

# Development settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development apps
INSTALLED_APPS = [
    'unfold',  # WAJIB PALING ATAS
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.import_export',
] + INSTALLED_APPS  # + buat nambahin apps dari base

# Development apps tambahan
INSTALLED_APPS += [
    'debug_toolbar',
]

# Development middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar settings
INTERNAL_IPS = ['127.0.0.1']

# Unfold settings
UNFOLD = {
    "SITE_TITLE": "Company System",
    "SITE_HEADER": "Company System Admin",
    "SITE_URL": "/",
    "SITE_ICON": None,
}