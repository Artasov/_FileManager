import os

from django.contrib.auth.models import User
from django.db import ProgrammingError


def ReadFile(path, printing=False, encoding='utf-8') -> str:
    if printing:
        print(open(path, 'r', encoding=encoding).read())
    return open(path, 'r', encoding=encoding).read()


def ParseIFC(IFC: str) -> dict:
    IFC = str(IFC)
    parsed = {'HEADER': IFC[0:IFC.index('ENDSEC;')], 'DATA': {}}

    IFC_DATA = IFC[IFC.index('DATA;'):len(IFC)]
    IFC_DATA = IFC_DATA[0:IFC_DATA.index('ENDSEC;')].replace('DATA;', '')
    IFC_DATA_SPLITED = IFC_DATA.split('\n')
    for i in IFC_DATA_SPLITED:
        if len(i) > 2:
            parsed['DATA'][i[0:i.index('=')]] = i[i.index('=') + 1: len(i)]

    return parsed


def CompareParsedIFC(IFC_old: dict, IFC_new: dict) -> dict:
    diffIFCData = {}
    IFC_old = IFC_old['DATA']
    IFC_new = IFC_new['DATA']
    for i in IFC_old:
        if (i not in IFC_new) or (IFC_old[i] != IFC_new[i]):
            diffIFCData[i] = IFC_old[i]

    for i in IFC_new:
        if i not in IFC_old:
            diffIFCData[i] = IFC_new[i]

    return diffIFCData


def CreateSuperUserIfNotExist():
    try:
        if User.objects.all().count() == 0:
            User.objects.create_superuser(username=os.getenv('ADMIN_USERNAME'),
                                          email=os.getenv('ADMIN_EMAIL'),
                                          password=os.getenv('ADMIN_PASSWORD'))
    except ProgrammingError:
        pass
