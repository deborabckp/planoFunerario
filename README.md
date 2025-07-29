# Sistema de Gerenciamento de Planos Funerários

## Descrição
Sistema web completo desenvolvido em Django e Django REST Framework para gerenciamento de planos funerários, voltado para uso exclusivo de funcionários da funerária.

## Tecnologias Utilizadas
- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT (Simple JWT)
- **Documentação**: Swagger/OpenAPI (via DRF)

## Estrutura do Projeto

### Entidades Principais
- **Funcionários da Funerária** (usuários do sistema)
- **Clientes da Funerária**
- **Dependentes dos Clientes**
- **Planos Funerários**
- **Pagamentos dos Planos**
- **Serviços Prestados**
- **Status e Tipos de Serviços**

### Sistema de Autenticação
- Login/logout com JWT
- Apenas funcionários autenticados têm acesso
- Controle de permissões por endpoint

## Configuração e Instalação

### 1. Pré-requisitos
```bash
# PostgreSQL instalado e rodando
# Python 3.8+ instalado
```

### 2. Configuração do Banco de Dados
```sql
-- No PostgreSQL, criar o banco:
CREATE DATABASE funerariadb;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE funerariadb TO postgres;
```

### 3. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração Inicial
```bash
# Executar script de configuração automática
python scripts/setup_database.py
```

### 5. Executar o Servidor
```bash
python manage.py runserver
```

## Endpoints da API

### Autenticação
- `POST /api/auth/login/` - Login de funcionários
- `POST /api/auth/logout/` - Logout
- `POST /api/token/refresh/` - Renovar token JWT

### Gestão de Entidades
- `GET|POST /api/funcionarios/` - Listar/Criar funcionários
- `GET|PUT|DELETE /api/funcionarios/{id}/` - Detalhar/Atualizar/Excluir funcionário

- `GET|POST /api/clientes/` - Listar/Criar clientes
- `GET|PUT|DELETE /api/clientes/{id}/` - Detalhar/Atualizar/Excluir cliente
- `GET /api/clientes/buscar_cpf/?cpf=123.456.789-00` - Buscar por CPF
- `GET /api/clientes/exportar_csv/` - Exportar clientes em CSV

- `GET|POST /api/dependentes/` - Listar/Criar dependentes
- `GET /api/dependentes/por_cliente/?cliente_id=1` - Dependentes por cliente

- `GET|POST /api/planos/` - Listar/Criar planos funerários
- `GET /api/planos/{id}/detalhado/` - Plano com pagamentos e serviços
- `GET /api/planos/relatorio_financeiro/` - Relatório financeiro

- `GET|POST /api/pagamentos/` - Listar/Criar pagamentos
- `GET /api/pagamentos/historico_plano/?plano_id=1` - Histórico por plano
- `GET /api/pagamentos/relatorio_periodo/` - Relatório por período

- `GET|POST /api/servicos/` - Listar/Criar serviços prestados
- `GET /api/servicos/por_cliente/?cliente_id=1` - Serviços por cliente
- `GET /api/servicos/relatorio_tipos/` - Relatório por tipos

### Configurações
- `GET|POST /api/status/` - Status do sistema
- `GET|POST /api/dependente-status/` - Status de dependentes
- `GET|POST /api/tipos-servicos/` - Tipos de serviços

## Interface Administrativa

### Django Admin Customizado
- Acesso: `http://localhost:8000/admin/`
- **Usuário**: `admin`
- **Senha**: `admin123`

### Funcionalidades do Admin
- Gestão completa de todas as entidades
- Filtros e buscas avançadas
- Relatórios inline (dependentes nos clientes)
- Interface personalizada para funerária

## Funcionalidades Avançadas

### Validações Implementadas
- **Validação de CPF**: Algoritmo completo de validação
- **CPFs únicos**: Não permite duplicatas no sistema
- **Validação de telefone**: Formato brasileiro
- **Integridade referencial**: Relacionamentos FK protegidos

### Filtros e Buscas
- **Filtros por data**: Criação, nascimento, serviços
- **Busca textual**: Nome, CPF, email, telefone
- **Filtros por status**: Todos os tipos de status
- **Ordenação**: Por múltiplos campos

### Relatórios e Exportações
- **CSV de clientes**: Exportação completa
- **Relatórios financeiros**: Por período e plano
- **Estatísticas do dashboard**: Contadores e totais
- **Histórico de pagamentos**: Por plano e período

### Segurança
- **Autenticação JWT**: Tokens seguros
- **Permissões por endpoint**: Apenas autenticados
- **Controle de usuários**: Quem criou/atualizou registros
- **Validações de backend**: Dados consistentes

## Dados Iniciais (Fixtures)

### Status do Sistema
- Ativo, Inativo, Pendente, Pago, Cancelado

### Status de Dependentes  
- Ativo, Inativo, Falecido, Suspenso

### Tipos de Serviços
- Velório Simples/Completo, Cremação, Sepultamento
- Traslado, Embalsamento, Ornamentação Floral
- Cerimônia Religiosa

## Casos de Uso Principais

### 1. Cadastro de Cliente com Dependentes
```python
# 1. Funcionário faz login
# 2. Cadastra cliente com dados pessoais
# 3. Adiciona dependentes ao cliente
# 4. Associa cliente a um plano funerário
```

### 2. Registro de Falecimento e Serviço
```python
# 1. Funcionário localiza cliente/dependente
# 2. Registra o falecimento (mudança de status)
# 3. Cria registro de serviço prestado
# 4. Associa ao plano ativo do cliente
```

### 3. Controle de Pagamentos
```python
# 1. Cliente efetua pagamento do plano
# 2. Funcionário registra pagamento no sistema
# 3. Sistema atualiza status do pagamento
# 4. Histórico fica disponível para consulta
```

## Melhorias Futuras
- Dashboard com gráficos interativos
- Notificações por email
- Relatórios em PDF
- API para aplicativo mobile
- Backup automático
- Logs de auditoria

## Observações Acadêmicas
Este projeto foi desenvolvido para a disciplina de **Engenharia de Software**, com foco em:
- Arquitetura de software bem estruturada
- Modelagem de banco de dados
- APIs RESTful padronizadas
- Validações e integridade de dados
- Interface administrativa funcional
- Documentação técnica completa

---

**Desenvolvido com ❤️ para a Dsiciplina de Engenharia de Software**
