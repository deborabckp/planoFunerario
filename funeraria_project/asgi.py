"""
ASGI config for funeraria_project project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funeraria_project.settings')

application = get_asgi_application()