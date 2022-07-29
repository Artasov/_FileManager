from rest_framework import serializers

from APP_FileManager.models import File, Dir


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class DirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dir
        fields = '__all__'


class MkDirSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    parent_dir_id = serializers.IntegerField(required=False)


class DetailIFCSerializer(serializers.Serializer):
    file_id = serializers.IntegerField(required=True)
