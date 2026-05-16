"""
ASGI config for bibliotheca_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from copy import copy
from django.template.context import Context
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheca_project.settings')

try:
    def __copy__(self):
        duplicate = super().__copy__()
        duplicate.render_context = copy(self.render_context)
        return duplicate
    Context.__copy__ = __copy__
except Exception:
    pass

application = get_asgi_application()
