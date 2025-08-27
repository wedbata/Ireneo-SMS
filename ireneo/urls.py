from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Non-translated URLs
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# Translated URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')),
    path('staff/', include('staff.urls')),
    path('communication/', include('communication.urls')),
    path('finance/', include('finance.urls')),
    path('operations/', include('operations.urls')),
    path('reports/', include('reports.urls')),
    prefix_default_language=True,
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)