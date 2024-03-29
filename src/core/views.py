import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.utils._os import safe_join
from django.utils.http import http_date


def about(request):
    return render(request, 'core/about.html', {'title': 'About'})


def handler404(request, *args, **kwargs):
    return render(
        request, 'core/error.html',
        {'title': '404', 'message': 'Page Not Found', 'status': '404'},
        status=404,)


def handler500(request, *args, **kwargs):
    return render(
        request, 'core/error.html',
        {'title': '500', 'message': 'Internal Server Error', 'status': '500'},
        status=500)


def inuse(request):
    return render(
        request, 'core/error.html',
        {'title': '403 ',
         'message':
         'Twitter account is already linked to another user in our site',
         'status': '403'},)


def media(request, path):
    fullpath = Path(safe_join(settings.MEDIA_ROOT, path))
    statobj = fullpath.stat()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or 'application/octet-stream'
    response = FileResponse(fullpath.open('rb'), content_type=content_type)
    response["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response["Content-Encoding"] = encoding
    return response
