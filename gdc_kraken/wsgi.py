"""
WSGI config for gdc_kraken project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import json
import os
import sys
import site
from django.core.wsgi import get_wsgi_application
from pathlib import Path


# Get paths from config files
config_file_path = os.path.join(Path(__file__).resolve().parent.parent, "config.json")
if not os.path.exists(config_file_path):
    raise Exception(f"Missing config.json ({config_file_path})")
with open(config_file_path, 'r') as file:
    config_data = json.load(file)

if config_data["PLATFORM"] == "PROD":
    # Add python site packages, you can use virtualenvs also
    site.addsitedir(config_data["WSGI"]["PATH_SITE_PACKAGES"])

# Add the app's directory to the PYTHONPATH
sys.path.append(config_data["WSGI"]["PATH_GDC_KRAKEN"]) 
sys.path.append(config_data["WSGI"]["PATH_GDC_STORM"]) 

os.environ['DJANGO_SETTINGS_MODULE'] = 'gdc_kraken.settings' 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdc_kraken.settings')

application = get_wsgi_application()
