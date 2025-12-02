/**
 * Serviço de API - Comunicação com Backend
 * Dependência: config.js
 */

class ApiService {
  constructor() {
    this.baseURL = CONFIG.API_BASE;
    this.timeout = CONFIG.TIMEOUT;
  }

  /**
   * Fazer requisição HTTP
   */
  async request(endpoint, options = {}) {
    let url = `${this.baseURL}${endpoint}`;
    const method = options.method || 'GET';
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    // Adicionar token se autenticado
    const token = UTILS.getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    // Remover Content-Type se for FormData
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    const config = {
      method,
      headers,
      body: options.body instanceof FormData ? options.body : JSON.stringify(options.body)
    };

    // Avoid stale GET caching (especially on Edge/Chrome)
    if (method.toUpperCase() === 'GET') {
      const sep = url.includes('?') ? '&' : '?';
      url = `${url}${sep}_=${Date.now()}`;
      // Prevent using browser cache without adding forbidden CORS headers
      config.cache = 'no-store';
    }

    // Debug request line
    console.log(`${method} ${endpoint}`);

    try {
      const response = await this._fetchWithTimeout(url, config, this.timeout);

      if (!response.ok) {
        await this._handleError(response);
      }

      // For responses with no content (DELETE 204, etc)
      if (response.status === 204) {
        return { success: true };
      }

      const data = await response.json();
      console.log(`${method} ${endpoint}`, data);
      return data;

    } catch (error) {
      console.error(`Erro em ${endpoint}:`, error);
      this._showError(error.message);
      throw error;
    }
  }

  /**
   * Fazer requisição com timeout
   */
  async _fetchWithTimeout(url, config, timeout) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      config.signal = controller.signal;
      return await fetch(url, config);
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Tratamento de erros
   */
  async _handleError(response) {
    let errorMessage = CONFIG.MESSAGES.ERROR;

    try {
      const data = await response.json();
      errorMessage = data.detail || data.message || data.error || errorMessage;
    } catch {
      if (response.status === 401) {
        errorMessage = CONFIG.MESSAGES.UNAUTHORIZED;
        UTILS.clearToken();
        window.location.href = '/pages/login.html';
      } else if (response.status === 404) {
        errorMessage = CONFIG.MESSAGES.NOT_FOUND;
      } else if (response.status === 422) {
        errorMessage = CONFIG.MESSAGES.VALIDATION_ERROR;
      }
    }

    const error = new Error(errorMessage);
    error.status = response.status;
    throw error;
  }

  /**
   * Mostrar erro na UI
   */
  _showError(message) {
    const toast = document.getElementById('toast');
    if (toast) {
      toast.textContent = message;
      toast.classList.remove('hidden');
      toast.classList.add('bg-red-500');
      setTimeout(() => {
        toast.classList.add('hidden');
        toast.classList.remove('bg-red-500');
      }, 3000);
    }
  }

  /**
   * Mostrar sucesso na UI
   */
  _showSuccess(message) {
    const toast = document.getElementById('toast');
    if (toast) {
      toast.textContent = message;
      toast.classList.remove('hidden');
      toast.classList.add('bg-green-500');
      setTimeout(() => {
        toast.classList.add('hidden');
        toast.classList.remove('bg-green-500');
      }, 3000);
    }
  }

  // ==================== AUTHENTICATION ====================

  async login(email, senha) {
    const response = await this.request(`${CONFIG.ENDPOINTS.AUTH}/login/`, {
      method: 'POST',
      body: { email, password: senha }
    });
    if (response.token) {
      UTILS.setToken(response.token);
    }
    return response;
  }

  async logout() {
    UTILS.clearToken();
    return { success: true };
  }

  async verificarAuth() {
    try {
      const response = await this.request(`${CONFIG.ENDPOINTS.AUTH}/me`);
      return response;
    } catch (error) {
      UTILS.clearToken();
      throw error;
    }
  }

  // ==================== CLIENTES ====================

  async getClientes(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const endpoint = params ? `${CONFIG.ENDPOINTS.CLIENTES}/?${params}` : `${CONFIG.ENDPOINTS.CLIENTES}/`;
    return this.request(endpoint);
  }

  async getClienteById(id) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}/`);
  }

  async criarCliente(dados) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/`, {
      method: 'POST',
      body: dados
    });
  }

  async atualizarCliente(id, dados) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}/`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirCliente(id) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}/`, {
      method: 'DELETE'
    });
  }

  async deletarCliente(id) {
    return this.excluirCliente(id);
  }

  // ==================== NOTAS FISCAIS ====================

  async getNotasFiscais(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const endpoint = params ? `${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/?${params}` : `${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/`;
    return this.request(endpoint);
  }

  async getNotaFiscalById(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/`);
  }

  async criarNotaFiscal(dados) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/`, {
      method: 'POST',
      body: dados
    });
  }

  async atualizarNotaFiscal(id, dados) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirNotaFiscal(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/`, {
      method: 'DELETE'
    });
  }

  async buscarNotasSEFAZ(dados) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/buscar/`, {
      method: 'POST',
      body: dados
    });
  }

  async importarNotasXML(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/importar-xml/`, {
      method: 'POST',
      body: formData
    });
  }

  async autorizarNotaFiscal(id) {
    // DRF action change_status (PATCH) requer status
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/change_status/`, {
      method: 'PATCH',
      body: { status: 'authorized' }
    });
  }

  async cancelarNotaFiscal(id, motivo) {
    // DRF action cancel (POST)
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/cancel/`, {
      method: 'POST',
      body: { motivo: motivo || 'Cancelamento solicitado' }
    });
  }

  async generateXMLNotaFiscal(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/generate_xml/`, {
      method: 'POST',
      body: {}
    });
  }

  async generatePDFNotaFiscal(id) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/generate_pdf/`, {
      method: 'POST',
      body: {}
    });
  }

  async downloadXMLNotaFiscal(id) {
    // Primeiro gera o XML
    await this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/generate_xml/`, {
      method: 'POST'
    });
    
    // Depois faz o download
    const url = `${this.baseURL}${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/download_xml/`;
    const token = UTILS.getToken();
    const resp = await fetch(url, {
      headers: token ? { Authorization: `Token ${token}` } : {}
    });
    if (!resp.ok) throw new Error('Falha ao baixar XML');
    const blob = await resp.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `NFe_${id}.xml`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
    return true;
  }

  async downloadPDFNotaFiscal(id) {
    // Primeiro gera o PDF
    await this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/generate_pdf/`, {
      method: 'POST'
    });
    
    // Depois faz o download
    const url = `${this.baseURL}${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/download_pdf/`;
    const token = UTILS.getToken();
    const resp = await fetch(url, {
      headers: token ? { Authorization: `Token ${token}` } : {}
    });
    if (!resp.ok) throw new Error('Falha ao baixar PDF');
    const blob = await resp.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `DANFE_${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
    return true;
  }

  // ==================== NOTIFICATIONS ====================

  async criarNotificacao(dados) {
    // Generic endpoint; adjust according to backend
    const endpoint = CONFIG.ENDPOINTS.NOTIFICACOES || '/notifications';
    const url = endpoint.endsWith('/') ? endpoint : `${endpoint}/`;
    const resp = await this.request(url, {
      method: 'POST',
      body: dados
    });
    try {
      // Update notification icon/counter if available in UI
      if (typeof window.updateNotificationBadge === 'function') {
        window.updateNotificationBadge('increment');
      }
    } catch {}
    return resp;
  }

  // ==================== FINANCEIRO ====================

  async getLancamentos(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const endpoint = params ? `${CONFIG.ENDPOINTS.FINANCEIRO}/?${params}` : `${CONFIG.ENDPOINTS.FINANCEIRO}/`;
    return this.request(endpoint);
  }

  async getTransacoesFinanceiras(filtros = {}) {
    return this.getLancamentos(filtros);
  }

  async criarLancamento(dados) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/`, {
      method: 'POST',
      body: dados
    });
  }

  async atualizarLancamento(id, dados) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/${id}/`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirLancamento(id) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/${id}/`, {
      method: 'DELETE'
    });
  }

  async getFluxoCaixa(dataInicio, dataFim) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/fluxo-caixa/`, {
      params: { data_inicio: dataInicio, data_fim: dataFim }
    });
  }

  // ==================== DASHBOARD ====================

  async getDashboard() {
    return this.request(`${CONFIG.ENDPOINTS.DASHBOARD}/`);
  }

  // ==================== LEGAL ====================

  async getProcessos(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const endpoint = params ? `${CONFIG.ENDPOINTS.JURIDICO}/?${params}` : `${CONFIG.ENDPOINTS.JURIDICO}/`;
    return this.request(endpoint);
  }

  async getProcessoById(id) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/${id}/`);
  }

  async criarProcesso(dados) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/`, {
      method: 'POST',
      body: dados
    });
  }

  async atualizarProcesso(id, dados) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/${id}/`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirProcesso(id) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/${id}/`, {
      method: 'DELETE'
    });
  }
}

// Global instance
const apiService = new ApiService();
window.apiService = apiService;
