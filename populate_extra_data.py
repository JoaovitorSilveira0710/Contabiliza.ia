"""
Script para Adicionar Dados Extras
Notas Fiscais e Processos Jurídicos
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Adicionar path do backend
sys.path.append(str(Path(__file__).parent / "backend"))

from app.models.database import get_db, inicializar_banco_dados
from app.models.clientes import Cliente
from app.models.notas_fiscais import NotaFiscal
from app.models.juridico import Processo
from sqlalchemy.orm import Session

def criar_notas_fiscais(db: Session, clientes):
    """Criar 20 notas fiscais de exemplo"""
    print("📄 Criando notas fiscais...")
    
    hoje = date.today()
    notas = []
    
    for i, cliente in enumerate(clientes):
        # 4 notas por cliente
        for j in range(4):
            dias_atras = random.randint(10, 180)
            data_emissao = hoje - timedelta(days=dias_atras)
            
            numero_nf = f"{2024}{i+1:02d}{j+1:04d}"
            valor_produtos = round(random.uniform(1000, 20000), 2)
            valor_servicos = round(random.uniform(500, 5000), 2)
            valor_total = valor_produtos + valor_servicos
            
            situacoes = ['autorizada', 'cancelada', 'pendente']
            pesos = [0.8, 0.1, 0.1]  # 80% autorizadas
            situacao = random.choices(situacoes, weights=pesos)[0]
            
            nota = NotaFiscal(
                cliente_id=cliente.id,
                numero=numero_nf,
                serie="1",
                modelo="nfe",
                tipo="saida",  # Nota de saída
                data_emissao=datetime.combine(data_emissao, datetime.min.time()),
                data_autorizacao=datetime.combine(data_emissao, datetime.min.time()) if situacao == 'autorizada' else None,
                valor_total=valor_total,
                valor_produtos=valor_produtos,
                valor_servicos=valor_servicos,
                situacao=situacao,
                chave_acesso=None,  # Simplificado - pode ser NULL
                cnpj_emitente=cliente.cnpj_cpf,
                nome_emitente=cliente.nome_razao_social
            )
            db.add(nota)
            notas.append(nota)
    
    db.commit()
    print(f"✅ {len(notas)} notas fiscais criadas!")
    return notas

def criar_processos_juridicos(db: Session, clientes):
    """Criar 10 processos jurídicos de exemplo"""
    print("⚖️ Criando processos jur\u00eddicos...")
    
    hoje = date.today()
    processos = []
    
    assuntos = [
        "Recuperação de Crédito Tributário",
        "Ação Trabalhista - Rescisão",
        "Mandado de Segurança - ICMS",
        "Execução Fiscal - ISS",
        "Ação Anulatória - Multa INSS",
        "Embargos à Execução Fiscal",
        "Ação Declaratória - Isenção Tributária",
        "Recurso Administrativo - FGTS"
    ]
    
    status_opcoes = ['ativo', 'suspenso', 'encerrado']
    
    # 2 processos para os primeiros 5 clientes
    for i, cliente in enumerate(clientes[:5]):
        for j in range(2):
            dias_atras = random.randint(30, 730)  # Até 2 anos atrás
            data_distribuicao = hoje - timedelta(days=dias_atras)
            
            # Número de processo simulado
            ano = data_distribuicao.year
            numero = f"{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.{ano}.8.26.{random.randint(1000, 9999)}"
            
            valor_causa = round(random.uniform(10000, 500000), 2)
            honorarios = valor_causa * random.uniform(0.05, 0.15)
            
            status = random.choices(status_opcoes, weights=[0.7, 0.2, 0.1])[0]
            
            processo = Processo(
                cliente_id=cliente.id,
                numero_processo=numero,
                assunto=random.choice(assuntos),
                tipo_acao="Ação Ordinária",
                vara=f"{random.randint(1, 15)}ª Vara Cível",
                data_distribuicao=data_distribuicao,
                valor_causa=valor_causa,
                honorarios=honorarios,
                status=status,
                advogado_responsavel=f"Dr. {['Silva', 'Santos', 'Oliveira', 'Costa', 'Ferreira'][i % 5]}",
                parte_contraria="Fazenda Pública" if random.random() > 0.5 else "Parte Adversa Ltda",
                ultima_movimentacao=f"Processo em andamento - {random.choice(['Aguardando decisão', 'Em fase de instrução', 'Recurso apresentado', 'Audiência designada'])}",
                data_ultima_movimentacao=hoje - timedelta(days=random.randint(1, 60)),
                data_prazo=hoje + timedelta(days=random.randint(5, 90)) if status == 'ativo' else None
            )
            db.add(processo)
            processos.append(processo)
    
    db.commit()
    print(f"✅ {len(processos)} processos jurídicos criados!")
    return processos

def main():
    """Executar população"""
    print("\n" + "="*60)
    print("🚀 ADICIONANDO DADOS EXTRAS AO BANCO")
    print("="*60 + "\n")
    
    # Inicializar banco
    inicializar_banco_dados()
    db = next(get_db())
    
    try:
        # Buscar clientes existentes
        clientes = db.query(Cliente).filter(Cliente.ativo == True).all()
        print(f"📊 {len(clientes)} clientes encontrados\n")
        
        if len(clientes) == 0:
            print("❌ Nenhum cliente encontrado! Execute primeiro populate_simple.py")
            return
        
        # Criar dados extras
        notas = criar_notas_fiscais(db, clientes)
        processos = criar_processos_juridicos(db, clientes)
        
        # Resumo
        print("\n" + "="*60)
        print("✅ DADOS EXTRAS ADICIONADOS COM SUCESSO!")
        print("="*60)
        print(f"📄 {len(notas)} notas fiscais")
        print(f"⚖️ {len(processos)} processos jurídicos")
        print(f"💰 Valor total em notas: R$ {sum(n.valor_total for n in notas):,.2f}")
        print(f"⚖️ Valor total em causas: R$ {sum(p.valor_causa for p in processos):,.2f}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
