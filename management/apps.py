from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class ManagementConfig(AppConfig):
    name = 'management'

    def ready(self):
        autodiscover_modules('stark')
