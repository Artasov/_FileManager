from django.urls import include
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.Navigation, name='navigations'),

    path('file-manager/', views.FileManager, name='file-manager'),
    path('file-manager/<int:pk>/', views.FileManager, name='file-manager-pk'),

    path('upload/', views.Upload, name='upload'),
    path('upload/<int:pk>/', views.Upload, name='upload-pk'),

    path('mkdir/', views.MkDir, name='mkdir'),
    path('mkdir/<int:pk>/', views.MkDir, name='mkdir-pk'),

    path('del/', views.Del, name='del'),
    path('not-found/', views.NotFound, name='not-found'),

    # re_path(r'download/(?P<path>.*)$', views.Download, name='download'),
]
