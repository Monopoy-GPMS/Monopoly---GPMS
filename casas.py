# src/casas.py
# Importação relativa, assumindo que constantes está no mesmo nível (src/)
from constantes import IMPOSTO_RENDA_VALOR, POSICAO_PRISAO

class Casa:
    """Classe base para qualquer espaço no tabuleiro (40 no total)."""
    def __init__(self, nome, tipo):
        self.nome = nome          
        self.tipo = tipo          

    def acao_ao_cair(self, jogador, banco):
        """Ação padrão (será sobrescrita nas classes específicas)."""
        print(f"  > {jogador.nome} parou em {self.nome} ({self.tipo}).")

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

    def __repr__(self):
        return self.__str__()
        
# --- Lógica da Task SCRUM-8: Casas Especiais ---

class CasaImposto(Casa):
    """Representa casas de impostos/taxas que cobram valor fixo"""
    def __init__(self, nome, valor_imposto): 
        super().__init__(nome, 'IMPOSTO')
        self.valor = valor_imposto
        
    def acao_ao_cair(self, jogador, banco):
        """Cobra o imposto do jogador"""
        super().acao_ao_cair(jogador, banco)
        print(f"  > Pagamento de Imposto: R${self.valor}.")
        banco.pagar(jogador.nome, self.valor, recebedor="Banco")

    def __str__(self):
        return f"{self.nome} - R${self.valor}"
        
class CasaVAPrisao(Casa):
    """Casa especial que envia o jogador para a prisão"""
    def __init__(self):
        super().__init__("Vá para a Prisão", 'VAPRISÃO')
        
    def acao_ao_cair(self, jogador, banco):
        """Envia o jogador diretamente para a prisão"""
        super().acao_ao_cair(jogador, banco)
        jogador.posicao = POSICAO_PRISAO
        jogador.em_prisao = True
        print(f"  > **{jogador.nome} FOI PRESO!** Moveu-se para a Posição {POSICAO_PRISAO}.")

class CasaSorteReves(Casa):
    """Casa de Sorte ou Revés - taxa ou prêmio de R$100"""
    def __init__(self, nome="Sorte ou Revés"):
        super().__init__(nome, 'SORTE')
    
    def acao_ao_cair(self, jogador, banco):
        """Sorteia se o jogador ganha ou perde R$100"""
        super().acao_ao_cair(jogador, banco)
        import random
        if random.choice([True, False]):
            print(f"  > 🍀 {jogador.nome} foi sorteado! Ganha R$100 do banco!")
            banco.depositar(jogador.nome, 100)
        else:
            print(f"  > ☠️ {jogador.nome} foi azarado! Paga R$100 ao banco!")
            banco.pagar(jogador.nome, 100, recebedor="Banco")

class CasaCofre(Casa):
    """Casa do Cofre Comunitário - taxa ou prêmio de R$100"""
    def __init__(self, nome="Cofre"):
        super().__init__(nome, 'COFRE')
    
    def acao_ao_cair(self, jogador, banco):
        """Sorteia se o jogador ganha ou perde R$100"""
        super().acao_ao_cair(jogador, banco)
        import random
        if random.choice([True, False]):
            print(f"  > 💰 {jogador.nome} abriu o cofre! Ganha R$100 do banco!")
            banco.depositar(jogador.nome, 100)
        else:
            print(f"  > 🔓 {jogador.nome} o cofre estava vazio! Paga R$100 ao banco!")
            banco.pagar(jogador.nome, 100, recebedor="Banco")

class CasaEstacionamento(Casa):
    """Casa de Estacionamento Grátis - nenhuma ação"""
    def __init__(self):
        super().__init__("Estacionamento Grátis", 'GRATIS')
    
    def acao_ao_cair(self, jogador, banco):
        """Nenhuma ação - apenas descanso"""
        super().acao_ao_cair(jogador, banco)
        print(f"  > {jogador.nome} está descansando no estacionamento grátis!")

class CasaInicio(Casa):
    """Casa de Início/Saída - ponto de partida"""
    def __init__(self):
        super().__init__("Ponto de Partida", 'INICIO')
    
    def acao_ao_cair(self, jogador, banco):
        """Nenhuma ação especial ao cair (bônus é dado ao passar)"""
        super().acao_ao_cair(jogador, banco)
        print(f"  > {jogador.nome} está no Ponto de Partida!")

class CasaPrisao(Casa):
    """Casa da Prisão - apenas visitando (posição 10)"""
    def __init__(self):
        super().__init__("Cadeia/Prisão", 'PRISAO')
    
    def acao_ao_cair(self, jogador, banco):
        """Se não estiver preso, apenas visitando"""
        super().acao_ao_cair(jogador, banco)
        if not jogador.em_prisao:
            print(f"  > {jogador.nome} está apenas visitando a prisão.")
        else:
            print(f"  > {jogador.nome} está PRESO!")
