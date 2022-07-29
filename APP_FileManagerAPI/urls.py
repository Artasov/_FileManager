from django.urls import include
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('file-list/', views.FileList, name='api-file-list'),
    path('dir-list/', views.DirList, name='api-file-dir'),
    path('mkdir/', views.MkDir, name='api-mkdir'),
    path('detail-ifc/<int:file_id>', views.DetailIFC, name='api-detail-ifc'),
    path('download/<int:file_id>/', views.download, name='api-download'),
    path('api-auth/', include('rest_framework.urls')),
]

