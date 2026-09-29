from django import forms

from usuarios.forms import BootstrapMixin

from .models import Livros


class CadastroLivro(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Livros
        exclude = ('usuario', 'emprestado', 'data_cadastro')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = 'Selecione uma categoria'
