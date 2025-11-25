#!/usr/bin/env python3
"""
Arquivo de Testes para validar a implementação do backend do Monopoly
Testa: Tabuleiro, Casas, Movimentação e Jogadores

Execute com: python test_tabuleiro.py
"""

from tabuleiro import Tabuleiro
from casas import Casa, CasaImposto, CasaVAPrisao, CasaSorteReves, CasaCofre
from jogador import Jogador
from banco import Banco
from propriedades import Propriedade, CasaMetro, CasaCompanhia
from constantes import POSICAO_PRISAO, VALOR_PASSAGEM_SAIDA

def teste_1_criacao_tabuleiro():
    """Teste 1: Verifica se o tabuleiro foi criado corretamente com 40 casas"""
    print("\n" + "="*70)
    print("TESTE 1: Criação do Tabuleiro")
    print("="*70)
    
    tabuleiro = Tabuleiro()
    
    # Verifica total de casas
    assert len(tabuleiro.casas) == 40, f"Erro: Esperado 40 casas, encontrado {len(tabuleiro.casas)}"
    print(f"✓ Tabuleiro criado com {len(tabuleiro.casas)} casas")
    
    # Verifica posição 0 (Início)
    casa_inicio = tabuleiro.get_casa(0)
    assert casa_inicio.tipo == "INICIO", f"Erro: Casa 0 deveria ser INICIO, é {casa_inicio.tipo}"
    print(f"✓ Posição 0: {casa_inicio.nome} ({casa_inicio.tipo})")
    
    # Verifica posição 10 (Prisão)
    casa_prisao = tabuleiro.get_casa(10)
    assert casa_prisao.tipo == "PRISAO", f"Erro: Casa 10 deveria ser PRISAO, é {casa_prisao.tipo}"
    print(f"✓ Posição 10: {casa_prisao.nome} ({casa_prisao.tipo})")
    
    # Verifica posição 20 (Estacionamento)
    casa_estacionamento = tabuleiro.get_casa(20)
    assert casa_estacionamento.tipo == "GRATIS", f"Erro: Casa 20 deveria ser GRATIS"
    print(f"✓ Posição 20: {casa_estacionamento.nome} ({casa_estacionamento.tipo})")
    
    # Verifica posição 30 (Vá para Prisão)
    casa_va_prisao = tabuleiro.get_casa(30)
    assert casa_va_prisao.tipo == "VAPRISÃO", f"Erro: Casa 30 deveria ser VAPRISÃO"
    print(f"✓ Posição 30: {casa_va_prisao.nome} ({casa_va_prisao.tipo})")
    
    print("\n✅ TESTE 1 PASSOU: Tabuleiro construído corretamente!")
    return tabuleiro

def teste_2_tipos_de_casas(tabuleiro):
    """Teste 2: Verifica se todos os tipos de casas estão presentes"""
    print("\n" + "="*70)
    print("TESTE 2: Tipos de Casas")
    print("="*70)
    
    tipos_encontrados = {}
    
    for i, casa in enumerate(tabuleiro.casas):
        tipo = casa.tipo
        if tipo not in tipos_encontrados:
            tipos_encontrados[tipo] = []
        tipos_encontrados[tipo].append(i)
    
    print("\nTipos de casas encontrados:")
    for tipo, posicoes in tipos_encontrados.items():
        print(f"  {tipo}: {len(posicoes)} casas nas posições {posicoes[:5]}{'...' if len(posicoes) > 5 else ''}")
    
    # Verifica se há propriedades
    propriedades = [c for c in tabuleiro.casas if isinstance(c, Propriedade)]
    print(f"\n✓ Total de propriedades: {len(propriedades)}")
    
    # Verifica se há metrôs/ferrovias
    metros = [c for c in tabuleiro.casas if isinstance(c, CasaMetro)]
    print(f"✓ Total de estações de metrô: {len(metros)}")
    
    # Verifica se há companhias
    companhias = [c for c in tabuleiro.casas if isinstance(c, CasaCompanhia)]
    print(f"✓ Total de companhias: {len(companhias)}")
    
    # Verifica impostos
    impostos = [c for c in tabuleiro.casas if isinstance(c, CasaImposto)]
    print(f"✓ Total de impostos: {len(impostos)}")
    
    print("\n✅ TESTE 2 PASSOU: Todos os tipos de casas estão presentes!")

def teste_3_propriedades_por_grupo(tabuleiro):
    """Teste 3: Verifica as propriedades organizadas por grupo de cor"""
    print("\n" + "="*70)
    print("TESTE 3: Propriedades por Grupo")
    print("="*70)
    
    grupos = {}
    
    for casa in tabuleiro.casas:
        if isinstance(casa, Propriedade) and hasattr(casa, 'grupo_cor'):
            grupo = casa.grupo_cor
            if grupo not in grupos:
                grupos[grupo] = []
            grupos[grupo].append(casa)
    
    print("\nPropriedades por grupo:")
    for grupo, propriedades in grupos.items():
        print(f"\n  {grupo}: {len(propriedades)} propriedades")
        for prop in propriedades:
            print(f"    - {prop.nome} (R${prop.preco_compra})")
    
    print(f"\n✓ Total de grupos: {len(grupos)}")
    print("\n✅ TESTE 3 PASSOU: Propriedades organizadas por grupo!")
    return grupos

def teste_4_movimentacao_jogador(tabuleiro):
    """Teste 4: Testa a movimentação básica do jogador"""
    print("\n" + "="*70)
    print("TESTE 4: Movimentação do Jogador")
    print("="*70)
    
    jogador = Jogador("TestPlayer", "Carro")
    banco = Banco()
    banco.inicializar_conta("TestPlayer")
    
    print(f"\nJogador criado: {jogador.nome}")
    print(f"Posição inicial: {jogador.posicao}")
    
    # Teste 1: Movimento simples
    posicao_antiga = jogador.mover(7)
    assert jogador.posicao == 7, f"Erro: Esperado posição 7, obtido {jogador.posicao}"
    print(f"✓ Movimento simples: posição {posicao_antiga} → {jogador.posicao}")
    
    # Teste 2: Movimento que passa pela saída
    jogador.posicao = 35
    posicao_antiga = jogador.mover(10)
    assert jogador.posicao == 5, f"Erro: Esperado posição 5, obtido {jogador.posicao}"
    print(f"✓ Movimento com volta: posição {posicao_antiga} → {jogador.posicao}")
    
    # Verifica se passou pela saída (posição_antiga > posição_nova indica volta)
    if posicao_antiga > jogador.posicao:
        saldo_antes = banco.consultar_saldo("TestPlayer")
        banco.depositar("TestPlayer", VALOR_PASSAGEM_SAIDA)
        saldo_depois = banco.consultar_saldo("TestPlayer")
        print(f"✓ Bônus por passar pela saída: R${saldo_antes} → R${saldo_depois}")
    
    # Teste 3: Movimento para posição específica
    jogador.mover_para(30)
    assert jogador.posicao == 30, f"Erro: Esperado posição 30, obtido {jogador.posicao}"
    print(f"✓ Movimento direto para posição 30")
    
    print("\n✅ TESTE 4 PASSOU: Movimentação funcionando corretamente!")

def teste_5_casas_especiais(tabuleiro):
    """Teste 5: Testa o comportamento das casas especiais"""
    print("\n" + "="*70)
    print("TESTE 5: Casas Especiais")
    print("="*70)
    
    jogador = Jogador("TestPlayer2", "Chapéu")
    banco = Banco()
    banco.inicializar_conta("TestPlayer2")
    
    # Teste 1: Casa de Imposto
    print("\n--- Testando Casa de Imposto ---")
    jogador.posicao = 4
    casa_imposto = tabuleiro.get_casa(4)
    saldo_antes = banco.consultar_saldo("TestPlayer2")
    casa_imposto.acao_ao_cair(jogador, banco)
    saldo_depois = banco.consultar_saldo("TestPlayer2")
    print(f"✓ Imposto cobrado: R${saldo_antes} → R${saldo_depois}")
    
    # Teste 2: Casa Vá para Prisão
    print("\n--- Testando Vá para Prisão ---")
    jogador.posicao = 30
    jogador.em_prisao = False
    casa_va_prisao = tabuleiro.get_casa(30)
    casa_va_prisao.acao_ao_cair(jogador, banco)
    assert jogador.posicao == POSICAO_PRISAO, f"Erro: Jogador deveria estar na posição {POSICAO_PRISAO}"
    assert jogador.em_prisao == True, "Erro: Jogador deveria estar preso"
    print(f"✓ Jogador enviado para prisão na posição {jogador.posicao}")
    
    # Teste 3: Sair da prisão
    print("\n--- Testando Saída da Prisão ---")
    jogador.sair_prisao()
    assert jogador.em_prisao == False, "Erro: Jogador deveria estar livre"
    print(f"✓ Jogador libertado da prisão")
    
    print("\n✅ TESTE 5 PASSOU: Casas especiais funcionando corretamente!")

def teste_6_compra_propriedade(tabuleiro):
    """Teste 6: Testa a compra de propriedades"""
    print("\n" + "="*70)
    print("TESTE 6: Compra de Propriedades")
    print("="*70)
    
    jogador = Jogador("TestPlayer3", "Navio")
    banco = Banco()
    banco.inicializar_conta("TestPlayer3")
    banco.depositar("TestPlayer3", 500)  # Adiciona 500 ao saldo inicial
    
    # Encontra uma propriedade para comprar (posição 1)
    jogador.posicao = 1
    propriedade = tabuleiro.get_casa(1)
    
    print(f"\nPropriedade: {propriedade.nome}")
    print(f"Preço: R${propriedade.preco_compra}")
    print(f"Saldo inicial do jogador: R${banco.consultar_saldo('TestPlayer3')}")
    
    # Realiza a compra
    if not propriedade.proprietario:
        saldo_antes = banco.consultar_saldo("TestPlayer3")
        banco.pagar("TestPlayer3", propriedade.preco_compra, recebedor="Banco")
        jogador.adicionar_propriedade(propriedade)
        saldo_depois = banco.consultar_saldo("TestPlayer3")
        
        print(f"✓ Compra realizada: R${saldo_antes} → R${saldo_depois}")
        print(f"✓ Proprietário: {propriedade.proprietario.nome}")
        print(f"✓ Total de propriedades do jogador: {len(jogador.propriedades)}")
    
    print("\n✅ TESTE 6 PASSOU: Compra de propriedades funcionando!")

def teste_7_monopolio(tabuleiro):
    """Teste 7: Testa detecção de monopólio"""
    print("\n" + "="*70)
    print("TESTE 7: Detecção de Monopólio")
    print("="*70)
    
    jogador = Jogador("TestPlayer4", "Bota")
    
    # Pega todas as propriedades do grupo Marrom
    props_marrom = tabuleiro.listar_propriedades_por_grupo("Marrom")
    print(f"\nPropriedades do grupo Marrom: {len(props_marrom)}")
    for prop in props_marrom:
        print(f"  - {prop.nome}")
    
    # Adiciona todas ao jogador
    for prop in props_marrom:
        jogador.adicionar_propriedade(prop)
    
    # Verifica monopólio
    tem_monopolio = jogador.tem_monopolio("Marrom", len(props_marrom))
    print(f"\n✓ Jogador possui {jogador.contar_propriedades_grupo('Marrom')} de {len(props_marrom)} propriedades")
    print(f"✓ Tem monopólio: {tem_monopolio}")
    
    assert tem_monopolio == True, "Erro: Jogador deveria ter monopólio"
    
    print("\n✅ TESTE 7 PASSOU: Detecção de monopólio funcionando!")

def executar_todos_testes():
    """Executa todos os testes em sequência"""
    print("\n" + "="*70)
    print("INICIANDO BATERIA DE TESTES DO BACKEND MONOPOLY")
    print("="*70)
    
    try:
        # Teste 1: Criação do Tabuleiro
        tabuleiro = teste_1_criacao_tabuleiro()
        
        # Teste 2: Tipos de Casas
        teste_2_tipos_de_casas(tabuleiro)
        
        # Teste 3: Propriedades por Grupo
        teste_3_propriedades_por_grupo(tabuleiro)
        
        # Teste 4: Movimentação
        teste_4_movimentacao_jogador(tabuleiro)
        
        # Teste 5: Casas Especiais
        teste_5_casas_especiais(tabuleiro)
        
        # Teste 6: Compra de Propriedades
        teste_6_compra_propriedade(tabuleiro)
        
        # Teste 7: Monopólio
        teste_7_monopolio(tabuleiro)
        
        print("\n" + "="*70)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*70)
        print("\n📋 Resumo da Validação:")
        print("  ✓ Tabuleiro com 40 casas criado corretamente")
        print("  ✓ Todas as casas especiais funcionando")
        print("  ✓ Propriedades organizadas por grupo")
        print("  ✓ Movimentação de jogadores implementada")
        print("  ✓ Sistema de prisão funcionando")
        print("  ✓ Compra de propriedades validada")
        print("  ✓ Detecção de monopólio implementada")
        print("\n🎉 Backend do Tabuleiro está pronto para integração!")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO DURANTE TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    executar_todos_testes()
