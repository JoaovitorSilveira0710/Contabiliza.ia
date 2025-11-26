"""
Script para Popular Banco de Dados com Dados Demo
Para apresentação do Contabiliza.IA
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Adicionar path do backend
sys.path.append(str(Path(__file__).parent / "backend"))

from app.models.database import get_db, inicializar_banco_dados
from app.models.clientes import Cliente
from app.models.financeiro import LancamentoFinanceiro, IndicadorFinanceiro
from app.models.notas_fiscais import NotaFiscal, ItemNotaFiscal
from app.models.juridico import Processo, Audiencia
from app.models.contabil import ObrigacaoAcessoria, DRE
from sqlalchemy.orm import Session

# Dados realistas para demo
CLIENTES_DEMO = [
    {
        "nome_razao_social": "Tech Inovação Ltda",
        "cnpj_cpf": "12.345.678/0001-90",
        "tipo_pessoa": "J",
        "email": "contato@techinovacao.com.br",
        "telefone": "(11) 98765-4321",
        "endereco": "Av. Paulista, 1000 - São Paulo, SP - CEP 01310-100",
        "regime_tributario": "Lucro Real",
        "ativo": True
    },
    {
        "nome_razao_social": "Comércio Silva & Cia",
        "cnpj_cpf": "23.456.789/0001-81",
        "tipo_pessoa": "J",
        "email": "financeiro@silvacia.com.br",
        "telefone": "(21) 97654-3210",
        "endereco": "Rua das Flores, 500 - Rio de Janeiro, RJ - CEP 20000-000",
        "regime_tributario": "Simples Nacional",
        "ativo": True
    },
    {
        "nome_razao_social": "Consultoria Estratégica ME",
        "cnpj_cpf": "34.567.890/0001-72",
        "tipo_pessoa": "J",
        "email": "contato@estrategica.com.br",
        "telefone": "(11) 96543-2109",
        "endereco": "Rua dos Pinheiros, 250 - São Paulo, SP - CEP 05422-001",
        "regime_tributario": "Lucro Presumido",
        "ativo": True
    },
    {
        "nome_razao_social": "Indústria MetalTech S.A.",
        "cnpj_cpf": "45.678.901/0001-63",
        "tipo_pessoa": "J",
        "email": "admin@metaltech.ind.br",
        "telefone": "(19) 3456-7890",
        "endereco": "Rodovia SP-330, Km 45 - Campinas, SP - CEP 13100-000",
        "regime_tributario": "Lucro Real",
        "ativo": True
    },
    {
        "nome_razao_social": "João Carlos Oliveira",
        "cnpj_cpf": "123.456.789-00",
        "tipo_pessoa": "F",
        "email": "joao.oliveira@email.com",
        "telefone": "(11) 95432-1098",
        "endereco": "Rua Augusta, 1500 - São Paulo, SP - CEP 01304-001",
        "regime_tributario": "MEI",
        "ativo": True
    }
]

def criar_clientes(db: Session):
    """Criar clientes de demonstração"""
    print("📊 Criando clientes demo...")
    clientes = []
    
    for cliente_data in CLIENTES_DEMO:
        cliente = Cliente(**cliente_data)
        db.add(cliente)
        clientes.append(cliente)
    
    db.commit()
    print(f"✅ {len(clientes)} clientes criados!")
    return clientes

def criar_lancamentos_financeiros(db: Session, clientes: list):
    """Criar lançamentos financeiros dos últimos 6 meses"""
    print("💰 Criando lançamentos financeiros...")
    
    hoje = datetime.now()
    lancamentos = []
    
    for mes in range(6, 0, -1):
        data_base = hoje - timedelta(days=30 * mes)
        
        for cliente in clientes[:3]:  # Primeiros 3 clientes
            # Receitas (5-8 por mês)
            for _ in range(random.randint(5, 8)):
                valor = random.uniform(5000, 50000)
                lancamento = LancamentoFinanceiro(
                    cliente_id=cliente.id,
                    tipo="receita",
                    categoria="servicos_prestados",
                    descricao=f"Serviços de consultoria - {data_base.strftime('%m/%Y')}",
                    valor=round(valor, 2),
                    data_lancamento=data_base + timedelta(days=random.randint(1, 28)),
                    data_vencimento=data_base + timedelta(days=random.randint(1, 28)),
                    status="pago",
                    forma_pagamento="transferencia"
                )
                db.add(lancamento)
                lancamentos.append(lancamento)
            
            # Despesas (3-5 por mês)
            for _ in range(random.randint(3, 5)):
                categorias = ["salarios", "fornecedores", "impostos", "aluguel", "outras"]
                categoria = random.choice(categorias)
                valor = random.uniform(2000, 15000)
                
                lancamento = LancamentoFinanceiro(
                    cliente_id=cliente.id,
                    tipo="despesa",
                    categoria=categoria,
                    descricao=f"{categoria.replace('_', ' ').title()} - {data_base.strftime('%m/%Y')}",
                    valor=round(valor, 2),
                    data_lancamento=data_base + timedelta(days=random.randint(1, 28)),
                    data_vencimento=data_base + timedelta(days=random.randint(1, 28)),
                    status="pago",
                    forma_pagamento="transferencia"
                )
                db.add(lancamento)
                lancamentos.append(lancamento)
    
    db.commit()
    print(f"✅ {len(lancamentos)} lançamentos criados!")
    return lancamentos

def criar_notas_fiscais(db: Session, clientes: list):
    """Criar notas fiscais de demonstração"""
    print("📄 Criando notas fiscais...")
    
    hoje = datetime.now()
    notas = []
    
    for mes in range(3, 0, -1):
        data_base = hoje - timedelta(days=30 * mes)
        
        for cliente in clientes[:3]:
            for _ in range(random.randint(2, 4)):
                numero = f"{random.randint(1000, 9999)}"
                valor_total = random.uniform(5000, 30000)
                
                nota = NotaFiscal(
                    cliente_id=cliente.id,
                    numero=numero,
                    serie="1",
                    tipo="saida",
                    data_emissao=data_base + timedelta(days=random.randint(1, 28)),
                    valor_total=round(valor_total, 2),
                    valor_icms=round(valor_total * 0.18, 2),
                    valor_ipi=round(valor_total * 0.05, 2),
                    chave_acesso=f"{random.randint(10000000, 99999999)}{random.randint(10000000, 99999999)}{random.randint(10000000, 99999999)}",
                    status="autorizada",
                    xml_nfe=f"<xml>NFe {numero}</xml>"
                )
                db.add(nota)
                notas.append(nota)
    
    db.commit()
    print(f"✅ {len(notas)} notas fiscais criadas!")
    return notas

def criar_obrigacoes_acessorias(db: Session, clientes: list):
    """Criar obrigações acessórias"""
    print("📋 Criando obrigações acessórias...")
    
    hoje = datetime.now()
    obrigacoes = []
    
    tipos = [
        {"tipo": "sped_fiscal", "descricao": "EFD-ICMS/IPI", "periodicidade": "mensal"},
        {"tipo": "sped_contribuicoes", "descricao": "EFD-Contribuições", "periodicidade": "mensal"},
        {"tipo": "dctf", "descricao": "DCTF - Declaração Débitos Federais", "periodicidade": "mensal"},
        {"tipo": "defis", "descricao": "DEFIS - Simples Nacional", "periodicidade": "anual"}
    ]
    
    for cliente in clientes[:3]:
        for obrig_data in tipos:
            obrigacao = ObrigacaoAcessoria(
                cliente_id=cliente.id,
                tipo=obrig_data["tipo"],
                descricao=obrig_data["descricao"],
                periodicidade=obrig_data["periodicidade"],
                data_vencimento=hoje + timedelta(days=random.randint(5, 30)),
                status="pendente"
            )
            db.add(obrigacao)
            obrigacoes.append(obrigacao)
    
    db.commit()
    print(f"✅ {len(obrigacoes)} obrigações acessórias criadas!")
    return obrigacoes

def criar_processos_juridicos(db: Session, clientes: list):
    """Criar processos jurídicos de demonstração"""
    print("⚖️ Criando processos jurídicos...")
    
    hoje = datetime.now()
    processos = []
    
    tipos = ["trabalhista", "tributario", "civel"]
    
    for cliente in clientes[:2]:
        for tipo in tipos:
            numero = f"{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.{datetime.now().year}.8.26.0100"
            
            processo = Processo(
                cliente_id=cliente.id,
                numero_processo=numero,
                tipo=tipo,
                vara=f"{random.randint(1, 50)}ª Vara {tipo.title()}",
                comarca="São Paulo",
                autor=cliente.nome_razao_social if random.choice([True, False]) else "Terceiro",
                reu="Terceiro" if processo.autor == cliente.nome_razao_social else cliente.nome_razao_social,
                valor_causa=random.uniform(10000, 500000),
                data_distribuicao=hoje - timedelta(days=random.randint(30, 365)),
                status="em_andamento"
            )
            db.add(processo)
            processos.append(processo)
    
    db.commit()
    print(f"✅ {len(processos)} processos criados!")
    return processos

def main():
    """Executar população do banco"""
    print("🚀 Iniciando população do banco de dados...")
    print("=" * 60)
    
    # Inicializar banco
    inicializar_banco_dados()
    db = next(get_db())
    
    try:
        # Criar dados
        clientes = criar_clientes(db)
        lancamentos = criar_lancamentos_financeiros(db, clientes)
        notas = criar_notas_fiscais(db, clientes)
        obrigacoes = criar_obrigacoes_acessorias(db, clientes)
        processos = criar_processos_juridicos(db, clientes)
        
        print("=" * 60)
        print("✅ BANCO POPULADO COM SUCESSO!")
        print(f"📊 Total de registros criados:")
        print(f"   - {len(clientes)} Clientes")
        print(f"   - {len(lancamentos)} Lançamentos Financeiros")
        print(f"   - {len(notas)} Notas Fiscais")
        print(f"   - {len(obrigacoes)} Obrigações Acessórias")
        print(f"   - {len(processos)} Processos Jurídicos")
        print("=" * 60)
        print("🎯 Pronto para apresentação!")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
