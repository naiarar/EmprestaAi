from .forms import CadastroLivro


def form_livro(request):
    if not request.user.is_authenticated:
        return {}
    return {'form_livro': CadastroLivro()}
