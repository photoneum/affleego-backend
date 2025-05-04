"""This file contains all the settings used in production.

This file is required and if development.py is present these
values are overridden.
"""

from server.settings.components import config
from server.settings.components.common import (
    SPECTACULAR_SETTINGS as SPECTACULAR_SETTINGS_BASE,
)
from server.settings.components.csp import CSP_CONNECT_SRC

# Production flags:
# https://docs.djangoproject.com/en/4.2/howto/deployment/

DEBUG = False

HOSTS = config('ALLOWED_HOSTS', default='')

ALLOWED_HOSTS = [
    # Split the domains by comma and filter out empty strings
    *[host.strip() for host in HOSTS.split(',') if host.strip()],  # type: ignore
    # We need this value for `healthcheck` to work:
    'localhost',
]


# Staticfiles
# https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/

# This is a hack to allow a special flag to be used with `--dry-run`
# to test things locally.
_COLLECTSTATIC_DRYRUN = config(
    'DJANGO_COLLECTSTATIC_DRYRUN',
    cast=bool,
    default=False,
)
# Adding STATIC_ROOT to collect static files via 'collectstatic':
STATIC_ROOT = '.static' if _COLLECTSTATIC_DRYRUN else '/var/www/affleego/django/static'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}


# Media files
# https://docs.djangoproject.com/en/4.2/topics/files/

MEDIA_ROOT = '/var/www/affleego/django/media'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

_PASS = 'django.contrib.auth.password_validation'  # noqa: S105
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'{_PASS}.UserAttributeSimilarityValidator'},
    {'NAME': f'{_PASS}.MinimumLengthValidator'},
    {'NAME': f'{_PASS}.CommonPasswordValidator'},
    {'NAME': f'{_PASS}.NumericPasswordValidator'},
]


# Security
# https://docs.djangoproject.com/en/4.2/topics/security/

SECURE_HSTS_SECONDS = 31536000  # the same as Caddy has
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [
    # This is required for healthcheck to work:
    '^health/',
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CSP
CSP_CONNECT_SRC += (
    "'self'",
    config('DOMAIN_NAME', default=''),
)

SPECTACULAR_SETTINGS = SPECTACULAR_SETTINGS_BASE.copy()
SPECTACULAR_SETTINGS['SERVERS'] = [
    {'url': config('DOMAIN_NAME', default=''), 'description': 'Staging server'},
]

# Email
# https://docs.djangoproject.com/en/4.2/topics/email/
# -------------------------------------------------------------------------------
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = 1025
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False)

CORS_ALLOWED_ORIGIN_REGEXES = [r'^/api/.*$', config('DOMAIN_NAME', default='')]
