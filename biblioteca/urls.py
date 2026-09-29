from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from index.views import about, index

urlpatterns = [
    path('', index, name='index'),
    path('sobre/', about, name='about'),
    path('admin/', admin.site.urls),
    path('livro/', include('livro.urls')),
    path('auth/', include('usuarios.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
