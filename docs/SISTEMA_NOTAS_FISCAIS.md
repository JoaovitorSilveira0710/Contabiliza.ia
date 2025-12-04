# Sistema de Notas Fiscais - Contabiliza.IA

## Visão Geral

O sistema de notas fiscais do Contabiliza.IA foi desenvolvido para gerar DANFE (Documento Auxiliar da Nota Fiscal Eletrônica) seguindo o padrão oficial da SEFAZ do Paraná, especialmente para Notas Fiscais do Produtor Rural.

## Funcionalidades Implementadas

Geração de DANFE no Padrão SEFAZ-PR
- Layout oficial do Estado do Paraná
- Código de barras da chave de acesso
- Formatação automática de CPF/CNPJ
- Cálculo automático de impostos
- Suporte a múltiplos produtos/serviços

Campos Implementados

#### Identificação
- Número da NF-e
- Série
- Chave de acesso (44 dígitos)
- Protocolo de autorização
- Data/hora de emissão

#### Emitente
- Nome/Razão Social
- CPF/CNPJ
- Inscrição Estadual
- Endereço completo
- Município/UF/CEP
- Telefone

#### Destinatário/Remetente
- Nome/Razão Social
- CPF/CNPJ
- Endereço completo
- Município/UF/CEP
- Data de entrada/saída

#### Produtos/Serviços
- Código do produto
- Descrição
- NCM/SH
- CST/CSOSN
- CFOP
- Unidade
- Quantidade (até 4 decimais)
- Valor unitário
- Valor total
- Impostos (ICMS, IPI, PIS, COFINS)

#### Valores e Impostos
- Base de cálculo ICMS
- Valor ICMS
- Base ICMS ST
- Valor ICMS ST
- Valor total dos produtos
- Frete
- Seguro
- Desconto
- Outras despesas
- Valor IPI
- Valor total da nota

#### Transporte
- Modalidade do frete
- Dados da transportadora (opcional)
- Dados de volumes

#### ISSQN
- Valor total dos serviços
- Base de cálculo
- Valor do ISSQN

## Como Usar

### 1. Via API REST

#### Criar uma Nota Fiscal

```bash
POST /api/invoices/
Content-Type: application/json

{
  "number": "3401814",
  "series": "890",
  "invoice_type": "nfe",
  "model_code": "55",
  "operation_nature": "venda_producao",
  "operation_type": "saida",
  "cfop": "5101",
  
  "issuer_name": "ADRIANE THIEVES ARAUJO DE AZEVEDO",
  "issuer_tax_id": "96633476949",
  "issuer_state_registration": "9588805457",
  "issuer_address": "Estrada para São Geraldinho",
  "issuer_number": "S/N",
  "issuer_city": "Campina do Simão",
  "issuer_state": "PR",
  "issuer_zip_code": "85148-000",
  
  "client": 1,
  "issue_date": "2025-11-27T08:44:00",
  
  "items": [
    {
      "code": "1636-88-00",
      "description": "BOCS PARA ABATE",
      "ncm": "01628000",
      "cfop": "5101",
      "unit": "KG",
      "quantity": 10000.00,
      "unit_value": 6.30,
      "icms_cst": "00",
      "icms_rate": 0.00
    }
  ]
}
```

#### Gerar PDF do DANFE

```bash
POST /api/invoices/{id}/generate_pdf/

# Para usar o layout do Paraná especificamente:
POST /api/invoices/{id}/generate_pdf/?layout=pr
```

#### Baixar PDF Gerado

```bash
GET /api/invoices/{id}/download_pdf/
```

### 2. Via Python/Django Shell

```python
# Importar módulos
from clients.models import Client
from invoices.models import Invoice, InvoiceItem
from invoices.services.danfe_pr_generator import DANFEParanaGenerator

# Criar cliente
client = Client.objects.create(
    name='Cooperativa Agroindustrial',
    tax_id='10015928000284',
    type='legal',
    street='PR 170, KM 395',
    city='Entre Rios',
    state='PR',
    zip_code='85138-300'
)

# Criar nota fiscal
invoice = Invoice.objects.create(
    number='3401814',
    series='890',
    client=client,
    issuer_name='PRODUTOR RURAL',
    issuer_tax_id='12345678901',
    issuer_state='PR',
    issue_date='2025-11-27 08:44:00',
    total_value=117000.00
)

# Adicionar itens
item = InvoiceItem.objects.create(
    invoice=invoice,
    code='1636-88-00',
    description='BOCS PARA ABATE',
    ncm='01628000',
    cfop='5101',
    unit='KG',
    quantity=10000.00,
    unit_value=6.30
)

# Gerar PDF
generator = DANFEParanaGenerator(invoice)
generator.generate_pdf()
```

### 3. Script de Teste

Execute o script de teste fornecido:

```bash
cd django_backend
python manage.py shell < test_danfe_pr.py
```

Ou:

```bash
python test_danfe_pr.py
```

## Estrutura de Arquivos

```
django_backend/
├── invoices/
│   ├── models.py              # Modelos de dados
│   ├── serializers.py         # Serializers REST
│   ├── views.py               # Views da API
│   ├── services/
│   │   ├── danfe_pr_generator.py    # Gerador DANFE-PR (NOVO)
│   │   ├── pdf_generator.py         # Gerador genérico
│   │   ├── xml_generator.py         # Gerador de XML
│   │   └── backup_service.py        # Serviço de backup
│   └── admin.py
├── test_danfe_pr.py           # Script de teste
└── storage/
    └── invoices/
        ├── pdf/               # PDFs gerados
        └── xml/               # XMLs gerados
```

## Configurações

### Settings.py

```python
# Diretório de armazenamento
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'storage'

# Instalados
INSTALLED_APPS = [
    ...
    'invoices',
    'clients',
    ...
]
```

## Validações Implementadas

Operações Interestaduais
- Detecta automaticamente quando emitente e destinatário estão em estados diferentes
- Aplica regras específicas de ICMS
- Adiciona observações automáticas

Formatação Automática
- CPF/CNPJ: formatação com pontos e traços
- Chave de acesso: grupos de 4 dígitos
- Valores monetários: R$ com vírgula decimal
- Datas: dd/mm/yyyy hh:mm:ss

Cálculos Automáticos
- Total de produtos
- Total de serviços
- Valor total da nota
- Base de cálculo de impostos

## Códigos Importantes

### CFOP (Código Fiscal de Operações e Prestações)
- `5101`: Venda de produção do estabelecimento (dentro do estado)
- `6101`: Venda de produção do estabelecimento (fora do estado)
- `5102`: Venda de mercadoria adquirida (dentro do estado)
- `6102`: Venda de mercadoria adquirida (fora do estado)

### CST/CSOSN (Código de Situação Tributária)
- `00`: Tributada integralmente
- `10`: Tributada com cobrança de ICMS por ST
- `20`: Com redução de BC
- `40`: Isenta
- `41`: Não tributada
- `60`: ICMS cobrado anteriormente por ST

### NCM (Nomenclatura Comum do Mercosul)
- `01628000`: Gado bovino vivo

## Próximos Passos Sugeridos

### 🔲 Integração com SEFAZ
- [ ] Assinatura digital do XML
- [ ] Envio para autorização
- [ ] Consulta de status
- [ ] Cancelamento
- [ ] Inutilização de numeração

### 🔲 Melhorias no DANFE
- [ ] Logo do emitente
- [ ] QR Code para consulta
- [ ] Múltiplas páginas para muitos itens
- [ ] Canhoto destacável

### 🔲 Funcionalidades Adicionais
- [ ] NFS-e (Nota Fiscal de Serviços Eletrônica)
- [ ] NFC-e (Nota Fiscal ao Consumidor Eletrônica)
- [ ] CT-e (Conhecimento de Transporte Eletrônico)
- [ ] Manifestação do Destinatário

### 🔲 Interface Web
- [ ] Formulário de cadastro de notas
- [ ] Visualização de notas emitidas
- [ ] Dashboard com estatísticas
- [ ] Relatórios fiscais

## Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `/docs`
2. Execute o script de teste
3. Consulte os logs de erro
4. Entre em contato com o suporte técnico

## Referências

- [Portal Nacional da NF-e](https://www.nfe.fazenda.gov.br)
- [Manual de Orientação do Contribuinte - SEFAZ-PR](https://www.fazenda.pr.gov.br)
- [Layout da NF-e](docs/LAYOUT_DANFE_PR.md)
- [Códigos de Município do PR](docs/CODIGOS_MUNICIPIOS_PR.md)
