# Frontend - Contabiliza.IA

Frontend moderno e responsivo para a plataforma de gestão contábil inteligente, construído com **HTML5, CSS3 (Tailwind CSS) e JavaScript Vanilla**.

## Características

- Design responsivo (mobile-first)
- Autenticação com JWT
- Integração completa com API REST
- Dashboard interativo com gráficos
- CRUD de clientes, notas fiscais, financeiro
- Relatórios e análises
- Notificações em tempo real
- Sem dependências pesadas (Vanilla JS)
- Tailwind CSS para estilos
- Suporte a temas

## Estrutura do Projeto

```
frontend/
├── index.html                    # Landing page
├── pages/                        # Páginas da aplicação
│   ├── login.html               # Login
│   ├── dashboard.html           # Dashboard
│   ├── clientes.html            # Gestão de clientes
│   ├── notas-fiscais.html       # Notas fiscais
│   ├── financeiro.html          # Financeiro
│   ├── relatorios.html          # Relatórios
│   ├── contabil.html            # Contábil
│   └── juridico.html            # Jurídico
├── src/
│   ├── js/
│   │   ├── config.js            # Configuração global
│   │   ├── api-service.js       # Serviço de API
│   │   ├── ui-helper.js         # Funções UI auxiliares
│   │   └── helpers.js           # Funções auxiliares gerais
│   └── styles/
│       └── globals.css          # Estilos globais
├── dist/                        # CSS compilado
├── package.json                 # Dependências
├── tailwind.config.js           # Config Tailwind
└── INSTALACAO.md               # Guia de instalação

```

## Início Rápido

### 1. Instalar Dependências

```bash
cd frontend
npm install
```

### 2. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

Acesse: `http://localhost:3000`

### 3. Credenciais de Teste

```
Email: admin@test.com
Senha: 123456
```

## Configuração

### API Base URL

Edite `src/js/config.js`:

```javascript
const CONFIG = {
  API_BASE: 'http://localhost:8000/api',
  // ...
};
```

Ou crie um arquivo `.env.local`:

```env
API_BASE=http://localhost:8000/api
```

## Tecnologias Utilizadas

- **HTML5** - Estrutura semântica
- **CSS3 + Tailwind CSS** - Estilização
- **JavaScript ES6+** - Lógica da aplicação
- **Chart.js** - Gráficos interativos
- **Fetch API** - Requisições HTTP

## Funcionalidades Por Página

### Landing Page (`index.html`)
- Apresentação da plataforma
- Showcase de funcionalidades
- Call-to-action para login

### Login (`pages/login.html`)
- Autenticação com email e senha
- Validação de campos
- Redirecionamento pós-login

### Dashboard (`pages/dashboard.html`)
- Métricas principais (clientes, receita, notas)
- Gráficos de faturamento mensal
- Distribuição de serviços
- Tabela de clientes recentes

### Clientes (`pages/clientes.html`) *Em desenvolvimento*
- Listagem de clientes
- Criar novo cliente
- Editar cliente
- Excluir cliente
- Busca e filtros

### Notas Fiscais (`pages/notas-fiscais.html`) *Em desenvolvimento*
- Listagem de NF-e
- Importação de XML
- Consulta SEFAZ
- Autorização/Cancelamento

### Financeiro (`pages/financeiro.html`) *Em desenvolvimento*
- Lançamentos de receita/despesa
- Fluxo de caixa
- Projeções
- Análises

### Relatórios (`pages/relatorios.html`) *Em desenvolvimento*
- DRE (Demonstração de Resultado)
- Análises financeiras
- Exportação (PDF/Excel)

### Contábil (`pages/contabil.html`) *Em desenvolvimento*
- Balanço patrimonial
- Diário
- Razão

### Jurídico (`pages/juridico.html`) *Em desenvolvimento*
- Gestão de processos
- Andamentos
- Prazos e alertas

## Autenticação

### Fluxo de Login

```javascript
// 1. Usuário faz login
const response = await apiService.login(email, senha);

// 2. Token é salvo
UTILS.setToken(response.token);

// 3. Token é enviado em requisições
// Authorization: Bearer {token}

// 4. Para fazer logout
UTILS.clearToken();
```

### Proteção de Rotas

Todas as páginas verificam autenticação:

```javascript
if (!UTILS.isAuthenticated()) {
  window.location.href = '/pages/login.html';
}
```

## Componentes Tailwind

### Botões

```html
<button class="btn-primary">Primário</button>
<button class="btn-secondary">Secundário</button>
<button class="btn-danger">Perigo</button>
<button class="btn-success">Sucesso</button>
<button class="btn-sm">Pequeno</button>
<button class="btn-lg">Grande</button>
```

### Inputs

```html
<input class="input" placeholder="Normal" />
<input class="input input-dark" placeholder="Escuro" />
<input class="input" type="email" required />
```

### Cards

```html
<div class="glass-card">Card com efeito Glass</div>
<div class="glass-card-dark">Card escuro</div>
```

### Badges

```html
<span class="badge-success">Sucesso</span>
<span class="badge-warning">Aviso</span>
<span class="badge-danger">Perigo</span>
```

## Chamadas de API

### Clientes

```javascript
// Obter clientes
const clientes = await apiService.getClientes();

// Obter cliente por ID
const cliente = await apiService.getClienteById(1);

// Criar cliente
await apiService.criarCliente({
  nome: 'Empresa X',
  cnpj: '12.345.678/0001-90'
});

// Atualizar cliente
await apiService.atualizarCliente(1, {
  nome: 'Novo Nome'
});

// Excluir cliente
await apiService.excluirCliente(1);
```

### Notas Fiscais

```javascript
// Obter notas fiscais
const notas = await apiService.getNotasFiscais();

// Buscar notas na SEFAZ
await apiService.buscarNotasSEFAZ({
  cnpj: '12.345.678/0001-90',
  data_inicio: '2024-01-01'
});
```

### Financeiro

```javascript
// Obter lançamentos
const lancamentos = await apiService.getLancamentos();

// Criar lançamento
await apiService.criarLancamento({
  descricao: 'Receita de serviço',
  valor: 1000,
  data: '2024-11-11'
});

// Fluxo de caixa
const fluxo = await apiService.getFluxoCaixa('2024-01-01', '2024-12-31');
```

## Funções Utilitárias

### Config & Utils (`src/js/config.js`)

```javascript
// Formatação
UTILS.formatarReal(1000);        // R$ 1.000,00
UTILS.formatarData('2024-11-11'); // 11/11/2024
UTILS.formatarCNPJ('12345678000190'); // 12.345.678/0001-90

// Validação
UTILS.validarCNPJ('12.345.678/0001-90'); // true
UTILS.validarCPF('123.456.789-00');     // true

// Autenticação
UTILS.getToken();       // Token JWT
UTILS.setToken(token);  // Salvar token
UTILS.clearToken();     // Remover token
UTILS.isAuthenticated(); // true/false
```

### UI Helper (`src/js/ui-helper.js`)

```javascript
// Modais
UIHelper.showModal('meuModal');
UIHelper.closeModal('meuModal');

// Notificações
UIHelper.showNotification('Sucesso!', 'success');
UIHelper.showNotification('Erro!', 'error');

// Formulários
UIHelper.getFormData('meuFormulario');
UIHelper.populateForm('meuFormulario', dados);
UIHelper.clearForm('meuFormulario');

// UI
UIHelper.showButtonLoading('meuBotao');
UIHelper.hideButtonLoading('meuBotao');
UIHelper.copyToClipboard('texto');

// Utilitários
UIHelper.debounce(funcao, 300);
UIHelper.sleep(1000);
UIHelper.generateId();
```

## Responsividade

Todos os componentes são responsivos:

- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md/lg)
- **Desktop**: > 1024px (xl)

```html
<!-- Oculto em mobile, visível em tablet+ -->
<div class="hidden md:block">
  Visível apenas em tablets e desktops
</div>
```

## Dark Mode

Suportado via media queries:

```css
@media (prefers-color-scheme: dark) {
  body { @apply bg-gray-900 text-white; }
}
```

## SEO

Todas as páginas incluem:
- Meta tags apropriadas
- Titles descritivos
- Semantic HTML

## Performance

- Tailwind CSS compilado
- Lazy loading
- Caching com localStorage
- Debounce em buscas
- Minificação em produção

## Troubleshooting

### CORS Error
Certifique-se que o backend tem CORS habilitado.

### Token Expirado
Faça login novamente. O sistema redireciona automaticamente.

### Gráficos não carregam
Verifique se Chart.js está carregado e o backend retorna dados.

### Estilos não aparecem
Execute `npm run build:css` para compilar Tailwind.

## Licença

MIT - Veja LICENSE.md

## Suporte

Para problemas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com dedicação para Contabiliza.IA**

Última atualização: 11 de Novembro de 2025
