"""
WSGI config for bibliotheca_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from copy import copy
from django.template.context import Context
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheca_project.settings')

try:
    def __copy__(self):
        duplicate = super().__copy__()
        duplicate.render_context = copy(self.render_context)
        return duplicate
    Context.__copy__ = __copy__
except Exception:
    pass

application = get_wsgi_application()
