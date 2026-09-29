from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=30)
    descricao = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.nome


class Livros(models.Model):
    image = models.ImageField('capa', upload_to='capa_livro', null=True, blank=True)
    titulo = models.CharField('título', max_length=100)
    autor = models.CharField(max_length=50)
    qnt_pag = models.PositiveIntegerField('número de páginas')
    editora = models.CharField(max_length=50)
    ano_publi = models.CharField('ano de publicação', max_length=10)
    nota = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], help_text='De 0 a 10')
    data_cadastro = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emprestado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Livro'

    def __str__(self):
        return self.titulo


class Emprestimo(models.Model):
    choices = (
        ('P', 'Péssimo'),
        ('R', 'Ruim'),
        ('B', 'Bom'),
        ('O', 'Ótimo')
    )
    ESTRELAS = {'P': 1, 'R': 2, 'B': 3, 'O': 4}

    nome_emprestado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='emprestimos_recebidos'
    )
    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(blank=True, null=True)
    livro = models.ForeignKey(Livros, on_delete=models.CASCADE)
    avaliacao = models.CharField(max_length=1, choices=choices, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.nome_emprestado} | {self.livro}"

    @property
    def estrelas(self):
        total = self.ESTRELAS.get(self.avaliacao, 0)
        return [True] * total + [False] * (len(self.ESTRELAS) - total)
