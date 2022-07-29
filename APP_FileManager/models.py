from django.db import models
from django_minio_backend import MinioBackend
from transliterate import translit


def TranslitFile(instance, filename):
    filename = translit(str(filename), language_code='ru', reversed=True).replace(' ', '_')
    return str(filename)


class Dir(models.Model):
    name = models.CharField(max_length=255, blank=True)
    parent_dir = models.ForeignKey('Dir', on_delete=models.CASCADE, null=True)


class File(models.Model):
    name = models.CharField(max_length=255, blank=True)
    extension = models.CharField(max_length=255, blank=True)
    size = models.IntegerField(blank=True)
    file = models.FileField(verbose_name="File Upload",
                            storage=MinioBackend(bucket_name='files-bucket', replace_existing=True),
                            upload_to=TranslitFile)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parent_dir = models.ForeignKey(Dir, on_delete=models.CASCADE, null=True)


class IFCObjects(models.Model):
    parent_file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    ifc_objects = models.TextField(blank=True)


class IFCChange(models.Model):
    parent_file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    ifc_change = models.TextField(blank=True)