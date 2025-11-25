# gerenciador_inicializacao.py
# Módulo para gerenciar inicialização do jogo com suporte dinâmico de jogadores (1-6)

import random

class GerenciadorInicializacao:
    """
    Gerencia a inicialização do jogo com suporte a 1-6 jogadores.
    Aloca automaticamente bots para preencher até 6 peões totais.
    """
    
    # Lista de peças disponíveis no Monopoly
    PECAS_DISPONIVEIS = [
        "Chapéu de Cilindro", 
        "Carro Blindado", 
        "Cachorro", 
        "Bota", 
        "Relógio", 
        "Bolsa"
    ]
    
    NOMES_BOTS = [
        "BotSilva", 
        "BotOliveira", 
        "BotCosta", 
        "BotAlves", 
        "BotGomes"
    ]
    
    @staticmethod
    def validar_numero_jogadores(num_jogadores):
        """Valida se o número de jogadores está entre 1 e 6"""
        if not isinstance(num_jogadores, int) or num_jogadores < 1 or num_jogadores > 6:
            raise ValueError("Número de jogadores deve estar entre 1 e 6")
        return True
    
    @staticmethod
    def gerar_lista_jogadores(num_humanos, nomes_humanos=None):
        """
        Gera lista completa de jogadores (humanos + bots).
        
        Args:
            num_humanos: Número de jogadores humanos (1-6)
            nomes_humanos: Lista com nomes dos jogadores humanos (opcional)
            
        Returns:
            list: Lista de tuplas (nome, eh_bot, dificuldade_bot)
        """
        GerenciadorInicializacao.validar_numero_jogadores(num_humanos)
        
        if nomes_humanos is None:
            nomes_humanos = [f"Jogador {i+1}" for i in range(num_humanos)]
        elif len(nomes_humanos) != num_humanos:
            raise ValueError(f"Número de nomes ({len(nomes_humanos)}) não corresponde ao número de jogadores ({num_humanos})")
        
        jogadores = []
        
        # Adiciona jogadores humanos
        for nome in nomes_humanos:
            jogadores.append({
                "nome": nome,
                "eh_bot": False,
                "dificuldade": None,
                "peca": GerenciadorInicializacao.PECAS_DISPONIVEIS[len(jogadores) % len(GerenciadorInicializacao.PECAS_DISPONIVEIS)]
            })
        
        # Adiciona bots para atingir 6 jogadores
        num_bots_necessarios = 6 - num_humanos
        dificuldades = ["facil", "medio", "dificil"]
        
        for i in range(num_bots_necessarios):
            dificuldade = random.choice(dificuldades)
            nome_bot = GerenciadorInicializacao.NOMES_BOTS[i % len(GerenciadorInicializacao.NOMES_BOTS)]
            
            jogadores.append({
                "nome": nome_bot,
                "eh_bot": True,
                "dificuldade": dificuldade,
                "peca": GerenciadorInicializacao.PECAS_DISPONIVEIS[len(jogadores) % len(GerenciadorInicializacao.PECAS_DISPONIVEIS)]
            })
        
        return jogadores
    
    @staticmethod
    def criar_jogadores_no_jogo(jogo, lista_jogadores):
        """
        Cria os jogadores no jogo e registra bots no gerenciador de bots.
        
        Args:
            jogo: Objeto do jogo
            lista_jogadores: Lista gerada por gerar_lista_jogadores()
        """
        for info in lista_jogadores:
            jogador = jogo.jogadores[[j.nome for j in jogo.jogadores].index(info["nome"]) if info["nome"] in [j.nome for j in jogo.jogadores] else -1] if info["nome"] in [j.nome for j in jogo.jogadores] else None
            
            if jogador:
                jogador.is_ia = info["eh_bot"]
                jogador.peca = info["peca"]
                
                if info["eh_bot"]:
                    jogo.gerenciador_bots.criar_bot(info["nome"], info["dificuldade"])
                    print(f"  > Bot '{info['nome']}' criado com dificuldade '{info['dificuldade']}'")
            else:
                print(f"  > Aviso: Jogador '{info['nome']}' não encontrado no jogo")
    
    @staticmethod
    def obter_estatisticas_jogadores(lista_jogadores):
        """Retorna estatísticas sobre a distribuição de jogadores"""
        num_humanos = sum(1 for j in lista_jogadores if not j["eh_bot"])
        num_bots = sum(1 for j in lista_jogadores if j["eh_bot"])
        
        return {
            "total_jogadores": len(lista_jogadores),
            "num_humanos": num_humanos,
            "num_bots": num_bots,
            "bots_por_dificuldade": {
                "facil": sum(1 for j in lista_jogadores if j["eh_bot"] and j["dificuldade"] == "facil"),
                "medio": sum(1 for j in lista_jogadores if j["eh_bot"] and j["dificuldade"] == "medio"),
                "dificil": sum(1 for j in lista_jogadores if j["eh_bot"] and j["dificuldade"] == "dificil")
            }
        }
