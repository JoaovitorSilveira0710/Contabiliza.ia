"""
Script Unificado para Popular Banco de Dados
Combina todos os dados em um único script confiável
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Adicionar path do backend
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from app.models.database import get_db, inicializar_banco_dados
    from app.models.clientes import Cliente
    from app.models.financeiro import LancamentoFinanceiro
    from app.models.notas_fiscais import NotaFiscal
    from app.models.juridico import Processo
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import IntegrityError
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Certifique-se de estar executando do diretório raiz do projeto")
    sys.exit(1)


def verificar_dados_existentes(db: Session):
    """Verifica se já existem dados no banco"""
    clientes = db.query(Cliente).count()
    lancamentos = db.query(LancamentoFinanceiro).count()
    notas = db.query(NotaFiscal).count()
    processos = db.query(Processo).count()
    
    print("\n📊 DADOS EXISTENTES NO BANCO:")
    print(f"   👥 Clientes: {clientes}")
    print(f"   💰 Lançamentos: {lancamentos}")
    print(f"   📄 Notas Fiscais: {notas}")
    print(f"   ⚖️ Processos: {processos}")
    
    if clientes > 0 or lancamentos > 0 or notas > 0 or processos > 0:
        print("\n⚠️  ATENÇÃO: O banco já possui dados!")
        resposta = input("\n❓ Deseja SOBRESCREVER todos os dados? (sim/não): ")
        if resposta.lower() not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada pelo usuário")
            return False
        
        # Limpar dados existentes
        print("\n🗑️  Limpando dados existentes...")
        db.query(LancamentoFinanceiro).delete()
        db.query(NotaFiscal).delete()
        db.query(Processo).delete()
        db.query(Cliente).delete()
        db.commit()
        print("✅ Dados limpos!")
    
    return True


def criar_clientes(db: Session):
    """Criar 5 clientes demo com validação"""
    print("\n👥 Criando clientes...")
    
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
    for i, data in enumerate(clientes_data, 1):
        try:
            cliente = Cliente(**data)
            db.add(cliente)
            db.flush()  # Validar antes de commit final
            clientes.append(cliente)
            print(f"   ✅ {i}. {data['nome_razao_social']}")
        except Exception as e:
            print(f"   ❌ Erro ao criar {data['nome_razao_social']}: {e}")
            raise
    
    db.commit()
    print(f"✅ Total: {len(clientes)} clientes criados!")
    return clientes


def criar_lancamentos(db: Session, clientes):
    """Criar lançamentos financeiros com validação"""
    print("\n💰 Criando lançamentos financeiros...")
    
    # Categorias válidas conforme modelo LancamentoFinanceiro
    categorias = {
        'receita': ['honorarios', 'servicos'],
        'despesa': ['impostos', 'folha_pagamento', 'aluguel', 'telefonia', 'material', 'outros']
    }
    formas_pagamento = ['pix', 'transferencia', 'boleto', 'cartao_credito']
    status_opcoes = ['pago', 'pendente', 'atrasado']
    
    lancamentos = []
    hoje = date.today()
    
    for cliente in clientes:
        # 20 lançamentos por cliente
        for i in range(20):
            try:
                tipo = random.choice(['receita', 'despesa'])
                categoria = random.choice(categorias[tipo])
                status = random.choice(status_opcoes)
                
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
            except Exception as e:
                print(f"   ❌ Erro no lançamento {i+1} do cliente {cliente.nome_razao_social}: {e}")
                raise
    
    db.commit()
    print(f"✅ Total: {len(lancamentos)} lançamentos criados!")
    
    # Resumo financeiro
    total_receitas = sum(l.valor for l in lancamentos if l.tipo == 'receita')
    total_despesas = sum(l.valor for l in lancamentos if l.tipo == 'despesa')
    print(f"   💰 Receitas: R$ {total_receitas:,.2f}")
    print(f"   💸 Despesas: R$ {total_despesas:,.2f}")
    print(f"   📊 Saldo: R$ {total_receitas - total_despesas:,.2f}")
    
    return lancamentos


def criar_notas_fiscais(db: Session, clientes):
    """Criar notas fiscais com validação"""
    print("\n📄 Criando notas fiscais...")
    
    hoje = date.today()
    notas = []
    
    for i, cliente in enumerate(clientes):
        # 4 notas por cliente
        for j in range(4):
            try:
                dias_atras = random.randint(10, 180)
                data_emissao = hoje - timedelta(days=dias_atras)
                
                numero_nf = f"{2024}{i+1:02d}{j+1:04d}"
                valor_produtos = round(random.uniform(1000, 20000), 2)
                valor_servicos = round(random.uniform(500, 5000), 2)
                valor_total = valor_produtos + valor_servicos
                
                situacoes = ['autorizada', 'cancelada', 'pendente']
                pesos = [0.8, 0.1, 0.1]
                situacao = random.choices(situacoes, weights=pesos)[0]
                
                nota = NotaFiscal(
                    cliente_id=cliente.id,
                    numero=numero_nf,
                    serie="1",
                    modelo="nfe",
                    tipo="saida",
                    data_emissao=datetime.combine(data_emissao, datetime.min.time()),
                    data_autorizacao=datetime.combine(data_emissao, datetime.min.time()) if situacao == 'autorizada' else None,
                    valor_total=valor_total,
                    valor_produtos=valor_produtos,
                    valor_servicos=valor_servicos,
                    situacao=situacao,
                    chave_acesso=None,
                    cnpj_emitente=cliente.cnpj_cpf,
                    nome_emitente=cliente.nome_razao_social
                )
                db.add(nota)
                notas.append(nota)
            except Exception as e:
                print(f"   ❌ Erro na nota {j+1} do cliente {cliente.nome_razao_social}: {e}")
                raise
    
    db.commit()
    print(f"✅ Total: {len(notas)} notas fiscais criadas!")
    print(f"   💰 Valor total: R$ {sum(n.valor_total for n in notas):,.2f}")
    
    return notas


def criar_processos_juridicos(db: Session, clientes):
    """Criar processos jurídicos com validação"""
    print("\n⚖️  Criando processos jurídicos...")
    
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
    hoje = date.today()
    processos = []
    
    # 2 processos para os primeiros 5 clientes
    for i, cliente in enumerate(clientes[:5]):
        for j in range(2):
            try:
                dias_atras = random.randint(30, 730)
                data_distribuicao = hoje - timedelta(days=dias_atras)
                
                ano = data_distribuicao.year
                numero = f"{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.{ano}.8.26.{random.randint(1000, 9999)}"
                
                valor_causa = round(random.uniform(10000, 500000), 2)
                honorarios = round(valor_causa * random.uniform(0.05, 0.15), 2)
                
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
            except Exception as e:
                print(f"   ❌ Erro no processo {j+1} do cliente {cliente.nome_razao_social}: {e}")
                raise
    
    db.commit()
    print(f"✅ Total: {len(processos)} processos criados!")
    print(f"   ⚖️  Valor em causas: R$ {sum(p.valor_causa for p in processos):,.2f}")
    
    return processos


def main():
    """Executar população completa"""
    print("\n" + "="*70)
    print("🚀 CONTABILIZA.IA - POPULAÇÃO COMPLETA DO BANCO DE DADOS")
    print("="*70)
    
    try:
        # Inicializar banco
        print("\n🔧 Inicializando banco de dados...")
        inicializar_banco_dados()
        db = next(get_db())
        print("✅ Banco inicializado!")
        
        # Verificar dados existentes
        if not verificar_dados_existentes(db):
            return
        
        print("\n" + "="*70)
        print("📝 INICIANDO POPULAÇÃO DE DADOS")
        print("="*70)
        
        # Criar todos os dados
        clientes = criar_clientes(db)
        lancamentos = criar_lancamentos(db, clientes)
        notas = criar_notas_fiscais(db, clientes)
        processos = criar_processos_juridicos(db, clientes)
        
        # Resumo final
        print("\n" + "="*70)
        print("✅ BANCO POPULADO COM SUCESSO!")
        print("="*70)
        print(f"\n📊 RESUMO DOS DADOS:")
        print(f"   👥 Clientes: {len(clientes)}")
        print(f"   💰 Lançamentos Financeiros: {len(lancamentos)}")
        print(f"   📄 Notas Fiscais: {len(notas)}")
        print(f"   ⚖️  Processos Jurídicos: {len(processos)}")
        print(f"\n💵 VALORES:")
        print(f"   Receitas: R$ {sum(l.valor for l in lancamentos if l.tipo == 'receita'):,.2f}")
        print(f"   Despesas: R$ {sum(l.valor for l in lancamentos if l.tipo == 'despesa'):,.2f}")
        print(f"   Notas Fiscais: R$ {sum(n.valor_total for n in notas):,.2f}")
        print(f"   Causas Judiciais: R$ {sum(p.valor_causa for p in processos):,.2f}")
        print("\n🎉 Sistema pronto para demonstração!")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        db.rollback()
    except Exception as e:
        print(f"\n\n❌ ERRO FATAL: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        print(f"\n📋 Traceback completo:")
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
