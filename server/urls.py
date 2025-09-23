"""Main URL mapping configuration file.

Include other URLConfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This examples uses Django's default media
files serving technique in development.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from health_check import urls as health_urls

from server.apps.deals import urls as deals_urls
from server.apps.main import urls as main_urls
from server.apps.users import urls as users_urls

admin.autodiscover()

API_PREFIX = 'api'
API_VERSION = 'v1'

urlpatterns = [
    path(
        f'{API_PREFIX}/{API_VERSION}/schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),
    path(
        f'{API_PREFIX}/{API_VERSION}/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        f'{API_PREFIX}/{API_VERSION}/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
    # Apps:
    path(
        f'{API_PREFIX}/{API_VERSION}/',
        include(users_urls, namespace='users'),
    ),
    path(
        f'{API_PREFIX}/{API_VERSION}/',
        include(deals_urls, namespace='deals'),
    ),
    path(
        f'{API_PREFIX}/{API_VERSION}/',
        include(main_urls, namespace='main'),
    ),
    # Health checks:
    path('health/', include(health_urls)),
    # tinymce:
    path('tinymce/', include('tinymce.urls')),
    # django-admin:
    path('admin/doc/', include(admindocs_urls)),
    path('admin/', admin.site.urls),
    # Text and xml static files:
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='common/txt/robots.txt',
            content_type='text/plain',
        ),
    ),
    path(
        'humans.txt',
        TemplateView.as_view(
            template_name='common/txt/humans.txt',
            content_type='text/plain',
        ),
    ),
    # It is a good practice to have explicit index view:
    # path('', index, name='index'),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns = [
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include(debug_toolbar.urls)),
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
