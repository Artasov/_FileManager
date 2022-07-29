from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('docs/', RedirectView.as_view(url='/swagger/'), name='docs'),
    path('admin/', admin.site.urls),

    path('', include('APP_FileManager.urls')),
    path('api/v1/', include('APP_FileManagerAPI.urls')),

]

urlpatterns += doc_urls
