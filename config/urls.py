from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Index Page (/)
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    # Accounts app
    path('accounts/', include('accounts.urls', namespace='accounts')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
