/**
 * API Helper - Sincronizado com Django Backend
 * Última atualização: 2025-12-01
 */

class API {
  constructor() {
    this.baseURL = CONFIG.API_BASE;
  }

  /**
   * Helper para fazer requisições HTTP
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = UTILS.getToken();
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    };

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        UTILS.clearToken();
        UTILS.clearCurrentUser();
        window.location.href = '/pages/login.html';
        throw new Error('Não autorizado');
      }

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Erro na requisição');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ==================== CLIENTES ====================
  
  async getClients(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${queryString ? '?' + queryString : ''}`);
  }

  async getClient(id) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}/`);
  }

  async createClient(data) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateClient(id, data) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteClient(id) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}/`, {
      method: 'DELETE'
    });
  }

  async getClientStatistics() {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/statistics/`);
  }

  async addClientContact(clientId, contactData) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${clientId}/add_contact/`, {
      method: 'POST',
      body: JSON.stringify(contactData)
    });
  }

  async changeClientStatus(clientId, status) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${clientId}/change_status/`, {
      method: 'POST',
      body: JSON.stringify({ status })
    });
  }

  // ==================== NOTAS FISCAIS ====================
  
  async getInvoices(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${queryString ? '?' + queryString : ''}`);
  }

  async getInvoice(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/`);
  }

  async createInvoice(data) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateInvoice(id, data) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteInvoice(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/`, {
      method: 'DELETE'
    });
  }

  async generateInvoiceXML(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/generate_xml/`, {
      method: 'POST'
    });
  }

  async generateInvoicePDF(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/generate_pdf/`, {
      method: 'POST'
    });
  }

  async downloadInvoiceXML(id) {
    window.open(`${this.baseURL}${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/download_xml/`, '_blank');
  }

  async downloadInvoicePDF(id) {
    window.open(`${this.baseURL}${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/download_pdf/`, '_blank');
  }

  async cancelInvoice(id, reason) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/cancel/`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
  }

  async changeInvoiceStatus(id, status) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/change_status/`, {
      method: 'POST',
      body: JSON.stringify({ status })
    });
  }

  // ==================== FINANCEIRO ====================
  
  async getFinancialCategories() {
    return this.request(`${CONFIG.ENDPOINTS.FINANCIAL_CATEGORIES}/`);
  }

  async getBankAccounts() {
    return this.request(`${CONFIG.ENDPOINTS.BANK_ACCOUNTS}/`);
  }

  async getBankAccountsSummary() {
    return this.request(`${CONFIG.ENDPOINTS.BANK_ACCOUNTS}/summary/`);
  }

  async getFinancialTransactions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/${queryString ? '?' + queryString : ''}`);
  }

  async createFinancialTransaction(data) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async payTransaction(id, data) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/${id}/pay/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async cancelTransaction(id) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/${id}/cancel/`, {
      method: 'POST'
    });
  }

  async importInvoices(data) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/import_invoices/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async getFinancialSummary(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/summary/${queryString ? '?' + queryString : ''}`);
  }

  async getAccountsPayable(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.ACCOUNTS_PAYABLE}/${queryString ? '?' + queryString : ''}`);
  }

  async getAccountsReceivable(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.ACCOUNTS_RECEIVABLE}/${queryString ? '?' + queryString : ''}`);
  }

  async getCashFlow(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.CASH_FLOW}/${queryString ? '?' + queryString : ''}`);
  }

  // ==================== JURÍDICO ====================
  
  async getLawyers() {
    return this.request(`${CONFIG.ENDPOINTS.LAWYERS}/`);
  }

  async getLegalProcesses(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/${queryString ? '?' + queryString : ''}`);
  }

  async getLegalProcess(id) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/${id}/`);
  }

  async createLegalProcess(data) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateLegalProcess(id, data) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async changeLegalProcessStatus(id, status) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/${id}/change_status/`, {
      method: 'POST',
      body: JSON.stringify({ status })
    });
  }

  async getLegalProcessStatistics() {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/statistics/`);
  }

  async getHearings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.HEARINGS}/${queryString ? '?' + queryString : ''}`);
  }

  async getUpcomingHearings() {
    return this.request(`${CONFIG.ENDPOINTS.HEARINGS}/upcoming/`);
  }

  async getLegalContracts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.LEGAL_CONTRACTS}/${queryString ? '?' + queryString : ''}`);
  }

  async getExpiringContracts() {
    return this.request(`${CONFIG.ENDPOINTS.LEGAL_CONTRACTS}/expiring_soon/`);
  }

  async getLegalDeadlines(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.LEGAL_DEADLINES}/${queryString ? '?' + queryString : ''}`);
  }

  async completeDeadline(id) {
    return this.request(`${CONFIG.ENDPOINTS.LEGAL_DEADLINES}/${id}/complete/`, {
      method: 'POST'
    });
  }

  async getOverdueDeadlines() {
    return this.request(`${CONFIG.ENDPOINTS.LEGAL_DEADLINES}/overdue/`);
  }

  // ==================== ESTOQUE ====================
  
  async getProductCategories() {
    return this.request(`${CONFIG.ENDPOINTS.PRODUCT_CATEGORIES}/`);
  }

  async getSuppliers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.SUPPLIERS}/${queryString ? '?' + queryString : ''}`);
  }

  async getWarehouses() {
    return this.request(`${CONFIG.ENDPOINTS.WAREHOUSES}/`);
  }

  async getProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/${queryString ? '?' + queryString : ''}`);
  }

  async getProduct(id) {
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/${id}/`);
  }

  async createProduct(data) {
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateProduct(id, data) {
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteProduct(id) {
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/${id}/`, {
      method: 'DELETE'
    });
  }

  async getLowStockProducts() {
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/low_stock/`);
  }

  async getProductStatistics() {
    return this.request(`${CONFIG.ENDPOINTS.ESTOQUE}/statistics/`);
  }

  async getStockMovements(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.STOCK_MOVEMENTS}/${queryString ? '?' + queryString : ''}`);
  }

  async createStockMovement(data) {
    return this.request(`${CONFIG.ENDPOINTS.STOCK_MOVEMENTS}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // ==================== DASHBOARD ====================
  
  async getDashboardOverview() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/overview/`);
  }

  async getRevenueChart() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/revenue-chart/`);
  }

  async getInvoicesByStatus() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/invoices-by-status/`);
  }

  async getInvoicesByType() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/invoices-by-type/`);
  }

  async getRecentActivities() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/recent-activities/`);
  }

  async getTaxesSummary() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/taxes-summary/`);
  }

  async getWeeklyPerformance() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/weekly-performance/`);
  }

  // ==================== USUÁRIOS ====================
  
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${CONFIG.ENDPOINTS.USERS}/${queryString ? '?' + queryString : ''}`);
  }

  async getUser(id) {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/${id}/`);
  }

  async createUser(data) {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateUser(id, data) {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteUser(id) {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/${id}/`, {
      method: 'DELETE'
    });
  }

  async changeUserPassword(id, oldPassword, newPassword) {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/${id}/change_password/`, {
      method: 'POST',
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword
      })
    });
  }

  async changeUserRole(id, role) {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/${id}/change_role/`, {
      method: 'POST',
      body: JSON.stringify({ role })
    });
  }

  async getUserStatistics() {
    return this.request(`${CONFIG.ENDPOINTS.USERS}/statistics/`);
  }
}

// Criar instância global
window.api = new API();
