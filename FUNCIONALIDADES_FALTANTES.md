# 📋 Funcionalidades Faltantes no Backend Django

## ❌ FUNCIONALIDADES QUE O FRONTEND TEM MAS O BACKEND NÃO

### 1. 💰 **MÓDULO FINANCEIRO COMPLETO**

#### Models necessários:
- ✅ `FinancialCategory` - Categorias (receitas/despesas)
- ✅ `BankAccount` - Contas bancárias
- ✅ `FinancialTransaction` - Lançamentos financeiros
- ✅ `AccountsPayable` - Contas a pagar
- ✅ `AccountsReceivable` - Contas a receber
- ✅ `CashFlow` - Fluxo de caixa diário

#### Endpoints necessários:
```
POST   /api/financial/transactions/          # Criar lançamento
GET    /api/financial/transactions/          # Listar lançamentos
PUT    /api/financial/transactions/{id}/     # Atualizar
DELETE /api/financial/transactions/{id}/     # Excluir
POST   /api/financial/transactions/{id}/pay/ # Marcar como pago
GET    /api/financial/accounts-payable/      # Contas a pagar
GET    /api/financial/accounts-receivable/   # Contas a receber
GET    /api/financial/cash-flow/             # Fluxo de caixa
POST   /api/financial/import-invoices/       # Importar notas fiscais
GET    /api/financial/categories/            # Categorias
POST   /api/financial/categories/            # Criar categoria
GET    /api/financial/bank-accounts/         # Contas bancárias
POST   /api/financial/bank-accounts/         # Criar conta
```

#### Funcionalidades:
- Lançamentos de receitas e despesas
- Contas a pagar e receber
- Categorização de transações
- Múltiplas contas bancárias
- Conciliação bancária
- Fluxo de caixa
- Importação automática de notas fiscais
- Recorrência de lançamentos
- Anexos em lançamentos
- Relatórios financeiros

---

### 2. ⚖️ **MÓDULO JURÍDICO**

#### Models necessários:
- `LegalProcess` - Processos jurídicos
- `LegalContract` - Contratos
- `LegalDocument` - Documentos legais
- `Hearing` - Audiências
- `Deadline` - Prazos processuais
- `Lawyer` - Advogados

#### Endpoints necessários:
```
POST   /api/legal/processes/                # Criar processo
GET    /api/legal/processes/                # Listar processos
PUT    /api/legal/processes/{id}/           # Atualizar
DELETE /api/legal/processes/{id}/           # Excluir
GET    /api/legal/contracts/                # Contratos
POST   /api/legal/contracts/                # Criar contrato
GET    /api/legal/hearings/                 # Audiências
POST   /api/legal/hearings/                 # Agendar audiência
GET    /api/legal/deadlines/                # Prazos
POST   /api/legal/documents/upload/         # Upload documento
```

#### Funcionalidades:
- Gestão de processos judiciais
- Controle de contratos
- Agenda de audiências
- Controle de prazos
- Upload de documentos legais
- Alertas de vencimento
- Histórico de movimentações

---

### 3. 📦 **MÓDULO ESTOQUE**

#### Models necessários:
- `Product` - Produtos/Itens
- `ProductCategory` - Categorias de produtos
- `Supplier` - Fornecedores
- `StockMovement` - Movimentações
- `StockCount` - Contagens de estoque
- `Warehouse` - Depósitos/Armazéns

#### Endpoints necessários:
```
POST   /api/stock/products/                 # Criar produto
GET    /api/stock/products/                 # Listar produtos
PUT    /api/stock/products/{id}/            # Atualizar
DELETE /api/stock/products/{id}/            # Excluir
POST   /api/stock/movements/                # Movimentação (entrada/saída)
GET    /api/stock/movements/                # Histórico
POST   /api/stock/count/                    # Contagem de estoque
GET    /api/stock/low-stock/                # Produtos com estoque baixo
GET    /api/stock/suppliers/                # Fornecedores
POST   /api/stock/suppliers/                # Criar fornecedor
```

#### Funcionalidades:
- Cadastro de produtos
- Controle de estoque (quantidade)
- Movimentações de entrada e saída
- Contagem de estoque
- Alertas de estoque mínimo
- Gestão de fornecedores
- Múltiplos depósitos
- Custo médio e preço de venda
- Relatórios de inventário

---

### 4. 📊 **MÓDULO RELATÓRIOS**

#### Relatórios necessários:
1. **Relatório de Notas Fiscais**
   - Por período
   - Por cliente
   - Por tipo (NF-e, NFS-e, NFC-e)
   - Resumo de impostos

2. **Relatório Financeiro**
   - DRE (Demonstração do Resultado)
   - Fluxo de caixa projetado
   - Contas a pagar/receber
   - Balanço patrimonial

3. **Relatório de Clientes**
   - Top clientes por faturamento
   - Inadimplência
   - Análise de crédito

4. **Relatório Contábil**
   - Livro razão
   - Balancete
   - Plano de contas
   - Demonstrativos contábeis

5. **Relatório de Estoque**
   - Inventário
   - Movimentações
   - Produtos mais vendidos

#### Endpoints necessários:
```
GET  /api/reports/invoices/                 # Relatório de notas
GET  /api/reports/financial/dre/            # DRE
GET  /api/reports/financial/cash-flow/      # Fluxo de caixa
GET  /api/reports/clients/top/              # Top clientes
GET  /api/reports/accounting/balance/       # Balancete
GET  /api/reports/stock/inventory/          # Inventário
POST /api/reports/export/pdf/               # Exportar PDF
POST /api/reports/export/excel/             # Exportar Excel
```

---

### 5. 👥 **GESTÃO DE USUÁRIOS**

#### Models necessários:
- ✅ `User` (já existe no core)
- `UserPermission` - Permissões personalizadas
- `ActivityLog` - Log de atividades
- `SystemSettings` - Configurações do sistema

#### Endpoints necessários:
```
GET    /api/users/                          # Listar usuários
POST   /api/users/                          # Criar usuário
PUT    /api/users/{id}/                     # Atualizar
DELETE /api/users/{id}/                     # Excluir
PATCH  /api/users/{id}/change-password/    # Trocar senha
PATCH  /api/users/{id}/change-role/        # Alterar perfil
GET    /api/users/activity-log/            # Log de atividades
GET    /api/settings/                       # Configurações
PUT    /api/settings/                       # Salvar configurações
```

---

### 6. 📈 **DASHBOARDS ADICIONAIS**

#### Já implementado:
- ✅ Dashboard overview
- ✅ Gráfico de faturamento mensal
- ✅ Distribuição de notas por status/tipo
- ✅ Resumo de impostos

#### Faltam:
- Projeção de receitas/despesas
- Análise de inadimplência
- Metas e objetivos
- Comparativos (mês atual vs anterior)

---

## 🚀 RESUMO DO QUE PRECISA SER FEITO

### **PRIORIDADE ALTA** (Frontend usa ativamente):
1. ✅ **Módulo Financeiro** - 70% pronto (models criados, faltam views/serializers)
2. ❌ **Módulo Jurídico** - 0% pronto
3. ❌ **Módulo Estoque** - 0% pronto (tem apenas Product vazio)
4. ❌ **Relatórios** - 0% pronto
5. ❌ **CRUD de Usuários** - 0% pronto (tem apenas model User)

### **PRIORIDADE MÉDIA**:
- Configurações do sistema
- Logs de auditoria
- Notificações

### **PRIORIDADE BAIXA**:
- Dashboards adicionais
- Exportação de relatórios em Excel
- Integração com APIs externas

---

## 📝 PRÓXIMOS PASSOS

Para completar o backend, você precisa:

1. **Terminar o Módulo Financeiro**:
   - Criar serializers
   - Criar views/viewsets
   - Registrar no admin
   - Adicionar às URLs

2. **Criar o Módulo Jurídico completo**:
   - Models
   - Serializers
   - Views
   - URLs
   - Admin

3. **Completar o Módulo Estoque**:
   - Models adicionais
   - Serializers
   - Views
   - URLs
   - Admin

4. **Implementar Relatórios**:
   - Views para geração de relatórios
   - Exportação PDF/Excel
   - URLs

5. **CRUD de Usuários**:
   - Serializers
   - ViewSets
   - Permissões
   - URLs

---

## 💡 ESTIMATIVA DE CÓDIGO

Para completar 100% do backend, você precisará de aproximadamente:

- **10-15 models** adicionais
- **15-20 serializers**
- **15-20 viewsets**
- **50-70 endpoints** no total
- **~3000-4000 linhas de código** adicional

---

## ✅ O QUE JÁ ESTÁ FUNCIONANDO

1. ✅ CRUD completo de Clientes
2. ✅ Notas Fiscais com XML e PDF
3. ✅ Dashboard principal
4. ✅ Autenticação com bcrypt
5. ✅ Admin Django completo
6. ✅ Models financeiros (faltam apenas views/serializers)

---

**Status Atual: ~40% do backend implementado**
**Frontend pronto: ~90%**
**Gap: ~50% de funcionalidades faltando**
