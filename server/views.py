from django.http import Http404
from django.shortcuts import render


def vue_app(request, path=None):
    return render(request, "app.html")


def not_found(request, path):
    raise Http404
