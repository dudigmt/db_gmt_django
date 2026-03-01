import os

# Pilih settings berdasarkan environment variable
environment = os.getenv('DJANGO_ENVIRONMENT', 'dev')

if environment == 'production':
    from .prod import *
else:
    from .dev import *