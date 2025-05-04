"""This file contains all the settings used in production.

This file is required and if development.py is present these
values are overridden.
"""

import structlog

from server.settings.components import config

# from server.settings.components.common import (
#     INSTALLED_APPS,
# )
from server.settings.components.common import (
    SPECTACULAR_SETTINGS as SPECTACULAR_SETTINGS_BASE,  # type: ignore
)
from server.settings.components.csp import CSP_CONNECT_SRC, CSP_IMG_SRC, CSP_SCRIPT_SRC

# Production flags:
# https://docs.djangoproject.com/en/4.2/howto/deployment/
DEBUG = False

HOSTS = config('ALLOWED_HOSTS', default='')

ALLOWED_HOSTS = [
    # Split the domains by comma and filter out empty strings
    *[host.strip() for host in HOSTS.split(',') if host.strip()],  # type: ignore
    'localhost',
    '0.0.0.0',  # noqa: S104
    '127.0.0.1',
    '[::1]',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # We use these formatters in our `'handlers'` configuration.
    # Probably, you won't need to modify these lines.
    # Unless, you know what you are doing.
    'formatters': {
        'json_formatter': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        },
        'console': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.KeyValueRenderer(
                key_order=['timestamp', 'level', 'event', 'logger'],
            ),
            'foreign_pre_chain': [
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt='iso'),
            ],
        },
    },
    # You can easily swap `key/value` (default) output and `json` ones.
    # Use `'json_console'` if you need `json` logs.
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'json_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_formatter',
        },
    },
    # These loggers are required by our app:
    # - django is required when using `logger.getLogger('django')`
    # - security is required by `axes`
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


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
        'BACKEND': 'django.core.files.storage.ManifestStaticFilesStorage',
    },
}

# STORAGES = {
#     "default": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

# Installed apps:
# INSTALLED_APPS += (
#     'whitenoise.runserver_nostatic',
# )

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
CSP_CONNECT_SRC += (  # type: ignore
    "'self'",
    config('DOMAIN_NAME', default=''),
)
CSP_SCRIPT_SRC += ('ajax.googleapis.com',)
CSP_IMG_SRC += ('data:',)

SPECTACULAR_SETTINGS = SPECTACULAR_SETTINGS_BASE.copy()
SPECTACULAR_SETTINGS['SERVERS'] = [
    {'url': config('DOMAIN_NAME', default=''), 'description': 'Production server'},
]

# CORS_ALLOWED_ORIGIN_REGEXES = [r'^/api/.*$', config('DOMAIN_NAME', default='')]
CORS_ALLOWED_ORIGINS = [config('DOMAIN_NAME', default=''), config('FRONTEND_URL', default='')]

# Emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = '587'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
