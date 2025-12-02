# bd_CarJa — Sistema de Aluguel e Venda de Veículos (Documento Técnico)

# Autores e Contribuidores
- -----------------------
- Samara
- Eduardo Henrique
- Matheus

# 1. Levantamento e Análise de Requisitos (Escopo)
------------------------------------------------

Minimundo / Contexto:

- Sistema web para gerenciamento de um pequeno sistema de aluguel e venda de veículos. Usuários podem visualizar veículos, alugar por dias ou comprar. Administradores cadastram, editam e removem veículos e acompanham transações.

Requisitos de dados (principais informações a armazenar):

- Veículo: marca, modelo, ano, cor, combustível, preço de venda (campo `preco` atualmente como string), preço diário (`preco_diaria` Decimal), foto.
- Usuário: informações básicas do `django.contrib.auth.User` (username, email, flags como `is_staff`).
- Compra: relação usuário-veículo, preço efetivo da compra, data/hora.
- Locação: relação usuário-veículo, dias, preço unitário, total, data/hora.

Requisitos funcionais (resumo):

- Visualizar catálogo de veículos e detalhes de cada veículo.
- Registrar/Autenticar usuários.
- Alugar veículo por número de dias (calcular total) e salvar a locação.
- Comprar veículo e salvar a compra com o preço efetivo.
- Painel administrativo com listagem de Compras e Locações.
- Dashboard do usuário com suas compras e locações (remoção permitida pelo próprio usuário).

# 2. Análise Funcional (Transações e Regras de Negócio)
----------------------------------------------------

Transações principais e descrição (entradas, saídas e regras):

- Consultar catálogo
  - Entrada: parâmetros de filtro (opcional)
  - Saída: lista de veículos

- Visualizar detalhe de veículo
  - Entrada: `veiculo_id`
  - Saída: ficha do veículo (atributos + foto)

- Comprar veículo
  - Entrada: `user_id` (autenticado), `veiculo_id`
  - Regras: preço salvo deve ser o preço de venda do veículo; se o campo `preco` estiver vazio, o sistema faz fallback no `preco_diaria` (implementação atual). Converter e validar valores numéricos.
  - Saída: registro em `Compra` com `preco` e `created_at`.

- Alugar veículo
  - Entrada: `user_id` (autenticado), `veiculo_id`, `dias` (int > 0)
  - Regras: `preco_unitario` definido por `preco_diaria` (preferido); `total = preco_unitario * dias`.
  - Saída: registro em `Locacao` com `preco_unitario`, `total` e `created_at`.

- Cadastrar/Editar/Excluir veículo (admin)
  - Entrada: dados do veículo e foto
  - Regras: somente `is_staff`/admin devem acessar essas rotas. (Validação server-side recomendada)

# 3. Projeto Conceitual — MER (Modelo Entidade-Relacionamento)
-----------------------------------------------------------

Entidades principais (texto do MER):

- `Veiculo` (PK: `id`) — atributos: `marca`, `combustivel`, `cor`, `modelo`, `ano`, `preco`, `preco_diaria`, `foto`.
- `User` (PK: `id`) — entidade do Django.
- `Compra` (PK: `id`) — FK -> `User`, FK -> `Veiculo`, atributo `preco` (Decimal), `created_at`.
- `Locacao` (PK: `id`) — FK -> `User`, FK -> `Veiculo`, `dias`, `preco_unitario`, `total`, `created_at`.

Relacionamentos e cardinalidades:

- `User` 1 — N `Compra`
- `User` 1 — N `Locacao`
- `Veiculo` 1 — N `Compra`
- `Veiculo` 1 — N `Locacao`

Observação: fotos estão diretamente associadas a `Veiculo` como um atributo (`ImageField`).

# 4. Projeto Lógico (Modelo* Relacional — DER)
-------------------------------------------

Mapeamento e tipos de dados (resumido a partir do código):

- `veiculo_veiculo`:
  - `id` SERIAL PK
  - `marca` SMALLINT
  - `combustivel` SMALLINT
  - `cor` SMALLINT
  - `modelo` VARCHAR(100)
  - `ano` INTEGER
  - `preco` VARCHAR(100)  -- atualmente string formatada
  - `preco_diaria` NUMERIC(10,2)
  - `foto` VARCHAR(255) (path stored by ImageField)

- `veiculo_compra`:
  - `id` SERIAL PK
  - `user_id` INTEGER FK -> auth_user(id)
  - `veiculo_id` INTEGER FK -> veiculo_veiculo(id)
  - `preco` NUMERIC(10,2)
  - `created_at` TIMESTAMP

- `veiculo_locacao`:
  - `id` SERIAL PK
  - `user_id` INTEGER FK
  - `veiculo_id` INTEGER FK
  - `dias` INTEGER
  - `preco_unitario` NUMERIC(10,2)
  - `total` NUMERIC(12,2)
  - `created_at` TIMESTAMP

Normalização:

- O modelo respeita 1FN/2FN/3FN para as entidades listadas. A exceção é o uso de `preco` como string em `Veiculo`, o que dificulta garantias de integridade e operações numéricas.

# 5. Projeto Físico (DDL) — Exemplo PostgreSQL
-------------------------------------------

Exemplo de DDL compatível com PostgreSQL (simplificado):

```sql
CREATE TABLE veiculo_veiculo (
  id SERIAL PRIMARY KEY,
  marca SMALLINT,
  combustivel SMALLINT,
  cor SMALLINT,
  modelo VARCHAR(100) NOT NULL,
  ano INTEGER NOT NULL,
  preco VARCHAR(100),
  preco_diaria NUMERIC(10,2),
  foto VARCHAR(255)
);

CREATE TABLE veiculo_compra (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES auth_user(id),
  veiculo_id INTEGER REFERENCES veiculo_veiculo(id),
  preco NUMERIC(10,2),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE veiculo_locacao (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES auth_user(id),
  veiculo_id INTEGER REFERENCES veiculo_veiculo(id),
  dias INTEGER NOT NULL DEFAULT 1,
  preco_unitario NUMERIC(10,2),
  total NUMERIC(12,2),
  created_at TIMESTAMP DEFAULT now()
);
```

Observação: Django aplica esse DDL via migrations. Use `python manage.py migrate` para criar as tabelas.

# 6. Projeto da Aplicação — Implementação (o que está implementado)
---------------------------------------------------------------

Tecnologia e arquitetura:
- Implementado em Python/Django (MVC-like). Camada de dados em `models.py`, lógica em `views.py`, e interface em `templates/`.

Arquivos e mapeamento (onde ver no projeto):

- Modelos: `sistema/veiculo/models.py` (`Veiculo`, `Compra`, `Locacao`).
- Views e lógica: `sistema/veiculo/views.py` (comprar, alugar, dashboards, etc.).
- URLs do app: `sistema/veiculo/urls.py`.
- Templates: `sistema/templates/` e `sistema/templates/veiculo/` (`listar.html`, `exibir.html`, `user_dashboard.html`, `admin_dashboard.html`, `resumo.html`, etc.).
- Comando de populamento: `sistema/veiculo/management/commands/populate_veiculos.py`.

Funcionalidades completas já implementadas:
- Exibição de catálogo e detalhes de veículos.
- Compra e armazenamento em `Compra` (com parser para converter preço string para Decimal quando necessário).
- Locação com cálculo de total e armazenamento em `Locacao`.
- Dashboards (admin e usuário) e templates com botões e ações básicas.
- Upload de fotos via `ImageField` (`Veiculo.foto`) com fallback para placeholder.

Itens pendentes / Recomendações (priorizadas)
---------------------------------------------

ALTA
- Migrar `Veiculo.preco` para `DecimalField` com migração de dados (garantir backup e testes de conversão).  
- Harden server-side permissions: aplicar `UserPassesTestMixin` ou `@user_passes_test` nas views de CRUD de veículos.

MÉDIO
- Testes automatizados (unit + integração) para fluxos de compra/locação e validações.  
- Documentar variáveis de ambiente e criar `ENV.example`.

BAIXO
- Melhorar UX (thumbnail CSS centralizado, mensagens de erro mais claras).  
- Adicionar badges/README mais curto para apresentação.

Checklist detalhado está disponível em `checklist.md` neste repositório.

Próximos passos sugeridos (posso implementar):

- Gerar a migração e script de conversão para `preco -> DecimalField` (com preview de linhas que não convertam).  
- Implementar proteção de views administrativas (mixins/permissions).  
- Criar `ENV.example` e instruções curtas para PostgreSQL local.
- Adicionar testes básicos para compra/locação.

---
Arquivo `checklist.md` criado com checklist detalhado.
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

# Como rodar (desenvolvimento)
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

# 6. Rodar o servidor de desenvolvimento:

```powershell
python manage.py runserver
```

Observações importantes
----------------------
- As imagens de veículos são armazenadas via `ImageField` (MEDIA). Configure `MEDIA_ROOT`/`MEDIA_URL` em `settings.py` e sirva-as em desenvolvimento com `django.conf.urls.static.static()`.
- O campo `Veiculo.preco` atualmente é uma string formatada — em futuras melhorias recomenda-se converter esse campo para `DecimalField` com uma migração para normalizar os dados.

Autores
-------
- Samara Coelha
- Eduardo Henrique
- Matheus Sulino

Licença
-------
Este repositório é parte de um trabalho acadêmico e não possui licença explícita definida aqui. Adicione uma licença se necessário.

Mais informações
