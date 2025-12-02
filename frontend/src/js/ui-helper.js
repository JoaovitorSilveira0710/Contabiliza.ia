/**
 * Funções Auxiliares para UI e Lógica
 */

class UIHelper {
  /**
   * Mostrar modal
   */
  static showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('animation-fade-in');
    }
  }

  /**
   * Fechar modal
   */
  static closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  /**
   * Mostrar notificação
   */
  static showNotification(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.classList.remove('hidden', 'bg-blue-500', 'bg-green-500', 'bg-red-500', 'bg-yellow-500');
    
    const colors = {
      'info': 'bg-blue-500',
      'success': 'bg-green-500',
      'error': 'bg-red-500',
      'warning': 'bg-yellow-500'
    };

    toast.classList.add(colors[type] || colors['info']);
    
    setTimeout(() => {
      toast.classList.add('hidden');
    }, 3000);
  }

  /**
   * Confirmar ação
   */
  static async confirm(message) {
    return new Promise((resolve) => {
      if (confirm(message)) {
        resolve(true);
      } else {
        resolve(false);
      }
    });
  }

  /**
   * Habilitar/desabilitar formulário
   */
  static disableForm(formId, disabled = true) {
    const form = document.getElementById(formId);
    if (!form) return;

    const inputs = form.querySelectorAll('input, select, textarea, button');
    inputs.forEach(input => {
      input.disabled = disabled;
    });
  }

  /**
   * Limpar formulário
   */
  static clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
      form.reset();
    }
  }

  /**
   * Obter dados de formulário
   */
  static getFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return null;

    const formData = new FormData(form);
    const data = {};

    formData.forEach((value, key) => {
      if (data.hasOwnProperty(key)) {
        if (Array.isArray(data[key])) {
          data[key].push(value);
        } else {
          data[key] = [data[key], value];
        }
      } else {
        data[key] = value;
      }
    });

    return data;
  }

  /**
   * Popular formulário
   */
  static populateForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;

    Object.keys(data).forEach(key => {
      const input = form.querySelector(`[name="${key}"]`);
      if (input) {
        if (input.type === 'checkbox') {
          input.checked = !!data[key];
        } else if (input.type === 'radio') {
          const radio = form.querySelector(`[name="${key}"][value="${data[key]}"]`);
          if (radio) radio.checked = true;
        } else {
          input.value = data[key];
        }
      }
    });
  }

  /**
   * Mostrar loading em botão
   */
  static showButtonLoading(buttonId, loadingText = 'Carregando...') {
    const button = document.getElementById(buttonId);
    if (!button) return;

    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
    button.disabled = true;
  }

  /**
   * Esconder loading em botão
   */
  static hideButtonLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    button.textContent = button.dataset.originalText || 'Enviar';
    button.disabled = false;
  }

  /**
   * Scroll suave
   */
  static smoothScroll(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  /**
   * Copiar para clipboard
   */
  static async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.showNotification('Copiado para área de transferência!', 'success');
      return true;
    } catch (error) {
      console.error('Erro ao copiar:', error);
      this.showNotification('Erro ao copiar', 'error');
      return false;
    }
  }

  /**
   * Download de arquivo
   */
  static downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'arquivo';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Validar email
   */
  static isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  /**
   * Validar URL
   */
  static isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Formatar tamanho de arquivo
   */
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Gerar ID único
   */
  static generateId() {
    return '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Debounce de função
   */
  static debounce(func, delay = 300) {
    let timeoutId;
    return function(...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * Throttle de função
   */
  static throttle(func, delay = 300) {
    let lastCall = 0;
    return function(...args) {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        return func.apply(this, args);
      }
    };
  }

  /**
   * Aguardar
   */
  static sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Criar tabela HTML
   */
  static createTable(data, columns) {
    let html = '<table class="w-full"><thead><tr>';
    
    // Header
    columns.forEach(col => {
      html += `<th class="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">${col.label}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Corpo
    data.forEach(row => {
      html += '<tr class="border-b hover:bg-gray-50">';
      columns.forEach(col => {
        const value = row[col.key];
        html += `<td class="px-6 py-4 text-sm">${value || '-'}</td>`;
      });
      html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
  }
}

// Exportar globalmente
window.UIHelper = UIHelper;
