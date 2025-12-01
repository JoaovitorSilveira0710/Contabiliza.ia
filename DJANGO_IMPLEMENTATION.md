# Django Backend - Implementações Realizadas

## ✅ Requisitos Implementados

### 1. Framework Django com Padrão MVC
- ✅ Estrutura Django completa com apps modulares
- ✅ Apps criados: `core`, `clients`, `invoices`, `financial`, `accounting`, `documents`
- ✅ Separação clara: Models, Views (ViewSets), Serializers
- ✅ Django REST Framework para API RESTful

### 2. Código em Inglês
- ✅ Todos os nomes de classes, variáveis, funções e pastas em inglês
- ✅ Textos para usuário (labels, mensagens) mantidos em português
- ✅ Exemplos:
  - Classes: `User`, `Client`, `Contract`, `Document`
  - Campos: `company_name`, `tax_id`, `file_path`
  - Mensagens: "Documento gerado em", "Razão Social"

### 3. ACL - Controle de Acesso (Roles & Permissions)
- ✅ Modelo `User` customizado herdando de `AbstractUser`
- ✅ Campo `role` com escolhas: master, admin, accountant, assistant, client_view
- ✅ Modelo `Role` para gerenciar papéis e permissões
- ✅ Permissões customizadas:
  - `view_dashboard`
  - `manage_clients`
  - `manage_invoices`
  - `manage_contracts`
  - `manage_financial`
  - `manage_accounting`
  - `generate_reports`
  - `manage_users`
  - `view_audit_logs`
  - `backup_database`
- ✅ ViewSets com `IsAuthenticated` e checagem de permissões

### 4. Autenticação com Bcrypt
- ✅ Configurado `BCryptSHA256PasswordHasher` como hasher principal
- ✅ Settings atualizados com `PASSWORD_HASHERS`
- ✅ Fallback para PBKDF2, Argon2 para compatibilidade

### 5. Storage de Arquivos
- ✅ Modelo `Document` com campo `file_path` (FileField)
- ✅ Configurado `MEDIA_ROOT` apontando para `storage/`
- ✅ Apenas caminho salvo no banco, arquivo físico em storage
- ✅ Upload automático organizado por `documents/YYYY/MM/`
- ✅ Metadados: file_size, mime_type, uploaded_by

### 6. Geração de PDF
- ✅ Serviço `PDFGenerator` em `core/services/pdf_generator.py`
- ✅ Usa ReportLab para gerar PDFs profissionais
- ✅ Métodos implementados:
  - `generate_invoice_pdf()` - Nota Fiscal
  - `generate_report_pdf()` - Relatórios gerais
- ✅ Conteúdo em português (títulos, labels)
- ✅ Estilização: tabelas, cores, cabeçalhos

### 7. Mecanismo de Backup
- ✅ Management command: `python manage.py backup_database`
- ✅ Copia database SQLite para `backups/backup_YYYYMMDD_HHMMSS/`
- ✅ Copia arquivos de mídia (storage/)
- ✅ Gera arquivo `backup_info.txt` com metadados
- ✅ Mensagens em português

## 📁 Estrutura Criada

```
django_backend/
├── core/                          # App principal - ACL, Users, Utils
│   ├── models.py                  # User, Role
│   ├── views.py                   # UserViewSet, RoleViewSet
│   ├── serializers.py             # UserSerializer, RoleSerializer
│   ├── admin.py                   # Admin customizado
│   ├── management/
│   │   └── commands/
│   │       └── backup_database.py # Comando de backup
│   └── services/
│       └── pdf_generator.py       # Geração de PDFs
├── clients/                       # Clientes, Contratos
├── invoices/                      # Notas Fiscais
├── documents/                     # Gestão de Documentos
│   ├── models.py                  # Document
│   ├── views.py                   # DocumentViewSet
│   ├── serializers.py             # DocumentSerializer
│   └── admin.py
├── financial/                     # Financeiro (futuro)
├── accounting/                    # Contábil (futuro)
└── contabiliza_backend/
    ├── settings.py                # AUTH_USER_MODEL, MEDIA, PASSWORD_HASHERS
    └── urls.py                    # Rotas API

storage/                           # Arquivos físicos (uploads)
backups/                           # Backups do sistema
```

## 🔌 API Endpoints

```
/api/users/                        # Gerenciar usuários
/api/roles/                        # Gerenciar papéis
/api/clients/                      # Clientes
/api/contracts/                    # Contratos
/api/contracted-services/          # Serviços contratados
/api/invoices/                     # Notas fiscais
/api/documents/                    # Upload e gestão de documentos
/api/dashboard-metrics/            # Métricas do dashboard
/api/audits/                       # Logs de auditoria
/admin/                            # Django Admin
```

## 🔧 Configuração

### settings.py - Principais Adições

```python
AUTH_USER_MODEL = 'core.User'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ...
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'storage'
BACKUP_DIR = BASE_DIR.parent / 'backups'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 📦 Dependências Adicionadas

```
bcrypt==4.1.2              # Autenticação segura
reportlab==4.2.5           # Geração de PDFs
Pillow==10.4.0             # Processamento de imagens
```

## 🚀 Comandos Úteis

### Executar servidor
```bash
python run.py
```

### Criar superusuário
```bash
python manage.py createsuperuser
```

### Fazer backup
```bash
python manage.py backup_database
```

### Aplicar migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🔐 Exemplo de Uso - ACL

```python
# View protegida por permissão
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@permission_classes([IsAuthenticated])
def my_view(request):
    if request.user.has_perm('core.manage_clients'):
        # Usuário tem permissão
        pass
```

## 📄 Exemplo de Uso - PDF

```python
from core.services.pdf_generator import PDFGenerator

generator = PDFGenerator('invoice.pdf')

invoice_data = {
    'number': '0001',
    'series': '1',
    'issue_date': '2025-12-01',
    'status': 'pending',
    'client_name': 'Acme Corp',
    'client_tax_id': '12345678000100',
    'total_value': '1000.00'
}

pdf_path = generator.generate_invoice_pdf(invoice_data, 'output/invoice.pdf')
```

## 📤 Exemplo de Upload

```python
# POST /api/documents/
# Content-Type: multipart/form-data

{
    "title": "Contrato Social",
    "document_type": "contract",
    "description": "Contrato social da empresa",
    "file_path": <arquivo>,
    "client": 1
}
```

## ✅ Status Final

Todos os 8 requisitos foram implementados com sucesso:
1. ✅ Django com MVC
2. ✅ Código em inglês, textos em português
3. ✅ ACL com roles e permissões
4. ✅ Autenticação bcrypt
5. ✅ Storage de arquivos (path no BD)
6. ✅ Geração de PDF com ReportLab
7. ✅ Mecanismo de backup
8. ✅ Dependencies atualizadas

## 🎯 Próximos Passos Sugeridos

1. Popular apps `financial` e `accounting` com modelos específicos
2. Implementar endpoints de geração de PDF via API
3. Criar jobs agendados para backup automático
4. Adicionar testes unitários
5. Documentar API com drf-spectacular ou Swagger
