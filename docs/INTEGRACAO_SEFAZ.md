# Integração com SEFAZ - Ambiente de Homologação

## 📋 Visão Geral

A SEFAZ (Secretaria da Fazenda) disponibiliza dois ambientes para emissão de Notas Fiscais Eletrônicas:

### 1. **Ambiente de Homologação (Testes)**
- **Código**: `2`
- **Propósito**: Testes e desenvolvimento
- **Características**:
  - ✅ Notas emitidas NÃO têm validade fiscal
  - ✅ Permite testar toda a integração
  - ✅ Validações idênticas ao ambiente de produção
  - ✅ Não há risco de emitir notas reais
  - ✅ Gratuito e sem limitações

### 2. **Ambiente de Produção**
- **Código**: `1`
- **Propósito**: Emissão real de notas fiscais
- **Características**:
  - ⚠️ Notas têm validade fiscal
  - ⚠️ Gera obrigações tributárias
  - ⚠️ Requer certificado digital válido

## 🔧 Serviços Web da SEFAZ

### URLs dos Ambientes (Paraná - SEFAZ-PR)

#### Homologação
```
https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao4
https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao4
https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeConsultaProtocolo4
https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeStatusServico4
https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao4
```

#### Produção
```
https://nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao4
https://nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao4
https://nfe.fazenda.pr.gov.br/nfe/NFeConsultaProtocolo4
https://nfe.fazenda.pr.gov.br/nfe/NFeStatusServico4
https://nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao4
```

## 📚 Serviços Disponíveis

### 1. **NFeAutorizacao4** - Autorização de NF-e
Envia uma NF-e para autorização.

**Requisitos**:
- XML da NF-e assinado digitalmente
- Certificado A1 ou A3
- Validação do schema XSD

**Retorno**:
- Recibo de lote
- Número do protocolo
- Status da autorização

### 2. **NFeRetAutorizacao4** - Consulta Retorno
Consulta o resultado do processamento de um lote.

**Requisitos**:
- Número do recibo do lote

**Retorno**:
- Status de processamento
- Protocolo de autorização (se aprovado)
- Mensagens de erro (se rejeitado)

### 3. **NFeConsultaProtocolo4** - Consulta NF-e
Consulta situação de uma NF-e pela chave de acesso.

**Requisitos**:
- Chave de acesso (44 dígitos)

**Retorno**:
- Status da NF-e
- Dados completos da nota
- Protocolo de autorização

### 4. **NFeStatusServico4** - Status do Serviço
Verifica se o serviço está disponível.

**Requisitos**:
- UF e código do ambiente

**Retorno**:
- Status do serviço (online/offline)
- Tempo médio de resposta

### 5. **NFeInutilizacao4** - Inutilização de Numeração
Inutiliza uma faixa de numeração não utilizada.

**Requisitos**:
- Faixa de números
- Justificativa (mínimo 15 caracteres)

Certificado Digital

### Para Testes (Homologação)
A SEFAZ permite usar certificados de teste ou o mesmo certificado de produção.

**Opções para Teste**:
1. **Certificado de Teste** (recomendado)
   - Solicitar à AC (Autoridade Certificadora)
   - Específico para homologação
   - Gratuito ou baixo custo

2. **Certificado de Produção**
   - Pode ser usado em homologação
   - Não gera risco (ambiente isolado)

### Tipos de Certificado
- **A1**: Arquivo digital (.pfx/.p12) - Válido por 1 ano
- **A3**: Token/Cartão físico - Válido por 3 anos

## 🧪 Regras para Testes em Homologação

### 1. **CNPJs Especiais para Teste**
```
Emitente:
99.999.999/9999-99 (CNPJ inválido para teste)

Destinatário:
99.999.999/9999-99
```

### 2. **Série de Teste**
Recomenda-se usar série diferente da produção:
- Produção: Série 1
- Homologação: Série 890 ou 900-999

### 3. **Valores para Teste**
Pode usar valores reais ou fictícios, não há restrição.

### 4. **Mensagem Obrigatória**
Toda NF-e de homologação deve conter no campo `infAdFisco`:
```
"SEM VALOR FISCAL - EMITIDA EM AMBIENTE DE HOMOLOGAÇÃO"
```

## 📦 Bibliotecas Python Recomendadas

### 1. **python-nfe** (Recomendada)
```bash
pip install python-nfe
```

**Características**:
- Geração de XML conforme layout SEFAZ
- Assinatura digital
- Envio para webservices
- Validação de schemas

### 2. **PyNFe**
```bash
pip install pynfe
```

**Características**:
- Mais completa
- Suporta NF-e, NFC-e, CT-e
- Maior curva de aprendizado

### 3. **signxml** (Para assinatura)
```bash
pip install signxml cryptography
```

Exemplo de Fluxo de Teste

### Passo 1: Verificar Status do Serviço
```python
from nfe.client import NFeClient

client = NFeClient(
    certificado='certificado.pfx',
    senha='senha_certificado',
    uf='PR',
    ambiente='homologacao'
)

status = client.consultar_status_servico()
print(f"Serviço: {status['status']}")
```

### Passo 2: Gerar XML da NF-e
```python
from nfe.builder import NFeBuilder

nfe = NFeBuilder()
nfe.set_ambiente(2)  # Homologação
nfe.set_serie(890)
nfe.set_numero(1)
nfe.add_emitente(
    cnpj='99999999999999',
    nome='EMPRESA TESTE LTDA',
    # ... outros dados
)
nfe.add_destinatario(
    cnpj='99999999999999',
    nome='CLIENTE TESTE',
    # ... outros dados
)
nfe.add_produto(
    codigo='001',
    descricao='PRODUTO TESTE',
    valor=100.00,
    # ... outros dados
)

xml = nfe.gerar_xml()
```

### Passo 3: Assinar XML
```python
from nfe.assinatura import assinar_xml

xml_assinado = assinar_xml(
    xml=xml,
    certificado='certificado.pfx',
    senha='senha'
)
```

### Passo 4: Enviar para Autorização
```python
resultado = client.autorizar_nfe(xml_assinado)

if resultado['codigo'] == '100':
    print(f"✅ NF-e Autorizada!")
    print(f"Protocolo: {resultado['protocolo']}")
    print(f"Chave: {resultado['chave_acesso']}")
else:
    print(f"❌ Erro: {resultado['mensagem']}")
```

### Passo 5: Consultar NF-e
```python
consulta = client.consultar_nfe(chave_acesso='44210812345678901234550010000000011234567890')
print(f"Status: {consulta['situacao']}")
```

Códigos de Retorno Importantes

### Sucessos
- **100**: Autorizada
- **101**: Cancelada
- **135**: Evento registrado

### Rejeições Comuns
- **202**: NF-e já foi autorizada
- **204**: Duplicidade de NF-e
- **206**: NF-e com período de emissão ultrapassado
- **213**: CNPJ-Base do Emitente difere do CNPJ-Base do Certificado Digital
- **227**: Erro na Chave de Acesso
- **539**: CNPJ do emitente inválido
- **540**: CPF/CNPJ do destinatário inválido

### Erros de Validação
- **215**: Rejeição: Falha no Schema XML
- **225**: Rejeição: Protocolo de Autorização de Uso inválido
- **234**: Rejeição: Número da NF-e fora de ordem

Validações da SEFAZ

### 1. **Schema XML**
- Estrutura do XML deve seguir o layout oficial
- Versão correta do schema (4.00 atual)

### 2. **Assinatura Digital**
- XML deve estar assinado com certificado válido
- Assinatura na tag `<infNFe>`

### 3. **Chave de Acesso**
- 44 dígitos calculados corretamente
- Dígito verificador correto
- Formato: `UF + AAMM + CNPJ + Modelo + Serie + Numero + TpEmis + CodNum + DV`

### 4. **Impostos**
- Cálculos corretos de ICMS, PIS, COFINS, IPI
- CST/CSOSN válidos
- CFOP adequado à operação

### 5. **Cadastro**
- Emitente e Destinatário devem estar cadastrados
- CNPJ/CPF válidos
- Inscrição Estadual válida (quando obrigatória)

Dicas para Testes

### 1. **Comece Simples**
- Primeiro teste: Status do serviço
- Segundo teste: Consulta de NF-e existente
- Terceiro teste: Emissão de nota simples

### 2. **Valide Localmente Primeiro**
- Use validadores de XML
- Verifique cálculos manualmente
- Teste assinatura digital separadamente

### 3. **Use Logs Detalhados**
- Registre todas as requisições
- Salve XMLs enviados e recebidos
- Documente erros e soluções

### 4. **Teste Cenários Diversos**
- Operação interna
- Operação interestadual
- Diferentes regimes tributários
- Diversos tipos de produtos

## 🔗 Links Úteis

### Documentação Oficial
- [Portal da NF-e](https://www.nfe.fazenda.gov.br)
- [Documentação SEFAZ-PR](https://www.fazenda.pr.gov.br)
- [Schemas XML](http://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=BMPFMBoln3w=)
- [Manual de Integração](http://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=/fwLvLUSmU8=)

### Ferramentas
- [Validador de NF-e](https://www.nfe.fazenda.gov.br/portal/validador.aspx)
- [Consulta Pública](https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx)
- [Danfe Viewer](http://www.nfe.fazenda.gov.br/portal/consulta.aspx)



Ver arquivo: `django_backend/invoices/services/sefaz_integration.py`


