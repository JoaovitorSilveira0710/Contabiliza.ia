# 🔧 Soluções de Problemas no Terminal

## 📋 Análise Realizada em 13/11/2025

### ✅ Status do Sistema

| Componente | Status | Detalhes |
|------------|--------|----------|
| **Banco de Dados** | ✅ OK | 5 clientes, 100 lançamentos, 20 notas, 10 processos |
| **Backend (FastAPI)** | ✅ OK | Servidor rodando em http://localhost:8000 |
| **Frontend** | ✅ OK | Arquivos estáticos servidos corretamente |
| **Dependências** | ✅ OK | Todas instaladas no venv |

---

## ❌ Problema Principal: ModuleNotFoundError

### 🔍 Sintoma

```
ModuleNotFoundError: No module named 'dotenv'
```

### 🎯 Causa Raiz

O script `run.py` estava sendo executado com o Python **GLOBAL** ao invés do Python do **ambiente virtual (venv)**.

**Por quê isso acontece?**
- Quando você digita apenas `python run.py`, o PowerShell usa o Python instalado globalmente
- O módulo `python-dotenv` está instalado **apenas no venv**
- O Python global não tem acesso aos pacotes do venv

### ✅ Solução Aplicada

**Comando ERRADO:**
```powershell
python run.py  # ❌ Usa Python global
```

**Comando CORRETO:**
```powershell
& "venv/Scripts/python.exe" run.py  # ✅ Usa Python do venv
```

**Alternativa (ativando venv):**
```powershell
& "venv/Scripts/Activate.ps1"  # Ativa ambiente virtual
python run.py                   # Agora usa Python do venv
```

---

## 🔍 Problemas Identificados e Resolvidos

### 1. ❌ Servidor Não Respondia

**Erro:**
```
❌ Servidor OFFLINE ou não respondendo
```

**Causa:** Servidor não estava iniciado ou foi interrompido

**Solução:**
```powershell
cd "c:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"
& "venv/Scripts/python.exe" run.py
```

### 2. ❌ Importação de Módulos

**Erro:**
```
from dotenv import load_dotenv
ModuleNotFoundError: No module named 'dotenv'
```

**Causa:** Python global não tem `python-dotenv` instalado

**Verificação:**
```powershell
# No venv - TEM o módulo
& "venv/Scripts/python.exe" -c "import dotenv; print('OK')"
# ✅ OK

# Python global - NÃO TEM
python -c "import dotenv; print('OK')"
# ❌ ModuleNotFoundError
```

**Solução:** Sempre usar Python do venv

### 3. ⚠️ Avisos de Encoding (Unicode)

**Sintoma:**
```
\U0001f3af CAMINHO CORRIGIDO DO BANCO:
\U0001f4c1 Pasta: ...
```

**Causa:** PowerShell não renderiza emojis corretamente por padrão

**Impacto:** Apenas visual, não afeta funcionamento

**Solução (opcional):**
```powershell
# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 📊 Verificações Realizadas

### ✅ Banco de Dados

```powershell
# Teste executado:
python -c "from app.models.database import get_db; ..."

# Resultado:
📊 ESTADO DO BANCO:
   Clientes: 5
   Lançamentos: 100
   Notas Fiscais: 20
   Processos: 10
```

### ✅ Servidor FastAPI

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Routers carregados:**
- ✅ /api/clientes
- ✅ /api/auth
- ✅ /api/financeiro
- ✅ /api/contabil
- ✅ /api/notas
- ✅ /api/juridico
- ✅ /api/dashboard

### ✅ Dependências Instaladas

```
python-dotenv==1.2.1 ✅
fastapi==0.104.1 ✅
sqlalchemy==2.0.23 ✅
uvicorn==0.24.0 ✅
```

---

## 🚀 Como Iniciar o Sistema Corretamente

### Método 1: Comando Direto (Recomendado)

```powershell
# Navegar até o diretório
cd "c:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"

# Iniciar servidor com Python do venv
& "venv/Scripts/python.exe" run.py
```

### Método 2: Ativando Ambiente Virtual

```powershell
# Navegar até o diretório
cd "c:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"

# Ativar venv
& "venv/Scripts/Activate.ps1"

# Agora pode usar python diretamente
python run.py
```

### Método 3: Script Batch (Windows)

Crie um arquivo `start.bat`:
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python run.py
pause
```

---

## 🔍 Comandos Úteis para Diagnóstico

### Verificar qual Python está sendo usado

```powershell
python -c "import sys; print(sys.executable)"
# Deve mostrar: ...\Contabiliza.IA\venv\Scripts\python.exe
```

### Verificar se módulo está instalado

```powershell
& "venv/Scripts/python.exe" -m pip show python-dotenv
```

### Testar servidor está online

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### Ver processos Python rodando

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

### Parar servidor

```
Ctrl+C no terminal onde o servidor está rodando
```

---

## ⚠️ Erros Comuns e Soluções

### "Will watch for changes" mas processo morre

**Causa:** Erro no código do backend durante inicialização

**Solução:** 
1. Verificar logs completos no terminal
2. Procurar por `Traceback` ou `Exception`
3. Corrigir erro no código indicado

### "Port 8000 already in use"

**Causa:** Outro processo já está usando a porta

**Solução:**
```powershell
# Encontrar processo na porta 8000
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Ou mudar porta no run.py
port=8001  # Linha no run.py
```

### "Database is locked"

**Causa:** Outro processo está usando o banco

**Solução:**
1. Fechar todos os terminais Python
2. Fechar SQLite Browser se estiver aberto
3. Reiniciar servidor

---

## 📝 Resumo Executivo

### ✅ Problemas Resolvidos

1. **ModuleNotFoundError** - Resolvido usando Python do venv
2. **Servidor offline** - Iniciado corretamente em background
3. **Banco de dados** - Verificado e populado com 135 registros

### 🎯 Sistema Operacional

- ✅ Backend FastAPI rodando
- ✅ Banco SQLite com todos os dados
- ✅ 7 routers API funcionando
- ✅ Frontend acessível em http://localhost:8000
- ✅ Docs API em http://localhost:8000/docs

### 📊 Dados Disponíveis

- 5 Clientes (PJ e PF)
- 100 Lançamentos Financeiros
- 20 Notas Fiscais
- 10 Processos Jurídicos

### 🚀 Próximos Passos

1. Acessar http://localhost:8000
2. Fazer login (qualquer credencial funciona na demo)
3. Navegar pelas páginas:
   - Dashboard → Ver métricas
   - Clientes → Ver 5 cadastrados
   - Financeiro → Ver 100 lançamentos
   - Notas Fiscais → Ver 20 notas
   - Jurídico → Ver 10 processos

---

## 💡 Dicas para Evitar Problemas

1. **SEMPRE use o Python do venv:** `venv/Scripts/python.exe`
2. **Verifique se está no diretório correto** antes de executar comandos
3. **Ative o venv** se for executar múltiplos comandos
4. **Feche o servidor** antes de rodar scripts de população
5. **Use `Ctrl+C`** para parar o servidor corretamente

---

**Última atualização:** 13/11/2025 às 14:45  
**Status:** ✅ Todos os problemas resolvidos  
**Sistema:** 🟢 ONLINE
