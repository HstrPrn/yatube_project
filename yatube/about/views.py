# from django.shortcuts import render
from django.views.generic.base import TemplateView


# Описать класс AboutAuthorView для страницы about/author
class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

# Описать класс AboutTechView для страницы about/tech
