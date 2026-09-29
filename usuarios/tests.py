from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

Usuario = get_user_model()

SENHA = 'Segredo-forte-123'


class CadastroTests(TestCase):
    def cadastrar(self, **dados):
        payload = {'nome': 'Maria', 'email': 'Maria@Exemplo.com', 'password1': SENHA, 'password2': SENHA}
        payload.update(dados)
        return self.client.post(reverse('cadastro'), payload)

    def test_cadastro_cria_usuario_com_senha_hasheada(self):
        resposta = self.cadastrar()

        self.assertRedirects(resposta, reverse('login'))
        usuario = Usuario.objects.get(email='maria@exemplo.com')
        self.assertTrue(usuario.check_password(SENHA))
        self.assertNotEqual(usuario.password, SENHA)
        mensagens = [str(m) for m in get_messages(resposta.wsgi_request)]
        self.assertIn('Cadastro realizado com sucesso. Faça login para continuar.', mensagens)

    def test_cadastro_rejeita_email_duplicado(self):
        Usuario.objects.create_user(email='maria@exemplo.com', password='x', nome='Maria')

        resposta = self.cadastrar(nome='Outra')

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Já existe um usuário com este email.')
        self.assertEqual(Usuario.objects.count(), 1)

    def test_cadastro_aplica_validadores_de_senha(self):
        resposta = self.cadastrar(password1='123', password2='123')

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Usuario.objects.exists())

    def test_cadastro_rejeita_senhas_diferentes(self):
        resposta = self.cadastrar(password2='outra-senha-456')

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Usuario.objects.exists())

    def test_usuario_logado_e_redirecionado(self):
        usuario = Usuario.objects.create_user(email='maria@exemplo.com', password=SENHA, nome='Maria')
        self.client.force_login(usuario)

        self.assertRedirects(self.client.get(reverse('cadastro')), reverse('home'))
        self.assertRedirects(self.client.get(reverse('login')), reverse('home'))


class LoginTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(email='maria@exemplo.com', password=SENHA, nome='Maria')

    def test_login_com_credenciais_validas(self):
        resposta = self.client.post(reverse('login'), {'username': 'MARIA@exemplo.com', 'password': SENHA})

        self.assertRedirects(resposta, reverse('home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.usuario.id)

    def test_login_com_senha_errada(self):
        resposta = self.client.post(reverse('login'), {'username': 'maria@exemplo.com', 'password': 'errada'})

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_respeita_next(self):
        destino = reverse('seus_emprestimos')
        resposta = self.client.post(
            f"{reverse('login')}?next={destino}",
            {'username': 'maria@exemplo.com', 'password': SENHA, 'next': destino},
        )

        self.assertRedirects(resposta, destino)

    def test_sair_faz_logout(self):
        self.client.force_login(self.usuario)

        resposta = self.client.post(reverse('sair'))

        self.assertRedirects(resposta, reverse('index'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_sair_nao_aceita_get(self):
        self.client.force_login(self.usuario)

        self.assertEqual(self.client.get(reverse('sair')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)


class SuperusuarioTests(TestCase):
    def test_create_superuser_usa_email(self):
        admin = Usuario.objects.create_superuser(email='Admin@Exemplo.com', password=SENHA, nome='Admin')

        self.assertTrue(admin.is_staff and admin.is_superuser)
        self.assertEqual(admin.email, 'admin@exemplo.com')
        self.assertTrue(self.client.login(username='admin@exemplo.com', password=SENHA))
        self.assertEqual(self.client.get('/admin/').status_code, 200)
