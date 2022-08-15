"""
WSGI config for apiserver project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

env = os.environ.get('ENV', 'dev')
if env == 'prod':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                        'apiserver.settings.prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                        'apiserver.settings.dev')

application = get_wsgi_application()
