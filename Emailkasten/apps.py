from django.apps import AppConfig
import logging

class Appconfig(AppConfig):
    name = 'Emailkasten'

    def ready(self):
        import Emailkasten.signals
