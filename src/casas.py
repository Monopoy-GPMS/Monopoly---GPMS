# src/casas.py
# Importação relativa, assumindo que constantes está no mesmo nível (src/)
from src.constantes import IMPOSTO_RENDA_VALOR, POSICAO_PRISAO

class Casa:
    """Classe base para qualquer espaço no tabuleiro (40 no total)."""
    def __init__(self, nome, tipo):
        self.nome = nome          
        self.tipo = tipo          

    def acao_ao_cair(self, jogador, banco):
        """Ação padrão (será sobrescrita nas classes específicas)."""
        print(f"  > {jogador.nome} parou em {self.nome} ({self.tipo}).")
        
# --- Lógica da Task SCRUM-8: Casas Especiais ---

class CasaImposto(Casa):
    # Aceita APENAS o nome, o valor é puxado da constante
    def __init__(self, nome, valor_imposto): 
        super().__init__(nome, 'IMPOSTO')
        self.valor = valor_imposto # AQUI, o valor é definido AUTOMATICAMENTE!
        
    def acao_ao_cair(self, jogador, banco):
        super().acao_ao_cair(jogador, banco)
        print(f"  > Pagamento de Imposto: R${self.valor}.")
        banco.pagar(jogador.nome, self.valor, recebedor="Banco")
        
class CasaVAPrisao(Casa):
    def __init__(self):
        super().__init__("Vá para a Prisão", 'VAPRISÃO')
        
    def acao_ao_cair(self, jogador, banco):
        super().acao_ao_cair(jogador, banco)
        # 1. Muda o estado do jogador
        jogador.posicao = POSICAO_PRISAO
        jogador.em_prisao = True
        print(f"  > **{jogador.nome} FOI PRESO!** Moveu-se para a Posição {POSICAO_PRISAO}.")