from django.contrib import admin

from .models import Categoria, Emprestimo, Livros


@admin.register(Livros)
class LivrosAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'usuario', 'categoria', 'emprestado')
    list_filter = ('emprestado', 'categoria')
    search_fields = ('titulo', 'autor')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'nome_emprestado', 'data_emprestimo', 'data_devolucao', 'avaliacao')


admin.site.register(Categoria)
