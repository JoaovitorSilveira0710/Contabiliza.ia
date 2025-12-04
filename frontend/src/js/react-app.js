(function(){
  const { useState } = React;

  function ClientChoiceModal({ open, xmlData, onChoose, onSkip }) {
    if (!open) return null;
    const emissor = xmlData?.emissor || {};
    const dest = xmlData?.destinatario || {};
    const emissorDoc = emissor.cnpj || '';
    const destDoc = dest.cnpj || '';

    return React.createElement(
      'div',
      { className: 'fixed inset-0 bg-black/50 flex items-center justify-center z-50' },
      React.createElement(
        'div',
        { className: 'bg-gray-800 rounded-xl p-8 max-w-2xl w-full mx-4 glass-card' },
        React.createElement('div', { className: 'mb-6' },
          React.createElement('h2', { className: 'text-2xl font-bold flex items-center gap-2 mb-2' },
            React.createElement('i', { className: 'fas fa-users text-purple-400' }),
            'Selecionar Cliente para Cadastro'
          ),
          React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Ambos não estão cadastrados. Escolha qual deseja cadastrar primeiro:')
        ),
        React.createElement('div', { className: 'space-y-4 mb-6' },
          React.createElement('div', {
            className: 'border-2 border-gray-700 rounded-lg p-4 hover:border-purple-600 hover:bg-gray-700/30 hover:shadow-lg hover:shadow-purple-500/20 cursor-pointer transition-all',
            onClick: () => onChoose('emissor')
          },
            React.createElement('div', { className: 'flex items-start gap-3' },
              React.createElement('div', { className: 'flex-shrink-0 w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center' },
                React.createElement('i', { className: 'fas fa-building text-white' })
              ),
              React.createElement('div', { className: 'flex-1' },
                React.createElement('h4', { className: 'font-semibold text-lg mb-1' }, 'Emissor (Fornecedor)'),
                React.createElement('p', { className: 'text-gray-400 text-sm' }, `${emissor.nome || emissor.fantasia || 'Sem nome'} - ${emissorDoc ? (emissorDoc.length > 11 ? 'CNPJ' : 'CPF') + ': ' + emissorDoc : 'Sem documento'}`)
              )
            )
          ),
          React.createElement('div', {
            className: 'border-2 border-gray-700 rounded-lg p-4 hover:border-purple-600 hover:bg-gray-700/30 hover:shadow-lg hover:shadow-purple-500/20 cursor-pointer transition-all',
            onClick: () => onChoose('destinatario')
          },
            React.createElement('div', { className: 'flex items-start gap-3' },
              React.createElement('div', { className: 'flex-shrink-0 w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center' },
                React.createElement('i', { className: 'fas fa-user text-white' })
              ),
              React.createElement('div', { className: 'flex-1' },
                React.createElement('h4', { className: 'font-semibold text-lg mb-1' }, 'Destinatário (Cliente)'),
                React.createElement('p', { className: 'text-gray-400 text-sm' }, `${dest.nome || 'Sem nome'} - ${destDoc ? (destDoc.length > 11 ? 'CNPJ' : 'CPF') + ': ' + destDoc : 'Sem documento'}`)
              )
            )
          )
        ),
        React.createElement('div', { className: 'pt-4 border-t border-gray-700' },
          React.createElement('button', {
            type: 'button',
            className: 'w-full px-6 py-3 border border-gray-600 rounded-lg hover:bg-gray-700 transition-all',
            onClick: onSkip
          },
            React.createElement('i', { className: 'fas fa-times mr-2' }),
            'Pular (Não cadastrar nenhum)'
          )
        )
      )
    );
  }

  function App() {
    const [open, setOpen] = useState(false);
    const [xmlData, setXmlData] = useState(null);
    const [registerOpen, setRegisterOpen] = useState(false);
    const [registerTipo, setRegisterTipo] = useState('destinatario');
    const [registerClient, setRegisterClient] = useState(null);

    // Expose global functions to integrate with existing flow
    window.openClientChoiceModal = function(data) {
      setXmlData(data);
      setOpen(true);
    };
    window.closeClientChoiceModal = function() {
      setOpen(false);
      setXmlData(null);
      if (typeof window.continueImportAfterRegister === 'function') {
        window.continueImportAfterRegister();
      }
    };
    window.selectClientType = function(tipo) {
      setOpen(false);
      // Open registration modal in React
      const clientData = tipo === 'emissor' ? xmlData?.emissor : xmlData?.destinatario;
      setRegisterClient(clientData || null);
      setRegisterTipo(tipo);
      setRegisterOpen(true);
    };

    return React.createElement(React.Fragment, null,
      React.createElement(ClientChoiceModal, {
        open,
        xmlData,
        onChoose: window.selectClientType,
        onSkip: window.closeClientChoiceModal
      }),
      React.createElement(ClientRegisterModal, {
        open: registerOpen,
        tipo: registerTipo,
        clientData: registerClient,
        onClose: () => setRegisterOpen(false),
        onSubmitted: async () => {
          setRegisterOpen(false);
          if (typeof window.continueImportAfterRegister === 'function') {
            await window.continueImportAfterRegister();
          }
        }
      })
    );
  }

  const rootEl = document.getElementById('react-client-choice-root');
  if (rootEl) {
    const root = ReactDOM.createRoot(rootEl);
    root.render(React.createElement(App));
  }
})();

// ===== React Client Register Modal =====
(function(){
  const { useState, useEffect } = React;

  window.ClientRegisterModal = function ClientRegisterModal({ open, tipo, clientData, onClose, onSubmitted }){
    const [form, setForm] = useState({
      nome_razao_social: '',
      cnpj_cpf: '',
      tipo_pessoa: 'pessoa_juridica',
      email: '',
      telefone: '',
      cep: '',
      endereco: '',
      numero: '',
      complemento: '',
      bairro: '',
      cidade: '',
      uf: '',
      ativo: true,
      documentos_pendentes: []
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
      if (!open || !clientData) return;
      const nome = clientData?.nome || clientData?.fantasia || '';
      const doc = clientData?.cnpj || '';
      const end = clientData?.endereco || {};
      const cleanDoc = (doc || '').replace(/[^\d]/g, '');
      const tipoPessoa = cleanDoc.length === 14 ? 'pessoa_juridica' : 'pessoa_fisica';
      setForm(prev => ({
        ...prev,
        nome_razao_social: nome,
        cnpj_cpf: doc,
        tipo_pessoa: tipoPessoa,
        email: clientData?.email || '',
        telefone: clientData?.fone || '',
        cep: end?.cep || '',
        endereco: end?.logradouro || '',
        numero: end?.numero || '',
        complemento: end?.complemento || '',
        bairro: end?.bairro || '',
        cidade: end?.municipio || '',
        uf: end?.uf || ''
      }));
    }, [open, clientData]);

    const handleChange = (e) => {
      const { id, value } = e.target;
      setForm(prev => ({ ...prev, [id.replace('reg_', '')]: value }));
      if (id === 'reg_complemento') {
        const isFazenda = (value || '').toLowerCase().includes('fazenda');
        setForm(prev => ({
          ...prev,
          documentos_pendentes: isFazenda ? ['CCIR','CAR','ITR','Docs Proprietário/Arrendatário'] : []
        }));
      }
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (loading) return;
      setLoading(true);
      try {
        await window.apiService.criarCliente(form);
        window.UTILS.showToast('Cliente cadastrado com sucesso!', 'success');
        if (form.documentos_pendentes.length > 0) {
          window.UTILS.showToast('Documentação pendente detectada. Uma notificação foi gerada.', 'warning');
          try {
            await window.apiService.criarNotificacao({
              tipo: 'pendencia_documental',
              titulo: 'Completar documentação de cliente (Fazenda)',
              mensagem: `Cliente ${form.nome_razao_social} requer: ${form.documentos_pendentes.join(', ')}`,
              prioridade: 'alta'
            });
          } catch {}
        }
        onClose && onClose();
        onSubmitted && onSubmitted();
      } catch (err) {
        console.error(err);
        window.UTILS.showToast('Erro ao cadastrar cliente', 'error');
      } finally {
        setLoading(false);
      }
    };

    if (!open) return null;
    return React.createElement('div', { className: 'fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto' },
      React.createElement('div', { className: 'bg-gray-800 rounded-xl p-8 max-w-3xl w-full mx-4 my-8 glass-card' },
        React.createElement('div', { className: 'flex justify-between items-center mb-6' },
          React.createElement('h2', { className: 'text-2xl font-bold flex items-center gap-2' },
            React.createElement('i', { className: 'fas fa-user-plus text-purple-400' }),
            tipo === 'emissor' ? 'Cadastrar Emissor da Nota' : 'Cadastrar Cliente (Destinatário)'
          ),
          React.createElement('button', { className: 'text-gray-400 hover:text-white', onClick: onClose },
            React.createElement('i', { className: 'fas fa-times text-xl' })
          )
        ),
        React.createElement('div', { className: 'bg-yellow-900/20 border border-yellow-600/30 rounded-lg p-4 mb-6' },
          React.createElement('p', { className: 'text-yellow-400 text-sm' }, 'Complete os dados abaixo para cadastrar automaticamente.')
        ),
        React.createElement('form', { className: 'space-y-4', onSubmit: handleSubmit },
          React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
            React.createElement('div', { className: 'md:col-span-2' },
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Nome/Razão Social *'),
              React.createElement('input', { id: 'reg_nome_razao_social', required: true, value: form.nome_razao_social, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'CNPJ/CPF *'),
              React.createElement('input', { id: 'reg_cnpj_cpf', required: true, readOnly: true, value: form.cnpj_cpf, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-gray-400 cursor-not-allowed' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Tipo *'),
              React.createElement('select', { id: 'reg_tipo_pessoa', required: true, value: form.tipo_pessoa, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' },
                React.createElement('option', { value: 'pessoa_juridica' }, 'Pessoa Jurídica'),
                React.createElement('option', { value: 'pessoa_fisica' }, 'Pessoa Física')
              )
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Email'),
              React.createElement('input', { id: 'reg_email', type: 'email', value: form.email, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Telefone'),
              React.createElement('input', { id: 'reg_telefone', value: form.telefone, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'CEP'),
              React.createElement('input', { id: 'reg_cep', value: form.cep, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', { className: 'md:col-span-2' },
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Endereço'),
              React.createElement('input', { id: 'reg_endereco', value: form.endereco, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Número'),
              React.createElement('input', { id: 'reg_numero', value: form.numero, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Complemento'),
              React.createElement('input', { id: 'reg_complemento', value: form.complemento, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' }),
              form.documentos_pendentes.length > 0 && React.createElement('div', { className: 'mt-2 bg-purple-900/20 border border-purple-600/30 rounded-lg p-3' },
                React.createElement('p', { className: 'text-purple-300 text-sm mb-2' }, 'Detectamos que o cliente é uma Fazenda. Documentações necessárias:'),
                React.createElement('ul', { className: 'text-purple-200 text-sm list-disc ml-5 space-y-1' },
                  form.documentos_pendentes.map((d, i) => React.createElement('li', { key: i }, d))
                )
              )
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Bairro'),
              React.createElement('input', { id: 'reg_bairro', value: form.bairro, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Cidade'),
              React.createElement('input', { id: 'reg_cidade', value: form.cidade, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' })
            ),
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'UF'),
              React.createElement('select', { id: 'reg_uf', value: form.uf, onChange: handleChange, className: 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-600' },
                React.createElement('option', { value: '' }, 'Selecione'),
                ['SP','RJ','MG','ES','PR','SC','RS','BA','PE','CE','DF','GO','MT','MS','AM','PA'].map(uf => React.createElement('option', { key: uf, value: uf }, uf))
              )
            )
          )
        ),
        React.createElement('div', { className: 'flex gap-3 justify-end pt-4 border-t border-gray-700' },
          React.createElement('button', { type: 'button', onClick: onClose, className: 'px-6 py-2 border border-gray-600 rounded-lg hover:bg-gray-700 transition-all' }, 'Pular'),
          React.createElement('button', { type: 'submit', disabled: loading, className: 'px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg hover:shadow-lg transition-all flex items-center gap-2' },
            loading ? React.createElement('i', { className: 'fas fa-spinner fa-spin' }) : React.createElement('i', { className: 'fas fa-save' }),
            loading ? ' Cadastrando...' : ' Cadastrar e Continuar'
          )
        )
      )
    );
  };
})();

// ===== React Notas Table =====
(function(){
  const { useState, useEffect, useMemo } = React;

  function statusBadgeClass(status) {
    const map = {
      authorized: 'bg-green-600/20 text-green-400 border border-green-600/30 rounded-md',
      cancelled: 'bg-red-600/20 text-red-400 border border-red-600/30 rounded-md',
      pending: 'bg-yellow-600/20 text-yellow-400 border border-yellow-600/30 rounded-md',
      draft: 'bg-gray-600/20 text-gray-400 border border-gray-600/30 rounded-md',
      denied: 'bg-orange-600/20 text-orange-400 border border-orange-600/30 rounded-md'
    };
    return map[status] || 'bg-gray-600/20 text-gray-400';
  }

  function statusLabel(status) {
    const map = {
      authorized: 'Autorizada',
      cancelled: 'Cancelada',
      pending: 'Pendente',
      draft: 'Rascunho',
      denied: 'Negada'
    };
    return map[status] || status;
  }

  function NotasTable() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState('');
    const [status, setStatus] = useState('');
    const [page, setPage] = useState(1);
    const [selectedNota, setSelectedNota] = useState(null);
    const pageSize = 10;

    useEffect(() => {
      let mounted = true;
      (async () => {
        try {
          const resp = await window.apiService.getNotasFiscais();
          const list = Array.isArray(resp) ? resp : (resp?.results || []);
          if (mounted) {
            setData(list);
            if (window.updateNotasStats) {
              window.updateNotasStats(list);
            }
          }
        } catch (e) {
          window.UTILS.showToast('Error loading invoices', 'error');
        } finally {
          if (mounted) setLoading(false);
        }
      })();
      return () => { mounted = false; };
    }, []);

    const filtered = useMemo(() => {
      let list = data;
      if (query) {
        const q = query.toLowerCase();
        list = list.filter(n =>
          String(n.number || '').toLowerCase().includes(q) ||
          String(n.series || '').toLowerCase().includes(q) ||
          String(n.client_name || '').toLowerCase().includes(q)
        );
      }
      if (status) {
        list = list.filter(n => n.status === status);
      }
      return list;
    }, [data, query, status]);

    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const pageItems = useMemo(() => {
      const start = (page - 1) * pageSize;
      return filtered.slice(start, start + pageSize);
    }, [filtered, page]);

    const autorizar = async (id) => {
      try {
        await window.apiService.autorizarNotaFiscal(id);
        window.UTILS.showToast('Invoice authorized', 'success');
        const resp = await window.apiService.getNotasFiscais();
        const list = Array.isArray(resp) ? resp : (resp?.results || []);
        setData(list);
        if (window.updateNotasStats) {
          window.updateNotasStats(list);
        }
      } catch (e) {
        window.UTILS.showToast('Error authorizing', 'error');
      }
    };

    const downloadXML = async (id) => {
      try {
        window.UTILS.showToast('Gerando XML...', 'info');
        await window.apiService.downloadXMLNotaFiscal(id);
        window.UTILS.showToast('XML baixado com sucesso!', 'success');
      } catch (e) {
        console.error('Erro ao baixar XML:', e);
        window.UTILS.showToast('Failed to download XML', 'error');
      }
    };

    const downloadPDF = async (id) => {
      try {
        window.UTILS.showToast('Gerando PDF DANFE...', 'info');
        await window.apiService.downloadPDFNotaFiscal(id);
        window.UTILS.showToast('PDF baixado com sucesso!', 'success');
      } catch (e) {
        console.error('Erro ao baixar PDF:', e);
        window.UTILS.showToast('Failed to download PDF', 'error');
      }
    };

    useEffect(() => {
      const handler = () => {
        const el = document.querySelector('input[placeholder*="🔍 Buscar"]');
        if (el) el.focus();
      };
      window.addEventListener('react:focus-search', handler);
      return () => window.removeEventListener('react:focus-search', handler);
    }, []);

    if (loading) {
      return React.createElement('div', { className: 'flex items-center justify-center py-12' },
        React.createElement('div', { className: 'text-center' },
          React.createElement('i', { className: 'fas fa-spinner fa-spin text-4xl text-purple-600 mb-4' }),
          React.createElement('p', { className: 'text-gray-400' }, 'Carregando notas fiscais...')
        )
      );
    }

    return React.createElement('div', { className: 'glass-card rounded-xl overflow-hidden' },
      // Modal
      selectedNota && React.createElement('div', { 
        className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50',
        onClick: () => setSelectedNota(null)
      },
        React.createElement('div', { 
          className: 'bg-gray-800 rounded-xl p-8 max-w-3xl w-full mx-4 glass-card',
          onClick: e => e.stopPropagation()
        },
          React.createElement('div', { className: 'flex justify-between items-center mb-6' },
            React.createElement('h2', { className: 'text-2xl font-bold text-white flex items-center gap-3' }, 
              React.createElement('i', { className: 'fas fa-file-invoice text-purple-400' }),
              `NFe ${selectedNota.number}-${selectedNota.series}`
            ),
            React.createElement('button', { 
              className: 'text-gray-400 hover:text-white text-3xl transition-colors',
              onClick: () => setSelectedNota(null)
            }, '×')
          ),
          React.createElement('div', { className: 'grid grid-cols-2 gap-4 mb-6' },
            React.createElement('div', { className: 'bg-gray-700/30 p-4 rounded-lg' },
              React.createElement('p', { className: 'text-gray-400 text-sm mb-1' }, 'Cliente'),
              React.createElement('p', { className: 'font-semibold text-white' }, selectedNota.client_name || '-')
            ),
            React.createElement('div', { className: 'bg-gray-700/30 p-4 rounded-lg' },
              React.createElement('p', { className: 'text-gray-400 text-sm mb-1' }, 'Status'),
              React.createElement('span', { className: `inline-block px-3 py-1 text-sm font-semibold ${statusBadgeClass(selectedNota.status)}` }, 
                statusLabel(selectedNota.status)
              )
            ),
            React.createElement('div', { className: 'bg-gray-700/30 p-4 rounded-lg' },
              React.createElement('p', { className: 'text-gray-400 text-sm mb-1' }, 'Valor Total'),
              React.createElement('p', { className: 'font-semibold text-white text-lg' }, window.UTILS.formatarReal(selectedNota.total_value || 0))
            ),
            React.createElement('div', { className: 'bg-gray-700/30 p-4 rounded-lg' },
              React.createElement('p', { className: 'text-gray-400 text-sm mb-1' }, 'Data de Emissão'),
              React.createElement('p', { className: 'font-semibold text-white' }, 
                selectedNota.issue_date ? new Date(selectedNota.issue_date).toLocaleDateString('pt-BR') : '-'
              )
            )
          ),
          React.createElement('div', { className: 'flex gap-3 pt-4 border-t border-gray-700' },
            React.createElement('button', {
              className: 'flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center justify-center gap-2 transition-all',
              onClick: () => {
                try {
                  const url = `/pages/nota-fiscal-view.html?id=${encodeURIComponent(selectedNota.id)}`;
                  window.open(url, '_blank');
                } catch (err) {
                  console.error('Erro ao abrir visualização da NFe:', err);
                  window.UTILS.showToast('Não foi possível abrir a visualização', 'error');
                }
              }
            },
              React.createElement('i', { className: 'fas fa-eye' }),
              'Visualizar'
            ),
            React.createElement('button', { 
              className: 'flex-1 px-4 py-3 bg-green-600 hover:bg-green-700 rounded-lg flex items-center justify-center gap-2 transition-all',
              onClick: () => downloadXML(selectedNota.id)
            }, 
              React.createElement('i', { className: 'fas fa-file-code' }),
              'Baixar XML'
            ),
            React.createElement('button', { 
              className: 'flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 rounded-lg flex items-center justify-center gap-2 transition-all',
              onClick: () => downloadPDF(selectedNota.id)
            }, 
              React.createElement('i', { className: 'fas fa-file-pdf' }),
              'Baixar DANFE'
            ),
            selectedNota.status !== 'authorized' && React.createElement('button', { 
              className: 'flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center justify-center gap-2 transition-all',
              onClick: () => { autorizar(selectedNota.id); setSelectedNota(null); }
            }, 
              React.createElement('i', { className: 'fas fa-check-circle' }),
              'Autorizar'
            )
          )
        )
      ),

      // Filters
      React.createElement('div', { className: 'p-6 bg-gray-800/50 border-b border-gray-700' },
        React.createElement('div', { className: 'flex gap-4' },
          React.createElement('input', {
            placeholder: '🔍 Buscar por número, série ou cliente...',
            className: 'flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors',
            value: query,
            onChange: e => { setPage(1); setQuery(e.target.value); }
          }),
          React.createElement('select', {
            className: 'px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors',
            value: status,
            onChange: e => { setPage(1); setStatus(e.target.value); }
          },
            React.createElement('option', { value: '' }, 'Todos os Status'),
            React.createElement('option', { value: 'authorized' }, '✅ Autorizadas'),
            React.createElement('option', { value: 'pending' }, '⏳ Pendentes'),
            React.createElement('option', { value: 'draft' }, '📝 Rascunho'),
            React.createElement('option', { value: 'denied' }, '❌ Negadas'),
            React.createElement('option', { value: 'cancelled' }, '🚫 Canceladas')
          )
        )
      ),

      // Table
      React.createElement('div', { className: 'overflow-x-auto' },
        React.createElement('table', { className: 'w-full' },
          React.createElement('thead', { className: 'bg-gray-800/50' },
            React.createElement('tr', null,
              React.createElement('th', { className: 'px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider' }, 'Nota Fiscal'),
              React.createElement('th', { className: 'px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider' }, 'Cliente'),
              React.createElement('th', { className: 'px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider' }, 'Status'),
              React.createElement('th', { className: 'px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider' }, 'Valor'),
              React.createElement('th', { className: 'px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider' }, 'Data'),
              React.createElement('th', { className: 'px-6 py-4 text-right text-xs font-medium text-gray-400 uppercase tracking-wider' }, 'Ações')
            )
          ),
          React.createElement('tbody', { className: 'bg-gray-800/20 divide-y divide-gray-700' },
            pageItems.length === 0 ? 
              React.createElement('tr', null,
                React.createElement('td', { colSpan: 6, className: 'px-6 py-12 text-center' },
                  React.createElement('div', { className: 'text-gray-500' },
                    React.createElement('i', { className: 'fas fa-inbox text-4xl mb-3' }),
                    React.createElement('p', null, 'Nenhuma nota fiscal encontrada')
                  )
                )
              ) :
              pageItems.map(n => React.createElement('tr', { 
                key: n.id, 
                className: 'hover:bg-gray-700/30 transition-colors cursor-pointer',
                onClick: () => setSelectedNota(n)
              },
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'flex items-center gap-3' },
                    React.createElement('div', { className: 'w-10 h-10 bg-gradient-to-br from-green-600/20 to-emerald-600/20 rounded-lg flex items-center justify-center flex-shrink-0' },
                      React.createElement('i', { className: 'fas fa-file-invoice text-green-400 text-sm' })
                    ),
                    React.createElement('div', null,
                      React.createElement('div', { className: 'text-sm font-medium text-white' }, `#${n.number || '-'}`),
                      React.createElement('div', { className: 'text-sm text-gray-400' }, `Série ${n.series || '-'}`)
                    )
                  )
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'text-sm text-white' }, n.client_name || '-')
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('span', { className: `px-2.5 py-1 inline-flex text-xs leading-5 font-semibold ${statusBadgeClass(n.status)}` }, 
                    statusLabel(n.status)
                  )
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'text-sm font-medium text-white' }, window.UTILS.formatarReal(n.total_value || 0))
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'text-sm text-gray-300' }, 
                    n.issue_date ? new Date(n.issue_date).toLocaleDateString('pt-BR') : '-'
                  )
                ),
                React.createElement('td', { className: 'px-6 py-4 text-right' },
                  React.createElement('div', { className: 'flex justify-end gap-2', onClick: e => e.stopPropagation() },
                    React.createElement('button', {
                      className: 'p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded-lg transition-all',
                      onClick: (e) => { 
                        e.stopPropagation(); 
                        try {
                          const url = `/pages/nota-fiscal-view.html?id=${encodeURIComponent(n.id)}`;
                          window.open(url, '_blank');
                        } catch (err) {
                          console.error('Erro ao abrir visualização da NFe:', err);
                          window.UTILS.showToast('Não foi possível abrir a visualização', 'error');
                        }
                      },
                      title: 'Visualizar DANFE'
                    }, React.createElement('i', { className: 'fas fa-eye' })),
                    React.createElement('button', { 
                      className: 'p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-all',
                      onClick: (e) => { e.stopPropagation(); downloadXML(n.id); },
                      title: 'Baixar XML'
                    }, React.createElement('i', { className: 'fas fa-file-code' })),
                    React.createElement('button', { 
                      className: 'p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-all',
                      onClick: (e) => { e.stopPropagation(); downloadPDF(n.id); },
                      title: 'Baixar DANFE'
                    }, React.createElement('i', { className: 'fas fa-file-pdf' }))
                  )
                )
              ))
          )
        )
      ),

      // Pagination
      React.createElement('div', { className: 'px-6 py-4 bg-gray-800/40 border-t border-gray-700 flex items-center justify-between' },
        React.createElement('div', { className: 'text-sm text-gray-400' }, 
          `Mostrando ${pageItems.length} de ${filtered.length} nota${filtered.length !== 1 ? 's' : ''}`
        ),
        React.createElement('div', { className: 'flex items-center gap-2' },
          React.createElement('button', { 
            className: `px-4 py-2 border ${page <= 1 ? 'border-gray-700 text-gray-600 cursor-not-allowed' : 'border-gray-600 text-white hover:bg-gray-700'} rounded-lg transition-all`,
            disabled: page <= 1,
            onClick: () => setPage(p => Math.max(1, p - 1))
          }, 
            React.createElement('i', { className: 'fas fa-chevron-left mr-2' }),
            'Anterior'
          ),
          React.createElement('span', { className: 'px-4 py-2 text-gray-300 font-medium' }, `${page} / ${totalPages}`),
          React.createElement('button', { 
            className: `px-4 py-2 border ${page >= totalPages ? 'border-gray-700 text-gray-600 cursor-not-allowed' : 'border-gray-600 text-white hover:bg-gray-700'} rounded-lg transition-all`,
            disabled: page >= totalPages,
            onClick: () => setPage(p => Math.min(totalPages, p + 1))
          }, 
            'Próxima',
            React.createElement('i', { className: 'fas fa-chevron-right ml-2' })
          )
        )
      )
    );
  }

  const rootEl = document.getElementById('react-notas-table-root');
  if (rootEl) {
    const root = ReactDOM.createRoot(rootEl);
    root.render(React.createElement(NotasTable));
  }

  // ============================================
  // CLIENTES TABLE
  // ============================================
  function ClientesTable() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState('');
    const [status, setStatus] = useState('');
    const [page, setPage] = useState(1);
    const [selectedClient, setSelectedClient] = useState(null);
    const pageSize = 10;

    useEffect(() => {
      let mounted = true;
      (async () => {
        try {
          const resp = await window.apiService.getClientes();
          const list = Array.isArray(resp) ? resp : (resp?.results || []);
          if (mounted) setData(list);
        } catch (e) {
          window.UTILS.showToast('Error loading clients', 'error');
        } finally {
          if (mounted) setLoading(false);
        }
      })();
      return () => { mounted = false; };
    }, []);

    const filtered = useMemo(() => {
      let list = data;
      if (query) {
        const q = query.toLowerCase();
        list = list.filter(c => 
          String(c.name || '').toLowerCase().includes(q) ||
          String(c.tax_id || '').toLowerCase().includes(q) ||
          String(c.email || '').toLowerCase().includes(q)
        );
      }
      if (status) {
        list = list.filter(c => c.status === status);
      }
      return list;
    }, [data, query, status]);

    const totalPages = Math.ceil(filtered.length / pageSize);
    const pageItems = filtered.slice((page - 1) * pageSize, page * pageSize);

    const editClient = (id) => {
      window.UTILS.showToast('Funcionalidade de edição em desenvolvimento', 'info');
    };

    const deleteClient = async (id) => {
      if (!confirm('Deseja realmente excluir este cliente?')) return;
      try {
        await window.apiService.deletarCliente(id);
        setData(prev => prev.filter(c => c.id !== id));
        window.UTILS.showToast('Cliente excluído', 'success');
      } catch (e) {
        window.UTILS.showToast('Error deleting client', 'error');
      }
    };

    if (loading) return React.createElement('div', { className: 'text-white text-center py-5' }, 'Carregando...');

    return React.createElement('div', null,
      selectedClient && React.createElement('div', { 
        className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50',
        onClick: () => setSelectedClient(null)
      },
        React.createElement('div', { 
          className: 'bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4',
          onClick: e => e.stopPropagation()
        },
          React.createElement('div', { className: 'flex justify-between items-center mb-4' },
            React.createElement('h2', { className: 'text-xl font-bold text-white' }, selectedClient.name),
            React.createElement('button', { 
              className: 'text-gray-400 hover:text-white text-2xl',
              onClick: () => setSelectedClient(null)
            }, '×')
          ),
          React.createElement('div', { className: 'space-y-3 text-white' },
            React.createElement('div', { className: 'grid grid-cols-2 gap-3' },
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'CPF/CNPJ'),
                React.createElement('p', { className: 'font-semibold' }, selectedClient.tax_id || '-')
              ),
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Email'),
                React.createElement('p', { className: 'font-semibold' }, selectedClient.email || '-')
              ),
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Telefone'),
                React.createElement('p', { className: 'font-semibold' }, selectedClient.phone || '-')
              ),
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Status'),
                React.createElement('span', { 
                  className: `px-2 py-1 rounded text-sm font-semibold ${selectedClient.status === 'active' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`
                }, selectedClient.status === 'active' ? 'Ativo' : 'Inativo')
              ),
              React.createElement('div', { className: 'col-span-2' },
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Endereço'),
                React.createElement('p', { className: 'font-semibold' }, 
                  [selectedClient.street, selectedClient.number, selectedClient.city, selectedClient.state]
                    .filter(Boolean).join(', ') || '-'
                )
              )
            )
          )
        )
      ),
      React.createElement('div', { className: 'flex gap-3 mb-4' },
        React.createElement('input', {
          placeholder: 'Buscar por nome, CPF/CNPJ ou email...',
          className: 'flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white',
          value: query,
          onChange: e => { setPage(1); setQuery(e.target.value); }
        }),
        React.createElement('select', {
          className: 'px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white',
          value: status,
          onChange: e => { setPage(1); setStatus(e.target.value); }
        },
          React.createElement('option', { value: '' }, 'Todos'),
          React.createElement('option', { value: 'active' }, 'Ativo'),
          React.createElement('option', { value: 'inactive' }, 'Inativo')
        )
      ),
      React.createElement('table', { className: 'w-full text-left' },
        React.createElement('thead', null,
          React.createElement('tr', null,
            ['Nome','CPF/CNPJ','Email','Telefone','Status','Ações'].map(h => 
              React.createElement('th', { key: h, className: 'px-3 py-2 text-gray-300' }, h)
            )
          )
        ),
        React.createElement('tbody', null,
          pageItems.map(c => React.createElement('tr', { key: c.id, className: 'border-t border-gray-700' },
            React.createElement('td', { className: 'px-3 py-2 text-white' }, c.name || '-'),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, c.tax_id || '-'),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, c.email || '-'),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, c.phone || '-'),
            React.createElement('td', { className: 'px-3 py-2' },
              React.createElement('span', { 
                className: `px-2 py-1 rounded font-semibold ${c.status === 'active' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`
              }, c.status === 'active' ? 'Ativo' : 'Inativo')
            ),
            React.createElement('td', { className: 'px-3 py-2 flex gap-2' },
              React.createElement('button', { 
                className: 'px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded', 
                onClick: () => setSelectedClient(c) 
              }, 'Ver'),
              React.createElement('button', { 
                className: 'px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded', 
                onClick: () => editClient(c.id) 
              }, 'Editar'),
              React.createElement('button', { 
                className: 'px-3 py-1 bg-red-600 hover:bg-red-700 rounded', 
                onClick: () => deleteClient(c.id) 
              }, 'Excluir')
            )
          ))
        )
      ),
      React.createElement('div', { className: 'flex items-center gap-3 mt-3' },
        React.createElement('button', { 
          className: 'px-3 py-1 border border-gray-600 rounded', 
          disabled: page<=1, 
          onClick: () => setPage(p => Math.max(1, p-1)) 
        }, 'Anterior'),
        React.createElement('span', { className: 'text-gray-300' }, `${page} / ${totalPages}`),
        React.createElement('button', { 
          className: 'px-3 py-1 border border-gray-600 rounded', 
          disabled: page>=totalPages, 
          onClick: () => setPage(p => Math.min(totalPages, p+1)) 
        }, 'Próxima')
      )
    );
  }

  const clientesRootEl = document.getElementById('react-clientes-table-root');
  if (clientesRootEl) {
    const root = ReactDOM.createRoot(clientesRootEl);
    root.render(React.createElement(ClientesTable));
  }

  // ============================================
  // FINANCEIRO TABLE
  // ============================================
  function FinanceiroTable() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState('');
    const [tipo, setTipo] = useState('');
    const [categoria, setCategoria] = useState('');
    const [page, setPage] = useState(1);
    const [selectedTransaction, setSelectedTransaction] = useState(null);
    const [editing, setEditing] = useState(null);
    const pageSize = 10;
    const categories = React.useMemo(() => {
      const base = tipo ? data.filter(t => t.transaction_type === tipo) : data;
      return Array.from(new Set(base.map(t => t.category_name).filter(Boolean)));
    }, [data, tipo]);

    useEffect(() => {
      let mounted = true;
      (async () => {
        try {
          const resp = await window.apiService.getTransacoesFinanceiras();
          const list = Array.isArray(resp) ? resp : (resp?.results || []);
          // Normalize fields from API for grid display
          const normalized = list.map(t => ({
            id: t.id,
            description: t.description,
            client_name: t.client_name || '-',
            transaction_type: t.transaction_type, // 'revenue' | 'expense' | 'transfer'
            category_name: t.category_name || '-',
            amount: Number(t.final_amount ?? t.amount ?? 0),
            date: t.payment_date || t.due_date,
            status: t.status,
            payment_method: t.payment_method || null,
            attachment: t.attachment || null,
          }));
          if (mounted) setData(normalized);
        } catch (e) {
          window.UTILS.showToast('Error loading transactions', 'error');
        } finally {
          if (mounted) setLoading(false);
        }
      })();
      const refreshHandler = async () => {
        try {
          const resp = await window.apiService.getTransacoesFinanceiras();
          const list = Array.isArray(resp) ? resp : (resp?.results || []);
          const normalized = list.map(t => ({
            id: t.id,
            description: t.description,
            client_name: t.client_name || '-',
            transaction_type: t.transaction_type,
            category_name: t.category_name || '-',
            amount: Number(t.final_amount ?? t.amount ?? 0),
            date: t.payment_date || t.due_date,
            status: t.status,
            payment_method: t.payment_method || null,
            attachment: t.attachment || null,
          }));
          setData(normalized);
        } catch {}
      };
      // Expose global reload function
      window.financeiroReload = refreshHandler;
      window.addEventListener('financeiro:refresh', refreshHandler);
      return () => { 
        mounted = false; 
        try { delete window.financeiroReload; } catch {}
        window.removeEventListener('financeiro:refresh', refreshHandler);
      };
    }, []);

    const filtered = useMemo(() => {
      let list = data;
      if (query) {
        const q = query.toLowerCase();
        list = list.filter(t => 
          String(t.description || '').toLowerCase().includes(q) ||
          String(t.category_name || '').toLowerCase().includes(q) ||
          String(t.client_name || '').toLowerCase().includes(q)
        );
      }
      if (tipo) {
        list = list.filter(t => t.transaction_type === tipo);
      }
      if (categoria) {
        list = list.filter(t => String(t.category_name || '').toLowerCase() === categoria.toLowerCase());
      }
      return list;
    }, [data, query, tipo, categoria]);

    const totalPages = Math.ceil(filtered.length / pageSize);
    const pageItems = filtered.slice((page - 1) * pageSize, page * pageSize);

    const formatDateBR = (s) => {
      if (!s) return '-';
      // Handle YYYY-MM-DD safely without timezone shifts
      const m = /^\d{4}-\d{2}-\d{2}$/.exec(s);
      if (m) {
        const [y, mo, d] = s.split('-');
        return `${d.padStart(2,'0')}/${mo.padStart(2,'0')}/${y}`;
      }
      try {
        const dt = new Date(s);
        return isNaN(dt.getTime()) ? s : dt.toLocaleDateString('pt-BR');
      } catch { return s; }
    };

    const paymentLabel = (m) => {
      const map = {
        pix: 'PIX',
        cash: 'Dinheiro',
        money: 'Dinheiro',
        ted: 'TED',
        doc: 'DOC',
        transfer: 'Transferência',
        boleto: 'Boleto',
        card: 'Cartão',
        credit_card: 'Cartão',
        debit_card: 'Cartão Débito'
      };
      return map[m] || (m ? String(m).toUpperCase() : '-');
    };

    if (loading) return React.createElement('div', { className: 'text-white text-center py-5' }, 'Carregando...');

    return React.createElement('div', null,
      selectedTransaction && React.createElement('div', { 
        className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50',
        onClick: () => setSelectedTransaction(null)
      },
        React.createElement('div', { 
          className: 'bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4',
          onClick: e => e.stopPropagation()
        },
          React.createElement('div', { className: 'flex justify-between items-center mb-4' },
            React.createElement('h2', { className: 'text-xl font-bold text-white' }, 'Detalhes da Transação'),
            React.createElement('button', { 
              className: 'text-gray-400 hover:text-white text-2xl',
              onClick: () => setSelectedTransaction(null)
            }, '×')
          ),
          React.createElement('div', { className: 'space-y-3 text-white' },
            React.createElement('div', { className: 'grid grid-cols-2 gap-3' },
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Descrição'),
                React.createElement('p', { className: 'font-semibold' }, selectedTransaction.description || '-')
              ),
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Tipo'),
                React.createElement('span', { 
                  className: `px-2 py-1 rounded text-sm font-semibold ${selectedTransaction.transaction_type === 'revenue' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`
                }, selectedTransaction.transaction_type === 'revenue' ? 'Receita' : 'Despesa')
              ),
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Valor'),
                React.createElement('p', { className: 'font-semibold text-lg' }, window.UTILS.formatarReal(selectedTransaction.amount || 0))
              ),
              React.createElement('div', null,
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Data'),
                React.createElement('p', { className: 'font-semibold' }, formatDateBR(selectedTransaction.date))
              ),
              React.createElement('div', { className: 'col-span-2' },
                React.createElement('p', { className: 'text-gray-400 text-sm' }, 'Categoria'),
                React.createElement('p', { className: 'font-semibold' }, selectedTransaction.category_name || '-')
              )
            )
          )
        )
      ),
      editing && React.createElement('div', {
        className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50',
        onClick: () => setEditing(null)
      },
        React.createElement('div', {
          className: 'bg-gray-800 rounded-lg p-6 max-w-lg w-full mx-4',
          onClick: e => e.stopPropagation()
        },
          React.createElement('div', { className: 'flex justify-between items-center mb-4' },
            React.createElement('h2', { className: 'text-xl font-bold text-white' }, 'Modificar Lançamento'),
            React.createElement('button', { className: 'text-gray-400 hover:text-white text-2xl', onClick: () => setEditing(null) }, '×')
          ),
          // Form
          React.createElement('div', { className: 'space-y-3 text-white' },
            React.createElement('div', null,
              React.createElement('label', { className: 'block text-sm text-gray-400 mb-1' }, 'Descrição'),
              React.createElement('input', { className: 'w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded',
                value: editing.description || '',
                onChange: e => setEditing({ ...editing, description: e.target.value }) })
            ),
            React.createElement('div', { className: 'grid grid-cols-2 gap-3' },
              React.createElement('div', null,
                React.createElement('label', { className: 'block text-sm text-gray-400 mb-1' }, 'Status'),
                React.createElement('select', { className: 'w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded',
                    value: editing.status || 'pending',
                    onChange: e => setEditing({ ...editing, status: e.target.value }) },
                  ['pending','paid','received','cancelled','overdue'].map(s => React.createElement('option', { key: s, value: s }, s))
                )
              ),
              React.createElement('div', null,
                React.createElement('label', { className: 'block text-sm text-gray-400 mb-1' }, 'Data Pagamento'),
                React.createElement('input', { type: 'date', className: 'w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded',
                  value: editing.payment_date || '',
                  onChange: e => setEditing({ ...editing, payment_date: e.target.value }) })
              )
            )
          ),
          React.createElement('div', { className: 'flex justify-end gap-2 mt-4' },
            React.createElement('button', { className: 'px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded', onClick: () => setEditing(null) }, 'Cancelar'),
            React.createElement('button', { className: 'px-3 py-2 bg-green-600 hover:bg-green-700 rounded', onClick: async () => {
              try {
                await window.apiService.atualizarLancamento(editing.id, {
                  description: editing.description,
                  status: editing.status,
                  payment_date: editing.payment_date || null
                });
                window.UTILS.showToast('Lançamento atualizado', 'success');
                // Atualizar na lista
                setData(ds => ds.map(d => d.id === editing.id ? { ...d, description: editing.description, status: editing.status, date: editing.payment_date || d.date } : d));
                setEditing(null);
                // Update charts and other views
                if (typeof window.reloadFinanceiroData === 'function') {
                  window.reloadFinanceiroData();
                } else {
                  window.dispatchEvent(new Event('financeiro:refresh'));
                }
              } catch (e) {
                window.UTILS.showToast('Error updating entry', 'error');
              }
            } }, 'Salvar')
          )
        )
      ),
      React.createElement('div', { className: 'flex gap-3 mb-4' },
        React.createElement('input', {
          placeholder: 'Buscar por cliente, descrição ou categoria...',
          className: 'flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white',
          value: query,
          onChange: e => { setPage(1); setQuery(e.target.value); }
        }),
        React.createElement('div', { className: 'flex gap-2' },
          React.createElement('button', {
            className: `px-3 py-2 rounded-lg border ${tipo === '' ? 'border-gray-500 bg-gray-700 text-white' : 'border-gray-600 bg-gray-800 text-gray-300'} hover:border-gray-500`,
            onClick: () => { setPage(1); setTipo(''); setCategoria(''); }
          }, 'Todos'),
          React.createElement('button', {
            className: `px-3 py-2 rounded-lg border ${tipo === 'revenue' ? 'border-green-500 bg-green-600 text-white' : 'border-gray-600 bg-gray-800 text-gray-300'} hover:border-green-500`,
            onClick: () => { setPage(1); setTipo('revenue'); setCategoria(''); }
          }, 'Receitas'),
          React.createElement('button', {
            className: `px-3 py-2 rounded-lg border ${tipo === 'expense' ? 'border-red-500 bg-red-600 text-white' : 'border-gray-600 bg-gray-800 text-gray-300'} hover:border-red-500`,
            onClick: () => { setPage(1); setTipo('expense'); setCategoria(''); }
          }, 'Despesas')
        )
      ),
      categories && categories.length ? React.createElement('div', { className: 'flex flex-wrap gap-2 mb-3' },
        React.createElement('span', { className: 'text-gray-400 text-sm mr-1 self-center' }, 'Categorias:'),
        ...categories.map(c => React.createElement('button', {
          key: c,
          className: (categoria === c)
            ? 'px-3 py-1 rounded-full text-sm border border-purple-500 bg-purple-600 text-white'
            : 'px-3 py-1 rounded-full text-sm border border-gray-600 bg-gray-800 text-gray-300',
          onClick: () => { setPage(1); setCategoria(prev => prev === c ? '' : c); }
        }, c || '-')),
        categoria ? React.createElement('button', {
          className: 'px-3 py-1 rounded-full text-sm border border-gray-600 bg-gray-800 text-gray-300',
          onClick: () => { setPage(1); setCategoria(''); }
        }, 'Limpar') : null
      ) : null,
      React.createElement('table', { className: 'w-full text-left' },
        React.createElement('thead', null,
          React.createElement('tr', null,
            ['Cliente','Descrição','Tipo','Categoria','Método','Data','Valor','Comprovante','Ações'].map(h => 
              React.createElement('th', { key: h, className: 'px-3 py-2 text-gray-300' }, h)
            )
          )
        ),
        React.createElement('tbody', null,
          pageItems.map(t => React.createElement('tr', { key: t.id, className: 'border-t border-gray-700' },
            React.createElement('td', { className: 'px-3 py-2 text-white' }, t.client_name || '-'),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, t.description || '-'),
            React.createElement('td', { className: 'px-3 py-2' },
              React.createElement('span', { 
                className: `px-2 py-1 rounded font-semibold ${t.transaction_type === 'revenue' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`
              }, t.transaction_type === 'revenue' ? 'Receita' : 'Despesa')
            ),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, 
              t.category_name || '-'
            ),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, paymentLabel(t.payment_method)),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, formatDateBR(t.date)),
            React.createElement('td', { className: 'px-3 py-2 text-white' }, window.UTILS.formatarReal(t.amount || 0)),
            React.createElement('td', { className: 'px-3 py-2' },
              t.attachment ? React.createElement('a', { href: t.attachment, target: '_blank', rel: 'noopener noreferrer', className: 'text-blue-400 hover:underline' }, 'Abrir') : React.createElement('span', { className: 'text-gray-400' }, '-')
            ),
            React.createElement('td', { className: 'px-3 py-2 flex gap-2' },
              React.createElement('button', { 
                className: 'px-3 py-1 bg-amber-600 hover:bg-amber-700 rounded', 
                onClick: () => setEditing(t)
              }, 'Modificar'),
              React.createElement('button', { 
                className: 'px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded', 
                onClick: () => setSelectedTransaction(t) 
              }, 'Visualizar')
            )
          ))
        )
      ),
      React.createElement('div', { className: 'flex items-center gap-3 mt-3' },
        React.createElement('button', { 
          className: 'px-3 py-1 border border-gray-600 rounded', 
          disabled: page<=1, 
          onClick: () => setPage(p => Math.max(1, p-1)) 
        }, 'Anterior'),
        React.createElement('span', { className: 'text-gray-300' }, `${page} / ${totalPages}`),
        React.createElement('button', { 
          className: 'px-3 py-1 border border-gray-600 rounded', 
          disabled: page>=totalPages, 
          onClick: () => setPage(p => Math.min(totalPages, p+1)) 
        }, 'Próxima')
      )
    );
  }

  const financeiroRootEl = document.getElementById('react-financeiro-table-root');
  if (financeiroRootEl) {
    const root = ReactDOM.createRoot(financeiroRootEl);
    root.render(React.createElement(FinanceiroTable));
  }
})();

// ===== React Clientes Table =====
(function(){
  const { useState, useEffect, useMemo } = React;

  function statusBadgeClass(status) {
    const isActive = status === 'active' || status === 'ativo';
    return isActive 
      ? 'bg-green-600/20 text-green-400 border border-green-600/30 rounded-md'
      : 'bg-red-600/20 text-red-400 border border-red-600/30 rounded-md';
  }

  function statusLabel(status) {
    const isActive = status === 'active' || status === 'ativo';
    return isActive ? 'Ativo' : 'Inativo';
  }

  function ClientesTable() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [page, setPage] = useState(1);
    const [selectedClient, setSelectedClient] = useState(null);
    const pageSize = 10;

    const loadData = async () => {
      try {
        const resp = await window.apiService.getClientes();
        const list = Array.isArray(resp) ? resp : (resp?.results || []);
        setData(list);
      } catch (e) {
        window.UTILS.showToast('Erro ao carregar clientes', 'error');
      } finally {
        setLoading(false);
      }
    };

    useEffect(() => {
      loadData();
    }, []);

    useEffect(() => {
      window.openClientModalFromReact = (clientId) => {
        const client = data.find(c => c.id === clientId);
        if (client) setSelectedClient(client);
      };
    }, [data]);

    const filtered = useMemo(() => {
      let list = data;
      if (query) {
        const q = query.toLowerCase();
        list = list.filter(c =>
          String(c.name || '').toLowerCase().includes(q) ||
          String(c.trade_name || '').toLowerCase().includes(q) ||
          String(c.tax_id || '').toLowerCase().includes(q) ||
          String(c.email || '').toLowerCase().includes(q)
        );
      }
      if (statusFilter) {
        list = list.filter(c => c.status === statusFilter);
      }
      return list;
    }, [data, query, statusFilter]);

    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const pageItems = useMemo(() => {
      const start = (page - 1) * pageSize;
      return filtered.slice(start, start + pageSize);
    }, [filtered, page]);

    useEffect(() => {
      const handler = () => {
        const el = document.querySelector('input[placeholder*="Buscar por nome, CPF/CNPJ"]');
        if (el) el.focus();
      };
      window.addEventListener('react:focus-search', handler);
      return () => window.removeEventListener('react:focus-search', handler);
    }, []);

    if (loading) {
      return React.createElement('div', { className: 'flex items-center justify-center py-12' },
        React.createElement('div', { className: 'text-center' },
          React.createElement('i', { className: 'fas fa-spinner fa-spin text-4xl text-purple-600 mb-4' }),
          React.createElement('p', { className: 'text-gray-400' }, 'Carregando clientes...')
        )
      );
    }

    if (filtered.length === 0 && !query && !statusFilter) {
      return React.createElement('div', { className: 'text-center py-12' },
        React.createElement('i', { className: 'fas fa-inbox text-5xl text-gray-700 mb-4' }),
        React.createElement('p', { className: 'text-gray-400 mb-4' }, 'Nenhum cliente cadastrado'),
        React.createElement('button', { 
          className: 'px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-all',
          onClick: () => window.openClientModal && window.openClientModal()
        }, 'Criar Primeiro Cliente')
      );
    }

    return React.createElement('div', { className: 'glass-card rounded-xl overflow-hidden' },
      selectedClient && React.createElement('div', { 
        className: 'fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4',
        onClick: () => setSelectedClient(null)
      },
        React.createElement('div', { 
          className: 'bg-gray-800 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto',
          onClick: e => e.stopPropagation()
        },
          React.createElement('div', { className: 'border-b border-gray-700 p-6' },
            React.createElement('div', { className: 'flex justify-between items-start mb-4' },
              React.createElement('h2', { className: 'text-2xl font-bold text-white' }, 
                selectedClient.name || selectedClient.trade_name || 'Client'
              ),
              React.createElement('button', { 
                className: 'text-gray-400 hover:text-white',
                onClick: () => setSelectedClient(null)
              }, React.createElement('i', { className: 'fas fa-times text-xl' }))
            ),
            React.createElement('div', { className: 'flex items-center gap-3 flex-wrap' },
              React.createElement('span', { className: `px-3 py-1 rounded-full text-xs font-semibold ${selectedClient.status === 'active' ? 'bg-green-600/20 text-green-400 border border-green-600/30' : 'bg-red-600/20 text-red-400 border border-red-600/30'}` },
                statusLabel(selectedClient.status)
              ),
              React.createElement('span', { className: 'text-sm text-gray-400' }, 
                window.UTILS.formatarCNPJ(selectedClient.tax_id) || '-'
              )
            )
          ),
          
          React.createElement('div', { className: 'p-6' },
            React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-3 gap-6 mb-6' },
              React.createElement('div', null,
                React.createElement('h3', { className: 'text-sm font-semibold text-purple-400 uppercase mb-3 flex items-center gap-2' },
                  React.createElement('i', { className: 'fas fa-envelope' }),
                  'Contact'
                ),
                React.createElement('div', { className: 'space-y-3' },
                  React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Email'),
                    React.createElement('div', { className: 'flex items-center justify-between gap-2' },
                      React.createElement('p', { className: 'text-sm text-white break-all' }, selectedClient.email || '-'),
                      selectedClient.email && React.createElement('div', { className: 'flex gap-1' },
                        React.createElement('a', { 
                          className: 'text-blue-400 hover:text-blue-300 text-xs', 
                          href: `mailto:${selectedClient.email}`,
                          title: 'Enviar email'
                        }, React.createElement('i', { className: 'fas fa-envelope' })),
                        React.createElement('button', { 
                          className: 'text-gray-400 hover:text-white text-xs',
                          onClick: () => {
                            navigator.clipboard.writeText(selectedClient.email);
                            window.UTILS.showToast('Email copiado!', 'success');
                          }
                        }, React.createElement('i', { className: 'fas fa-copy' }))
                      )
                    )
                  ),
                  React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Telefone'),
                    React.createElement('div', { className: 'flex items-center justify-between gap-2' },
                      React.createElement('p', { className: 'text-sm text-white' }, selectedClient.phone || '-'),
                      selectedClient.phone && React.createElement('div', { className: 'flex gap-1' },
                        React.createElement('a', { 
                          className: 'text-green-400 hover:text-green-300 text-xs', 
                          href: `https://wa.me/${String(selectedClient.phone).replace(/\D/g,'')}`,
                          target: '_blank', rel: 'noopener noreferrer', title: 'WhatsApp'
                        }, React.createElement('i', { className: 'fab fa-whatsapp' })),
                        React.createElement('button', { 
                          className: 'text-gray-400 hover:text-white text-xs',
                          onClick: () => {
                            navigator.clipboard.writeText(String(selectedClient.phone).replace(/\D/g,''));
                            window.UTILS.showToast('Telefone copiado!', 'success');
                          }
                        }, React.createElement('i', { className: 'fas fa-copy' }))
                      )
                    )
                  )
                )
              ),
              
              // Documentos
              React.createElement('div', null,
                React.createElement('h3', { className: 'text-sm font-semibold text-blue-400 uppercase mb-3 flex items-center gap-2' },
                  React.createElement('i', { className: 'fas fa-file-alt' }),
                  'Documentos'
                ),
                React.createElement('div', { className: 'space-y-3' },
                  React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Inscrição Estadual'),
                    React.createElement('p', { className: 'text-sm text-white' }, selectedClient.state_registration || '-')
                  ),
                  React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Inscrição Municipal'),
                    React.createElement('p', { className: 'text-sm text-white' }, selectedClient.municipal_registration || '-')
                  ),
                  selectedClient.person_type && React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Tipo de Pessoa'),
                    React.createElement('p', { className: 'text-sm text-white' },
                      selectedClient.person_type === 'PJ' ? 'Pessoa Jurídica' : 'Pessoa Física'
                    )
                  )
                )
              ),
              
              React.createElement('div', null,
                React.createElement('h3', { className: 'text-sm font-semibold text-green-400 uppercase mb-3 flex items-center gap-2' },
                  React.createElement('i', { className: 'fas fa-info-circle' }),
                  'Information'
                ),
                React.createElement('div', { className: 'space-y-3' },
                  React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Registration Date'),
                    React.createElement('p', { className: 'text-sm text-white' }, 
                      selectedClient.created_at ? new Date(selectedClient.created_at).toLocaleDateString('pt-BR') : '01/12/2025'
                    )
                  ),
                  selectedClient.activity && React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Activity'),
                    React.createElement('p', { className: 'text-sm text-white' }, selectedClient.activity)
                  ),
                  selectedClient.tax_regime && React.createElement('div', null,
                    React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Tax Regime'),
                    React.createElement('p', { className: 'text-sm text-white' }, selectedClient.tax_regime)
                  )
                )
              )
            ),
            
            React.createElement('div', { className: 'border-t border-gray-700 pt-6' },
              React.createElement('h3', { className: 'text-sm font-semibold text-orange-400 uppercase mb-4 flex items-center gap-2' },
                React.createElement('i', { className: 'fas fa-map-marker-alt' }),
                'Address'
              ),
              React.createElement('div', { className: 'grid grid-cols-2 md:grid-cols-4 gap-4' },
                React.createElement('div', null,
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'ZIP Code'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.zip_code || '-')
                ),
                React.createElement('div', { className: 'col-span-2' },
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Street'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.street || '-')
                ),
                React.createElement('div', null,
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Number'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.number || '-')
                ),
                React.createElement('div', null,
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Complemento'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.complement || '-')
                ),
                React.createElement('div', null,
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Bairro'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.neighborhood || '-')
                ),
                React.createElement('div', null,
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Cidade'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.city || '-')
                ),
                React.createElement('div', null,
                  React.createElement('p', { className: 'text-xs text-gray-400 uppercase mb-1' }, 'Estado'),
                  React.createElement('p', { className: 'text-sm text-white' }, selectedClient.state || '-')
                )
              )
            )
          ),
          
          // Footer
          React.createElement('div', { className: 'border-t border-gray-700 p-6 flex justify-end gap-3' },
            React.createElement('button', { 
              className: 'px-6 py-2 border border-gray-600 rounded-lg hover:bg-gray-700 transition-all',
              onClick: () => setSelectedClient(null)
            }, 'Fechar'),
            React.createElement('button', { 
              className: 'px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg hover:shadow-lg transition-all',
              onClick: () => {
                setSelectedClient(null);
                if (window.editClient) window.editClient(selectedClient.id);
              }
            }, 'Editar Cliente')
          )
        )
      ),


      // Tabela
      React.createElement('div', { className: 'overflow-x-auto' },
        React.createElement('table', { className: 'w-full' },
          React.createElement('thead', { className: 'bg-gray-800/50 border-b border-gray-700' },
            React.createElement('tr', null,
              React.createElement('th', { className: 'px-6 py-4 text-left text-sm font-semibold text-gray-300' },
                React.createElement('i', { className: 'fas fa-user mr-2 text-purple-400' }),
                'Cliente'
              ),
              React.createElement('th', { className: 'px-6 py-4 text-left text-sm font-semibold text-gray-300' },
                React.createElement('i', { className: 'fas fa-id-card mr-2 text-purple-400' }),
                'CNPJ/CPF'
              ),
              React.createElement('th', { className: 'px-6 py-4 text-left text-sm font-semibold text-gray-300' },
                React.createElement('i', { className: 'fas fa-envelope mr-2 text-purple-400' }),
                'Email'
              ),
              React.createElement('th', { className: 'px-6 py-4 text-left text-sm font-semibold text-gray-300' },
                React.createElement('i', { className: 'fas fa-info-circle mr-2 text-purple-400' }),
                'Status'
              ),
              React.createElement('th', { className: 'px-6 py-4 text-right text-sm font-semibold text-gray-300' },
                React.createElement('i', { className: 'fas fa-cog mr-2 text-purple-400' }),
                'Ações'
              )
            )
          ),
          React.createElement('tbody', { className: 'divide-y divide-gray-700' },
            pageItems.length === 0 ? React.createElement('tr', null,
              React.createElement('td', { className: 'px-6 py-8 text-center text-gray-400', colspan: '5' },
                React.createElement('i', { className: 'fas fa-search text-3xl mb-2' }),
                React.createElement('p', null, 'Nenhum cliente encontrado com os filtros aplicados')
              )
            ) : pageItems.map(c =>
              React.createElement('tr', { 
                key: c.id,
                className: 'hover:bg-gray-700/30 transition-colors cursor-pointer',
                onClick: () => setSelectedClient(c)
              },
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'flex items-center gap-3' },
                    React.createElement('div', { className: 'w-10 h-10 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center' },
                      React.createElement('i', { className: 'fas fa-user text-white' })
                    ),
                    React.createElement('div', null,
                      React.createElement('div', { className: 'text-sm font-medium text-white' }, c.name || c.trade_name || '-'),
                      c.trade_name && c.name && React.createElement('div', { className: 'text-xs text-gray-400' }, c.name)
                    )
                  )
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'text-sm text-gray-300' }, window.UTILS.formatarCNPJ(c.tax_id) || '-')
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('div', { className: 'text-sm text-gray-300' }, c.email || '-')
                ),
                React.createElement('td', { className: 'px-6 py-4' },
                  React.createElement('span', { className: `px-2.5 py-1 inline-flex text-xs leading-5 font-semibold ${statusBadgeClass(c.status)}` },
                    statusLabel(c.status)
                  )
                ),
                React.createElement('td', { className: 'px-6 py-4 text-right' },
                  React.createElement('div', { className: 'flex items-center justify-end gap-2', onClick: e => e.stopPropagation() },
                    React.createElement('button', { 
                      className: 'p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded-lg transition-all',
                      onClick: () => setSelectedClient(c),
                      title: 'Ver detalhes'
                    }, React.createElement('i', { className: 'fas fa-eye' })),
                    React.createElement('button', { 
                      className: 'p-2 text-purple-400 hover:text-purple-300 hover:bg-purple-400/10 rounded-lg transition-all',
                      onClick: () => window.editClient && window.editClient(c.id),
                      title: 'Editar'
                    }, React.createElement('i', { className: 'fas fa-edit' })),
                    React.createElement('button', { 
                      className: 'p-2 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-lg transition-all',
                      onClick: () => window.deleteClient && window.deleteClient(c.id),
                      title: 'Excluir'
                    }, React.createElement('i', { className: 'fas fa-trash' }))
                  )
                )
              )
            )
          )
        )
      ),

      React.createElement('div', { className: 'p-4 border-t border-gray-700/50 flex items-center justify-between' },
        React.createElement('div', { className: 'text-sm text-gray-400' },
          `Mostrando ${pageItems.length} de ${filtered.length} cliente(s)`
        ),
        React.createElement('div', { className: 'flex items-center gap-2' },
          React.createElement('button', { 
            className: `px-4 py-2 rounded-lg transition-all ${page <= 1 ? 'bg-gray-700/50 text-gray-500 cursor-not-allowed' : 'bg-gray-700 text-white hover:bg-gray-600'}`,
            disabled: page <= 1,
            onClick: () => setPage(p => Math.max(1, p - 1))
          }, 
            React.createElement('i', { className: 'fas fa-chevron-left' })
          ),
          React.createElement('span', { className: 'px-4 py-2 text-gray-300' }, 
            `Página ${page} de ${totalPages}`
          ),
          React.createElement('button', { 
            className: `px-4 py-2 rounded-lg transition-all ${page >= totalPages ? 'bg-gray-700/50 text-gray-500 cursor-not-allowed' : 'bg-gray-700 text-white hover:bg-gray-600'}`,
            disabled: page >= totalPages,
            onClick: () => setPage(p => Math.min(totalPages, p + 1))
          }, 
            React.createElement('i', { className: 'fas fa-chevron-right' })
          )
        )
      )
    );
  }

  const clientesRootEl = document.getElementById('react-clientes-table-root');
  if (clientesRootEl) {
    const root = ReactDOM.createRoot(clientesRootEl);
    root.render(React.createElement(ClientesTable));
  }
})();
