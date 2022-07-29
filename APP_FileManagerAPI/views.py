import json

from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from APP_FileManager.models import *
from APP_FileManagerAPI.serializers import FileSerializer, DirSerializer, MkDirSerializer, DetailIFCSerializer


@swagger_auto_schema(method='get', operation_description="Get info about all files.")
@api_view(['GET'])  # 4
def FileList(request):
    permission_classes = (IsAdminUser,)

    queryset = File.objects.all()
    serializer = FileSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK, content_type="application/json")


@swagger_auto_schema(method='get', operation_description="Get info about all dirs.")
@api_view(['GET'])  # 4
def DirList(request):
    permission_classes = (IsAdminUser,)

    queryset = Dir.objects.all()
    serializer = DirSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK, content_type="application/json")


@swagger_auto_schema(method='post', request_body=MkDirSerializer, )
@api_view(['POST'])  # 1
def MkDir(request):
    permission_classes = (IsAdminUser,)

    serializer = MkDirSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    if 'parent_dir_id' in serializer.validated_data:  # If parent_dir_id in POST
        if Dir.objects.filter(id=serializer.validated_data['parent_dir_id']).exists():  # If parent_dir exists
            dir_ = Dir.objects.create(name=serializer.validated_data['name'],
                                      parent_dir_id=serializer.validated_data['parent_dir_id'])
        else:  # If parent_dir NOT exists
            dir_ = Dir.objects.create(name=serializer.validated_data['name'])
    else:  # If without parent_dir_id in POST
        dir_ = Dir.objects.create(name=serializer.validated_data['name'])

    dir_.save()
    return Response({'dir_id': dir_.id,
                     'dir_name': dir_.name},
                    status=status.HTTP_200_OK,
                    content_type="application/json")


@api_view(['GET'])  # IFC point 3
def DetailIFC(request, file_id):
    permission_classes = (IsAdminUser,)
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]

    # Check valid
    if not File.objects.filter(id=file_id).exists():
        return Response({f'File with id:{file_id} does not exist.'},
                        status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    if File.objects.get(id=file_id).extension != '.ifc':
        return Response({f'.ifc file with id:{file_id} does not exist.'},
                        status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    # Create Response
    IFC_file = File.objects.get(id=file_id)
    IFC_objects_dict = json.loads(IFCObjects.objects.get(parent_file=IFC_file).ifc_objects)
    changes = json.loads(IFCChange.objects.get(parent_file=IFC_file).ifc_change) \
        if IFCChange.objects.filter(parent_file=IFC_file).exists() \
        else {}

    return Response({
        'IFC_file': IFC_file.name + IFC_file.extension,
        'IFC_objects': IFC_objects_dict,
        'IFC_changes': changes,
    },
        status=status.HTTP_200_OK,
        content_type="application/json")


@api_view(['GET'])
def download(request, file_id=None):
    permission_classes = (IsAdminUser,)

    if not File.objects.filter(id=file_id).exists():
        return Response({f'File with id:{file_id} does not exist.'},
                        status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    file = File.objects.get(id=file_id)
    response = HttpResponse(file.file.read(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'inline; filename=' + file.name + file.extension
    return response
