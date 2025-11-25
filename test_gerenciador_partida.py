"""
Testes para o Gerenciador de Partidas
Valida inicialização, condições de vitória/derrota e regras do jogo
"""

from gerenciador_partida import GerenciadorPartida, EstadoPartida, TipoVitoria
from validador_regras import ValidadorRegras


def teste_1_criacao_partida():
    """Testa criação básica de uma partida"""
    print("=" * 70)
    print("TESTE 1: Criação de Partida")
    print("=" * 70)
    
    try:
        # Criar partida com 4 jogadores
        nomes = ["Alice", "Bob", "Carlos", "Diana"]
        partida = GerenciadorPartida(nomes, saldo_inicial=1500)
        
        # Verificações
        assert len(partida.jogadores) == 4, "Deveria ter 4 jogadores"
        assert partida.estado == EstadoPartida.NAO_INICIADA, "Estado inicial incorreto"
        assert partida.turno_numero == 0, "Turno deveria ser 0"
        
        # Verificar saldos iniciais
        for nome in nomes:
            saldo = partida.banco.consultar_saldo(nome)
            assert saldo == 1500, f"Saldo inicial de {nome} deveria ser 1500, mas é {saldo}"
        
        print("✓ Partida criada com sucesso")
        print(f"✓ 4 jogadores inicializados corretamente")
        print(f"✓ Estado inicial: {partida.estado}")
        print(f"✓ Saldos iniciais verificados")
        
        return partida
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None


def teste_2_iniciar_partida():
    """Testa o início oficial da partida"""
    print("\n" + "=" * 70)
    print("TESTE 2: Início de Partida")
    print("=" * 70)
    
    try:
        partida = GerenciadorPartida(["Jogador1", "Jogador2"])
        
        # Iniciar partida
        sucesso = partida.iniciar_partida()
        assert sucesso == True, "Deveria iniciar com sucesso"
        assert partida.estado == EstadoPartida.EM_ANDAMENTO, "Estado deveria ser EM_ANDAMENTO"
        assert partida.data_inicio is not None, "Data de início deveria estar definida"
        
        # Tentar iniciar novamente (não deve permitir)
        sucesso2 = partida.iniciar_partida()
        assert sucesso2 == False, "Não deveria permitir iniciar duas vezes"
        
        print("✓ Partida iniciada corretamente")
        print(f"✓ Estado: {partida.estado}")
        print(f"✓ Data de início: {partida.data_inicio}")
        print("✓ Proteção contra dupla inicialização funcionando")
        
        return partida
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None


def teste_3_condicao_vitoria():
    """Testa as condições de vitória por eliminação"""
    print("\n" + "=" * 70)
    print("TESTE 3: Condições de Vitória")
    print("=" * 70)
    
    try:
        partida = GerenciadorPartida(["Jogador1", "Jogador2", "Jogador3"])
        partida.iniciar_partida()
        
        jogador1 = partida.jogadores[0]
        jogador2 = partida.jogadores[1]
        jogador3 = partida.jogadores[2]
        
        # Simular falência de dois jogadores
        print("\nSimulando falência de Jogador2...")
        partida.banco.ajustar_saldo(jogador2.nome, 0)
        partida.verificar_falencia(jogador2)
        
        assert len(partida.jogadores) == 2, "Deveria ter 2 jogadores ativos"
        assert jogador2 in partida.jogadores_falidos, "Jogador2 deveria estar falido"
        
        print(f"✓ Jogador2 faliu corretamente")
        print(f"✓ Jogadores ativos: {len(partida.jogadores)}")
        
        # Simular falência do terceiro jogador (deveria declarar vencedor)
        print("\nSimulando falência de Jogador3...")
        partida.banco.ajustar_saldo(jogador3.nome, 0)
        partida.verificar_falencia(jogador3)
        
        assert partida.estado == EstadoPartida.FINALIZADA, "Partida deveria ter finalizado"
        assert partida.vencedor == jogador1, "Jogador1 deveria ser o vencedor"
        assert partida.tipo_vitoria == TipoVitoria.ULTIMOS_SOBREVIVENTE, "Tipo de vitória incorreto"
        
        print(f"✓ Partida finalizada corretamente")
        print(f"✓ Vencedor: {partida.vencedor.nome}")
        print(f"✓ Tipo de vitória: {partida.tipo_vitoria}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_4_validacao_regras():
    """Testa o validador de regras"""
    print("\n" + "=" * 70)
    print("TESTE 4: Validação de Regras")
    print("=" * 70)
    
    try:
        partida = GerenciadorPartida(["Alice", "Bob"])
        partida.iniciar_partida()
        
        alice = partida.jogadores[0]
        bob = partida.jogadores[1]
        
        # Pegar uma propriedade do tabuleiro
        propriedade = partida.tabuleiro.get_casa(1)  # Avenida Sumaré
        
        # Teste 1: Validar compra válida
        valido, msg = ValidadorRegras.validar_compra_propriedade(alice, propriedade, partida.banco)
        assert valido == True, f"Compra deveria ser válida: {msg}"
        print(f"✓ Validação de compra válida: {msg}")
        
        # Simular compra
        propriedade.proprietario = alice
        alice.adicionar_propriedade(propriedade)
        
        # Teste 2: Validar compra de propriedade já comprada (deve falhar)
        valido, msg = ValidadorRegras.validar_compra_propriedade(bob, propriedade, partida.banco)
        assert valido == False, "Compra deveria ser inválida (já tem dono)"
        print(f"✓ Validação de compra inválida: {msg}")
        
        # Teste 3: Validar hipoteca válida
        valido, msg = ValidadorRegras.validar_hipoteca(alice, propriedade)
        assert valido == True, f"Hipoteca deveria ser válida: {msg}"
        print(f"✓ Validação de hipoteca válida: {msg}")
        
        # Teste 4: Validar hipoteca inválida (não é dono)
        valido, msg = ValidadorRegras.validar_hipoteca(bob, propriedade)
        assert valido == False, "Hipoteca deveria ser inválida (não é dono)"
        print(f"✓ Validação de hipoteca inválida: {msg}")
        
        print(f"\n✓ Todas as validações de regras funcionando corretamente")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_5_patrimonio_e_ranking():
    """Testa cálculo de patrimônio e ranking"""
    print("\n" + "=" * 70)
    print("TESTE 5: Patrimônio e Ranking")
    print("=" * 70)
    
    try:
        partida = GerenciadorPartida(["Rico", "Pobre", "Medio"], saldo_inicial=1000)
        partida.iniciar_partida()
        
        rico = partida.jogadores[0]
        pobre = partida.jogadores[1]
        medio = partida.jogadores[2]
        
        # Dar mais dinheiro ao "Rico"
        partida.banco.depositar(rico.nome, 2000)
        
        # Dar propriedades ao "Medio"
        prop1 = partida.tabuleiro.get_casa(1)
        prop2 = partida.tabuleiro.get_casa(3)
        prop1.proprietario = medio
        prop2.proprietario = medio
        medio.adicionar_propriedade(prop1)
        medio.adicionar_propriedade(prop2)
        
        # Calcular patrimônios
        patrimonio_rico = partida._calcular_patrimonio_total(rico)
        patrimonio_pobre = partida._calcular_patrimonio_total(pobre)
        patrimonio_medio = partida._calcular_patrimonio_total(medio)
        
        print(f"\nPatrimônios:")
        print(f"  Rico: R${patrimonio_rico}")
        print(f"  Medio: R${patrimonio_medio}")
        print(f"  Pobre: R${patrimonio_pobre}")
        
        assert patrimonio_rico > patrimonio_pobre, "Rico deveria ter mais que Pobre"
        assert patrimonio_medio > patrimonio_pobre, "Medio deveria ter mais que Pobre"
        
        # Testar ranking
        ranking = partida.obter_ranking_jogadores()
        print(f"\nRanking:")
        for i, info in enumerate(ranking, 1):
            print(f"  {i}. {info['nome']}: R${info['patrimonio']} ({info['propriedades']} propriedades)")
        
        assert ranking[0]['nome'] == "Rico", "Rico deveria estar em primeiro"
        assert len(ranking) == 3, "Deveria ter 3 jogadores no ranking"
        
        print(f"\n✓ Cálculo de patrimônio funcionando")
        print(f"✓ Ranking correto")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_6_pausar_retomar():
    """Testa pausar e retomar partida"""
    print("\n" + "=" * 70)
    print("TESTE 6: Pausar e Retomar")
    print("=" * 70)
    
    try:
        partida = GerenciadorPartida(["Jogador1", "Jogador2"])
        partida.iniciar_partida()
        
        # Pausar
        sucesso = partida.pausar_partida()
        assert sucesso == True, "Deveria pausar com sucesso"
        assert partida.estado == EstadoPartida.PAUSADA, "Estado deveria ser PAUSADA"
        print(f"✓ Partida pausada: {partida.estado}")
        
        # Retomar
        sucesso = partida.retomar_partida()
        assert sucesso == True, "Deveria retomar com sucesso"
        assert partida.estado == EstadoPartida.EM_ANDAMENTO, "Estado deveria ser EM_ANDAMENTO"
        print(f"✓ Partida retomada: {partida.estado}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def executar_todos_testes():
    """Executa todos os testes em sequência"""
    print("\n" + "=" * 70)
    print("INICIANDO BATERIA DE TESTES - GERENCIADOR DE PARTIDA")
    print("=" * 70 + "\n")
    
    resultados = []
    
    # Teste 1
    partida1 = teste_1_criacao_partida()
    resultados.append(("Criação de Partida", partida1 is not None))
    
    # Teste 2
    partida2 = teste_2_iniciar_partida()
    resultados.append(("Início de Partida", partida2 is not None))
    
    # Teste 3
    resultado3 = teste_3_condicao_vitoria()
    resultados.append(("Condições de Vitória", resultado3))
    
    # Teste 4
    resultado4 = teste_4_validacao_regras()
    resultados.append(("Validação de Regras", resultado4))
    
    # Teste 5
    resultado5 = teste_5_patrimonio_e_ranking()
    resultados.append(("Patrimônio e Ranking", resultado5))
    
    # Teste 6
    resultado6 = teste_6_pausar_retomar()
    resultados.append(("Pausar e Retomar", resultado6))
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    for nome, sucesso in resultados:
        status = "✓ PASSOU" if sucesso else "✗ FALHOU"
        print(f"{status} - {nome}")
    
    total = len(resultados)
    passou = sum(1 for _, s in resultados if s)
    
    print(f"\nResultado Final: {passou}/{total} testes passaram")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    executar_todos_testes()
