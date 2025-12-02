/**
 * Configuração Global da Aplicação
 * Última atualização: 2025-11-11 - Endpoints corrigidos com barra final
 */

const CONFIG = {
  // API Base URL
  API_BASE: localStorage.getItem('API_BASE') || 'http://127.0.0.1:8000/api',
  BASE_URL: localStorage.getItem('API_BASE') || 'http://127.0.0.1:8000/api',
  
  // Endpoints (sincronizados com Django backend)
  ENDPOINTS: {
    // Core
    AUTH: '/auth',
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
    CONTABIL: '/contabil',
    // Notifications
    NOTIFICACOES: '/notifications'
  },

  // Settings
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  
  // Mensagens
  MESSAGES: {
    SUCCESS: 'Operação realizada com sucesso!',
    ERROR: 'Erro ao processar requisição',
    LOADING: 'Carregando...',
    UNAUTHORIZED: 'Acesso não autorizado. Faça login novamente.',
    NOT_FOUND: 'Recurso não encontrado',
    VALIDATION_ERROR: 'Erro de validação. Verifique os dados.',
  }
};

/**
 * Utilitários globais
 */
const UTILS = {
  /**
   * Formatar valor em Real
   */
  formatarReal(valor) {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  },

  /**
   * Formatar data
   */
  formatarData(dataString) {
    if (!dataString) return 'N/A';
    try {
      const data = new Date(dataString);
      return data.toLocaleDateString('pt-BR');
    } catch {
      return 'Data inválida';
    }
  },

  /**
   * Formatar data e hora
   */
  formatarDataHora(dataString) {
    if (!dataString) return 'N/A';
    try {
      const data = new Date(dataString);
      return data.toLocaleString('pt-BR');
    } catch {
      return 'Data inválida';
    }
  },

  /**
   * Formatar CNPJ
   */
  formatarCNPJ(cnpj) {
    cnpj = cnpj.replace(/[^\d]/g, '');
    return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  },

  /**
   * Formatar CPF
   */
  formatarCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  },

  /**
   * Validar CNPJ
   */
  validarCNPJ(cnpj) {
    cnpj = cnpj.replace(/[^\d]/g, '');
    if (cnpj.length !== 14) return false;
    if (/^(\d)\1+$/.test(cnpj)) return false;

    let tamanho = cnpj.length - 2;
    let numeros = cnpj.substring(0, tamanho);
    let digitos = cnpj.substring(tamanho);
    let soma = 0;
    let pos = tamanho - 7;

    for (let i = tamanho; i >= 1; i--) {
      soma += numeros.charAt(tamanho - i) * pos--;
      if (pos < 2) pos = 9;
    }

    let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
    if (resultado !== parseInt(digitos.charAt(0))) return false;

    tamanho = tamanho + 1;
    numeros = cnpj.substring(0, tamanho);
    soma = 0;
    pos = tamanho - 7;

    for (let i = tamanho; i >= 1; i--) {
      soma += numeros.charAt(tamanho - i) * pos--;
      if (pos < 2) pos = 9;
    }

    resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
    if (resultado !== parseInt(digitos.charAt(1))) return false;

    return true;
  },

  /**
   * Validar CPF
   */
  validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');
    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;

    let soma = 0;
    let resto;

    for (let i = 1; i <= 9; i++) {
      soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }

    resto = (soma * 10) % 11;
    if ((resto === 10) || (resto === 11)) resto = 0;
    if (resto !== parseInt(cpf.substring(9, 10))) return false;

    soma = 0;
    for (let i = 1; i <= 10; i++) {
      soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }

    resto = (soma * 10) % 11;
    if ((resto === 10) || (resto === 11)) resto = 0;
    if (resto !== parseInt(cpf.substring(10, 11))) return false;

    return true;
  },

  /**
   * Obter token JWT do localStorage
   */
  getToken() {
    return localStorage.getItem('token');
  },

  /**
   * Salvar token JWT
   */
  setToken(token) {
    localStorage.setItem('token', token);
  },

  /**
   * Limpar token (logout)
   */
  clearToken() {
    localStorage.removeItem('token');
  },

  /**
   * Verificar se usuário está autenticado
   */
  isAuthenticated() {
    // Requires token to make authenticated requests
    return !!this.getToken();
  },

  getCurrentUser() {
    const email = localStorage.getItem('USER_EMAIL') || localStorage.getItem('MASTER_EMAIL');
    const role = localStorage.getItem('USER_ROLE') || (localStorage.getItem('MASTER_EMAIL') ? 'master' : null);
    if (!email || !role) return null;
    return { email, role };
  },

  setCurrentUser(email, role) {
    if (email) localStorage.setItem('USER_EMAIL', email);
    if (role) localStorage.setItem('USER_ROLE', role);
  },

  clearCurrentUser() {
    localStorage.removeItem('USER_EMAIL');
    localStorage.removeItem('USER_ROLE');
    localStorage.removeItem('MASTER_EMAIL');
  },

  /**
   * Exibir toast de notificação
   */
  showToast(message, type = 'info') {
    try {
      if (window.UIHelper && typeof window.UIHelper.showNotification === 'function') {
        window.UIHelper.showNotification(message, type);
        return;
      }

      let container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '16px';
        container.style.right = '16px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '8px';
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      toast.textContent = message;
      toast.style.color = '#fff';
      toast.style.padding = '10px 14px';
      toast.style.borderRadius = '8px';
      toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.25)';
      toast.style.fontSize = '14px';
      toast.style.maxWidth = '360px';
      toast.style.wordBreak = 'break-word';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-6px)';
      toast.style.transition = 'opacity 150ms ease, transform 150ms ease';

      const colors = {
        info: '#3b82f6',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b'
      };
      toast.style.background = colors[type] || colors.info;

      container.appendChild(toast);
      requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
      });

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-6px)';
        setTimeout(() => toast.remove(), 180);
      }, 3000);
    } catch (e) {
      // Minimal fallback
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }
};

// Exportar para uso global
window.CONFIG = CONFIG;
window.UTILS = UTILS;

/**
 * Helper para fetch com autenticação automática
 */
window.authenticatedFetch = async function(url, options = {}) {
  const token = UTILS.getToken();
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Token ${token}`;
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };
  
  const response = await fetch(url, config);
  
  // Redirect to login if not authorized
  if (response.status === 401) {
    UTILS.clearToken();
    window.location.href = '/pages/login.html';
    throw new Error('Não autorizado');
  }
  
  return response;
};
