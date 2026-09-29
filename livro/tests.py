import shutil
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Categoria, Emprestimo, Livros

Usuario = get_user_model()

MEDIA_TEMP = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TEMP)
class LivroTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMP, ignore_errors=True)

    def setUp(self):
        self.dono = Usuario.objects.create_user(email='ana@exemplo.com', password='x', nome='Ana')
        self.amigo = Usuario.objects.create_user(email='bruno@exemplo.com', password='x', nome='Bruno')
        self.categoria = Categoria.objects.get(nome='Romance')
        self.livro = Livros.objects.create(
            titulo='Dom Casmurro', autor='Machado de Assis', qnt_pag=256, editora='Penguin',
            ano_publi='1899', nota=10, categoria=self.categoria, usuario=self.dono,
        )

    def mensagens(self, resposta):
        return [str(m) for m in get_messages(resposta.wsgi_request)]


class AcessoTests(LivroTestCase):
    def test_paginas_publicas(self):
        for nome in ('index', 'about', 'login', 'cadastro'):
            with self.subTest(pagina=nome):
                self.assertEqual(self.client.get(reverse(nome)).status_code, 200)

    def test_paginas_privadas_exigem_login(self):
        for url in (reverse('home'), reverse('ver_livros', args=[self.livro.id]), reverse('seus_emprestimos')):
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_paginas_do_dono(self):
        self.client.force_login(self.dono)
        urls = (
            reverse('index'), reverse('home'), reverse('ver_livros', args=[self.livro.id]),
            reverse('historico_emprestimos', args=[self.livro.id]), reverse('seus_emprestimos'),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_outro_usuario_nao_acessa_livro_alheio(self):
        self.client.force_login(self.amigo)

        self.assertEqual(self.client.get(reverse('ver_livros', args=[self.livro.id])).status_code, 404)
        self.assertEqual(self.client.post(reverse('excluir_livro', args=[self.livro.id])).status_code, 404)
        self.assertTrue(Livros.objects.filter(id=self.livro.id).exists())

    def test_livro_inexistente_retorna_404(self):
        self.client.force_login(self.dono)
        self.assertEqual(self.client.get(reverse('ver_livros', args=[9999])).status_code, 404)


class CadastroLivroTests(LivroTestCase):
    def test_cadastrar_livro_associa_ao_usuario_logado(self):
        self.client.force_login(self.dono)

        resposta = self.client.post(reverse('cadastrar_livro'), {
            'titulo': 'O Hobbit', 'autor': 'Tolkien', 'qnt_pag': 336, 'editora': 'HarperCollins',
            'ano_publi': '1937', 'nota': 8, 'categoria': self.categoria.id, 'usuario': self.amigo.id,
        })

        self.assertRedirects(resposta, reverse('home'))
        self.assertIn('Livro cadastrado com sucesso', self.mensagens(resposta))
        self.assertEqual(Livros.objects.get(titulo='O Hobbit').usuario, self.dono)

    def test_cadastro_invalido_nao_cria_livro(self):
        self.client.force_login(self.dono)

        resposta = self.client.post(reverse('cadastrar_livro'), {'titulo': 'Sem dados'})

        self.assertRedirects(resposta, reverse('home'))
        self.assertTrue(self.mensagens(resposta)[0].startswith('Não foi possível cadastrar o livro.'))
        self.assertFalse(Livros.objects.filter(titulo='Sem dados').exists())

    def test_excluir_livro(self):
        self.client.force_login(self.dono)

        resposta = self.client.post(reverse('excluir_livro', args=[self.livro.id]))

        self.assertRedirects(resposta, reverse('home'))
        self.assertFalse(Livros.objects.filter(id=self.livro.id).exists())

    def test_excluir_livro_nao_aceita_get(self):
        self.client.force_login(self.dono)
        self.assertEqual(self.client.get(reverse('excluir_livro', args=[self.livro.id])).status_code, 405)


class EmprestimoTests(LivroTestCase):
    def emprestar(self, para=None):
        para = para or self.amigo
        return self.client.post(reverse('emprestar_livro', args=[self.livro.id]), {'nome_emprestado': para.id})

    def test_fluxo_completo_emprestar_devolver_avaliar(self):
        self.client.force_login(self.dono)

        resposta = self.emprestar()
        self.assertRedirects(resposta, reverse('home'))
        self.assertIn('Empréstimo realizado com sucesso', self.mensagens(resposta))
        self.livro.refresh_from_db()
        self.assertTrue(self.livro.emprestado)

        resposta = self.client.post(reverse('devolver_livro', args=[self.livro.id]))
        self.assertIn('Devolução realizada com sucesso', self.mensagens(resposta))
        self.livro.refresh_from_db()
        emprestimo = Emprestimo.objects.get(livro=self.livro)
        self.assertFalse(self.livro.emprestado)
        self.assertIsNotNone(emprestimo.data_devolucao)

        resposta = self.client.post(reverse('processa_avaliacao'), {'id_emprestimo': emprestimo.id, 'opcoes': 'B'})
        self.assertRedirects(resposta, reverse('historico_emprestimos', args=[self.livro.id]))
        emprestimo.refresh_from_db()
        self.assertEqual(emprestimo.avaliacao, 'B')
        self.assertEqual(emprestimo.estrelas, [True, True, True, False])

    def test_nao_empresta_livro_ja_emprestado(self):
        self.client.force_login(self.dono)
        self.emprestar()

        resposta = self.emprestar()

        self.assertIn('Desculpe, esse livro já está emprestado', self.mensagens(resposta))
        self.assertEqual(Emprestimo.objects.count(), 1)

    def test_nao_empresta_para_si_mesmo(self):
        self.client.force_login(self.dono)

        resposta = self.emprestar(para=self.dono)

        self.assertRedirects(resposta, reverse('ver_livros', args=[self.livro.id]))
        self.assertFalse(Emprestimo.objects.exists())

    def test_nao_avalia_emprestimo_em_aberto(self):
        self.client.force_login(self.dono)
        self.emprestar()
        emprestimo = Emprestimo.objects.get()

        resposta = self.client.post(reverse('processa_avaliacao'), {'id_emprestimo': emprestimo.id, 'opcoes': 'O'})

        self.assertEqual(resposta.status_code, 404)

    def test_seus_emprestimos_lista_livros_recebidos(self):
        self.client.force_login(self.dono)
        self.emprestar()
        self.client.force_login(self.amigo)

        resposta = self.client.get(reverse('seus_emprestimos'))

        self.assertContains(resposta, 'Dom Casmurro')


@override_settings(MEDIA_ROOT=MEDIA_TEMP)
class DadosIniciaisTests(TestCase):
    def test_categorias_sao_criadas_pela_migration(self):
        self.assertTrue(Categoria.objects.filter(nome='Tecnologia').exists())

    def test_seed_cria_dados_e_nao_duplica(self):
        call_command('seed', stdout=StringIO())
        call_command('seed', stdout=StringIO())

        self.assertEqual(Usuario.objects.count(), 5)
        self.assertEqual(Livros.objects.count(), 16)
        self.assertEqual(Emprestimo.objects.count(), 15)
        self.assertEqual(Livros.objects.filter(emprestado=True).count(), 4)
        self.assertFalse(Livros.objects.filter(image='').exists())
        self.assertTrue(all(livro.image.storage.exists(livro.image.name) for livro in Livros.objects.all()))
        self.assertTrue(self.client.login(username='ana@empresta.ai', password='demo1234'))

    def test_seed_reset_recria_os_dados(self):
        call_command('seed', stdout=StringIO())
        Livros.objects.filter(titulo='Duna').delete()

        call_command('seed', '--reset', stdout=StringIO())

        self.assertEqual(Usuario.objects.count(), 5)
        self.assertTrue(Livros.objects.filter(titulo='Duna').exists())
