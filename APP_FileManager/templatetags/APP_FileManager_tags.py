from django import template

from APP_FileManager.models import *

register = template.Library()


@register.simple_tag()
def GetPathToDir(dir_id, main_dir_id):
    path = ''
    if Dir.objects.filter(id=dir_id).exists():
        DIR = Dir.objects.get(id=dir_id)
        path += '/'+DIR.name
        while DIR.id != main_dir_id:
            DIR = Dir.objects.get(id=DIR.parent_dir.id)
            path = '/'+DIR.name + path
    return path[1:len(path)]

# @register.simple_tag()
# def diff(a, b, digits_after_dot=5, type_returned=1):
#     if type_returned == 1:
#         return float(str(a/b)[0:digits_after_dot])
#     else:
#         return int(float(str(a/b)[0:digits_after_dot]))
#
#
# @register.simple_tag()
# def get_GOOGLE_RECAPTCHA_SITE_KEY():
#     return settings.GOOGLE_RECAPTCHA_SITE_KEY
