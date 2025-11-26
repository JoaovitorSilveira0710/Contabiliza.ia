# 📚 Guia dos Scripts de População

## 🎯 Visão Geral

Temos 3 scripts para popular o banco de dados:

1. **`populate_all.py`** ⭐ **RECOMENDADO** - Script completo e robusto
2. **`populate_simple.py`** - Apenas clientes e lançamentos (básico)
3. **`populate_extra_data.py`** - Adiciona notas fiscais e processos

---

## ⭐ Script Recomendado: `populate_all.py`

### ✅ Vantagens

- **Completo**: Cria todos os dados em uma única execução
- **Seguro**: Valida categorias e campos antes de inserir
- **Inteligente**: Verifica dados existentes antes de sobrescrever
- **Robusto**: Tratamento de erros detalhado com rollback
- **Interativo**: Pergunta antes de apagar dados existentes

### 📝 Como Usar

```powershell
# Ativar ambiente virtual
& "venv/Scripts/Activate.ps1"

# Executar script
python populate_all.py
```

### 📊 O que Cria

- **5 Clientes** (4 PJ + 1 PF com diferentes regimes tributários)
- **100 Lançamentos Financeiros** (receitas e despesas nos últimos 6 meses)
- **20 Notas Fiscais** (4 por cliente, mix de situações)
- **10 Processos Jurídicos** (2 para os primeiros 5 clientes)

---

## 🔧 Problemas Corrigidos

### ❌ Problema 1: Categoria Inválida

**Erro:**
```
CHECK constraint failed: check_categoria_lancamento
```

**Causa:**
- Script usava `'consultoria'` como categoria
- Modelo só aceita: `'honorarios'`, `'servicos'`, `'impostos'`, `'folha_pagamento'`, `'aluguel'`, `'telefonia'`, `'material'`, `'outros'`

**Solução:**
```python
# ❌ ERRADO
categorias_receita = ['honorarios', 'servicos', 'consultoria']

# ✅ CORRETO
categorias_receita = ['honorarios', 'servicos']
```

### ❌ Problema 2: Imports Não Resolvidos

**Erro (Pylance):**
```
Import "app.models.database" could not be resolved
```

**Causa:**
- Pylance não reconhece path dinâmico via `sys.path.append()`
- É apenas um **aviso estático**, o código funciona em runtime

**Solução:**
```python
# Melhor método de adicionar path
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Try-except para melhor feedback
try:
    from app.models.database import get_db, inicializar_banco_dados
    from app.models.clientes import Cliente
    # ... outros imports
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Certifique-se de estar executando do diretório raiz do projeto")
    sys.exit(1)
```

### ❌ Problema 3: Campo `numero_nota` vs `numero`

**Erro:**
```
TypeError: 'numero_nota' is an invalid keyword argument
```

**Causa:**
- Campo no modelo `NotaFiscal` é `numero`, não `numero_nota`

**Solução:**
```python
# ❌ ERRADO
nota = NotaFiscal(
    numero_nota="202401001",  # Campo não existe
    ...
)

# ✅ CORRETO
nota = NotaFiscal(
    numero="202401001",  # Campo correto
    ...
)
```

### ❌ Problema 4: Constraint `chave_acesso`

**Erro:**
```
CHECK constraint failed: chave_acesso length must be 44
```

**Causa:**
- Campo `chave_acesso` deve ter exatamente 44 caracteres OU ser NULL

**Solução:**
```python
# ✅ Usar None/NULL ao invés de string aleatória
nota = NotaFiscal(
    chave_acesso=None,  # Permite NULL
    ...
)
```

### ❌ Problema 5: Tipo de Pessoa Inválido

**Erro:**
```
CHECK constraint failed: tipo_pessoa IN ('F', 'J')
```

**Causa:**
- Scripts antigos usavam `'juridica'` ou `'fisica'`
- Modelo aceita apenas `'J'` (jurídica) ou `'F'` (física)

**Solução:**
```python
# ❌ ERRADO
tipo_pessoa = 'juridica'

# ✅ CORRETO
tipo_pessoa = 'J'  # ou 'F' para física
```

---

## 📋 Constraints e Validações

### Cliente

```python
tipo_pessoa: 'F' ou 'J'
regime_tributario: 'Simples Nacional', 'Lucro Presumido', 'Lucro Real', 'MEI'
cnpj_cpf: UNIQUE (não pode repetir)
```

### LancamentoFinanceiro

```python
tipo: 'receita' ou 'despesa'
status: 'pendente', 'pago', 'atrasado', 'cancelado'
categoria: 'honorarios', 'servicos', 'impostos', 'folha_pagamento', 
           'aluguel', 'telefonia', 'material', 'outros'
forma_pagamento: 'dinheiro', 'pix', 'transferencia', 'cartao_credito',
                 'cartao_debito', 'boleto'
valor: > 0 (deve ser positivo)
```

### NotaFiscal

```python
numero: String (não numero_nota)
tipo: 'entrada' ou 'saida'
modelo: 'nfe', 'nfse', 'nfce'
situacao: 'autorizada', 'cancelada', 'pendente', 'rejeitada'
chave_acesso: length = 44 ou NULL
valor_total: = valor_produtos + valor_servicos
```

### Processo

```python
status: 'ativo', 'suspenso', 'encerrado', 'arquivado'
numero_processo: formato CNJ recomendado
```

---

## 🚀 Sequência Recomendada

### Opção 1: Tudo de Uma Vez (Recomendado)

```powershell
python populate_all.py
```

### Opção 2: Passo a Passo

```powershell
# 1. Resetar banco (se necessário)
python reset_database.py

# 2. Dados básicos
python populate_simple.py

# 3. Dados extras
python populate_extra_data.py
```

---

## 🔍 Verificar Dados

```powershell
# Via Python
python -c "import sys; from pathlib import Path; sys.path.append(str(Path.cwd() / 'backend')); from app.models.database import get_db, inicializar_banco_dados; from app.models.clientes import Cliente; from app.models.financeiro import LancamentoFinanceiro; from app.models.notas_fiscais import NotaFiscal; from app.models.juridico import Processo; inicializar_banco_dados(); db = next(get_db()); print(f'Clientes: {db.query(Cliente).count()}'); print(f'Lançamentos: {db.query(LancamentoFinanceiro).count()}'); print(f'Notas: {db.query(NotaFiscal).count()}'); print(f'Processos: {db.query(Processo).count()}')"

# Via SQLite CLI (se tiver instalado)
sqlite3 backend/database/contabiliza_ia.db "SELECT COUNT(*) FROM clientes;"
```

---

## 📊 Dados de Demonstração

### Clientes Criados

1. **Tech Inovação Ltda** - CNPJ 12.345.678/0001-90 (Lucro Real)
2. **Comércio Silva & Cia** - CNPJ 23.456.789/0001-81 (Simples Nacional)
3. **Consultoria Estratégica ME** - CNPJ 34.567.890/0001-72 (Lucro Presumido)
4. **Indústria MetalTech S.A.** - CNPJ 45.678.901/0001-63 (Lucro Real)
5. **João Carlos Oliveira** - CPF 123.456.789-00 (MEI)

### Valores Típicos (variam a cada execução)

- **Receitas**: ~R$ 350.000
- **Despesas**: ~R$ 380.000
- **Notas Fiscais**: ~R$ 250.000
- **Causas Judiciais**: ~R$ 2.500.000

---

## ⚠️ Avisos Importantes

### Pylance Warnings

Os avisos do Pylance sobre imports não resolvidos são **normais** e **não impedem execução**:

```
Import "app.models.database" could not be resolved
```

**Por quê?**
- Pylance analisa código estaticamente
- Não consegue ver `sys.path.append()` dinâmico
- Em runtime o Python encontra os módulos corretamente

**Solução:** Ignore os avisos ou configure `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": [
    "./backend"
  ]
}
```

### Dados Existentes

O script `populate_all.py` **sempre pergunta** antes de sobrescrever:

```
⚠️  ATENÇÃO: O banco já possui dados!
❓ Deseja SOBRESCREVER todos os dados? (sim/não):
```

- Digite `sim` para limpar e recriar
- Digite `não` para cancelar

---

## 🐛 Troubleshooting

### "Module not found" ao executar

```powershell
# Certifique-se de estar no diretório correto
cd "c:\Users\dudab\OneDrive\Área de Trabalho\Contabiliza.IA"

# Ative o ambiente virtual
& "venv/Scripts/Activate.ps1"

# Execute novamente
python populate_all.py
```

### "Database locked"

```powershell
# Pare o servidor FastAPI se estiver rodando
# (Ctrl+C no terminal do servidor)

# Execute novamente
python populate_all.py
```

### Erro de constraint

Sempre confira se os valores estão nas listas permitidas:
- Veja seção **"Constraints e Validações"** acima
- Leia mensagem de erro completa para identificar qual campo

---

## 📝 Conclusão

✅ **Use `populate_all.py`** para população completa e segura

✅ **Ignore avisos do Pylance** - são falsos positivos

✅ **Sempre confira constraints** antes de adicionar novos dados

✅ **Use modo interativo** para evitar sobrescrever dados por engano

---

**Última atualização:** 12/11/2025  
**Versão:** 1.0
