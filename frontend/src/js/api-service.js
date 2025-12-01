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
    const url = `${this.baseURL}${endpoint}`;
    const method = options.method || 'GET';
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    // Adicionar token se autenticado
    const token = UTILS.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
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

    console.log(`📡 ${method} ${endpoint}`);

    try {
      const response = await this._fetchWithTimeout(url, config, this.timeout);

      if (!response.ok) {
        await this._handleError(response);
      }

      // Para respostas sem conteúdo (DELETE 204, etc)
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

  // ==================== AUTENTICAÇÃO ====================

  async login(email, senha) {
    const response = await this.request(`${CONFIG.ENDPOINTS.AUTH}/login`, {
      method: 'POST',
      body: { email, senha }
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
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirCliente(id) {
    return this.request(`${CONFIG.ENDPOINTS.CLIENTES}/${id}`, {
      method: 'DELETE'
    });
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
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/autorizar`, {
      method: 'POST',
      body: {}
    });
  }

  async cancelarNotaFiscal(id, motivo) {
    return this.request(`${CONFIG.ENDPOINTS.NOTAS_FISCAIS}/${id}/cancelar`, {
      method: 'POST',
      body: { motivo: motivo || 'Cancelamento solicitado' }
    });
  }

  // ==================== FINANCEIRO ====================

  async getLancamentos(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const endpoint = params ? `${CONFIG.ENDPOINTS.FINANCEIRO}/lancamentos/?${params}` : `${CONFIG.ENDPOINTS.FINANCEIRO}/lancamentos/`;
    return this.request(endpoint);
  }

  async criarLancamento(dados) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/lancamentos/`, {
      method: 'POST',
      body: dados
    });
  }

  async atualizarLancamento(id, dados) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/lancamentos/${id}`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirLancamento(id) {
    return this.request(`${CONFIG.ENDPOINTS.FINANCEIRO}/lancamentos/${id}`, {
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

  // ==================== JURÍDICO ====================

  async getProcessos(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const endpoint = params ? `${CONFIG.ENDPOINTS.JURIDICO}/processos/?${params}` : `${CONFIG.ENDPOINTS.JURIDICO}/processos/`;
    return this.request(endpoint);
  }

  async getProcessoById(id) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/${id}`);
  }

  async criarProcesso(dados) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/`, {
      method: 'POST',
      body: dados
    });
  }

  async atualizarProcesso(id, dados) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/${id}`, {
      method: 'PATCH',
      body: dados
    });
  }

  async excluirProcesso(id) {
    return this.request(`${CONFIG.ENDPOINTS.JURIDICO}/processos/${id}`, {
      method: 'DELETE'
    });
  }
}

// Instância global
const apiService = new ApiService();
window.apiService = apiService;
