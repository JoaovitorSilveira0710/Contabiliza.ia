# Script de teste dos endpoints principais
# Execute com: python test_endpoints.py

import requests
import json
from datetime import date, datetime

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def print_response(response, label):
    """Imprime resposta formatada"""
    print(f"\n{'='*60}")
    print(f"🔍 {label}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()

def test_health():
    """Testa health check"""
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200

def test_login():
    """Testa login de desenvolvimento"""
    payload = {
        "email": "admin@contabiliza.ia",
        "senha": "dev123"
    }
    response = requests.post(f"{API_URL}/auth/login", json=payload)
    print_response(response, "Login")
    if response.status_code == 200:
        return response.json().get("token")
    return None

def test_auth_me(token):
    """Testa endpoint /me"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/auth/me", headers=headers)
    print_response(response, "Auth - Me")
    return response.status_code == 200

def test_list_clientes():
    """Testa listagem de clientes"""
    response = requests.get(f"{API_URL}/clientes/?limit=5")
    print_response(response, "Listar Clientes")
    return response.json() if response.status_code == 200 else []

def test_create_cliente():
    """Testa criação de cliente"""
    payload = {
        "nome_razao_social": "Teste Automatizado LTDA",
        "cnpj_cpf": "12345678901234",
        "tipo_pessoa": "J",
        "email": "teste@automatizado.com",
        "telefone": "11987654321",
        "regime_tributario": "Simples Nacional",
        "atividade_principal": "Consultoria Empresarial"
    }
    response = requests.post(f"{API_URL}/clientes/", json=payload)
    print_response(response, "Criar Cliente")
    if response.status_code == 201:
        return response.json().get("id")
    return None

def test_create_contrato(cliente_id):
    """Testa criação de contrato"""
    payload = {
        "cliente_id": cliente_id,
        "tipo_servico": "contabil",
        "valor_mensal": 500.00,
        "data_inicio": "2025-01-01",
        "dia_vencimento": 10
    }
    response = requests.post(f"{API_URL}/clientes/{cliente_id}/contratos", json=payload)
    print_response(response, "Criar Contrato")
    return response.status_code == 201

def test_list_lancamentos():
    """Testa listagem de lançamentos financeiros"""
    response = requests.get(f"{API_URL}/financeiro/lancamentos/?limit=5")
    print_response(response, "Listar Lançamentos Financeiros")
    return response.status_code == 200

def test_dashboard_financeiro():
    """Testa dashboard financeiro"""
    response = requests.get(f"{API_URL}/financeiro/dashboard/?periodo=mensal")
    print_response(response, "Dashboard Financeiro")
    return response.status_code == 200

def test_list_obrigacoes():
    """Testa listagem de obrigações acessórias"""
    response = requests.get(f"{API_URL}/contabil/obrigacoes/?limit=5")
    print_response(response, "Listar Obrigações Acessórias")
    return response.status_code == 200

def test_list_processos():
    """Testa listagem de processos jurídicos"""
    response = requests.get(f"{API_URL}/juridico/processos/?limit=5")
    print_response(response, "Listar Processos Jurídicos")
    return response.status_code == 200

def test_dashboard_juridico():
    """Testa dashboard jurídico"""
    response = requests.get(f"{API_URL}/juridico/dashboard/")
    print_response(response, "Dashboard Jurídico")
    return response.status_code == 200

def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "🚀 INICIANDO BATERIA DE TESTES".center(60, "="))
    print(f"Base URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    
    results = []
    
    # 1. Health Check
    print("\n" + "📍 MÓDULO: HEALTH".center(60, "-"))
    results.append(("Health Check", test_health()))
    
    # 2. Autenticação
    print("\n" + "📍 MÓDULO: AUTENTICAÇÃO".center(60, "-"))
    token = test_login()
    if token:
        results.append(("Login", True))
        results.append(("Auth Me", test_auth_me(token)))
    else:
        results.append(("Login", False))
        results.append(("Auth Me", False))
    
    # 3. Clientes
    print("\n" + "📍 MÓDULO: CLIENTES".center(60, "-"))
    clientes = test_list_clientes()
    results.append(("Listar Clientes", True if clientes is not None else False))
    
    cliente_id = test_create_cliente()
    if cliente_id:
        results.append(("Criar Cliente", True))
        results.append(("Criar Contrato", test_create_contrato(cliente_id)))
    else:
        results.append(("Criar Cliente", False))
        results.append(("Criar Contrato", False))
    
    # 4. Financeiro
    print("\n" + "📍 MÓDULO: FINANCEIRO".center(60, "-"))
    results.append(("Listar Lançamentos", test_list_lancamentos()))
    results.append(("Dashboard Financeiro", test_dashboard_financeiro()))
    
    # 5. Contábil
    print("\n" + "📍 MÓDULO: CONTÁBIL".center(60, "-"))
    results.append(("Listar Obrigações", test_list_obrigacoes()))
    
    # 6. Jurídico
    print("\n" + "📍 MÓDULO: JURÍDICO".center(60, "-"))
    results.append(("Listar Processos", test_list_processos()))
    results.append(("Dashboard Jurídico", test_dashboard_juridico()))
    
    # Resumo
    print("\n" + "📊 RESUMO DOS TESTES".center(60, "="))
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    for test_name, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    print(f"{'='*60}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor!")
        print("Certifique-se de que o backend está rodando em http://localhost:8000")
        print("\nPara iniciar o backend, execute:")
        print("  python run.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        exit(1)
