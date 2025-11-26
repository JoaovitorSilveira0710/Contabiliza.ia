# 🎬 Tutorial Rápido - Contabiliza.IA

## 🎯 Objetivo
Aprender a usar o sistema Contabiliza.IA testando localmente antes de integrar automações.

---

## 📺 Parte 1: Iniciando o Projeto (5 minutos)

### Passo 1: Ativar Ambiente Virtual

```powershell
# Na pasta raiz do projeto (Contabiliza.IA/)
cd "C:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"
.\venv\Scripts\Activate.ps1
```

**O que você verá**: `(venv)` aparecerá no início da linha do terminal.

---

### Passo 2: Iniciar o Backend

```powershell
python run.py
```

**O que você verá**:
```
INFO:run:🚀 Iniciando Contabiliza.IA...
INFO:run:📚 Docs disponíveis em: http://localhost:8000/docs
INFO:run:🏥 Health check em: http://localhost:8000/health
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:backend.app.models.database:✅ Tabelas criadas com sucesso!
INFO:backend.app.models.database:📊 16 tabelas criadas
INFO:     Application startup complete.
```

**✅ Checkpoint**: Se você viu "Application startup complete", está tudo certo!

---

### Passo 3: Testar o Backend

#### Opção A: No Navegador

1. Abra: **http://localhost:8000/docs**
2. Você verá a documentação interativa Swagger UI
3. Explore as seções: auth, clientes, financeiro, contabil, juridico

#### Opção B: No Terminal (nova aba PowerShell)

```powershell
# Health check
curl http://localhost:8000/health
# Resposta esperada: {"status":"ok","timestamp":"..."}

# Listar clientes (vazio inicialmente)
curl http://localhost:8000/api/clientes/
# Resposta esperada: []
```

---

## 📺 Parte 2: Usando o Frontend (10 minutos)

### Passo 1: Acessar a Interface

No navegador, abra: **http://localhost:8000**

Você será redirecionado para: **http://localhost:8000/pages/login.html**

---

### Passo 2: Fazer Login

**Tela de Login**:
- Email: `admin@contabiliza.ia` (ou qualquer email válido)
- Senha: `dev123` (ou qualquer senha)
- Clique em **"Entrar"**

**O que acontece**:
1. Frontend chama `/api/auth/login` (POST)
2. Backend retorna `{"token": "dev-token", "usuario": {...}}`
3. Token é salvo no `localStorage`
4. Você é redirecionado para o **Dashboard**

---

### Passo 3: Navegar pelo Dashboard

**Elementos visíveis**:
- **Menu Lateral Esquerdo**:
  - 🏠 Dashboard
  - 👥 Clientes
  - 💰 Financeiro
  - ⚖️ Jurídico
  - 📄 Notas Fiscais
  - 📊 Relatórios
  - 🚪 Sair

- **Cards Principais**:
  - Total de Clientes
  - Receitas do Mês
  - Despesas do Mês
  - Processos Ativos

**Teste**: Clique em cada item do menu e veja as páginas carregarem.

---

### Passo 4: Cadastrar um Cliente

1. No menu, clique em **"Clientes"**
2. Clique no botão **"+ Novo Cliente"** (canto superior direito)
3. Preencha o formulário:

   ```
   Nome/Razão Social: Tech Solutions LTDA
   CNPJ/CPF: 12.345.678/0001-90
   Tipo de Pessoa: Jurídica (J)
   Email: contato@techsolutions.com
   Telefone: (11) 98765-4321
   Regime Tributário: Simples Nacional
   Atividade Principal: Desenvolvimento de Software
   ```

4. Clique em **"Salvar"**

**O que acontece**:
- Frontend chama `/api/clientes/` (POST) com os dados
- Backend valida e salva no banco SQLite
- Cliente aparece na lista da tela "Clientes"

---

### Passo 5: Criar um Contrato para o Cliente

1. Na lista de clientes, localize "Tech Solutions LTDA"
2. Clique em **"Contratos"** na linha do cliente
3. Clique em **"+ Novo Contrato"**
4. Preencha:

   ```
   Tipo de Serviço: Contábil
   Valor Mensal: R$ 800,00
   Data de Início: 01/01/2025
   Dia de Vencimento: 10
   Observações: Contrato padrão mensal
   ```

5. Clique em **"Salvar"**

**Verificação**: O contrato aparece listado nos contratos do cliente.

---

### Passo 6: Lançar uma Receita

1. No menu, clique em **"Financeiro"**
2. Aba **"Lançamentos"** → Clique em **"+ Novo Lançamento"**
3. Preencha:

   ```
   Tipo: Receita
   Descrição: Honorários Tech Solutions - Janeiro/2025
   Valor: R$ 800,00
   Data de Vencimento: 10/01/2025
   Categoria: Honorários
   Cliente: Tech Solutions LTDA (selecione do dropdown)
   ```

4. Clique em **"Salvar"**

**O que acontece**:
- Frontend chama `/api/financeiro/lancamentos/` (POST)
- Backend cria o lançamento e retorna status 201
- Lançamento aparece na lista da aba "Lançamentos"

---

### Passo 7: Visualizar Fluxo de Caixa

1. Na tela "Financeiro", clique na aba **"Fluxo de Caixa"**
2. Selecione o período:
   - Data Início: 01/01/2025
   - Data Fim: 31/01/2025
3. Clique em **"Filtrar"**

**O que você verá**:
- Gráfico de barras mostrando receitas e despesas por dia
- Saldo acumulado no período
- Totais consolidados

---

## 📺 Parte 3: Testando a API com Swagger (5 minutos)

### Passo 1: Abrir o Swagger UI

No navegador: **http://localhost:8000/docs**

---

### Passo 2: Testar Endpoint de Clientes

1. Encontre a seção **"clientes"** (ícone de tag azul)
2. Clique em **`GET /api/clientes/`** para expandir
3. Clique em **"Try it out"**
4. Ajuste parâmetros (opcional):
   - `limit`: 10
   - `skip`: 0
5. Clique em **"Execute"**

**Resposta esperada** (código 200):
```json
[
  {
    "id": "uuid-aqui",
    "nome_razao_social": "Tech Solutions LTDA",
    "cnpj_cpf": "12345678000190",
    "email": "contato@techsolutions.com",
    ...
  }
]
```

---

### Passo 3: Criar DRE via Swagger

1. Encontre a seção **"contabilidade"**
2. Clique em **`POST /api/contabil/dre/`**
3. Clique em **"Try it out"**
4. Edite o Request Body (JSON):

   ```json
   {
     "cliente_id": "cole-id-do-cliente-aqui",
     "mes_referencia": "2025-01-01",
     "receita_bruta": 10000.00,
     "deducoes": 1000.00,
     "custos": 3000.00,
     "despesas_operacionais": 2000.00,
     "despesas_nao_operacionais": 500.00
   }
   ```

5. Clique em **"Execute"**

**Resposta esperada** (código 201):
```json
{
  "id": "uuid-dre",
  "cliente_id": "uuid-cliente",
  "mes_referencia": "2025-01-01",
  "receita_bruta": 10000.00,
  ...
}
```

---

## 📺 Parte 4: Testando com Script Python (3 minutos)

### Passo 1: Instalar requests (se necessário)

```powershell
pip install requests
```

---

### Passo 2: Executar o Script de Teste

```powershell
python test_endpoints.py
```

**O que você verá**:
```
🚀 ============= INICIANDO BATERIA DE TESTES =============
Base URL: http://localhost:8000

📍 --------------- MÓDULO: HEALTH ---------------
✅ Health Check

📍 --------------- MÓDULO: AUTENTICAÇÃO ---------------
✅ Login
✅ Auth Me

📍 --------------- MÓDULO: CLIENTES ---------------
✅ Listar Clientes
✅ Criar Cliente
✅ Criar Contrato

...

📊 ================ RESUMO DOS TESTES ================
✅ Health Check
✅ Login
✅ Auth Me
✅ Listar Clientes
...

Total: 11/11 testes passaram (100.0%)
```

---

## 🎯 Checklist de Validação Completa

Marque cada item ao completar:

### Backend
- [ ] Servidor inicia sem erros (`python run.py`)
- [ ] 16 tabelas criadas no banco SQLite
- [ ] `/health` retorna `{"status":"ok"}`
- [ ] `/docs` carrega interface Swagger
- [ ] Nenhum aviso de importação nos logs

### Frontend
- [ ] Login funciona e redireciona para dashboard
- [ ] Menu lateral navega entre todas as páginas
- [ ] Formulário de cliente salva e lista
- [ ] Formulário de contrato salva e associa ao cliente
- [ ] Lançamentos financeiros são criados
- [ ] Fluxo de caixa exibe gráfico

### API
- [ ] `GET /api/clientes/` retorna lista
- [ ] `POST /api/clientes/` cria novo cliente (status 201)
- [ ] `POST /api/clientes/{id}/contratos` cria contrato
- [ ] `GET /api/financeiro/dashboard/` retorna métricas
- [ ] `GET /api/juridico/dashboard/` retorna dashboard

### Script de Teste
- [ ] `python test_endpoints.py` passa todos os testes (11/11)

---

## 🚧 Próximos Passos (Após Validação)

Agora que o projeto está testado e funcionando, você pode:

1. **Integrar Automações**:
   - Validação de CNPJ/CPF com Receita Federal
   - Consulta de NFe via API SEFAZ
   - Envio de emails com SendGrid/AWS SES
   - Webhooks para notificações

2. **Melhorar Segurança**:
   - Substituir `dev-token` por JWT real
   - Hashear senhas com bcrypt
   - Implementar rate limiting
   - Adicionar logs de auditoria

3. **Deploy em Produção**:
   - Configurar PostgreSQL
   - Usar variáveis de ambiente (.env)
   - Deploy no Railway/Render/Heroku
   - Configurar domínio e HTTPS

---

## 🆘 Problemas Comuns

### Backend não inicia

**Sintoma**: `ModuleNotFoundError: No module named 'backend'`

**Solução**:
```powershell
# Certifique-se de estar na raiz do projeto
cd "C:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"

# Use run.py (não uvicorn diretamente)
python run.py
```

---

### Frontend não carrega dados

**Sintoma**: Tabelas vazias, erro 404 no console

**Checklist**:
1. Backend está rodando? `curl http://localhost:8000/health`
2. CORS configurado? Verifique logs do backend
3. URL da API correta? Veja `frontend/src/js/config.js`:
   ```javascript
   API_BASE: 'http://localhost:8000/api'
   ```

---

### Porta 8000 ocupada

**Sintoma**: `address already in use`

**Solução**:
```powershell
# Parar processos Python
Get-Process python | Stop-Process -Force

# Aguardar 2 segundos e reiniciar
Start-Sleep -Seconds 2
python run.py
```

---

## 📚 Referências

- Documentação API: http://localhost:8000/docs
- Schema OpenAPI: http://localhost:8000/openapi.json
- Guia completo: `GUIA_TESTES.md`
- Script de teste: `test_endpoints.py`

---

**Pronto! Agora você pode testar todo o projeto localmente antes de integrar automações. 🎉**
