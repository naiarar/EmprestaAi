from django.db import migrations

CATEGORIAS = [
    ('Romance', 'Histórias de amor e relacionamentos'),
    ('Ficção científica', 'Futuro, tecnologia e outros mundos'),
    ('Fantasia', 'Magia, criaturas e mundos imaginários'),
    ('Suspense', 'Mistério, investigação e tensão'),
    ('Biografia', 'Histórias de vidas reais'),
    ('Autoajuda', 'Desenvolvimento pessoal'),
    ('Tecnologia', 'Programação, computação e afins'),
    ('Infantil', 'Livros para crianças'),
    ('Outros', 'Livros que não se encaixam nas demais categorias'),
]


def criar_categorias(apps, schema_editor):
    Categoria = apps.get_model('livro', 'Categoria')
    for nome, descricao in CATEGORIAS:
        Categoria.objects.get_or_create(nome=nome, defaults={'descricao': descricao})


def remover_categorias(apps, schema_editor):
    Categoria = apps.get_model('livro', 'Categoria')
    Categoria.objects.filter(nome__in=[nome for nome, _ in CATEGORIAS], livros__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('livro', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_categorias, remover_categorias),
    ]
