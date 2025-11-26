# 🧾 Módulo de Emissão de Notas Fiscais Eletrônicas

## 📋 Visão Geral

O sistema agora possui funcionalidade completa para **emitir Notas Fiscais Eletrônicas (NFe)** diretamente pela interface, com integração simulada com a SEFAZ.

### ✅ Funcionalidades Implementadas

1. **Emissão de NFe**
   - Formulário completo para preenchimento
   - Validação de dados obrigatórios
   - Geração automática de chave de acesso (44 dígitos)
   - Cálculo automático de valores
   - Simulação de transmissão para SEFAZ
   - Autorização automática

2. **Consulta de Status**
   - Endpoint para consultar status na SEFAZ
   - Verificação de protocolo de autorização

3. **Cancelamento na SEFAZ**
   - Cancelamento com justificativa (mínimo 15 caracteres)
   - Geração de evento de cancelamento
   - Protocolo de cancelamento

---

## 🎯 Como Usar

### Emitir uma Nota Fiscal

1. **Acesse** a página de Notas Fiscais
2. **Clique** no botão verde "Emitir NFe"
3. **Preencha** o formulário:
   - Selecione o cliente (preenche automaticamente CNPJ e nome)
   - Informe número, série e modelo
   - Digite valor de produtos e/ou serviços
   - Adicione observações (opcional)
4. **Clique** em "Emitir NFe"
5. **Aguarde** o processamento (2-3 segundos)
6. **Sucesso!** A nota é autorizada e salva automaticamente

### Campos do Formulário

#### 📋 Dados do Destinatário
- **Cliente**: Seleção do cliente cadastrado
- **CNPJ/CPF**: Preenchido automaticamente ao selecionar cliente
- **Nome/Razão Social**: Preenchido automaticamente

#### 📄 Dados da Nota
- **Número**: Número sequencial da nota (gerado automaticamente)
- **Série**: Série da nota (padrão: 1)
- **Modelo**: 
  - NFe (55) - Nota Fiscal Eletrônica
  - NFCe (65) - Nota Fiscal ao Consumidor Eletrônica
  - NFSe - Nota Fiscal de Serviços Eletrônica
- **Tipo**: Entrada ou Saída
- **CNPJ Emitente**: CNPJ da sua empresa

#### 💰 Valores
- **Valor Produtos**: Valor total dos produtos (obrigatório)
- **Valor Serviços**: Valor total dos serviços (opcional)
- **Valor Total**: Calculado automaticamente (produtos + serviços)

---

## 🔧 Detalhes Técnicos

### Backend

#### Novo Serviço: `nfe_service.py`

```python
class NFeService:
    def gerar_chave_acesso()      # Gera chave de 44 dígitos
    def emitir_nfe()               # Emite e autoriza NFe
    def consultar_status_nfe()     # Consulta na SEFAZ
    def cancelar_nfe()             # Cancela NFe autorizada
    def validar_dados_emissao()    # Valida campos obrigatórios
```

**Chave de Acesso (44 dígitos)**
```
Formato: UF + AAMM + CNPJ + MOD + SERIE + NNF + TPEMIS + CNF + DV
Exemplo: 35210410898409000174550010000012341001234567
```

#### Novos Endpoints API

```
POST /api/notas-fiscais/emitir
- Emite uma nova NFe
- Gera chave de acesso automaticamente
- Transmite para SEFAZ (simulado)
- Retorna nota autorizada com protocolo

GET /api/notas-fiscais/{nota_id}/consultar-status
- Consulta status atual na SEFAZ
- Retorna protocolo e situação

POST /api/notas-fiscais/{nota_id}/cancelar-sefaz
- Cancela NFe na SEFAZ
- Requer justificativa (mín. 15 caracteres)
- Gera evento de cancelamento
```

### Frontend

#### Novo Modal: "Emitir NFe"

- Interface intuitiva com 3 seções
- Validação client-side e server-side
- Feedback visual durante emissão
- Mensagens de sucesso/erro

#### Funcionalidades JavaScript

```javascript
openEmitirModal()       // Abre modal e gera número
handleEmitir(event)     // Processa emissão
calcularValorTotal()    // Calcula total automaticamente
loadClientes()          // Carrega clientes para seleção
```

---

## 📊 Fluxo de Emissão

```
1. Usuário preenche formulário
   ↓
2. Sistema valida dados
   ↓
3. Gera chave de acesso (44 dígitos)
   ↓
4. Monta XML da NFe
   ↓
5. Assina digitalmente (simulado)
   ↓
6. Transmite para SEFAZ (simulado)
   ↓
7. SEFAZ processa (2-3 segundos)
   ↓
8. Retorna protocolo de autorização
   ↓
9. Salva no banco com status "autorizada"
   ↓
10. Cria evento de autorização
```

---

## 🔐 Validações Implementadas

### Campos Obrigatórios
- ✅ cliente_id
- ✅ tipo (entrada/saida)
- ✅ modelo (nfe/nfce/nfse)
- ✅ numero
- ✅ serie
- ✅ cnpj_emitente
- ✅ nome_emitente
- ✅ cnpj_destinatario
- ✅ nome_destinatario
- ✅ valor_produtos
- ✅ valor_total

### Regras de Negócio
- ✅ Tipo deve ser: entrada, saida ou servico
- ✅ Modelo deve ser: nfe, nfce ou nfse
- ✅ Valor total > 0
- ✅ CNPJ emitente: 14 dígitos
- ✅ CPF/CNPJ destinatário: 11 ou 14 dígitos
- ✅ Chave de acesso única (não duplicada)

---

## 🎨 Interface

### Botão de Emissão
```html
<button class="bg-gradient-to-r from-green-600 to-emerald-600">
    <i class="fas fa-plus-circle"></i> Emitir NFe
</button>
```

### Estados do Modal

**1. Preenchimento**
- Formulário em branco
- Campos habilitados
- Botão "Emitir NFe" ativo

**2. Processando**
- Botão desabilitado
- Ícone de loading
- Mensagem "Emitindo NFe..."
- Barra azul com spinner

**3. Sucesso**
- Ícone de check verde
- Mensagem "NFe emitida com sucesso!"
- Exibe chave de acesso
- Fecha automaticamente em 2 segundos

**4. Erro**
- Ícone de erro vermelho
- Mensagem de erro detalhada
- Botão reabilitado

---

## 📝 Exemplo de Uso

### Requisição API

```json
POST /api/notas-fiscais/emitir

{
  "cliente_id": "abc-123",
  "numero": "12345",
  "serie": "1",
  "modelo": "nfe",
  "tipo": "saida",
  "cnpj_emitente": "12.345.678/0001-90",
  "nome_emitente": "Sua Empresa Ltda",
  "cnpj_destinatario": "98.765.432/0001-01",
  "nome_destinatario": "Cliente ABC Ltda",
  "valor_produtos": 5000.00,
  "valor_servicos": 1500.00,
  "valor_total": 6500.00,
  "observacoes": "Nota fiscal referente a venda"
}
```

### Resposta API

```json
{
  "id": "nota-xyz",
  "chave_acesso": "35241110898409000174550010001234510012345678",
  "numero": "12345",
  "serie": "1",
  "situacao": "autorizada",
  "data_emissao": "2024-11-13T10:30:00",
  "data_autorizacao": "2024-11-13T10:30:03",
  "valor_total": 6500.00,
  "protocolo": "202411131030031234567"
}
```

---

## ⚠️ Importante

### Ambiente de Homologação

Atualmente o sistema opera em **modo de simulação** (homologação):
- ✅ Todas as funcionalidades implementadas
- ✅ Fluxo completo funcional
- ⚠️ Não transmite para SEFAZ real
- ⚠️ Chaves de acesso são geradas mas não validadas externamente
- ⚠️ Taxa de sucesso: 95% (simulado)

### Para Produção

Para usar em ambiente real, é necessário:

1. **Certificado Digital A1**
   - Obter certificado e-CNPJ ou e-CPF
   - Instalar no servidor

2. **Integração Real**
   - Implementar webservice SOAP da SEFAZ
   - Ou usar gateway (TecnoSpeed, WebMania, etc)
   - Ou biblioteca python-nfe

3. **Configurações**
   - Alterar `ambiente` de "homologacao" para "producao"
   - Configurar endpoints da SEFAZ do estado
   - Implementar assinatura digital real

4. **Segurança**
   - Armazenar certificados com segurança
   - Criptografar senhas
   - Implementar logs de auditoria

---

## 🚀 Próximos Passos

### Melhorias Sugeridas

1. **Itens da Nota**
   - Adicionar tabela de produtos/serviços
   - Calcular impostos por item
   - Validar NCM/CFOP

2. **Impostos**
   - Calcular ICMS, IPI, PIS, COFINS
   - Aplicar regime tributário do cliente
   - Gerar totalizadores

3. **DANFE**
   - Gerar PDF do DANFE
   - Download automático
   - Envio por email

4. **Carta de Correção**
   - Emitir CC-e
   - Histórico de correções

5. **Manifestação do Destinatário**
   - Ciência da operação
   - Confirmação/desconhecimento
   - Operação não realizada

6. **Integração Contábil**
   - Sincronizar com lançamentos financeiros
   - Gerar movimentações automaticamente
   - Atualizar estoque

---

## 📚 Referências

- **Portal da NFe**: http://www.nfe.fazenda.gov.br
- **Manual de Integração**: Versão 4.0
- **python-nfe**: https://github.com/TadaSoftware/PyNFe
- **Consulta Chave**: https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx

---

## ✅ Checklist de Teste

- [x] Emitir NFe com cliente cadastrado
- [x] Calcular valor total automaticamente
- [x] Validar campos obrigatórios
- [x] Gerar chave de acesso válida
- [x] Simular autorização SEFAZ
- [x] Salvar nota no banco
- [x] Criar evento de autorização
- [x] Exibir mensagem de sucesso
- [x] Atualizar lista de notas
- [x] Tratar erros de validação
- [x] Cancelar nota autorizada
- [x] Consultar status

---

**Data de Implementação**: 13/11/2025  
**Versão**: 1.0  
**Status**: ✅ Funcional (Simulação)
