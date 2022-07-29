import json
import logging
import os
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect

from .funcs import ParseIFC, CompareParsedIFC
from .models import *

logger = logging.getLogger(__name__)


def DirExists(pk: int) -> bool:
    return Dir.objects.filter(id=pk).exists()


def CreateMainDirIfNotExists():
    if not Dir.objects.filter(name=os.getenv('NAME_MAIN_FILEMANAGER_DIR')).exists():
        Dir.objects.create(name=os.getenv('NAME_MAIN_FILEMANAGER_DIR')).save()


def GetMainDirId() -> int:
    CreateMainDirIfNotExists()
    return Dir.objects.get(name=os.getenv('NAME_MAIN_FILEMANAGER_DIR')).id


def Navigation(request):
    CreateMainDirIfNotExists()
    return render(request, 'APP_FileManager/Navigation.html')


def FileManager(request, pk=None):
    CreateMainDirIfNotExists()
    if pk is None:
        dir_ = Dir.objects.get(name=os.getenv('NAME_MAIN_FILEMANAGER_DIR'))
    elif not Dir.objects.filter(id=pk).exists():
        return redirect('not-found')
    else:
        dir_ = Dir.objects.get(id=pk)

    dir_dirs = Dir.objects.filter(parent_dir=dir_)
    dir_files = File.objects.filter(parent_dir=dir_)

    return render(request, 'APP_FileManager/FileManager.html',
                  context={'dir_dirs': dir_dirs,
                           'dir_files': dir_files,
                           'parent_dir': dir_,
                           'main_dir_id': GetMainDirId()})


def Upload(request, pk=None):
    CreateMainDirIfNotExists()
    if pk is None or not DirExists(pk):
        pk = GetMainDirId()

    if request.method == 'POST':
        # Check valid
        if 'dir_id' not in request.POST:
            return render(request, 'APP_FileManager/Upload.html',
                          context={'invalid': 'The folder ID field is not filled in.'})
        if not str(request.POST['dir_id']).isdigit():
            return render(request, 'APP_FileManager/Upload.html',
                          context={'invalid': 'The folder ID field is filled in incorrectly.'})
        if not Dir.objects.filter(id=int(request.POST['dir_id'])).exists():
            return render(request, 'APP_FileManager/Upload.html',
                          context={'invalid': f'The folder with ID {int(request.POST["dir_id"])} is missing.'})
        if 'files[]' not in dict(request.FILES.lists()):  # If no any files
            return render(request, 'APP_FileManager/Upload.html', context={'invalid': "You haven't added any files"})

        files = dict(request.FILES.lists())['files[]']
        dir_ = Dir.objects.get(id=int(request.POST['dir_id']))
        # Start saving
        for file in files:
            filename_translited = str(translit(str(file.name), language_code='ru', reversed=True).replace(' ', '_'))
            filename, file_extension = os.path.splitext(filename_translited)

            # If IFC
            if file_extension.lower() == '.ifc':
                file_read = file.read()
                NEW_IFC_objects = ParseIFC(str(file_read, encoding='utf-8'))

                # if this file already exists
                if File.objects.filter(name=filename, parent_dir=dir_).exists():
                    OLD_FILE = File.objects.get(name=filename, parent_dir=dir_)
                    OLD_IFC_objects = json.loads(IFCObjects.objects.get(parent_file=OLD_FILE).ifc_objects)
                    CHANGE_NOW = CompareParsedIFC(OLD_IFC_objects, NEW_IFC_objects)

                    # CHANGES
                    DONE_CHANGES = {}
                    if len(CHANGE_NOW) != 0:
                        DONE_CHANGES[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = CHANGE_NOW
                        if IFCChange.objects.filter(parent_file=OLD_FILE).exists():
                            DONE_CHANGES.update(dict(json.loads(IFCChange.objects.get(parent_file=OLD_FILE).ifc_change)))
                    else:
                        if IFCChange.objects.filter(parent_file=OLD_FILE).exists():
                            DONE_CHANGES.update(
                                dict(json.loads(IFCChange.objects.get(parent_file=OLD_FILE).ifc_change)))

                    OLD_FILE.delete()
                    NEW_FILE = File.objects.create(name=filename, extension=file_extension, size=file.size, file=file,
                                                   parent_dir=dir_)
                    NEW_FILE.save()

                    IFCObjects.objects.create(parent_file=NEW_FILE, ifc_objects=str(json.dumps(NEW_IFC_objects))).save()

                    if len(DONE_CHANGES.keys()) != 0:
                        IFCChange.objects.create(parent_file=NEW_FILE, ifc_change=str(json.dumps(DONE_CHANGES))).save()
                else:
                    NEW_FILE = File.objects.create(name=filename,
                                                   extension=file_extension,
                                                   size=file.size,
                                                   file=file,
                                                   parent_dir=dir_)
                    NEW_FILE.save()
                    IFCObjects.objects.create(parent_file=NEW_FILE, ifc_objects=str(json.dumps(NEW_IFC_objects)))

            else:
                if File.objects.filter(name=filename, parent_dir=dir_).exists():
                    File.objects.get(name=filename, parent_dir=dir_).delete()
                File.objects.create(name=filename,
                                    extension=file_extension,
                                    size=file.size,
                                    file=file,
                                    parent_dir=dir_).save()

        return redirect('file-manager-pk', dir_.id)

    return render(request, 'APP_FileManager/Upload.html', {'parent_dir_id': pk})


def Del(request):
    CreateMainDirIfNotExists()
    if request.method == 'POST':
        if request.POST['del_type'] == 'file':
            dir_id_for_redirect = File.objects.get(id=request.POST['del_id']).parent_dir.id
            File.objects.filter(id=request.POST['del_id']).delete()
            return redirect('file-manager-pk', dir_id_for_redirect)
        elif request.POST['del_type'] == 'dir':
            dir_id_for_redirect = Dir.objects.get(id=request.POST['del_id']).parent_dir.id
            Dir.objects.filter(id=request.POST['del_id']).delete()
            return redirect('file-manager-pk', dir_id_for_redirect)


def MkDir(request, pk=None):
    CreateMainDirIfNotExists()
    if pk is None or not DirExists(pk):
        pk = GetMainDirId()

    if request.method == 'POST':
        if 'name' in request.POST and 'parent_dir_id' in request.POST:
            if request.POST['name'] == os.getenv('NAME_MAIN_FILEMANAGER_DIR'):
                return render(request, 'APP_FileManager/MkDir.html',
                              {'invalid': 'You cannot create a folder with a name like the main folder.'})

            if not Dir.objects.filter(id=int(request.POST['parent_dir_id'])).exists():
                return render(request, 'APP_FileManager/MkDir.html',
                              {'invalid': f'The folder with ID {request.POST["parent_dir_id"]} does not exist.'})

            dir_ = Dir.objects.create(
                name=request.POST['name'],
                parent_dir_id=request.POST['parent_dir_id']
            ).save()
            return redirect('file-manager-pk', request.POST['parent_dir_id'])
        else:
            return render(request, 'APP_FileManager/MkDir.html',
                          {'invalid': 'The "name" or "id of the parent folder" field is not filled in.'})

    return render(request, 'APP_FileManager/MkDir.html', {'parent_dir_id': pk})


def NotFound(request):
    return render(request, 'APP_FileManager/NotFound.html')



