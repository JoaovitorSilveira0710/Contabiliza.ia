<div align="center">

# 🧾 Contabiliza.IA

Sistema integrado de gestão contábil, financeira, fiscal e jurídica.

![Status](https://img.shields.io/badge/status-MVP-orange)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 📌 Visão Geral
O **Contabiliza.IA** centraliza rotinas de escritórios (clientes, lançamentos financeiros, obrigações, processos jurídicos e notas fiscais) oferecendo métricas e alertas em tempo real para redução de tarefas repetitivas.

### Principais Módulos
- Clientes (PF/PJ, contratos, situação)
- Financeiro (lançamentos, fluxo de caixa, DRE gerencial)
- Contábil (obrigações, prazos, indicadores)
- Jurídico (processos, prazos, audiências, andamentos)
- Notas Fiscais (importação XML, impostos – expansão futura)
- Relatórios consolidados + alertas inteligentes

---

## 🗃️ Estrutura Simplificada
```
backend/
  app/
    main.py
    models/ (clientes, financeiro, contabil, juridico, notas_fiscais)
    routes/ (auth, clientes, financeiro, contabil, juridico, notas_fiscais)
    schemas/ services/ utils/
frontend/
  pages/ (dashboard, clientes, financeiro, juridico, notas-fiscais, relatorios, login)
  src/js/ (config, api-service, ui-helper)
  src/styles/ (globals.css)
scripts/ (init_database, backup, migrate)
populate_*.py (scripts de carga demo)
openapi.json (especificação da API)
```

---

## 🚀 Instalação Rápida
```powershell
git clone <repo-url>
cd Contabiliza.IA
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
python backend/scripts/init_database.py
python run.py
```
Acesse: `http://localhost:8000` • Docs: `/docs`

---

## 🔌 Principais Endpoints (resumo)
| Área | Exemplo |
|------|---------|
| Auth | POST /api/auth/login |
| Clientes | GET /api/clientes/ |
| Financeiro | GET /api/financeiro/lancamentos/ |
| Contábil | GET /api/contabil/obrigacoes/ |
| Jurídico | GET /api/juridico/processos/ |
| Notas Fiscais | GET /api/notas-fiscais/ |

Documentação completa: `/openapi.json` ou `/docs`.

---

## 🧪 Testes Rápidos
```powershell
python test_endpoints.py
```
Saída esperada inclui health, clientes, financeiro, contábil, jurídico.

---

## 🛠️ Tecnologias
Backend: FastAPI, SQLAlchemy, Pydantic, Uvicorn, SQLite (dev).  
Frontend: HTML + Tailwind + JavaScript puro.  
Utilidades: Scripts de povoamento, relatório automático, geração PDF (jsPDF).

---

## 📡 Scripts Úteis
```powershell
python populate_simple.py      # Dados mínimos
python populate_demo_data.py   # Dataset demonstrativo
python reset_database.py       # Limpa e recria base
python run.py                  # Inicia servidor
```

---

## 📊 Roadmap (Resumo)
Curto prazo: Ajustes de segurança (auth real, JWT), melhoria NFe.  
Médio prazo: Integrações externas (SEFAZ, Receita), previsões financeiras.  
Longo prazo: Multi-tenant, IA preditiva, automações avançadas.

---

## 🆘 Troubleshooting
| Problema | Solução |
|----------|---------|
| Porta 8000 ocupada | `Get-Process python | Stop-Process -Force` |
| Dependência faltando | `pip install -r requirements.txt` |
| Docs não abrem | Verificar `python run.py` ativo |
| Erro CORS | Limpar cache navegador / reiniciar servidor |

---

## 📄 Licença
MIT – consultar arquivo `LICENSE`.

---

## 👤 Autor
Nome: **Joao Vitor Cruz da Silveira**  
Email: **joaovitor2401@gmail.com**  
Telefone: **+55 42 99166-2179**

---

## ✂️ Limpeza de Documentação
Arquivos candidatos a remoção (após incorporação de conteúdo):  
`APRESENTACAO_EXECUTIVA.md`, `RESUMO_ENTREGA.md`, `SISTEMA_PRONTO.md`, `STATUS_PROJETO.md`, `REVISAO_BACKEND.md`, `VALIDACAO_FRONTEND.md`, `SCRIPT_DEMONSTRACAO.md`, `EMISSAO_NFE.md`, `README_PROFISSIONAL.md`.  
Manter ou resumir: `GUIA_TESTES.md`, `TUTORIAL_USO.md`, `GUIA_POPULATE_SCRIPTS.md` (podem migrar para wiki futura).

Confirme quais remover para aplicar.

---

**Contabiliza.IA – Foco em eficiência operacional.**

