import os
os.environ["DJANGO_SETTINGS_MODULE"] = "orcatrex.settings"
import django
django.setup()
from django.conf import settings
from orcatrex import views
