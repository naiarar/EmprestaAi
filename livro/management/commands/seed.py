import textwrap
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from livro.models import Categoria, Emprestimo, Livros

Usuario = get_user_model()

SENHA = 'demo1234'
DOMINIO = 'empresta.ai'
PASTA_CAPAS = 'capa_livro/seed'
FONTE = Path(__file__).resolve().parents[2] / 'fontes' / 'Quicksand.ttf'

USUARIOS = ['Ana', 'Bruno', 'Carla', 'Diego', 'Elisa']

LIVROS = [
    ('Ana', 'Código Limpo', 'Robert C. Martin', 425, 'Alta Books', '2009', 9, 'Tecnologia', 'capa_livro/cod_limpo.jpg'),
    ('Ana', 'Dom Casmurro', 'Machado de Assis', 256, 'Penguin', '1899', 10, 'Romance', None),
    ('Ana', 'O Hobbit', 'J. R. R. Tolkien', 336, 'HarperCollins', '1937', 8, 'Fantasia', None),
    ('Ana', 'Duna', 'Frank Herbert', 680, 'Aleph', '1965', 10, 'Ficção científica', None),
    ('Bruno', 'O Programador Pragmático', 'Andrew Hunt e David Thomas', 352, 'Bookman', '1999', 9, 'Tecnologia', None),
    ('Bruno', 'Assassinato no Expresso do Oriente', 'Agatha Christie', 240, 'HarperCollins', '1934', 8, 'Suspense', None),
    ('Bruno', 'O Pequeno Príncipe', 'Antoine de Saint-Exupéry', 96, 'Agir', '1943', 10, 'Infantil', None),
    ('Bruno', 'Introdução à Programação com Python', 'Nilo Ney Coutinho Menezes', 328, 'Novatec', '2019', 9, 'Tecnologia', 'capa_livro/livro1.jpg'),
    ('Carla', 'Orgulho e Preconceito', 'Jane Austen', 424, 'Martin Claret', '1813', 9, 'Romance', None),
    ('Carla', 'Eu Sou Malala', 'Malala Yousafzai', 360, 'Companhia das Letras', '2013', 8, 'Biografia', None),
    ('Carla', 'Hábitos Atômicos', 'James Clear', 320, 'Alta Life', '2018', 7, 'Autoajuda', None),
    ('Diego', 'Fundação', 'Isaac Asimov', 240, 'Aleph', '1951', 9, 'Ficção científica', None),
    ('Diego', 'O Nome do Vento', 'Patrick Rothfuss', 656, 'Arqueiro', '2007', 9, 'Fantasia', None),
    ('Diego', 'Garota Exemplar', 'Gillian Flynn', 448, 'Intrínseca', '2012', 7, 'Suspense', None),
    ('Elisa', 'Capitães da Areia', 'Jorge Amado', 280, 'Companhia das Letras', '1937', 9, 'Romance', None),
    ('Elisa', 'Steve Jobs', 'Walter Isaacson', 624, 'Companhia das Letras', '2011', 8, 'Biografia', None),
]

EMPRESTIMOS = [
    ('Código Limpo', 'Bruno', 60, 40, 'O'),
    ('Código Limpo', 'Diego', 30, 12, 'B'),
    ('Dom Casmurro', 'Carla', 50, 35, 'O'),
    ('Dom Casmurro', 'Bruno', 5, None, None),
    ('O Hobbit', 'Elisa', 20, 8, None),
    ('Duna', 'Diego', 90, 70, 'R'),
    ('O Programador Pragmático', 'Ana', 45, 30, 'O'),
    ('O Programador Pragmático', 'Carla', 10, None, None),
    ('Assassinato no Expresso do Oriente', 'Elisa', 25, 15, 'B'),
    ('Orgulho e Preconceito', 'Ana', 40, 20, 'O'),
    ('Eu Sou Malala', 'Elisa', 3, None, None),
    ('Hábitos Atômicos', 'Diego', 70, 60, 'P'),
    ('Fundação', 'Ana', 15, None, None),
    ('O Nome do Vento', 'Bruno', 35, 10, 'B'),
    ('Capitães da Areia', 'Carla', 28, 14, 'O'),
]

CORES = [
    ('#824104', '#F39E4E'), ('#185864', '#2BB0B0'), ('#5F2E18', '#D27246'), ('#2D3047', '#E0A458'),
    ('#1B4332', '#95D5B2'), ('#6A0572', '#F7B2BD'), ('#22223B', '#C9ADA7'), ('#003049', '#FCBF49'),
]


def email_de(nome):
    return f'{nome.lower()}@{DOMINIO}'


def fonte(tamanho, peso='Bold'):
    try:
        tipo = ImageFont.truetype(str(FONTE), tamanho)
    except OSError:
        return ImageFont.load_default(size=tamanho)
    try:
        tipo.set_variation_by_name(peso)
    except (OSError, ValueError):
        pass
    return tipo


def gerar_capa(titulo, autor, indice):
    relativo = f'{PASTA_CAPAS}/{indice:02d}.png'
    destino = Path(settings.MEDIA_ROOT) / relativo
    destino.parent.mkdir(parents=True, exist_ok=True)

    fundo, destaque = CORES[indice % len(CORES)]
    largura, altura = 400, 600
    imagem = Image.new('RGB', (largura, altura), fundo)
    desenho = ImageDraw.Draw(imagem)
    desenho.rectangle([24, 24, largura - 24, altura - 24], outline=destaque, width=6)
    desenho.rectangle([24, altura - 170, largura - 24, altura - 24], fill=destaque)

    area = largura - 90
    tamanho = 44
    while tamanho > 24:
        linhas = textwrap.wrap(titulo, width=max(8, int(area / (tamanho * 0.55))))
        if all(desenho.textlength(linha, font=fonte(tamanho)) <= area for linha in linhas):
            break
        tamanho -= 2
    y = 90
    for linha in linhas:
        desenho.text((largura / 2, y), linha, font=fonte(tamanho), fill='white', anchor='mm')
        y += int(tamanho * 1.25)

    tamanho_autor = 24
    while tamanho_autor > 14 and desenho.textlength(autor, font=fonte(tamanho_autor, 'SemiBold')) > area:
        tamanho_autor -= 1
    desenho.text((largura / 2, altura - 97), autor, font=fonte(tamanho_autor, 'SemiBold'), fill=fundo, anchor='mm')

    imagem.save(destino)
    return relativo


class Command(BaseCommand):
    help = 'Popula o banco com usuários, livros, capas e empréstimos de exemplo.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Apaga os dados de exemplo existentes e cria de novo.')

    @transaction.atomic
    def handle(self, *args, reset=False, **options):
        emails = [email_de(nome) for nome in USUARIOS]
        existentes = Usuario.objects.filter(email__in=emails)

        if existentes.exists():
            if not reset:
                self.stdout.write(self.style.WARNING(
                    'Os dados de exemplo já existem. Use "python manage.py seed --reset" para recriá-los.'
                ))
                return
            existentes.delete()

        usuarios = {
            nome: Usuario.objects.create_user(email=email_de(nome), password=SENHA, nome=nome)
            for nome in USUARIOS
        }

        livros = {}
        for indice, (dono, titulo, autor, paginas, editora, ano, nota, categoria, capa) in enumerate(LIVROS):
            if not capa or not (Path(settings.MEDIA_ROOT) / capa).exists():
                capa = gerar_capa(titulo, autor, indice)
            livros[titulo] = Livros.objects.create(
                usuario=usuarios[dono],
                titulo=titulo,
                autor=autor,
                qnt_pag=paginas,
                editora=editora,
                ano_publi=ano,
                nota=nota,
                categoria=Categoria.objects.get_or_create(nome=categoria)[0],
                image=capa,
            )

        agora = timezone.now()
        for titulo, tomador, dias_emprestimo, dias_devolucao, avaliacao in EMPRESTIMOS:
            livro = livros[titulo]
            Emprestimo.objects.create(
                livro=livro,
                nome_emprestado=usuarios[tomador],
                data_emprestimo=agora - timedelta(days=dias_emprestimo),
                data_devolucao=agora - timedelta(days=dias_devolucao) if dias_devolucao is not None else None,
                avaliacao=avaliacao,
            )
            if dias_devolucao is None:
                livro.emprestado = True
                livro.save(update_fields=['emprestado'])

        self.stdout.write(self.style.SUCCESS(
            f'Seed criado: {len(usuarios)} usuários, {len(livros)} livros e {len(EMPRESTIMOS)} empréstimos.'
        ))
        self.stdout.write(f'Entre com qualquer um destes emails e a senha "{SENHA}":')
        for email in emails:
            self.stdout.write(f'  {email}')
