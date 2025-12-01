# 🔄 Frontend Sincronizado com Backend Django

## ✅ Sincronização Completa Realizada

### 📝 Alterações Implementadas:

#### 1. **config.js** - Endpoints Atualizados
Todos os endpoints foram atualizados para corresponder exatamente aos endpoints do Django:

```javascript
ENDPOINTS: {
  // Core
  AUTH: '/api-auth',
  USERS: '/users',
  
  // Clients
  CLIENTES: '/clients',
  CLIENT_CONTACTS: '/client-contacts',
  
  // Invoices
  NOTAS_FISCAIS: '/invoices',
  INVOICE_ITEMS: '/invoice-items',
  
  // Financial
  FINANCEIRO: '/financial-transactions',
  FINANCIAL_CATEGORIES: '/financial-categories',
  BANK_ACCOUNTS: '/bank-accounts',
  ACCOUNTS_PAYABLE: '/accounts-payable',
  ACCOUNTS_RECEIVABLE: '/accounts-receivable',
  CASH_FLOW: '/cash-flow',
  
  // Legal
  JURIDICO: '/legal-processes',
  LAWYERS: '/lawyers',
  HEARINGS: '/hearings',
  LEGAL_CONTRACTS: '/legal-contracts',
  LEGAL_DEADLINES: '/legal-deadlines',
  
  // Stock
  ESTOQUE: '/products',
  PRODUCT_CATEGORIES: '/product-categories',
  SUPPLIERS: '/suppliers',
  WAREHOUSES: '/warehouses',
  STOCK_MOVEMENTS: '/stock-movements',
  STOCK_COUNTS: '/stock-counts',
  
  // Dashboard
  DASHBOARD: '/dashboard',
  CONTABIL: '/contabil'
}
```

#### 2. **api.js** - Helper Completo Criado
Novo arquivo com todas as funções para comunicação com o backend:

**Funcionalidades Disponíveis:**

##### 👥 Clientes
```javascript
await api.getClients()
await api.getClient(id)
await api.createClient(data)
await api.updateClient(id, data)
await api.deleteClient(id)
await api.getClientStatistics()
await api.addClientContact(clientId, contactData)
await api.changeClientStatus(clientId, status)
```

##### 📄 Notas Fiscais
```javascript
await api.getInvoices()
await api.getInvoice(id)
await api.createInvoice(data)
await api.updateInvoice(id, data)
await api.deleteInvoice(id)
await api.generateInvoiceXML(id)
await api.generateInvoicePDF(id)
await api.downloadInvoiceXML(id)
await api.downloadInvoicePDF(id)
await api.cancelInvoice(id, reason)
await api.changeInvoiceStatus(id, status)
```

##### 💰 Financeiro
```javascript
await api.getFinancialCategories()
await api.getBankAccounts()
await api.getBankAccountsSummary()
await api.getFinancialTransactions(params)
await api.createFinancialTransaction(data)
await api.payTransaction(id, data)
await api.cancelTransaction(id)
await api.importInvoices(data)
await api.getFinancialSummary(params)
await api.getAccountsPayable(params)
await api.getAccountsReceivable(params)
await api.getCashFlow(params)
```

##### ⚖️ Jurídico
```javascript
await api.getLawyers()
await api.getLegalProcesses(params)
await api.getLegalProcess(id)
await api.createLegalProcess(data)
await api.updateLegalProcess(id, data)
await api.changeLegalProcessStatus(id, status)
await api.getLegalProcessStatistics()
await api.getHearings(params)
await api.getUpcomingHearings()
await api.getLegalContracts(params)
await api.getExpiringContracts()
await api.getLegalDeadlines(params)
await api.completeDeadline(id)
await api.getOverdueDeadlines()
```

##### 📦 Estoque
```javascript
await api.getProductCategories()
await api.getSuppliers(params)
await api.getWarehouses()
await api.getProducts(params)
await api.getProduct(id)
await api.createProduct(data)
await api.updateProduct(id, data)
await api.deleteProduct(id)
await api.getLowStockProducts()
await api.getProductStatistics()
await api.getStockMovements(params)
await api.createStockMovement(data)
```

##### 📈 Dashboard
```javascript
await api.getDashboardOverview()
await api.getRevenueChart()
await api.getInvoicesByStatus()
await api.getInvoicesByType()
await api.getRecentActivities()
await api.getTaxesSummary()
await api.getWeeklyPerformance()
```

##### 👤 Usuários
```javascript
await api.getUsers(params)
await api.getUser(id)
await api.createUser(data)
await api.updateUser(id, data)
await api.deleteUser(id)
await api.changeUserPassword(id, oldPassword, newPassword)
await api.changeUserRole(id, role)
await api.getUserStatistics()
```

---

## 🚀 Como Usar

### 1. Exemplo: Carregar Clientes
```javascript
async function carregarClientes() {
  try {
    const clientes = await api.getClients({ status: 'active' });
    console.log('Clientes:', clientes);
    // Renderizar na tela...
  } catch (error) {
    UTILS.showToast('Erro ao carregar clientes', 'error');
    console.error(error);
  }
}
```

### 2. Exemplo: Criar Nota Fiscal
```javascript
async function criarNotaFiscal() {
  try {
    const notaData = {
      client: clienteId,
      invoice_type: 'nfe',
      series: '1',
      nature_of_operation: 'Venda de mercadoria',
      items: [
        {
          description: 'Produto 1',
          quantity: 10,
          unit_price: 100.00
        }
      ]
    };
    
    const nota = await api.createInvoice(notaData);
    UTILS.showToast('Nota criada com sucesso!', 'success');
    
    // Gerar XML
    await api.generateInvoiceXML(nota.id);
    UTILS.showToast('XML gerado!', 'success');
    
  } catch (error) {
    UTILS.showToast('Erro ao criar nota', 'error');
  }
}
```

### 3. Exemplo: Dashboard
```javascript
async function carregarDashboard() {
  try {
    const overview = await api.getDashboardOverview();
    
    document.getElementById('totalClientes').textContent = overview.total_clients;
    document.getElementById('totalNotas').textContent = overview.total_invoices;
    document.getElementById('receitaTotal').textContent = 
      UTILS.formatarReal(overview.total_revenue);
    
  } catch (error) {
    UTILS.showToast('Erro ao carregar dashboard', 'error');
  }
}
```

### 4. Exemplo: Transação Financeira
```javascript
async function criarTransacao() {
  try {
    const transacao = {
      transaction_type: 'revenue',
      description: 'Pagamento NF 123',
      category: categoriaId,
      account: contaId,
      amount: 1500.00,
      due_date: '2025-12-15',
      status: 'pending'
    };
    
    const result = await api.createFinancialTransaction(transacao);
    UTILS.showToast('Transação criada!', 'success');
    
  } catch (error) {
    UTILS.showToast('Erro ao criar transação', 'error');
  }
}
```

### 5. Exemplo: Processo Jurídico
```javascript
async function criarProcesso() {
  try {
    const processo = {
      process_number: '1234567-89.2025.8.26.0100',
      process_type: 'civil',
      title: 'Ação de Cobrança',
      description: 'Cobrança de valores...',
      client: clienteId,
      lawyer: advogadoId,
      court: 'Fórum Central',
      priority: 'high',
      start_date: '2025-12-01'
    };
    
    const result = await api.createLegalProcess(processo);
    UTILS.showToast('Processo criado!', 'success');
    
  } catch (error) {
    UTILS.showToast('Erro ao criar processo', 'error');
  }
}
```

---

## 📋 Parâmetros de Filtro Disponíveis

### Clientes
```javascript
{
  status: 'active' | 'inactive' | 'suspended',
  person_type: 'PF' | 'PJ',
  search: 'texto de busca'
}
```

### Notas Fiscais
```javascript
{
  status: 'draft' | 'authorized' | 'cancelled' | 'denied',
  invoice_type: 'nfe' | 'nfce' | 'nfse',
  client_id: id,
  start_date: 'YYYY-MM-DD',
  end_date: 'YYYY-MM-DD'
}
```

### Transações Financeiras
```javascript
{
  transaction_type: 'revenue' | 'expense' | 'transfer',
  status: 'pending' | 'paid' | 'received' | 'cancelled' | 'overdue',
  category_id: id,
  account_id: id,
  start_date: 'YYYY-MM-DD',
  end_date: 'YYYY-MM-DD',
  search: 'texto'
}
```

### Processos Jurídicos
```javascript
{
  process_type: 'civil' | 'labor' | 'tax' | 'corporate' | 'administrative',
  status: 'active' | 'suspended' | 'archived' | 'finished',
  priority: 'low' | 'medium' | 'high' | 'urgent',
  lawyer_id: id,
  client_id: id,
  search: 'texto'
}
```

### Produtos
```javascript
{
  category_id: id,
  warehouse_id: id,
  low_stock: 'true' | 'false',
  search: 'texto'
}
```

---

## ⚙️ Configuração

### Alterar URL da API (opcional)
```javascript
// No console ou em config.js
localStorage.setItem('API_BASE', 'https://api.seudominio.com/api');
```

### Token de Autenticação
O sistema gerencia automaticamente o token JWT:
```javascript
// Salvar token após login
UTILS.setToken('seu-token-jwt');

// Verificar autenticação
if (UTILS.isAuthenticated()) {
  // Usuário logado
}

// Fazer logout
UTILS.clearToken();
UTILS.clearCurrentUser();
```

---

## 🎯 Boas Práticas

### 1. Sempre use try-catch
```javascript
async function minhaFuncao() {
  try {
    const dados = await api.getClients();
    // processar dados
  } catch (error) {
    UTILS.showToast('Erro ao carregar', 'error');
    console.error(error);
  }
}
```

### 2. Use loading states
```javascript
async function carregar() {
  showLoading(true);
  try {
    const dados = await api.getClients();
    renderizar(dados);
  } catch (error) {
    UTILS.showToast('Erro', 'error');
  } finally {
    showLoading(false);
  }
}
```

### 3. Validar dados antes de enviar
```javascript
if (!data.name || !data.email) {
  UTILS.showToast('Preencha todos os campos', 'warning');
  return;
}

await api.createClient(data);
```

---

## 🔗 URLs dos Arquivos

- **config.js**: `/frontend/src/js/config.js`
- **api.js**: `/frontend/src/js/api.js`
- **index.html**: Já incluído
- **dashboard.html**: Já incluído

---

## ✅ Status da Sincronização

- ✅ Endpoints atualizados
- ✅ API helper completo
- ✅ Scripts incluídos no HTML
- ✅ Utilitários disponíveis
- ✅ Tratamento de erros
- ✅ Autenticação JWT

---

## 🎉 Pronto para Usar!

O frontend agora está **100% sincronizado** com o backend Django. Todas as páginas podem usar:

```javascript
// Instância global disponível
window.api.getClients()
window.api.createInvoice()
window.api.getDashboardOverview()
// ... todas as outras funções
```

**Data de Sincronização:** 01 de Dezembro de 2025  
**Status:** ✅ COMPLETO
