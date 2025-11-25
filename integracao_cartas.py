# integracao_cartas.py
# Módulo para integração completa de Cartas de Sorte e Cofre com eventos

from cartas import (
    Carta, CartaDinheiro, CartaMovimento, CartaMovimentoRelativo,
    CartaPrisao, CartaLivrePrisao, CartaReparos, CartaComunidade,
    BaralhoCartas
)
from sistema_eventos import SistemaEventos, TipoEvento

class GerenciadorCartasAvancado:
    """
    Gerencia a execução avançada de cartas com integração de eventos.
    Estende a funcionalidade básica de cartas com sistema de eventos.
    """
    
    def __init__(self, sistema_eventos):
        """
        Args:
            sistema_eventos: Instância do SistemaEventos
        """
        self.sistema_eventos = sistema_eventos
        self.baralho_sorte = BaralhoCartas('SORTE')
        self.baralho_cofre = BaralhoCartas('COFRE')
        self.ultima_carta_sorte = None
        self.ultima_carta_cofre = None
    
    def puxar_carta_sorte(self, jogador, jogo):
        """
        Puxa uma carta de Sorte e executa seu efeito.
        
        Args:
            jogador: Objeto jogador
            jogo: Objeto jogo
            
        Returns:
            dict: Resultado da execução da carta
        """
        carta = self.baralho_sorte.pegar_carta()
        if not carta:
            return {"sucesso": False, "mensagem": "Sem cartas de Sorte"}
        
        self.ultima_carta_sorte = carta
        
        # Dispara evento de carta puxada
        self.sistema_eventos.disparar_evento(
            TipoEvento.PEGAR_CARTA,
            jogador.nome,
            f"Puxou carta de Sorte: {carta.descricao[:50]}...",
            {'tipo_baralho': 'SORTE', 'descricao_completa': carta.descricao}
        )
        
        # Executa a carta
        resultado = self._executar_carta_com_eventos(carta, jogador, jogo, 'SORTE')
        
        # Retorna ao baralho se necessário
        if resultado.get('deve_retornar'):
            self.baralho_sorte.devolver_carta(carta)
        
        return resultado
    
    def puxar_carta_cofre(self, jogador, jogo):
        """
        Puxa uma carta de Cofre e executa seu efeito.
        
        Args:
            jogador: Objeto jogador
            jogo: Objeto jogo
            
        Returns:
            dict: Resultado da execução da carta
        """
        carta = self.baralho_cofre.pegar_carta()
        if not carta:
            return {"sucesso": False, "mensagem": "Sem cartas de Cofre"}
        
        self.ultima_carta_cofre = carta
        
        # Dispara evento de carta puxada
        self.sistema_eventos.disparar_evento(
            TipoEvento.PEGAR_CARTA,
            jogador.nome,
            f"Puxou carta de Cofre: {carta.descricao[:50]}...",
            {'tipo_baralho': 'COFRE', 'descricao_completa': carta.descricao}
        )
        
        # Executa a carta
        resultado = self._executar_carta_com_eventos(carta, jogador, jogo, 'COFRE')
        
        # Retorna ao baralho se necessário
        if resultado.get('deve_retornar'):
            self.baralho_cofre.devolver_carta(carta)
        
        return resultado
    
    def _executar_carta_com_eventos(self, carta, jogador, jogo, tipo_baralho):
        """
        Executa uma carta e dispara eventos apropriados.
        
        Args:
            carta: Objeto carta
            jogador: Objeto jogador
            jogo: Objeto jogo
            tipo_baralho: 'SORTE' ou 'COFRE'
            
        Returns:
            dict: Resultado com deve_retornar e detalhes
        """
        try:
            deve_retornar = carta.executar(jogador, jogo.banco, jogo.tabuleiro, jogo=jogo)
            
            # Dispara eventos específicos baseado no tipo de carta
            if isinstance(carta, CartaDinheiro):
                if carta.valor > 0:
                    self.sistema_eventos.disparar_evento(
                        TipoEvento.PASSAGEM_SAIDA,  # Ou evento de ganho
                        jogador.nome,
                        f"Ganhou R${carta.valor} por carta",
                        {'valor': carta.valor, 'tipo_baralho': tipo_baralho}
                    )
                else:
                    self.sistema_eventos.disparar_evento(
                        TipoEvento.PAGAR_IMPOSTO,
                        jogador.nome,
                        f"Pagou R${abs(carta.valor)} por carta",
                        {'valor': abs(carta.valor), 'tipo_baralho': tipo_baralho}
                    )
            
            elif isinstance(carta, CartaPrisao):
                self.sistema_eventos.disparar_evento(
                    TipoEvento.PRISAO,
                    jogador.nome,
                    "Enviado para a prisão por carta",
                    {'tipo_baralho': tipo_baralho}
                )
            
            elif isinstance(carta, CartaLivrePrisao):
                self.sistema_eventos.disparar_evento(
                    TipoEvento.PEGAR_CARTA,
                    jogador.nome,
                    "Ganhou carta Saia Livre da Prisão",
                    {'tipo_baralho': tipo_baralho}
                )
            
            return {
                "sucesso": True,
                "carta_descricao": carta.descricao,
                "deve_retornar": deve_retornar,
                "tipo_baralho": tipo_baralho
            }
        
        except Exception as e:
            print(f"  > ERRO ao executar carta: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "deve_retornar": True
            }
    
    def obter_status_baralhos(self):
        """Retorna status dos baralhos"""
        return {
            'sorte': {
                'cartas_disponiveis': len(self.baralho_sorte.cartas),
                'cartas_descartadas': len(self.baralho_sorte.cartas_descartadas),
                'total': len(self.baralho_sorte.cartas) + len(self.baralho_sorte.cartas_descartadas)
            },
            'cofre': {
                'cartas_disponiveis': len(self.baralho_cofre.cartas),
                'cartas_descartadas': len(self.baralho_cofre.cartas_descartadas),
                'total': len(self.baralho_cofre.cartas) + len(self.baralho_cofre.cartas_descartadas)
            }
        }
