# test_transacoes.py
# Testes completos para o sistema de transações financeiras

from banco import Banco
from jogador import Jogador
from transacoes import GerenciadorTransacoes
from propriedades import Propriedade
from constantes import (
    VALOR_PASSAGEM_SAIDA,
    IMPOSTO_RENDA_VALOR,
    TAXA_RIQUEZA_VALOR,
    MULTA_SAIDA_PRISAO
)

def teste_1_pagamento_aluguel():
    """Testa pagamento de aluguel entre jogadores"""
    print("\n" + "="*60)
    print("TESTE 1: PAGAMENTO DE ALUGUEL")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Alice")
    banco.inicializar_conta("Bob")
    
    jogador1 = Jogador("Alice", "Chapéu")
    jogador2 = Jogador("Bob", "Carro")
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # Bob paga aluguel para Alice
    sucesso = transacoes.pagar_aluguel(jogador2, jogador1, 200)
    
    print("\n--- Saldo Final ---")
    banco.status_contas()
    
    if sucesso and banco.consultar_saldo("Alice") == 1700 and banco.consultar_saldo("Bob") == 1300:
        print("\n✓ TESTE 1 PASSOU")
        return True
    else:
        print("\n✗ TESTE 1 FALHOU")
        return False

def teste_2_pagamento_impostos():
    """Testa pagamento de impostos e taxas ao banco"""
    print("\n" + "="*60)
    print("TESTE 2: PAGAMENTO DE IMPOSTOS E TAXAS")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Carlos")
    jogador = Jogador("Carlos", "Navio")
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # Paga imposto de renda
    sucesso1 = transacoes.pagar_imposto(jogador, IMPOSTO_RENDA_VALOR, "Imposto de Renda")
    
    # Paga taxa de riqueza
    sucesso2 = transacoes.pagar_imposto(jogador, TAXA_RIQUEZA_VALOR, "Taxa de Riqueza")
    
    print("\n--- Saldo Final ---")
    banco.status_contas()
    
    saldo_esperado = 1500 - IMPOSTO_RENDA_VALOR - TAXA_RIQUEZA_VALOR
    
    if sucesso1 and sucesso2 and banco.consultar_saldo("Carlos") == saldo_esperado:
        print("\n✓ TESTE 2 PASSOU")
        return True
    else:
        print("\n✗ TESTE 2 FALHOU")
        return False

def teste_3_recebimento_salario():
    """Testa recebimento de salário ao passar pela saída"""
    print("\n" + "="*60)
    print("TESTE 3: RECEBIMENTO DE SALÁRIO")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Diana")
    jogadora = Jogador("Diana", "Bota")
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # Recebe salário 3 vezes
    transacoes.receber_salario_saida(jogadora)
    transacoes.receber_salario_saida(jogadora)
    transacoes.receber_salario_saida(jogadora)
    
    print("\n--- Saldo Final ---")
    banco.status_contas()
    
    saldo_esperado = 1500 + (VALOR_PASSAGEM_SAIDA * 3)
    
    if banco.consultar_saldo("Diana") == saldo_esperado:
        print("\n✓ TESTE 3 PASSOU")
        return True
    else:
        print("\n✗ TESTE 3 FALHOU")
        return False

def teste_4_premios_e_transferencias():
    """Testa recebimento de prêmios e transferências entre jogadores"""
    print("\n" + "="*60)
    print("TESTE 4: PRÊMIOS E TRANSFERÊNCIAS")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Eva")
    banco.inicializar_conta("Frank")
    
    jogador1 = Jogador("Eva", "Dedal")
    jogador2 = Jogador("Frank", "Ferro")
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # Eva recebe prêmio
    transacoes.receber_premio(jogador1, 100, "Ganhou concurso de beleza")
    
    # Frank recebe prêmio
    transacoes.receber_premio(jogador2, 50, "Carta de sorte")
    
    # Eva transfere para Frank
    transacoes.transferir_entre_jogadores(jogador1, jogador2, 150, "Acordo comercial")
    
    print("\n--- Saldo Final ---")
    banco.status_contas()
    
    # Eva: 1500 + 100 - 150 = 1450
    # Frank: 1500 + 50 + 150 = 1700
    
    if banco.consultar_saldo("Eva") == 1450 and banco.consultar_saldo("Frank") == 1700:
        print("\n✓ TESTE 4 PASSOU")
        return True
    else:
        print("\n✗ TESTE 4 FALHOU")
        return False

def teste_5_multa_prisao():
    """Testa pagamento de multa da prisão"""
    print("\n" + "="*60)
    print("TESTE 5: MULTA DA PRISÃO")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("George")
    jogador = Jogador("George", "Cachorro")
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # George vai para a prisão
    jogador.entrar_prisao()
    
    # George paga multa para sair
    sucesso = transacoes.pagar_multa_prisao(jogador)
    
    print("\n--- Saldo Final ---")
    banco.status_contas()
    
    saldo_esperado = 1500 - MULTA_SAIDA_PRISAO
    
    if sucesso and not jogador.em_prisao and banco.consultar_saldo("George") == saldo_esperado:
        print("\n✓ TESTE 5 PASSOU")
        return True
    else:
        print("\n✗ TESTE 5 FALHOU")
        return False

def teste_6_hipoteca_propriedade():
    """Testa hipoteca e deshipoteca de propriedade"""
    print("\n" + "="*60)
    print("TESTE 6: HIPOTECA E DESHIPOTECA")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Helena")
    jogadora = Jogador("Helena", "Carrinho")
    
    # Cria uma propriedade simulada
    propriedade = Propriedade("Avenida Atlântica", 400, [50, 100, 150], "Amarelo")
    propriedade.hipotecada = False
    jogadora.adicionar_propriedade(propriedade)
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # Hipoteca a propriedade (recebe 200 = 400 / 2)
    transacoes.hipotecar_propriedade(jogadora, propriedade)
    
    saldo_apos_hipoteca = banco.consultar_saldo("Helena")
    print(f"\nSaldo após hipoteca: R${saldo_apos_hipoteca}")
    
    # Deshipoteca (paga 220 = 200 + 10%)
    transacoes.pagar_deshipoteca(jogadora, propriedade)
    
    print("\n--- Saldo Final ---")
    banco.status_contas()
    
    # 1500 + 200 - 220 = 1480
    saldo_esperado = 1480
    
    if not propriedade.hipotecada and banco.consultar_saldo("Helena") == saldo_esperado:
        print("\n✓ TESTE 6 PASSOU")
        return True
    else:
        print("\n✗ TESTE 6 FALHOU")
        return False

def teste_7_saldo_insuficiente():
    """Testa transações com saldo insuficiente"""
    print("\n" + "="*60)
    print("TESTE 7: SALDO INSUFICIENTE")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Igor")
    jogador = Jogador("Igor", "Sapato")
    
    print("\n--- Saldo Inicial ---")
    banco.status_contas()
    
    # Tenta pagar valor maior que o saldo
    sucesso = transacoes.pagar_imposto(jogador, 2000, "Imposto impossível")
    
    print("\n--- Saldo Final (deve estar intacto) ---")
    banco.status_contas()
    
    # Saldo deve continuar 1500
    if not sucesso and banco.consultar_saldo("Igor") == 1500:
        print("\n✓ TESTE 7 PASSOU - Transação bloqueada corretamente")
        return True
    else:
        print("\n✗ TESTE 7 FALHOU")
        return False

def teste_8_historico_transacoes():
    """Testa o histórico de transações"""
    print("\n" + "="*60)
    print("TESTE 8: HISTÓRICO DE TRANSAÇÕES")
    print("="*60)
    
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    banco.inicializar_conta("Julia")
    banco.inicializar_conta("Kevin")
    
    jogador1 = Jogador("Julia", "Gato")
    jogador2 = Jogador("Kevin", "Battleship")
    
    # Realiza várias transações
    transacoes.receber_salario_saida(jogador1)
    transacoes.pagar_aluguel(jogador2, jogador1, 100)
    transacoes.pagar_imposto(jogador1, 50, "Taxa")
    transacoes.receber_premio(jogador2, 75, "Prêmio")
    
    # Verifica histórico
    transacoes.imprimir_historico()
    
    historico = transacoes.obter_historico()
    
    if len(historico) == 4:
        print("\n✓ TESTE 8 PASSOU - 4 transações registradas")
        return True
    else:
        print(f"\n✗ TESTE 8 FALHOU - Esperado 4 transações, encontrado {len(historico)}")
        return False

def executar_todos_testes():
    """Executa todos os testes e mostra resultados"""
    print("\n" + "="*70)
    print(" "*15 + "SUITE DE TESTES - TRANSAÇÕES FINANCEIRAS")
    print("="*70)
    
    testes = [
        teste_1_pagamento_aluguel,
        teste_2_pagamento_impostos,
        teste_3_recebimento_salario,
        teste_4_premios_e_transferencias,
        teste_5_multa_prisao,
        teste_6_hipoteca_propriedade,
        teste_7_saldo_insuficiente,
        teste_8_historico_transacoes
    ]
    
    resultados = []
    
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
        except Exception as e:
            print(f"\n✗ ERRO DURANTE TESTE: {e}")
            import traceback
            traceback.print_exc()
            resultados.append(False)
    
    # Resumo final
    print("\n\n" + "="*70)
    print(" "*25 + "RESUMO DOS TESTES")
    print("="*70)
    
    passou = sum(resultados)
    total = len(resultados)
    
    for i, resultado in enumerate(resultados, 1):
        status = "✓ PASSOU" if resultado else "✗ FALHOU"
        print(f"Teste {i}: {status}")
    
    print("\n" + "-"*70)
    print(f"TOTAL: {passou}/{total} testes passaram ({passou/total*100:.1f}%)")
    print("="*70 + "\n")

if __name__ == '__main__':
    executar_todos_testes()
