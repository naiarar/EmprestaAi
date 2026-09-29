from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            classe = 'form-control-file' if isinstance(campo.widget, forms.ClearableFileInput) else 'form-control'
            campo.widget.attrs.setdefault('class', classe)


class CadastroForm(BootstrapMixin, UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('nome', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe um usuário com este email.')
        return email


class LoginForm(BootstrapMixin, AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()
