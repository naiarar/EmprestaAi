# EmprestaAi 📚

Sistema de **biblioteca compartilhada**: cada usuário cadastra seus livros, empresta para outras pessoas, registra a devolução e avalia como foi o empréstimo.

## Funcionalidades

- Cadastro e login por email usando o `django.contrib.auth` (user model customizado, senhas com hash e validadores de senha do Django)
- Cadastro de livros com capa, autor, editora, número de páginas, categoria e nota
- Empréstimo e devolução de livros, com controle de disponibilidade
- Histórico de empréstimos por livro
- Avaliação do empréstimo após a devolução (Péssimo, Ruim, Bom, Ótimo)
- Tela "Livros que peguei emprestado", com os livros que outras pessoas emprestaram ao usuário
- Landing page com os últimos livros cadastrados

## Stack

Python · Django (templates server-side) · SQLite · Bootstrap 4

## Como rodar

**Pré-requisitos:** Python 3.12 ou superior (exigido pelo Django 6.1) e `git`. Não precisa instalar banco de dados, o projeto usa SQLite.

```bash
git clone https://github.com/naiarar/EmprestaAi.git
cd EmprestaAi

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed            # opcional: popula o sistema com dados de exemplo
python manage.py runserver
```

Acesse <http://localhost:8000>.

### Dados de exemplo (seed)

O comando `python manage.py seed` cria 5 usuários, 16 livros com capa em várias categorias e 15 empréstimos, alguns ainda em aberto e outros já devolvidos e avaliados. Assim dá para ver todas as telas com conteúdo logo depois de clonar.

Todos os usuários usam a senha `demo1234`:

| Email               | Livros na estante                                      |
| ------------------- | ------------------------------------------------------ |
| `ana@empresta.ai`   | Código Limpo, Dom Casmurro, O Hobbit, Duna             |
| `bruno@empresta.ai` | O Programador Pragmático, Agatha Christie, O Pequeno Príncipe, Introdução à Programação com Python |
| `carla@empresta.ai` | Orgulho e Preconceito, Eu Sou Malala, Hábitos Atômicos |
| `diego@empresta.ai` | Fundação, O Nome do Vento, Garota Exemplar             |
| `elisa@empresta.ai` | Capitães da Areia, Steve Jobs                          |

As capas que não vêm do repositório são geradas pelo próprio comando com o Pillow, usando a fonte [Quicksand](https://github.com/andrew-paglinawan/QuicksandFamily) (licença SIL OFL, em `livro/fontes/`).

Rodar o comando de novo não duplica nada. Para apagar os dados de exemplo e criá-los outra vez, use `python manage.py seed --reset`. Contas criadas por você não são afetadas.

Para testar o fluxo de empréstimo do zero, basta criar duas contas em `/auth/cadastro/`. A senha precisa ter pelo menos 8 caracteres, não pode ser só números nem uma senha comum.

### Variáveis de ambiente (opcional)

Para rodar localmente não é preciso configurar nada. Para sobrescrever os padrões, copie o exemplo e edite:

```bash
cp .env.example .env
```

| Variável        | Padrão                     | Descrição                                   |
| --------------- | -------------------------- | ------------------------------------------- |
| `SECRET_KEY`    | chave insegura de dev      | Obrigatório trocar fora do ambiente local   |
| `DEBUG`         | `True`                     | Com `False`, o Django não serve `/media/`   |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1`      | Hosts separados por vírgula                 |

### Painel admin

```bash
python manage.py createsuperuser
```

O comando pede email, nome e senha. Acesse <http://localhost:8000/admin/> com esse email. O superusuário também consegue entrar no sistema normalmente, já que admin e aplicação usam o mesmo model de usuário.

## Testes

```bash
python manage.py test
```

Cobrem cadastro/login, controle de acesso (um usuário não vê nem apaga livro de outro), o fluxo de empréstimo → devolução → avaliação e os dados iniciais.

## Arquitetura

```text
EmprestaAi/
├── biblioteca/   settings e rotas principais
├── usuarios/     user model customizado (login por email), cadastro, login e logout
├── livro/        livros, categorias, empréstimos, avaliações e o comando seed
├── index/        landing page e página "Sobre"
├── templates/    layout base (Bootstrap)
├── css/          estilo da landing page (servido como static)
└── media/        capas dos livros enviadas pelos usuários
```

### Modelo de dados

- **Usuario**: estende o `AbstractUser` do Django; login pelo e-mail (único), com nome
- **Categoria**: agrupa os livros (categorias iniciais criadas por migration)
- **Livros**: pertence a um Usuario e a uma Categoria, com flag `emprestado`
- **Emprestimo**: liga um Livro a quem pegou emprestado, com datas e avaliação

## Autora

Feito por [Naiara Rodrigues](https://github.com/naiarar).
