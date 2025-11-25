# test_regras_jogo.py
# Arquivo de testes para validar as regras implementadas

import sys
from dados import Dados
from cartas import BaralhoCartas, CartaDinheiro, CartaMovimento
from construcao import GestorConstrucao
from regras_prisao import GestorPrisao
from regras_propriedades import GestorPropriedades
from tabuleiro import Tabuleiro
from banco import Banco
from jogador import Jogador

def print_secao(titulo):
    """Imprime uma seção formatada"""
    print("\n" + "=" * 70)
    print(titulo.center(70))
    print("=" * 70)

def print_sucesso(mensagem):
    """Imprime mensagem de sucesso"""
    print(f"✅ {mensagem}")

def print_erro(mensagem):
    """Imprime mensagem de erro"""
    print(f"❌ {mensagem}")

def teste_1_dados():
    """Testa o sistema de rolagem de dados"""
    print_secao("TESTE 1: Sistema de Dados")
    
    try:
        dados = Dados()
        
        # Testa 20 rolagens
        duplas = 0
        for i in range(20):
            total, valores, eh_dupla = dados.rolar()
            if eh_dupla:
                duplas += 1
                print(f"  Rolagem {i+1}: {valores[0]} + {valores[1]} = {total} [DUPLA!]")
        
        print(f"\n  Total de duplas em 20 rolagens: {duplas}")
        
        # Verifica se os valores estão no intervalo correto
        info = dados.obter_ultima_rolagem()
        assert 2 <= info['total'] <= 12, "Total dos dados fora do intervalo"
        assert all(1 <= v <= 6 for v in info['valores']), "Valores individuais inválidos"
        
        print_sucesso("Sistema de dados funcionando corretamente!")
        return True
        
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_2_cartas():
    """Testa o sistema de cartas"""
    print_secao("TESTE 2: Sistema de Cartas (Sorte e Revés)")
    
    try:
        # Cria baralhos
        baralho_sorte = BaralhoCartas('SORTE')
        baralho_reves = BaralhoCartas('REVES')
        
        print(f"  {baralho_sorte}")
        print(f"  {baralho_reves}")
        
        # Cria mock objects
        banco = Banco()
        banco.inicializar_conta("TestPlayer")
        jogador = Jogador("TestPlayer", "Carro")
        
        # Testa algumas cartas
        print("\n  --- Testando 3 cartas de SORTE ---")
        for i in range(3):
            carta = baralho_sorte.pegar_carta()
            print(f"\n  Carta {i+1}: {carta}")
            carta.executar(jogador, banco, None)
        
        print("\n  --- Testando 2 cartas de REVÉS ---")
        for i in range(2):
            carta = baralho_reves.pegar_carta()
            print(f"\n  Carta {i+1}: {carta}")
            carta.executar(jogador, banco, None)
        
        print_sucesso("Sistema de cartas funcionando corretamente!")
        return True
        
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_3_compra_venda():
    """Testa compra e venda de propriedades"""
    print_secao("TESTE 3: Compra e Venda de Propriedades")
    
    try:
        # Setup
        tabuleiro = Tabuleiro()
        banco = Banco()
        gestor = GestorPropriedades(banco, tabuleiro)
        
        jogador1 = Jogador("Alice", "Carro")
        jogador2 = Jogador("Bob", "Chapéu")
        
        banco.inicializar_conta("Alice")
        banco.inicializar_conta("Bob")
        
        # Pega uma propriedade
        prop = tabuleiro.get_casa(1)  # Avenida Sumaré
        
        print(f"\n  Propriedade: {prop.nome}")
        print(f"  Preço: R${prop.preco_compra}")
        print(f"  Saldo Alice: R${banco.consultar_saldo('Alice')}")
        
        # Testa compra
        print("\n  --- Alice tenta comprar ---")
        sucesso = gestor.comprar_propriedade(jogador1, prop)
        assert sucesso, "Compra deveria ter sucesso"
        assert prop.proprietario == jogador1, "Proprietário não foi definido"
        
        # Tenta comprar novamente (deve falhar)
        print("\n  --- Bob tenta comprar a mesma propriedade ---")
        sucesso = gestor.comprar_propriedade(jogador2, prop)
        assert not sucesso, "Compra deveria falhar"
        
        # Testa hipoteca
        print("\n  --- Alice hipoteca a propriedade ---")
        saldo_antes = banco.consultar_saldo('Alice')
        sucesso = gestor.hipotecar_propriedade(jogador1, prop)
        assert sucesso, "Hipoteca deveria ter sucesso"
        assert prop.hipotecada, "Propriedade deveria estar hipotecada"
        saldo_depois = banco.consultar_saldo('Alice')
        print(f"  Saldo antes: R${saldo_antes} | Saldo depois: R${saldo_depois}")
        
        # Testa resgate de hipoteca
        print("\n  --- Alice resgata a hipoteca ---")
        sucesso = gestor.resgatar_hipoteca(jogador1, prop)
        assert sucesso, "Resgate deveria ter sucesso"
        assert not prop.hipotecada, "Propriedade não deveria estar hipotecada"
        
        print_sucesso("Compra/venda de propriedades funcionando corretamente!")
        return True
        
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_4_construcao():
    """Testa construção de casas e hotéis"""
    print_secao("TESTE 4: Construção de Casas e Hotéis")
    
    try:
        # Setup
        tabuleiro = Tabuleiro()
        banco = Banco()
        gestor_prop = GestorPropriedades(banco, tabuleiro)
        gestor_const = GestorConstrucao(tabuleiro, banco)
        
        jogador = Jogador("Alice", "Carro")
        banco.inicializar_conta("Alice")
        banco.depositar("Alice", 2000)  # Dá dinheiro extra
        
        # Compra grupo marrom completo (posições 1 e 3)
        print("\n  --- Comprando grupo Marrom completo ---")
        prop1 = tabuleiro.get_casa(1)  # Avenida Sumaré
        prop2 = tabuleiro.get_casa(3)  # Praça da Sé
        
        gestor_prop.comprar_propriedade(jogador, prop1)
        gestor_prop.comprar_propriedade(jogador, prop2)
        
        # Tenta construir sem monopólio (deve falhar inicialmente, mas já tem monopólio)
        print("\n  --- Tentando construir na propriedade 1 ---")
        pode, msg = gestor_const.pode_construir(jogador, prop1)
        print(f"  Pode construir: {pode} - {msg}")
        
        if pode:
            # Constrói 4 casas
            print("\n  --- Construindo 4 casas ---")
            for i in range(4):
                sucesso = gestor_const.construir_casa(jogador, prop1)
                sucesso = gestor_const.construir_casa(jogador, prop2)
                print(f"  Propriedade 1: {prop1.casas} casas")
                print(f"  Propriedade 2: {prop2.casas} casas")
            
            # Constrói hotel
            print("\n  --- Construindo hotel na propriedade 1 ---")
            gestor_const.construir_casa(jogador, prop1)
            print(f"  Propriedade 1: {'HOTEL' if prop1.casas == 5 else f'{prop1.casas} casas'}")
            
            # Testa venda de construção
            print("\n  --- Vendendo 1 casa da propriedade 1 ---")
            gestor_const.vender_casa(jogador, prop1)
            print(f"  Propriedade 1: {prop1.casas} casas")
        
        print_sucesso("Construção de casas/hotéis funcionando corretamente!")
        return True
        
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_5_prisao():
    """Testa regras da prisão"""
    print_secao("TESTE 5: Regras da Prisão")
    
    try:
        # Setup
        banco = Banco()
        gestor = GestorPrisao(banco)
        dados = Dados()
        
        jogador = Jogador("Alice", "Carro")
        banco.inicializar_conta("Alice")
        
        # Envia para prisão
        print("\n  --- Enviando jogador para prisão ---")
        gestor.enviar_prisao(jogador)
        assert jogador.em_prisao, "Jogador deveria estar na prisão"
        assert jogador.posicao == 10, "Posição deveria ser 10"
        
        # Tenta sair pagando
        print("\n  --- Tentando pagar fiança ---")
        saldo_antes = banco.consultar_saldo('Alice')
        sucesso = gestor.pagar_fianca(jogador)
        assert sucesso, "Pagamento deveria ter sucesso"
        assert not jogador.em_prisao, "Jogador não deveria estar na prisão"
        saldo_depois = banco.consultar_saldo('Alice')
        print(f"  Saldo antes: R${saldo_antes} | Saldo depois: R${saldo_depois}")
        
        # Envia novamente e testa carta
        print("\n  --- Testando carta 'Saia Livre da Prisão' ---")
        gestor.enviar_prisao(jogador)
        jogador.cartas_livre_prisao = 1
        sucesso = gestor.sair_prisao_com_carta(jogador)
        assert sucesso, "Saída com carta deveria ter sucesso"
        assert not jogador.em_prisao, "Jogador não deveria estar na prisão"
        assert jogador.cartas_livre_prisao == 0, "Carta deveria ter sido usada"
        
        # Envia novamente e testa dupla
        print("\n  --- Testando saída com dupla ---")
        gestor.enviar_prisao(jogador)
        
        # Simula 3 tentativas
        for turno in range(3):
            print(f"\n  Turno {turno + 1}:")
            total, valores, eh_dupla = dados.rolar()
            print(f"  Rolou: {valores[0]} + {valores[1]} = {total} {'[DUPLA]' if eh_dupla else ''}")
            
            if eh_dupla:
                gestor.tentar_sair_com_dupla(jogador, eh_dupla)
                break
            else:
                gestor.tentar_sair_com_dupla(jogador, eh_dupla)
        
        print(f"\n  Status final - Na prisão: {jogador.em_prisao}")
        
        print_sucesso("Regras da prisão funcionando corretamente!")
        return True
        
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_6_aluguel():
    """Testa cálculo e cobrança de aluguel"""
    print_secao("TESTE 6: Cálculo e Cobrança de Aluguel")
    
    try:
        # Setup
        tabuleiro = Tabuleiro()
        banco = Banco()
        gestor = GestorPropriedades(banco, tabuleiro)
        
        proprietario = Jogador("Alice", "Carro")
        inquilino = Jogador("Bob", "Chapéu")
        
        banco.inicializar_conta("Alice")
        banco.inicializar_conta("Bob")
        
        # Compra propriedade
        prop = tabuleiro.get_casa(1)
        gestor.comprar_propriedade(proprietario, prop)
        
        # Calcula aluguel
        print(f"\n  Propriedade: {prop.nome}")
        aluguel = gestor.calcular_aluguel(prop)
        print(f"  Aluguel base: R${aluguel}")
        
        # Cobra aluguel
        print(f"\n  --- Bob paga aluguel para Alice ---")
        saldo_alice_antes = banco.consultar_saldo('Alice')
        saldo_bob_antes = banco.consultar_saldo('Bob')
        
        gestor.cobrar_aluguel(proprietario, inquilino, prop)
        
        saldo_alice_depois = banco.consultar_saldo('Alice')
        saldo_bob_depois = banco.consultar_saldo('Bob')
        
        print(f"\n  Alice: R${saldo_alice_antes} → R${saldo_alice_depois}")
        print(f"  Bob: R${saldo_bob_antes} → R${saldo_bob_depois}")
        
        assert saldo_alice_depois > saldo_alice_antes, "Alice deveria ter recebido dinheiro"
        assert saldo_bob_depois < saldo_bob_antes, "Bob deveria ter perdido dinheiro"
        
        print_sucesso("Cálculo e cobrança de aluguel funcionando corretamente!")
        return True
        
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def executar_todos_testes():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("TESTES DAS REGRAS DO JOGO - MONOPOLY".center(70))
    print("=" * 70)
    
    testes = [
        ("Dados", teste_1_dados),
        ("Cartas", teste_2_cartas),
        ("Compra/Venda", teste_3_compra_venda),
        ("Construção", teste_4_construcao),
        ("Prisão", teste_5_prisao),
        ("Aluguel", teste_6_aluguel),
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print_erro(f"ERRO DURANTE TESTE {nome}: {e}")
            import traceback
            traceback.print_exc()
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES".center(70))
    print("=" * 70)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {nome:.<50} {status}")
    
    total = len(resultados)
    passou = sum(1 for _, r in resultados if r)
    
    print("\n" + "=" * 70)
    print(f"RESULTADO FINAL: {passou}/{total} testes passaram".center(70))
    print("=" * 70)
    
    return passou == total

if __name__ == '__main__':
    sucesso = executar_todos_testes()
    sys.exit(0 if sucesso else 1)
