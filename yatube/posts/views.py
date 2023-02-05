from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('Главная страниц')


def group_posts(request):
    return HttpResponse('Группы')


def group_details(request, slug):
    return HttpResponse(f'Посты группы {slug}')

