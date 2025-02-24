import os
import sys

# Ruta al entorno virtual
path = '/home/mCEEE/.virtualenvs/myenv/lib/python3.10/site-packages'
if path not in sys.path:
    sys.path.append(path)

# Ruta al proyecto
project_path = '/home/mCEEE/mCEEE/backend'
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
