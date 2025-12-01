# 📊 Sistema Contábil Completo - Django

## ✅ O que foi implementado

### 1. **CRUD Completo de Clientes**
- ✅ Criar, Editar, Excluir e Listar clientes
- ✅ Pessoa Física (PF) e Pessoa Jurídica (PJ)
- ✅ Documentos: CPF/CNPJ, Inscrição Estadual, Municipal
- ✅ Endereço completo
- ✅ Múltiplos contatos por cliente
- ✅ Filtros: status, tipo de pessoa, busca por nome/documento
- ✅ Estatísticas de clientes

### 2. **Geração de Notas Fiscais**
- ✅ Criar notas fiscais (NF-e, NFS-e, NFC-e)
- ✅ **Gerar XML** automaticamente (formato SEFAZ)
- ✅ **Gerar PDF** (DANFE) profissional
- ✅ Download de XML e PDF
- ✅ Múltiplos itens por nota
- ✅ Cálculo automático de impostos (ICMS, IPI, PIS, COFINS, ISS)
- ✅ Chave de acesso automática
- ✅ Status: Rascunho, Pendente, Autorizada, Cancelada
- ✅ Cancelamento de notas
- ✅ Filtros por status, tipo, cliente, período

### 3. **Dashboard com Dados em Tempo Real**
- ✅ Visão geral do sistema
- ✅ Estatísticas de clientes e notas
- ✅ Faturamento mensal e semanal
- ✅ Gráficos de receita (12 meses)
- ✅ Distribuição por status e tipo
- ✅ Top 5 clientes
- ✅ Resumo de impostos
- ✅ Atividades recentes
- ✅ Desempenho semanal

### 4. **Contabilidade**
- ✅ Relatórios financeiros
- ✅ Consolidação de impostos
- ✅ Análise por período
- ✅ Valores totais e médios

---

## 🚀 Como Usar

### **1. Iniciar o Servidor**

```powershell
cd "C:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"
python run.py
```

O servidor estará disponível em: **http://localhost:8000**

### **2. Criar Superusuário**

```powershell
cd django_backend
python manage.py createsuperuser
```

### **3. Acessar Admin Django**

URL: **http://localhost:8000/admin/**

Login com o superusuário criado

---

## 📡 API Endpoints

### **Clientes**

#### Listar/Criar Clientes
```http
GET  /api/clients/
POST /api/clients/
```

**Filtros disponíveis:**
- `?status=active` - Filtrar por status
- `?person_type=PF` - Filtrar por tipo (PF/PJ)
- `?search=nome` - Buscar por nome/documento

#### Detalhes/Editar/Excluir Cliente
```http
GET    /api/clients/{id}/
PUT    /api/clients/{id}/
PATCH  /api/clients/{id}/
DELETE /api/clients/{id}/
```

#### Ações Especiais
```http
POST  /api/clients/{id}/add_contact/      # Adicionar contato
PATCH /api/clients/{id}/change_status/    # Alterar status
GET   /api/clients/statistics/            # Estatísticas
```

**Exemplo de criação de cliente:**
```json
{
  "person_type": "PJ",
  "name": "Empresa Exemplo LTDA",
  "trade_name": "Exemplo",
  "tax_id": "12345678000190",
  "email": "contato@exemplo.com",
  "phone": "(11) 99999-9999",
  "zip_code": "01310-100",
  "street": "Avenida Paulista",
  "number": "1000",
  "neighborhood": "Bela Vista",
  "city": "São Paulo",
  "state": "SP",
  "status": "active"
}
```

---

### **Notas Fiscais**

#### Listar/Criar Notas
```http
GET  /api/invoices/
POST /api/invoices/
```

**Filtros disponíveis:**
- `?status=authorized` - Por status
- `?invoice_type=nfe` - Por tipo
- `?client_id=1` - Por cliente
- `?start_date=2024-01-01` - Data inicial
- `?end_date=2024-12-31` - Data final
- `?search=123` - Buscar por número/chave

#### Detalhes/Editar/Excluir Nota
```http
GET    /api/invoices/{id}/
PUT    /api/invoices/{id}/
PATCH  /api/invoices/{id}/
DELETE /api/invoices/{id}/
```

#### 🔥 Gerar XML e PDF
```http
POST /api/invoices/{id}/generate_xml/    # Gerar XML (NF-e)
POST /api/invoices/{id}/generate_pdf/    # Gerar PDF (DANFE)
GET  /api/invoices/{id}/download_xml/    # Download XML
GET  /api/invoices/{id}/download_pdf/    # Download PDF
```

#### Outras Ações
```http
PATCH /api/invoices/{id}/change_status/  # Alterar status
POST  /api/invoices/{id}/cancel/         # Cancelar nota
GET   /api/invoices/statistics/          # Estatísticas
```

**Exemplo de criação de nota:**
```json
{
  "number": "001",
  "series": "1",
  "invoice_type": "nfe",
  "client": 1,
  "issuer_name": "Minha Empresa LTDA",
  "issuer_tax_id": "98765432000199",
  "issue_date": "2024-12-01T10:00:00",
  "discount": 0,
  "shipping": 50.00,
  "insurance": 0,
  "other_expenses": 0,
  "icms_base": 1000.00,
  "icms_value": 180.00,
  "ipi_value": 0,
  "pis_value": 16.50,
  "cofins_value": 76.00,
  "iss_value": 0,
  "items": [
    {
      "item_type": "product",
      "code": "PROD001",
      "description": "Produto Exemplo",
      "ncm": "12345678",
      "cfop": "5102",
      "unit": "UN",
      "quantity": 10,
      "unit_value": 100.00,
      "discount": 0,
      "icms_rate": 18.00,
      "icms_value": 180.00,
      "ipi_rate": 0,
      "ipi_value": 0,
      "pis_rate": 1.65,
      "pis_value": 16.50,
      "cofins_rate": 7.60,
      "cofins_value": 76.00
    }
  ]
}
```

---

### **Dashboard (Tempo Real)**

```http
GET /api/dashboard/overview/              # Visão geral completa
GET /api/dashboard/revenue-chart/         # Faturamento mensal (12 meses)
GET /api/dashboard/invoices-by-status/    # Distribuição por status
GET /api/dashboard/invoices-by-type/      # Distribuição por tipo
GET /api/dashboard/recent-activities/     # Atividades recentes
GET /api/dashboard/taxes-summary/         # Resumo de impostos
GET /api/dashboard/weekly-performance/    # Desempenho semanal
```

**Exemplo de resposta do overview:**
```json
{
  "clients": {
    "total": 50,
    "active": 45,
    "new_this_month": 5,
    "pessoa_fisica": 30,
    "pessoa_juridica": 20
  },
  "invoices": {
    "total": 200,
    "authorized": 180,
    "pending": 15,
    "cancelled": 5,
    "this_month": 25
  },
  "financial": {
    "total_value": "500000.00",
    "total_taxes": "85000.00",
    "avg_value": "2500.00",
    "month_revenue": "125000.00",
    "recent_revenue": "150000.00"
  },
  "top_clients": [...],
  "last_update": "2024-12-01T15:30:00"
}
```

---

## 🔐 Autenticação

O sistema usa **Basic Authentication**. Adicione o header:

```http
Authorization: Basic <base64(username:password)>
```

Ou use sessões do Django após login.

---

## 📊 Fluxo de Uso Completo

### 1. **Cadastrar Cliente**
```bash
POST /api/clients/
# Dados do cliente (JSON acima)
```

### 2. **Criar Nota Fiscal**
```bash
POST /api/invoices/
# Dados da nota com itens
```

### 3. **Gerar XML da Nota**
```bash
POST /api/invoices/1/generate_xml/
# Retorna URL do XML gerado
```

### 4. **Gerar PDF (DANFE)**
```bash
POST /api/invoices/1/generate_pdf/
# Retorna URL do PDF gerado
```

### 5. **Download dos Arquivos**
```bash
GET /api/invoices/1/download_xml/
GET /api/invoices/1/download_pdf/
```

### 6. **Autorizar Nota**
```bash
PATCH /api/invoices/1/change_status/
{ "status": "authorized" }
```

### 7. **Ver Dashboard Atualizado**
```bash
GET /api/dashboard/overview/
# Dados atualizados em tempo real
```

---

## 🎯 Recursos Implementados

✅ CRUD completo de clientes (criar, editar, excluir, listar)
✅ Geração de Notas Fiscais Eletrônicas (NF-e)
✅ **Geração de XML** no formato SEFAZ
✅ **Geração de PDF (DANFE)** profissional com ReportLab
✅ Download de XML e PDF
✅ Dashboard com estatísticas em **tempo real**
✅ Gráficos de faturamento mensal
✅ Resumo de impostos (ICMS, IPI, PIS, COFINS, ISS)
✅ Top clientes por faturamento
✅ Filtros avançados em todas as consultas
✅ Autenticação com bcrypt
✅ Paginação automática
✅ Admin Django completo

---

## 🗂️ Estrutura dos Arquivos

```
django_backend/
├── core/                           # Autenticação e ACL
│   ├── models.py                  # User model
│   └── admin.py                   # Admin de usuários
├── clients/                        # Gestão de clientes
│   ├── models.py                  # Client, ClientContact
│   ├── serializers.py             # Serializers
│   ├── views.py                   # ClientViewSet (CRUD)
│   └── admin.py                   # Admin
├── invoices/                       # Notas fiscais
│   ├── models.py                  # Invoice, InvoiceItem
│   ├── serializers.py             # Serializers
│   ├── views.py                   # InvoiceViewSet (CRUD + XML/PDF)
│   ├── admin.py                   # Admin
│   └── services/
│       ├── xml_generator.py       # 🔥 Gerador de XML (NF-e)
│       └── pdf_generator.py       # 🔥 Gerador de PDF (DANFE)
├── dashboard/                      # Dashboard e estatísticas
│   └── views.py                   # 7 endpoints de dashboard
└── contabiliza_backend/
    ├── settings.py                # Configurações Django
    └── urls.py                    # Rotas da API
```

---

## 🧪 Testando a API

### PowerShell (Windows):
```powershell
# Criar cliente
$headers = @{ "Content-Type" = "application/json" }
$body = '{"person_type":"PF","name":"João Silva","tax_id":"12345678900","email":"joao@email.com","phone":"11999999999","zip_code":"01310-100","street":"Av Paulista","number":"1000","neighborhood":"Bela Vista","city":"São Paulo","state":"SP"}'

Invoke-RestMethod -Uri "http://localhost:8000/api/clients/" -Method POST -Headers $headers -Body $body -Credential (Get-Credential)

# Listar clientes
Invoke-RestMethod -Uri "http://localhost:8000/api/clients/" -Method GET -Credential (Get-Credential)

# Dashboard
Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard/overview/" -Method GET -Credential (Get-Credential)
```

---

## 🎉 Pronto para Produção!

O sistema está **100% funcional** com:
- ✅ CRUD completo de clientes
- ✅ Geração de XML e PDF para notas fiscais
- ✅ Dashboard com dados em tempo real
- ✅ Todos os cálculos contábeis automatizados

**Execute `python run.py` e comece a usar!**
