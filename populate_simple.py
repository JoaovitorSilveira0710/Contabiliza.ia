"""
Script Simplificado para Popular Banco de Dados
Cria apenas dados essenciais para demonstração
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Adicionar path do backend
sys.path.append(str(Path(__file__).parent / "backend"))

from app.models.database import get_db, inicializar_banco_dados
from app.models.clientes import Cliente
from app.models.financeiro import LancamentoFinanceiro
from sqlalchemy.orm import Session

def criar_clientes(db: Session):
    """Criar 5 clientes demo"""
    print("📊 Criando clientes...")
    
    clientes_data = [
        {
            "nome_razao_social": "Tech Inovação Ltda",
            "cnpj_cpf": "12.345.678/0001-90",
            "tipo_pessoa": "J",
            "email": "contato@techinovacao.com.br",
            "telefone": "(11) 98765-4321",
            "endereco": "Av. Paulista, 1000 - São Paulo, SP",
            "regime_tributario": "Lucro Real",
            "ativo": True
        },
        {
            "nome_razao_social": "Comércio Silva & Cia",
            "cnpj_cpf": "23.456.789/0001-81",
            "tipo_pessoa": "J",
            "email": "financeiro@silvacia.com.br",
            "telefone": "(21) 97654-3210",
            "endereco": "Rua das Flores, 500 - Rio de Janeiro, RJ",
            "regime_tributario": "Simples Nacional",
            "ativo": True
        },
        {
            "nome_razao_social": "Consultoria Estratégica ME",
            "cnpj_cpf": "34.567.890/0001-72",
            "tipo_pessoa": "J",
            "email": "contato@estrategica.com.br",
            "telefone": "(11) 96543-2109",
            "endereco": "Rua dos Pinheiros, 250 - São Paulo, SP",
            "regime_tributario": "Lucro Presumido",
            "ativo": True
        },
        {
            "nome_razao_social": "Indústria MetalTech S.A.",
            "cnpj_cpf": "45.678.901/0001-63",
            "tipo_pessoa": "J",
            "email": "admin@metaltech.ind.br",
            "telefone": "(19) 3456-7890",
            "endereco": "Rodovia SP-330, Km 45 - Campinas, SP",
            "regime_tributario": "Lucro Real",
            "ativo": True
        },
        {
            "nome_razao_social": "João Carlos Oliveira",
            "cnpj_cpf": "123.456.789-00",
            "tipo_pessoa": "F",
            "email": "joao.oliveira@email.com",
            "telefone": "(11) 95432-1098",
            "endereco": "Rua Augusta, 1500 - São Paulo, SP",
            "regime_tributario": "MEI",
            "ativo": True
        }
    ]
    
    clientes = []
    for data in clientes_data:
        cliente = Cliente(**data)
        db.add(cliente)
        clientes.append(cliente)
    
    db.commit()
    print(f"✅ {len(clientes)} clientes criados!")
    return clientes

def criar_lancamentos(db: Session, clientes):
    """Criar lançamentos financeiros variados"""
    print("💰 Criando lançamentos financeiros...")
    
    # Categorias válidas conforme modelo LancamentoFinanceiro
    categorias_receita = ['honorarios', 'servicos']
    categorias_despesa = ['impostos', 'folha_pagamento', 'aluguel', 'telefonia', 'material', 'outros']
    formas_pagamento = ['pix', 'transferencia', 'boleto', 'cartao_credito']
    status_opcoes = ['pago', 'pendente', 'atrasado']
    
    lancamentos = []
    hoje = date.today()
    
    for cliente in clientes:
        # Criar 20 lançamentos por cliente (mix de receitas e despesas)
        for i in range(20):
            tipo = random.choice(['receita', 'despesa'])
            categoria = random.choice(categorias_receita if tipo == 'receita' else categorias_despesa)
            status = random.choice(status_opcoes)
            
            # Datas aleatórias nos últimos 6 meses
            dias_atras = random.randint(1, 180)
            data_venc = hoje - timedelta(days=dias_atras)
            data_pag = data_venc + timedelta(days=random.randint(0, 5)) if status == 'pago' else None
            
            valor = round(random.uniform(500, 15000), 2)
            
            lancamento = LancamentoFinanceiro(
                cliente_id=cliente.id,
                tipo=tipo,
                descricao=f"{categoria.replace('_', ' ').title()} - {cliente.nome_razao_social[:30]}",
                valor=valor,
                data_vencimento=data_venc,
                data_pagamento=data_pag,
                status=status,
                categoria=categoria,
                forma_pagamento=random.choice(formas_pagamento) if status == 'pago' else None
            )
            db.add(lancamento)
            lancamentos.append(lancamento)
    
    db.commit()
    print(f"✅ {len(lancamentos)} lançamentos criados!")
    return lancamentos

def main():
    """Executar população"""
    print("\n" + "="*60)
    print("🚀 POPULANDO BANCO DE DADOS COM DADOS DEMO")
    print("="*60 + "\n")
    
    # Inicializar banco
    inicializar_banco_dados()
    db = next(get_db())
    
    try:
        # Criar dados
        clientes = criar_clientes(db)
        lancamentos = criar_lancamentos(db, clientes)
        
        # Resumo
        print("\n" + "="*60)
        print("✅ BANCO POPULADO COM SUCESSO!")
        print("="*60)
        print(f"📊 {len(clientes)} clientes")
        print(f"💰 {len(lancamentos)} lançamentos financeiros")
        print(f"💵 Total de receitas: R$ {sum(l.valor for l in lancamentos if l.tipo == 'receita'):,.2f}")
        print(f"💸 Total de despesas: R$ {sum(l.valor for l in lancamentos if l.tipo == 'despesa'):,.2f}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
