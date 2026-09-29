from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CadastroForm, LoginForm


class Login(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cadastro realizado com sucesso. Faça login para continuar.')
        return redirect('login')

    return render(request, 'cadastro.html', {'form': form})


@require_POST
def sair(request):
    logout(request)
    return redirect('index')
