from django.shortcuts import render

from livro.models import Livros


def index(request):
    livros = Livros.objects.select_related('usuario').order_by('-data_cadastro')[:6]
    return render(request, 'index.html', {'livros': livros})


def about(request):
    return render(request, 'about.html')
