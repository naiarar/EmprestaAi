from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CadastroLivro
from .models import Emprestimo, Livros

Usuario = get_user_model()


def _livro_do_usuario(request, id):
    return get_object_or_404(Livros, id=id, usuario=request.user)


@login_required
def home(request):
    livros = Livros.objects.filter(usuario=request.user).select_related('categoria')
    return render(request, 'home.html', {'livros': livros})


@login_required
def ver_livros(request, id):
    livro = _livro_do_usuario(request, id)
    usuarios = Usuario.objects.filter(is_active=True).exclude(id=request.user.id).order_by('nome')
    return render(request, 'ver_livro.html', {
        'livro': livro,
        'usuarios': usuarios,
    })


@login_required
def historico_emprestimos(request, id):
    livro = _livro_do_usuario(request, id)
    emprestimos = livro.emprestimo_set.select_related('nome_emprestado').order_by('-data_emprestimo')
    return render(request, 'historico_emprestimos.html', {'livro': livro, 'emprestimos': emprestimos})


@require_POST
@login_required
def cadastrar_livro(request):
    form = CadastroLivro(request.POST, request.FILES)
    if form.is_valid():
        livro = form.save(commit=False)
        livro.usuario = request.user
        livro.save()
        messages.success(request, 'Livro cadastrado com sucesso')
        return redirect('home')

    erros = '; '.join(f'{form.fields[campo].label if campo in form.fields else campo}: {" ".join(msgs)}'
                      for campo, msgs in form.errors.items())
    messages.error(request, f'Não foi possível cadastrar o livro. {erros}')
    return redirect('home')


@require_POST
@login_required
def excluir_livro(request, id):
    livro = _livro_do_usuario(request, id)
    livro.delete()
    messages.info(request, 'Livro excluído')
    return redirect('home')


@require_POST
@login_required
def emprestar_livro(request, id):
    livro = _livro_do_usuario(request, id)
    if livro.emprestado:
        messages.error(request, 'Desculpe, esse livro já está emprestado')
        return redirect('home')

    tomador = (
        Usuario.objects.filter(is_active=True)
        .exclude(id=request.user.id)
        .filter(id=request.POST.get('nome_emprestado'))
        .first()
    )
    if tomador is None:
        messages.error(request, 'Escolha para quem emprestar o livro')
        return redirect('ver_livros', id=livro.id)

    Emprestimo.objects.create(nome_emprestado=tomador, livro=livro)
    livro.emprestado = True
    livro.save(update_fields=['emprestado'])
    messages.success(request, 'Empréstimo realizado com sucesso')
    return redirect('home')


@require_POST
@login_required
def devolver_livro(request, id):
    livro = _livro_do_usuario(request, id)
    emprestimo = livro.emprestimo_set.filter(data_devolucao=None).order_by('-data_emprestimo').first()
    if emprestimo is not None:
        emprestimo.data_devolucao = timezone.now()
        emprestimo.save(update_fields=['data_devolucao'])

    livro.emprestado = False
    livro.save(update_fields=['emprestado'])
    messages.success(request, 'Devolução realizada com sucesso')
    return redirect('home')


@login_required
def seus_emprestimos(request):
    emprestimos = (
        Emprestimo.objects.filter(nome_emprestado=request.user)
        .select_related('livro__usuario')
        .order_by('-data_emprestimo')
    )
    return render(request, 'seus_emprestimos.html', {'emprestimos': emprestimos})


@require_POST
@login_required
def processa_avaliacao(request):
    emprestimo = get_object_or_404(
        Emprestimo,
        id=request.POST.get('id_emprestimo'),
        livro__usuario=request.user,
        data_devolucao__isnull=False,
    )
    opcao = request.POST.get('opcoes')
    if opcao in dict(Emprestimo.choices):
        emprestimo.avaliacao = opcao
        emprestimo.save(update_fields=['avaliacao'])
        messages.success(request, 'Avaliação registrada')
    else:
        messages.error(request, 'Avaliação inválida')
    return redirect('historico_emprestimos', id=emprestimo.livro_id)
