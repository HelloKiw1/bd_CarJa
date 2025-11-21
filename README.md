# bd_CarJa

Projeto de Banco de Dados para um sistema de aluguel e venda de veículos.

Descrição
--------
Este repositório contém a implementação de um sistema simples para gerenciamento de veículos, com recursos para:

- Exibir catálogo de veículos
- Alugar veículos (locação por dias)
- Comprar veículos (compra definitiva)
- Registrar transações: `Compra` e `Locacao`
- Painel administrativo com listagem de transações
- Dashboard do usuário com histórico de compras e locações

Tecnologias
-----------
- Python 3.x
- Django 5.x
- PostgreSQL (configurável via variáveis de ambiente)
- Bootstrap + FontAwesome para a interface

Estrutura resumida
------------------
- `sistema/` - projeto Django
	- `veiculo/` - app principal (models, views, templates, management commands)
	- `templates/` - templates base e páginas
	- `static/` - recursos estáticos (logo, placeholder de imagem)

Como rodar (desenvolvimento)
----------------------------
1. Criar e ativar um ambiente virtual (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente (ex.: `DATABASE_URL` ou as variáveis usadas em `sistema/sistema/settings.py`).

4. Aplicar migrações:

```powershell
cd sistema
python manage.py migrate
```

5. Popular dados de exemplo (opcional):

```powershell
python manage.py populate_veiculos
```

6. Rodar o servidor de desenvolvimento:

```powershell
python manage.py runserver
```

Observações importantes
----------------------
- As imagens de veículos são armazenadas via `ImageField` (MEDIA). Configure `MEDIA_ROOT`/`MEDIA_URL` em `settings.py` e sirva-as em desenvolvimento com `django.conf.urls.static.static()`.
- O campo `Veiculo.preco` atualmente é uma string formatada — em futuras melhorias recomenda-se converter esse campo para `DecimalField` com uma migração para normalizar os dados.

Autores
-------
- Samara
- Eduardo Henrique
- Matheus

Licença
-------
Este repositório é parte de um trabalho acadêmico e não possui licença explícita definida aqui. Adicione uma licença se necessário.

Mais informações