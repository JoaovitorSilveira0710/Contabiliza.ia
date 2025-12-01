<div align="center">

# 🧾 Contabiliza.IA

Sistema integrado de gestão contábil, financeira, fiscal e jurídica.

![Status](https://img.shields.io/badge/status-MVP-orange)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Django](https://img.shields.io/badge/Django-5.1+-green)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 📌 Visão Geral
O **Contabiliza.IA** centraliza rotinas de escritórios contábeis (clientes, lançamentos financeiros, obrigações, processos jurídicos e notas fiscais) oferecendo métricas e alertas em tempo real para redução de tarefas repetitivas.

### Principais Módulos
- **Clientes** (PF/PJ, contratos, situação)
- **Financeiro** (lançamentos, fluxo de caixa, DRE gerencial)
- **Contábil** (obrigações, prazos, indicadores)
- **Jurídico** (processos, prazos, audiências, andamentos)
- **Notas Fiscais** (importação, gestão, impostos)
- **Documentos** (upload, armazenamento, gestão)
- **Relatórios** (consolidados, PDF, alertas inteligentes)

---

## 🗃️ Estrutura do Projeto
```
Contabiliza.IA/
├── django_backend/          # Backend Django
│   ├── core/                # ACL, usuários, serviços
│   │   ├── models.py        # User, Role
│   │   ├── services/        # PDF generator
│   │   └── management/      # Comandos (backup)
│   ├── clients/             # Clientes e contratos
│   ├── invoices/            # Notas fiscais
│   ├── documents/           # Gestão de documentos
│   ├── financial/           # Financeiro
│   ├── accounting/          # Contabilidade
│   └── contabiliza_backend/ # Settings e URLs
├── frontend/                # Frontend (HTML/JS)
│   ├── pages/               # Dashboard, clientes, etc.
│   └── src/                 # JavaScript e estilos
├── storage/                 # Arquivos enviados
├── backups/                 # Backups automáticos
├── venv/                    # Ambiente virtual Python
├── run.py                   # Script de inicialização
├── start_django.ps1         # Iniciar para rede local
└── requirements.txt         # Dependências Python
```

---

## 🚀 Instalação Rápida
```powershell
git clone https://github.com/JoaovitorSilveira0710/Contabiliza.ia.git
cd Contabiliza.IA
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

**O servidor estará disponível em:**
- API REST: `http://localhost:8000/api/`
- Painel Admin: `http://localhost:8000/admin/`

---

## 🔌 Principais Endpoints da API

| Área | Endpoint | Descrição |
|------|----------|-----------|
| Usuários | GET/POST `/api/users/` | Gerenciar usuários |
| Papéis | GET/POST `/api/roles/` | Papéis e permissões |
| Clientes | GET/POST `/api/clients/` | Gestão de clientes |
| Contratos | GET/POST `/api/contracts/` | Contratos de serviço |
| Notas Fiscais | GET/POST `/api/invoices/` | Notas fiscais |
| Documentos | GET/POST `/api/documents/` | Upload e gestão |
| Métricas | GET/POST `/api/dashboard-metrics/` | Dashboard |
| Auditoria | GET/POST `/api/audits/` | Logs de auditoria |

---

## 🔐 Autenticação

A API usa **Basic Authentication**. Exemplo de teste:

```powershell
$pair='admin:admin12345'
$b64=[Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
$Headers=@{Authorization=("Basic "+$b64)}
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/clients/' -Headers $Headers
```

---

## 🛠️ Comandos Úteis

**Criar superusuário:**
```powershell
cd django_backend
python manage.py createsuperuser
```

**Fazer backup do banco de dados:**
```powershell
cd django_backend
python manage.py backup_database
```

**Aplicar migrações manualmente:**
```powershell
cd django_backend
python manage.py makemigrations
python manage.py migrate
```

**Iniciar servidor para rede local:**
```powershell
.\start_django.ps1
```

---

## 🧪 Recursos Implementados

✅ Framework Django com padrão MVC  
✅ ACL (Controle de acesso por papéis)  
✅ Autenticação com Bcrypt  
✅ Storage de arquivos (caminho no BD, arquivo em disco)  
✅ Geração de PDF (notas fiscais, relatórios)  
✅ Mecanismo de backup automático  
✅ Código em inglês, textos em português  
✅ API RESTful completa com Django REST Framework  

---

## 🛠️ Tecnologias

**Backend:** Django 5.1, Django REST Framework  
**Banco de Dados:** SQLite (dev) / PostgreSQL (prod)  
**Autenticação:** Bcrypt  
**Geração de PDF:** ReportLab  
**Storage:** Sistema de arquivos local  
**Frontend:** HTML5, JavaScript, TailwindCSS  

---

## 📊 Roadmap

**Curto prazo:** JWT authentication, melhorias em NFe  
**Médio prazo:** Integrações externas (SEFAZ, Receita), previsões financeiras  
**Longo prazo:** Multi-tenant, IA preditiva, automações avançadas  

---

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| Porta 8000 ocupada | `Get-Process python \| Stop-Process -Force` |
| Dependência faltando | `pip install -r requirements.txt` |
| Erro de migração | `cd django_backend; python manage.py migrate` |
| Erro CORS | Limpar cache navegador / reiniciar servidor |

---

## 📖 Documentação Técnica

Consulte [DJANGO_IMPLEMENTATION.md](DJANGO_IMPLEMENTATION.md) para detalhes técnicos completos da implementação.

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

## 👤 Autor

**Nome:** Joao Vitor Cruz da Silveira  
**Email:** joaovitor2401@gmail.com  
**Telefone:** +55 42 99166-2179

---

**Contabiliza.IA – Foco em eficiência operacional.**

