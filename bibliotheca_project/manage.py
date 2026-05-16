#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def patch_django_context_copy():
    try:
        from copy import copy
        from django.template.context import Context

        def __copy__(self):
            duplicate = super().__copy__()
            duplicate.render_context = copy(self.render_context)
            return duplicate

        Context.__copy__ = __copy__
    except Exception:
        pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheca_project.settings')
    patch_django_context_copy()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
