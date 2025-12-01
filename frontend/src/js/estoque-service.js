window.EstoqueUI = (() => {
  const api = (path, opts={}) => fetch(`/api/estoque${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  }).then(r => r.json());

  const qs = sel => document.querySelector(sel);
  const tblFill = (tbody, rows, cols) => {
    tbody.innerHTML = rows.map(r => `<tr>${cols.map(c => `<td class="p-2 border">${c(r)}</td>`).join('')}</tr>`).join('');
  };

  let itens = [];

  const loadItens = async () => {
    itens = await api('/itens');
    const tbody = qs('#tbl-itens tbody');
    tblFill(tbody, itens, [
      r => r.codigo,
      r => r.nome,
      r => (r.saldo_atual ?? 0),
      r => (r.custo_medio ?? 0).toFixed(2)
    ]);
    const selects = ['#mov-item', '#cont-item'];
    selects.forEach(s => {
      const el = qs(s);
      el.innerHTML = itens.map(i => `<option value="${i.id}">${i.codigo} • ${i.nome}</option>`).join('');
    });
  };

  const loadMov = async () => {
    const data = await api('/movimentos');
    const tbody = qs('#tbl-mov tbody');
    const byId = Object.fromEntries(itens.map(i => [i.id, i]));
    tblFill(tbody, data, [
      r => new Date(r.realizado_em).toLocaleString(),
      r => byId[r.item_id]?.nome || r.item_id,
      r => r.tipo,
      r => r.quantidade,
      r => r.valor_unitario ?? ''
    ]);
  };

  const loadCont = async () => {
    const data = await api('/contagens');
    const tbody = qs('#tbl-cont tbody');
    const byId = Object.fromEntries(itens.map(i => [i.id, i]));
    tblFill(tbody, data, [
      r => new Date(r.contagem_em).toLocaleString(),
      r => byId[r.item_id]?.nome || r.item_id,
      r => r.quantidade_contada,
      r => r.diferença
    ]);
  };

  const bind = () => {
    qs('#btn-add-item').addEventListener('click', async () => {
      const payload = {
        codigo: qs('#item-codigo').value.trim(),
        nome: qs('#item-nome').value.trim(),
        unidade: qs('#item-unidade').value.trim() || 'un'
      };
      if (!payload.codigo) { alert('Informe o código'); return; }
      const res = await api('/itens', { method: 'POST', body: JSON.stringify(payload) });
      await loadItens();
    });

    qs('#btn-add-mov').addEventListener('click', async () => {
      const payload = {
        item_id: parseInt(qs('#mov-item').value, 10),
        tipo: qs('#mov-tipo').value,
        quantidade: parseFloat(qs('#mov-quantidade').value),
        valor_unitario: qs('#mov-valor').value ? parseFloat(qs('#mov-valor').value) : null
      };
      if (!payload.item_id || !payload.quantidade) { alert('Selecione item e quantidade'); return; }
      await api('/movimentos', { method: 'POST', body: JSON.stringify(payload) });
      await loadItens();
      await loadMov();
    });

    qs('#btn-add-cont').addEventListener('click', async () => {
      const payload = {
        item_id: parseInt(qs('#cont-item').value, 10),
        quantidade_contada: parseFloat(qs('#cont-quantidade').value)
      };
      if (!payload.item_id || !payload.quantidade_contada) { alert('Selecione item e quantidade'); return; }
      await api('/contagens', { method: 'POST', body: JSON.stringify(payload) });
      await loadCont();
    });

    qs('#btn-rel').addEventListener('click', async () => {
      const inicio = qs('#rel-inicio').value;
      const fim = qs('#rel-fim').value;
      const params = new URLSearchParams();
      if (inicio) params.set('inicio', new Date(inicio).toISOString());
      if (fim) params.set('fim', new Date(fim).toISOString());
      const data = await api(`/relatorios/resumo?${params.toString()}`);
      qs('#rel-out').textContent = `Entradas: ${data.entradas} | Saídas: ${data.saidas} | Valor entradas: ${data.valor_entradas.toFixed ? data.valor_entradas.toFixed(2) : data.valor_entradas} | Saldo total: ${data.saldo_total}`;
    });
  };

  const init = async () => {
    bind();
    await loadItens();
    await loadMov();
    await loadCont();
  };

  return { init };
})();
