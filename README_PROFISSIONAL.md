# 💼 Contabiliza.IA

<div align="center">

![Logo](https://img.shields.io/badge/Contabiliza-IA-4F46E5?style=for-the-badge&logo=robot&logoColor=white)

**Sistema de Gestão Contábil com Inteligência Artificial**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP-orange?style=flat)]()

[🚀 Demo](#-demo) • [📖 Documentação](#-documentação) • [💡 Features](#-features) • [🔧 Instalação](#-instalação)

</div>

---

## 📋 Sobre o Projeto

**Contabiliza.IA** é uma plataforma SaaS completa para gestão contábil, fiscal, financeira e jurídica, com **Inteligência Artificial integrada** para automação de processos repetitivos.

### 🎯 Objetivos

- ✅ **Reduzir em 70%** o tempo gasto em tarefas manuais
- ✅ **Eliminar 95%** dos erros humanos em lançamentos
- ✅ **Aumentar em 300%** a produtividade de escritórios contábeis
- ✅ **Visibilidade 100%** em tempo real da situação fiscal

---

## ✨ Features

### 🏢 **Gestão de Clientes**
- [x] Cadastro completo (Pessoa Física e Jurídica)
- [x] Histórico de relacionamento
- [x] Upload de documentos
- [ ] Portal do cliente (self-service)

### 💰 **Módulo Financeiro**
- [x] Lançamentos (receitas e despesas)
- [x] Fluxo de caixa com gráficos interativos
- [x] Categorização automática
- [x] Relatórios DRE gerencial
- [ ] Conciliação bancária automática (OFX/API)

### 📄 **Notas Fiscais Eletrônicas**
- [x] Importação de XML (NFe/NFSe)
- [x] Visualização de itens e impostos
- [x] Cálculo de ICMS, IPI, PIS, COFINS
- [ ] Integração SEFAZ (autorização em tempo real)
- [ ] Geração de DANFE

### 📊 **Contabilidade**
- [x] Dashboard com indicadores em tempo real
- [x] Obrigações acessórias (SPED, DCTF, DEFIS)
- [x] Alertas de vencimentos
- [ ] Geração automática de arquivos SPED
- [ ] eSocial integrado

### ⚖️ **Módulo Jurídico**
- [x] Controle de processos (trabalhista, tributário, cível)
- [x] Calendário de audiências
- [x] Acompanhamento de andamentos
- [ ] Integração PJe (Justiça Eletrônica)
- [ ] Alertas de prazos processuais via WhatsApp

### 🤖 **Inteligência Artificial**
- [ ] Classificação automática de lançamentos (ML)
- [ ] Previsão de fluxo de caixa (forecasting)
- [ ] Detecção de anomalias fiscais
- [ ] Assistente virtual conversacional (ChatGPT)
- [ ] Análise preditiva de risco tributário

---

## 🚀 Demo

### 🖼️ Screenshots

#### Landing Page
![Index](docs/screenshots/index.png)
*Landing page com animação Vanta.js e design moderno*

#### Tela de Login
![Login](docs/screenshots/login.png)
*Autenticação com animação de fundo 3D*

#### Dashboard Principal
![Dashboard](docs/screenshots/dashboard.png)
*Métricas em tempo real com gráficos Chart.js*

#### Gestão de Clientes
![Clientes](docs/screenshots/clientes.png)
*CRUD completo com validação de CNPJ/CPF*

#### Módulo Financeiro
![Financeiro](docs/screenshots/financeiro.png)
*Fluxo de caixa e DRE com gráficos interativos*

### 🎥 Vídeo Demo
> Vídeo de 3 minutos demonstrando funcionalidades principais

---

## 🏗️ Arquitetura

### Stack Tecnológico

#### **Backend**
- **Framework:** FastAPI 0.104+ (Python 3.11)
- **Database:** SQLite (MVP) → PostgreSQL (produção)
- **ORM:** SQLAlchemy 2.0
- **Autenticação:** JWT (JSON Web Tokens)
- **Validação:** Pydantic V2
- **API Docs:** Swagger/OpenAPI automático

#### **Frontend**
- **Framework:** HTML5 + Vanilla JavaScript
- **CSS:** Tailwind CSS 3.x (utility-first)
- **Gráficos:** Chart.js 4.x
- **Animações:** Vanta.js (Three.js)
- **Ícones:** Font Awesome 6.x

#### **DevOps**
- **Server:** Uvicorn (ASGI)
- **Deploy:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana (futuro)

### 📂 Estrutura de Pastas

```
Contabiliza.IA/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entrada da aplicação
│   │   ├── models/              # Modelos SQLAlchemy
│   │   │   ├── clientes.py
│   │   │   ├── financeiro.py
│   │   │   ├── notas_fiscais.py
│   │   │   └── ...
│   │   ├── routes/              # Endpoints da API
│   │   │   ├── auth.py
│   │   │   ├── clientes.py
│   │   │   └── ...
│   │   ├── schemas/             # Validação Pydantic
│   │   ├── services/            # Lógica de negócio
│   │   └── utils/               # Helpers
│   ├── database/                # SQLite database
│   └── docker-compose.yml
├── frontend/
│   ├── index.html               # Landing page
│   ├── pages/                   # Páginas da aplicação
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── clientes.html
│   │   └── ...
│   └── src/
│       ├── js/                  # JavaScript modules
│       └── styles/              # CSS customizado
├── docs/                        # Documentação
├── scripts/                     # Scripts utilitários
├── populate_demo_data.py        # Dados de demonstração
└── README.md
```

### 🔗 API Endpoints

```
POST   /api/auth/login           # Autenticação
GET    /api/dashboard/           # Métricas gerais
GET    /api/clientes/            # Listar clientes
POST   /api/clientes/            # Criar cliente
GET    /api/financeiro/lancamentos/  # Listar lançamentos
POST   /api/financeiro/lancamentos/  # Criar lançamento
GET    /api/notas-fiscais/       # Listar NFes
POST   /api/notas-fiscais/importar-xml/  # Importar XML
GET    /api/juridico/processos/  # Listar processos
```

Documentação completa: `http://localhost:8000/docs`

---

## 🔧 Instalação

### Pré-requisitos
- Python 3.11+
- Node.js 18+ (opcional, para build do frontend)
- Git

### 1️⃣ Clone o Repositório
```bash
git clone https://github.com/seu-usuario/contabiliza-ia.git
cd contabiliza-ia
```

### 2️⃣ Crie o Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as Variáveis de Ambiente
```bash
cp backend/.env.example backend/.env
```

Edite o arquivo `.env` com suas configurações:
```env
SECRET_KEY=seu_secret_key_aqui
DATABASE_URL=sqlite:///./database/contabiliza_ia.db
DEBUG=True
```

### 5️⃣ Inicialize o Banco de Dados
```bash
python backend/scripts/init_database.py
```

### 6️⃣ (Opcional) Popule com Dados Demo
```bash
python populate_demo_data.py
```

### 7️⃣ Execute o Servidor
```bash
python run.py
```

Acesse: **http://localhost:8000**

### 🐳 Docker (Alternativa)
```bash
cd backend
docker-compose up -d
```

---

## 👨‍💻 Desenvolvimento

### Credenciais de Teste
```
Email: admin@test.com
Senha: 123456
```

### Executar Testes
```bash
pytest tests/ -v
```

### Linter e Formatação
```bash
# Pylint
pylint backend/app/

# Black (formatador)
black backend/app/

# isort (organizar imports)
isort backend/app/
```

### Gerar Documentação da API
```bash
# Acesse automaticamente em:
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

---

## 📊 Roadmap

### ✅ **Versão 0.1.0 (MVP - Atual)**
- [x] Landing page com animações
- [x] Sistema de autenticação
- [x] CRUD de clientes
- [x] Módulo financeiro básico
- [x] Dashboard com gráficos
- [x] Importação de NFe (XML)

### 🚧 **Versão 0.2.0 (Q1 2026)**
- [ ] Integração bancária (OFX/API)
- [ ] IA para classificação de lançamentos
- [ ] Geração automática de SPED
- [ ] App mobile (React Native)
- [ ] Notificações WhatsApp (Twilio)

### 📅 **Versão 1.0.0 (Q2 2026)**
- [ ] Assistente virtual (ChatGPT-4)
- [ ] Integração SEFAZ (autorização NFe)
- [ ] Portal do cliente (self-service)
- [ ] Marketplace de integrações
- [ ] Multi-tenancy (SaaS completo)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### 📋 Diretrizes
- Código em **inglês** (comentários em português OK)
- Seguir **PEP 8** (Python)
- Testes unitários para novas features
- Documentar endpoints na docstring

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Contato

**Contabiliza.IA**

- 📧 Email: contato@contabiliza.ia
- 📱 WhatsApp: (11) 9999-9999
- 🌐 Website: [www.contabiliza.ia](https://contabiliza.ia)
- 💼 LinkedIn: [/company/contabiliza-ia](https://linkedin.com/company/contabiliza-ia)

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Chart.js](https://www.chartjs.org/) - Gráficos interativos
- [Vanta.js](https://www.vantajs.com/) - Animações 3D
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS

---

<div align="center">

**Feito com ❤️ para modernizar a contabilidade brasileira**

⭐ **Dê uma estrela se este projeto te ajudou!** ⭐

</div>
