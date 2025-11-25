# exibidor_cartas.py
# Módulo para exibir cartas de sorte/cofre com delay de 2 segundos antes de executar

import time
from enum import Enum

class EstadoExibicaoCartaEnum(Enum):
    AGUARDANDO = "aguardando"
    EXIBINDO = "exibindo"
    EXECUTANDO = "executando"
    COMPLETO = "completo"

class ExibidorCartas:
    """
    Gerencia a exibição de cartas na tela com delay antes da execução.
    Permite que o jogador veja o efeito da carta por 2 segundos antes de ser aplicado.
    """
    
    def __init__(self, tempo_exibicao=2.0):
        """
        Args:
            tempo_exibicao: Tempo em segundos que a carta fica visível (padrão: 2s)
        """
        self.tempo_exibicao = tempo_exibicao
        self.carta_exibindo = None
        self.estado = EstadoExibicaoCartaEnum.AGUARDANDO
        self.callback_pos_execucao = None
    
    def exibir_carta(self, carta, tempo_customizado=None):
        """
        Exibe uma carta na tela.
        
        Args:
            carta: Objeto da carta a exibir
            tempo_customizado: Tempo customizado em segundos (opcional)
            
        Returns:
            dict: Informações para renderização no frontend
        """
        tempo = tempo_customizado if tempo_customizado else self.tempo_exibicao
        
        self.carta_exibindo = carta
        self.estado = EstadoExibicaoCartaEnum.EXIBINDO
        
        info_exibicao = {
            "tipo": "EXIBICAO_CARTA",
            "carta": {
                "descricao": carta.descricao,
                "tipo_baralho": carta.tipo_carta,
                "eh_negociavel": carta.é_negociavel
            },
            "tempo_exibicao": tempo,
            "timestamp": time.time()
        }
        
        print(f"  > [CARTA EXIBIDA] {carta.descricao}")
        print(f"  > Aguardando {tempo} segundos antes de executar...")
        
        # Simula o delay de exibição
        time.sleep(tempo)
        
        print(f"  > [CARTA] Executando efeito...")
        self.estado = EstadoExibicaoCartaEnum.EXECUTANDO
        
        return info_exibicao
    
    def executar_carta_apos_delay(self, carta, jogador, banco, jogo):
        """
        Exibe a carta e a executa após o delay.
        
        Args:
            carta: Objeto da carta
            jogador: Jogador que pegou a carta
            banco: Objeto banco
            jogo: Objeto jogo (para contexto)
            
        Returns:
            dict: Resultado da execução
        """
        # Exibe a carta
        info_exibicao = self.exibir_carta(carta)
        
        # Executa a carta após delay
        resultado_execucao = carta.executar(jogador, banco, jogo.tabuleiro, jogo)
        
        self.estado = EstadoExibicaoCartaEnum.COMPLETO
        
        resultado = {
            "exibicao": info_exibicao,
            "execucao": {
                "sucesso": True,
                "mensagem": f"Efeito aplicado: {carta.descricao}",
                "resultado_execucao": resultado_execucao
            }
        }
        
        if self.callback_pos_execucao:
            self.callback_pos_execucao(resultado)
        
        self.carta_exibindo = None
        self.estado = EstadoExibicaoCartaEnum.AGUARDANDO
        
        return resultado
    
    def registrar_callback_pos_execucao(self, callback):
        """Registra callback a ser executado após a carta ser executada"""
        self.callback_pos_execucao = callback
    
    def obter_status(self):
        """Retorna status atual da exibição"""
        return {
            "estado": self.estado.value,
            "carta_exibindo": self.carta_exibindo.descricao if self.carta_exibindo else None,
            "tempo_exibicao": self.tempo_exibicao
        }
