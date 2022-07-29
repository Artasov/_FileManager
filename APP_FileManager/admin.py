from django.contrib import admin

from .models import *


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'extension', 'size', 'file', 'uploaded_at', ]


@admin.register(Dir)
class DirAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(IFCChange)
class IFCChangeAdmin(admin.ModelAdmin):
    list_display = ['id', 'ifc_change']


@admin.register(IFCObjects)
class IFCObjectsAdmin(admin.ModelAdmin):
    list_display = ['id', 'ifc_objects']
