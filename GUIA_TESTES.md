# 🧪 Guia de Testes - Contabiliza.IA

## 📋 Pré-requisitos

- Python 3.11+ com `venv` ativado
- Navegador moderno (Chrome, Edge, Firefox)
- Opcional: Postman, Thunder Client ou Insomnia para testes de API

---

## 🚀 1. Iniciando o Backend

### Opção A: Via run.py (Recomendado)

```powershell
# Na raiz do projeto (Contabiliza.IA/)
.\venv\Scripts\Activate.ps1
python run.py
```

O servidor iniciará em: **http://localhost:8000**

Você verá logs confirmando:
- ✅ Routers incluídos (clientes, auth, financeiro, contabil, notas, juridico)
- ✅ Frontend estático montado
- ✅ Banco de dados inicializado (16 tabelas criadas)

### Verificações Rápidas

```powershell
# Health check
curl http://localhost:8000/health

# Documentação interativa (Swagger)
# Abrir no navegador: http://localhost:8000/docs

# OpenAPI JSON
curl http://localhost:8000/openapi.json
```

---

## 🌐 2. Testando o Frontend

### Método 1: Via Backend (Frontend servido pelo FastAPI)

1. Com o backend rodando, abra no navegador:
   ```
   http://localhost:8000
   ```

2. Navegue pelas páginas:
   - **Login**: `http://localhost:8000/pages/login.html`
   - **Dashboard**: `http://localhost:8000/pages/dashboard.html`
   - **Clientes**: `http://localhost:8000/pages/clientes.html`
   - **Financeiro**: `http://localhost:8000/pages/financeiro.html`
   - **Jurídico**: `http://localhost:8000/pages/juridico.html`
   - **Notas Fiscais**: `http://localhost:8000/pages/notas-fiscais.html`
   - **Relatórios**: `http://localhost:8000/pages/relatorios.html`

### Método 2: Servidor Estático Separado (Opcional)

```powershell
# Em um terminal separado, na raiz do projeto:
python -m http.server 5173 --directory frontend
```

Acesse: `http://localhost:5173`

**Nota**: Certifique-se de que `frontend/src/js/config.js` aponta para:
```javascript
API_BASE: 'http://localhost:8000/api'
```

---

## 🔌 3. Testando Endpoints da API

### A. Usando Swagger UI (Mais Fácil)

1. Acesse: **http://localhost:8000/docs**
2. Explore os endpoints organizados por tags:
   - 🔐 **auth** - Login e autenticação
   - 👥 **clientes** - CRUD de clientes e contratos
   - 💰 **financeiro** - Lançamentos, fluxo de caixa, indicadores
   - 📊 **contabilidade** - DREs, obrigações acessórias
   - ⚖️ **juridico** - Processos, andamentos, audiências
   - 🏥 **health** - Health check

3. Clique em um endpoint → "Try it out" → Preencha os parâmetros → "Execute"

### B. Usando curl (Terminal)

#### 🔐 Autenticação

```powershell
# Login (retorna token de desenvolvimento)
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"admin@contabiliza.ia\",\"senha\":\"dev123\"}'

# Verificar usuário autenticado
curl "http://localhost:8000/api/auth/me" `
  -H "Authorization: Bearer dev-token"
```

#### 👥 Clientes

```powershell
# Listar clientes
curl "http://localhost:8000/api/clientes/?limit=10"

# Criar cliente
curl -X POST "http://localhost:8000/api/clientes/" `
  -H "Content-Type: application/json" `
  -d '{
    \"nome_razao_social\": \"Empresa Teste LTDA\",
    \"cnpj_cpf\": \"12345678901234\",
    \"tipo_pessoa\": \"J\",
    \"email\": \"contato@empresateste.com\",
    \"telefone\": \"11987654321\",
    \"regime_tributario\": \"Simples Nacional\"
  }'

# Obter cliente específico (substitua {id} pelo ID retornado)
curl "http://localhost:8000/api/clientes/{id}"

# Criar contrato para cliente
curl -X POST "http://localhost:8000/api/clientes/{id}/contratos" `
  -H "Content-Type: application/json" `
  -d '{
    \"tipo_servico\": \"contabil\",
    \"valor_mensal\": 500.00,
    \"data_inicio\": \"2025-01-01\",
    \"dia_vencimento\": 10,
    \"cliente_id\": \"{id}\"
  }'
```

#### 💰 Financeiro

```powershell
# Listar lançamentos
curl "http://localhost:8000/api/financeiro/lancamentos/?limit=10"

# Criar lançamento (receita)
curl -X POST "http://localhost:8000/api/financeiro/lancamentos/" `
  -H "Content-Type: application/json" `
  -d '{
    \"tipo\": \"receita\",
    \"descricao\": \"Honorários Cliente X\",
    \"valor\": 1500.00,
    \"data_vencimento\": \"2025-12-10\",
    \"categoria\": \"honorarios\",
    \"cliente_id\": \"{id_cliente}\"
  }'

# Fluxo de caixa (período)
curl "http://localhost:8000/api/financeiro/fluxo-caixa/?data_inicio=2025-01-01&data_fim=2025-12-31"

# Dashboard financeiro
curl "http://localhost:8000/api/financeiro/dashboard/?periodo=mensal"
```

#### 📊 Contabilidade

```powershell
# Listar DREs
curl "http://localhost:8000/api/contabil/dre/?ano=2025"

# Criar DRE
curl -X POST "http://localhost:8000/api/contabil/dre/" `
  -H "Content-Type: application/json" `
  -d '{
    \"cliente_id\": \"{id_cliente}\",
    \"mes_referencia\": \"2025-01-01\",
    \"receita_bruta\": 50000.00,
    \"deducoes\": 5000.00,
    \"custos\": 15000.00,
    \"despesas_operacionais\": 10000.00
  }'

# Listar obrigações acessórias
curl "http://localhost:8000/api/contabil/obrigacoes/?status=pendente"

# Relatório de obrigações pendentes
curl "http://localhost:8000/api/contabil/relatorios/obrigacoes-pendentes?dias_para_vencer=7"
```

#### ⚖️ Jurídico

```powershell
# Listar processos
curl "http://localhost:8000/api/juridico/processos/?status=ativo&limit=10"

# Criar processo
curl -X POST "http://localhost:8000/api/juridico/processos/" `
  -H "Content-Type: application/json" `
  -d '{
    \"cliente_id\": \"{id_cliente}\",
    \"numero_processo\": \"1234567-89.2025.8.26.0100\",
    \"assunto\": \"Ação de Cobrança\",
    \"tipo_acao\": \"civel\",
    \"valor_causa\": 10000.00
  }'

# Dashboard jurídico
curl "http://localhost:8000/api/juridico/dashboard/"
```

### C. Usando Postman / Thunder Client

1. Importe a coleção:
   - URL base: `http://localhost:8000`
   - Prefixo: `/api`

2. Configure um ambiente:
   ```json
   {
     "baseUrl": "http://localhost:8000",
     "token": "dev-token"
   }
   ```

3. Use `{{baseUrl}}/api/clientes/` nas requisições

---

## 🎯 4. Fluxo de Teste Completo (Frontend + Backend)

### Cenário: Cadastrar Cliente e Criar Contrato

#### Passo 1: Login via Frontend

1. Acesse: `http://localhost:8000/pages/login.html`
2. Credenciais de desenvolvimento:
   - **Email**: qualquer email válido
   - **Senha**: qualquer senha
3. Clique em "Entrar"
4. Você será redirecionado para o dashboard

#### Passo 2: Cadastrar Cliente

1. No menu lateral, clique em **"Clientes"**
2. Clique em **"Novo Cliente"**
3. Preencha os dados:
   - Nome/Razão Social
   - CNPJ/CPF
   - Tipo de Pessoa (F ou J)
   - Email, Telefone
   - Regime Tributário
4. Clique em **"Salvar"**
5. Verifique se o cliente aparece na lista

#### Passo 3: Criar Contrato

1. Na lista de clientes, clique em **"Ver Contratos"** do cliente criado
2. Clique em **"Novo Contrato"**
3. Preencha:
   - Tipo de Serviço (Contábil, Jurídico ou Ambos)
   - Valor Mensal
   - Data de Início
   - Dia de Vencimento
4. Clique em **"Salvar"**

#### Passo 4: Verificar Dados via API

```powershell
# Listar clientes (deve aparecer o cliente criado)
curl "http://localhost:8000/api/clientes/"

# Listar contratos do cliente
curl "http://localhost:8000/api/clientes/{id_cliente}/contratos"
```

---

## 🔍 5. Validações e Checklist

### ✅ Backend

- [ ] Servidor inicia sem erros
- [ ] `/health` retorna status 200
- [ ] `/docs` exibe Swagger UI
- [ ] `/openapi.json` retorna schema válido
- [ ] CORS permite requisições do frontend
- [ ] Banco de dados cria 16 tabelas
- [ ] Logs não mostram avisos de importação

### ✅ Frontend

- [ ] Página de login carrega
- [ ] Login redireciona para dashboard
- [ ] Menu lateral navega entre páginas
- [ ] Formulários de cadastro funcionam
- [ ] Tabelas carregam dados da API
- [ ] Mensagens de erro são exibidas (campo vazio, etc.)
- [ ] Console do navegador não mostra erros JS

### ✅ Integração

- [ ] Login no frontend chama `/api/auth/login`
- [ ] Requisições incluem token no header `Authorization`
- [ ] Dados cadastrados no frontend aparecem na API
- [ ] Filtros e paginação funcionam
- [ ] Botões de ação (editar, excluir) chamam endpoints corretos

---

## 🐛 6. Troubleshooting

### Backend não inicia

```powershell
# Verificar porta 8000 ocupada
netstat -ano | findstr :8000

# Parar processos Python
Get-Process python | Stop-Process -Force

# Verificar dependências
pip list | findstr -i "fastapi uvicorn sqlalchemy"
```

### Frontend não carrega

1. Verifique se o backend está rodando: `curl http://localhost:8000/health`
2. Abra o DevTools do navegador (F12) → aba Console
3. Verifique erros de CORS ou 404

### Erro 404 em endpoints

- Confirme que o prefixo `/api` está nas requisições
- Exemplo: `/api/clientes/` e não `/clientes/`

### Banco de dados vazio

```powershell
# Resetar banco (cuidado: apaga todos os dados!)
python reset_database.py

# Verificar tabelas
python backend/scripts/check_tables.py
```

---

## 📊 7. Testando com Dados de Exemplo

Execute o script de população de dados (se existir):

```powershell
python backend/scripts/populate_sample_data.py
```

Ou insira manualmente via Swagger UI:
1. Acesse http://localhost:8000/docs
2. Use os endpoints POST de cada recurso
3. Copie os exemplos do schema Pydantic

---

## 🎓 8. Próximos Passos (Após Validação)

Quando o projeto estiver testado e funcionando:

1. **Integração de Automações**:
   - Validação de CNPJ/CPF via API externa
   - Consulta de NFe via SEFAZ
   - Envio de emails/notificações

2. **Segurança**:
   - Implementar autenticação JWT real (substituir `dev-token`)
   - Hashear senhas com bcrypt
   - Adicionar rate limiting

3. **Deploy**:
   - Configurar variáveis de ambiente de produção
   - Usar PostgreSQL em vez de SQLite
   - Deploy no Heroku, Railway ou DigitalOcean

---

## 📞 Suporte

- Documentação da API: http://localhost:8000/docs
- Logs do backend: Console onde `run.py` está rodando
- DevTools do navegador: F12 → Console/Network

**Bons testes! 🚀**
