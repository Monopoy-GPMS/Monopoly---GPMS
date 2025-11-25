"""
Módulo de Gerenciamento de Partida
Responsável por iniciar, controlar e finalizar partidas seguindo as regras oficiais do Monopoly.
"""

from jogador import Jogador
from banco import Banco
from tabuleiro import Tabuleiro
from dados import Dados
from cartas import BaralhoSorte, BaralhoReves
from transacoes import GerenciadorTransacoes
from regras_prisao import GerenciadorPrisao
from datetime import datetime


class EstadoPartida:
    """Enumeração dos estados possíveis de uma partida"""
    NAO_INICIADA = "NAO_INICIADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    PAUSADA = "PAUSADA"
    FINALIZADA = "FINALIZADA"


class TipoVitoria:
    """Tipos de vitória possíveis"""
    ULTIMOS_SOBREVIVENTE = "ULTIMO_SOBREVIVENTE"
    DESISTENCIA_OUTROS = "DESISTENCIA_OUTROS"
    TEMPO_LIMITE = "TEMPO_LIMITE"


class GerenciadorPartida:
    """
    Classe principal que gerencia todo o fluxo de uma partida de Monopoly.
    Responsável por:
    - Iniciar e finalizar partidas
    - Controlar turnos
    - Verificar condições de vitória/derrota
    - Garantir cumprimento das regras oficiais
    """
    
    def __init__(self, nomes_jogadores, saldo_inicial=1500):
        """
        Inicializa uma nova partida.
        
        Args:
            nomes_jogadores: Lista com os nomes dos jogadores (2-8 jogadores)
            saldo_inicial: Saldo inicial de cada jogador (padrão: 1500)
        """
        # Validação do número de jogadores
        if not isinstance(nomes_jogadores, list) or len(nomes_jogadores) < 2:
            raise ValueError("É necessário pelo menos 2 jogadores para iniciar uma partida")
        
        if len(nomes_jogadores) > 8:
            raise ValueError("Máximo de 8 jogadores permitido")
        
        # Componentes do jogo
        self.banco = Banco()
        self.tabuleiro = Tabuleiro()
        self.dados = Dados()
        self.baralho_sorte = BaralhoSorte()
        self.baralho_reves = BaralhoReves()
        self.gerenciador_transacoes = GerenciadorTransacoes(self.banco)
        self.gerenciador_prisao = GerenciadorPrisao()
        
        # Jogadores
        self.jogadores = []
        self.jogadores_falidos = []
        
        # Inicializar jogadores
        pecas_disponiveis = ["Carro", "Chapéu", "Bota", "Cachorro", "Navio", "Ferro", "Carrinho", "Dedal"]
        for i, nome in enumerate(nomes_jogadores):
            jogador = Jogador(nome, pecas_disponiveis[i % len(pecas_disponiveis)])
            self.jogadores.append(jogador)
            self.banco.inicializar_conta(nome)
            
            # Ajustar saldo inicial se diferente do padrão
            if saldo_inicial != self.banco.SALDO_INICIAL_PADRAO:
                self.banco.ajustar_saldo(nome, saldo_inicial)
        
        # Controle de turno
        self.indice_turno_atual = 0
        self.turno_numero = 0
        self.duplas_consecutivas = 0
        
        # Estado da partida
        self.estado = EstadoPartida.NAO_INICIADA
        self.vencedor = None
        self.tipo_vitoria = None
        self.data_inicio = None
        self.data_fim = None
        self.tempo_limite_turnos = None  # Opcional: limite de turnos
        
        # Histórico e estatísticas
        self.historico_acoes = []
        self.rodadas_totais = 0
        
        print(f"\n{'='*60}")
        print(f"NOVA PARTIDA DE MONOPOLY CRIADA")
        print(f"{'='*60}")
        print(f"Jogadores: {', '.join(nomes_jogadores)}")
        print(f"Saldo inicial: R${saldo_inicial}")
        print(f"{'='*60}\n")

    def iniciar_partida(self):
        """
        Inicia oficialmente a partida.
        A partir daqui, os turnos podem ser executados.
        """
        if self.estado != EstadoPartida.NAO_INICIADA:
            print("ERRO: A partida já foi iniciada!")
            return False
        
        self.estado = EstadoPartida.EM_ANDAMENTO
        self.data_inicio = datetime.now()
        
        # Embaralhar baralhos
        self.baralho_sorte.embaralhar()
        self.baralho_reves.embaralhar()
        
        self._registrar_acao("INICIO_PARTIDA", f"Partida iniciada com {len(self.jogadores)} jogadores")
        
        print(f"\n{'='*60}")
        print(f"PARTIDA INICIADA!")
        print(f"Data/Hora: {self.data_inicio.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        return True

    def obter_jogador_atual(self):
        """Retorna o jogador do turno atual"""
        if not self.jogadores:
            return None
        return self.jogadores[self.indice_turno_atual]

    def verificar_falencia(self, jogador):
        """
        Verifica se um jogador está falido e executa as ações necessárias.
        Um jogador está falido quando não tem saldo e não pode levantar fundos.
        
        Args:
            jogador: Objeto Jogador a ser verificado
            
        Returns:
            bool: True se o jogador está falido
        """
        saldo = self.banco.consultar_saldo(jogador.nome)
        
        # Jogador tem dinheiro suficiente
        if saldo > 0:
            return False
        
        # Verificar se pode levantar fundos (hipotecando propriedades)
        valor_total_propriedades = 0
        for prop in jogador.propriedades:
            if hasattr(prop, 'valor_hipoteca') and not prop.hipotecada:
                valor_total_propriedades += prop.valor_hipoteca
        
        # Se mesmo hipotecando tudo não consegue pagar, está falido
        if valor_total_propriedades == 0 and saldo <= 0:
            self._executar_falencia(jogador)
            return True
        
        return False

    def _executar_falencia(self, jogador):
        """
        Executa o processo de falência de um jogador.
        Remove o jogador do jogo e transfere propriedades.
        
        Args:
            jogador: Jogador que faliu
        """
        print(f"\n{'='*60}")
        print(f"FALÊNCIA!")
        print(f"{jogador.nome} está falido e sai do jogo!")
        print(f"{'='*60}\n")
        
        # Devolver propriedades ao banco
        propriedades_perdidas = jogador.propriedades.copy()
        for prop in propriedades_perdidas:
            jogador.remover_propriedade(prop)
            prop.proprietario = None
            prop.hipotecada = False
            if hasattr(prop, 'casas'):
                prop.casas = 0
                prop.tem_hotel = False
        
        # Remover jogador da lista de ativos
        if jogador in self.jogadores:
            self.jogadores.remove(jogador)
            self.jogadores_falidos.append(jogador)
        
        # Ajustar índice do turno se necessário
        if self.indice_turno_atual >= len(self.jogadores) and self.jogadores:
            self.indice_turno_atual = 0
        
        self._registrar_acao("FALENCIA", f"{jogador.nome} faliu e saiu do jogo")
        
        # Verificar se há um vencedor
        self._verificar_condicao_vitoria()

    def _verificar_condicao_vitoria(self):
        """
        Verifica se a partida chegou ao fim (condições de vitória).
        Retorna True se a partida acabou.
        """
        # Condição 1: Apenas um jogador restante
        if len(self.jogadores) == 1:
            self._finalizar_partida(
                vencedor=self.jogadores[0],
                tipo_vitoria=TipoVitoria.ULTIMOS_SOBREVIVENTE
            )
            return True
        
        # Condição 2: Nenhum jogador restante (empate técnico - raro)
        if len(self.jogadores) == 0:
            self._finalizar_partida(
                vencedor=None,
                tipo_vitoria="EMPATE"
            )
            return True
        
        # Condição 3: Tempo limite atingido (se configurado)
        if self.tempo_limite_turnos and self.rodadas_totais >= self.tempo_limite_turnos:
            vencedor = self._determinar_vencedor_por_patrimonio()
            self._finalizar_partida(
                vencedor=vencedor,
                tipo_vitoria=TipoVitoria.TEMPO_LIMITE
            )
            return True
        
        return False

    def _determinar_vencedor_por_patrimonio(self):
        """
        Determina o vencedor com base no patrimônio total.
        Usado quando há limite de tempo.
        
        Returns:
            Jogador com maior patrimônio
        """
        melhor_jogador = None
        maior_patrimonio = -1
        
        for jogador in self.jogadores:
            patrimonio = self._calcular_patrimonio_total(jogador)
            if patrimonio > maior_patrimonio:
                maior_patrimonio = patrimonio
                melhor_jogador = jogador
        
        return melhor_jogador

    def _calcular_patrimonio_total(self, jogador):
        """
        Calcula o patrimônio total de um jogador.
        Inclui: dinheiro + valor das propriedades + valor das construções
        
        Args:
            jogador: Jogador a ter o patrimônio calculado
            
        Returns:
            int: Valor total do patrimônio
        """
        patrimonio = self.banco.consultar_saldo(jogador.nome)
        
        # Somar valor das propriedades
        for prop in jogador.propriedades:
            if hasattr(prop, 'preco_compra'):
                patrimonio += prop.preco_compra
            
            # Somar valor das construções
            if hasattr(prop, 'casas'):
                patrimonio += prop.casas * (prop.preco_casa if hasattr(prop, 'preco_casa') else 50)
            if hasattr(prop, 'tem_hotel') and prop.tem_hotel:
                patrimonio += (prop.preco_hotel if hasattr(prop, 'preco_hotel') else 100)
        
        return patrimonio

    def _finalizar_partida(self, vencedor, tipo_vitoria):
        """
        Finaliza a partida e declara o vencedor.
        
        Args:
            vencedor: Jogador vencedor (ou None em caso de empate)
            tipo_vitoria: Tipo de vitória alcançada
        """
        self.estado = EstadoPartida.FINALIZADA
        self.vencedor = vencedor
        self.tipo_vitoria = tipo_vitoria
        self.data_fim = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"FIM DE JOGO!")
        print(f"{'='*60}")
        
        if vencedor:
            patrimonio = self._calcular_patrimonio_total(vencedor)
            print(f"VENCEDOR: {vencedor.nome}")
            print(f"Tipo de Vitória: {tipo_vitoria}")
            print(f"Patrimônio Final: R${patrimonio}")
        else:
            print(f"Resultado: EMPATE")
        
        print(f"\nEstatísticas:")
        print(f"  - Rodadas jogadas: {self.rodadas_totais}")
        print(f"  - Duração: {self._calcular_duracao()}")
        print(f"  - Jogadores falidos: {len(self.jogadores_falidos)}")
        print(f"{'='*60}\n")
        
        self._registrar_acao("FIM_PARTIDA", f"Vencedor: {vencedor.nome if vencedor else 'Empate'}")

    def _calcular_duracao(self):
        """Calcula a duração da partida"""
        if not self.data_inicio or not self.data_fim:
            return "N/A"
        
        duracao = self.data_fim - self.data_inicio
        horas = int(duracao.total_seconds() // 3600)
        minutos = int((duracao.total_seconds() % 3600) // 60)
        
        return f"{horas}h {minutos}min"

    def pausar_partida(self):
        """Pausa a partida atual"""
        if self.estado == EstadoPartida.EM_ANDAMENTO:
            self.estado = EstadoPartida.PAUSADA
            print("Partida pausada.")
            return True
        return False

    def retomar_partida(self):
        """Retoma uma partida pausada"""
        if self.estado == EstadoPartida.PAUSADA:
            self.estado = EstadoPartida.EM_ANDAMENTO
            print("Partida retomada.")
            return True
        return False

    def proximo_turno(self):
        """
        Avança para o próximo jogador, respeitando as regras de duplas.
        Retorna False se a partida terminou.
        """
        if self.estado != EstadoPartida.EM_ANDAMENTO:
            return False
        
        # Se não foram dados duplos, passa para o próximo jogador
        if self.duplas_consecutivas == 0:
            self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
            
            # Se voltou ao primeiro jogador, incrementa rodada
            if self.indice_turno_atual == 0:
                self.rodadas_totais += 1
                print(f"\n--- RODADA {self.rodadas_totais} COMPLETA ---\n")
        
        # Verificar fim de jogo
        return not self._verificar_condicao_vitoria()

    def _registrar_acao(self, tipo, descricao):
        """Registra uma ação no histórico da partida"""
        self.historico_acoes.append({
            'turno': self.turno_numero,
            'tipo': tipo,
            'descricao': descricao,
            'timestamp': datetime.now()
        })

    def obter_status_partida(self):
        """
        Retorna um dicionário com o status completo da partida.
        Útil para interfaces e debugging.
        """
        return {
            'estado': self.estado,
            'turno_atual': self.turno_numero,
            'rodada_atual': self.rodadas_totais,
            'jogador_atual': self.obter_jogador_atual().nome if self.jogadores else None,
            'jogadores_ativos': [j.nome for j in self.jogadores],
            'jogadores_falidos': [j.nome for j in self.jogadores_falidos],
            'vencedor': self.vencedor.nome if self.vencedor else None,
            'duracao': self._calcular_duracao() if self.data_fim else "Em andamento"
        }

    def obter_ranking_jogadores(self):
        """
        Retorna o ranking de jogadores por patrimônio.
        Útil para exibir placar durante o jogo.
        """
        ranking = []
        for jogador in self.jogadores:
            patrimonio = self._calcular_patrimonio_total(jogador)
            ranking.append({
                'nome': jogador.nome,
                'patrimonio': patrimonio,
                'saldo': self.banco.consultar_saldo(jogador.nome),
                'propriedades': len(jogador.propriedades)
            })
        
        # Ordenar por patrimônio decrescente
        ranking.sort(key=lambda x: x['patrimonio'], reverse=True)
        return ranking

    def forcar_desistencia(self, jogador):
        """
        Força a desistência de um jogador (equivalente a falência).
        
        Args:
            jogador: Jogador que desistiu
        """
        print(f"\n{jogador.nome} desistiu da partida!")
        self._executar_falencia(jogador)

    def salvar_estado(self):
        """
        Retorna um dicionário com o estado completo da partida.
        Pode ser usado para salvar/carregar jogos.
        """
        return {
            'estado_partida': self.obter_status_partida(),
            'ranking': self.obter_ranking_jogadores(),
            'historico': self.historico_acoes[-10:]  # Últimas 10 ações
        }

    def __str__(self):
        status = self.obter_status_partida()
        return f"Partida[{status['estado']}] - Rodada {status['rodada_atual']} - {len(self.jogadores)} jogadores ativos"

    def __repr__(self):
        return self.__str__()
