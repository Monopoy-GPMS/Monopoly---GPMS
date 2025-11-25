# src/casas.py
# Importação relativa, assumindo que constantes está no mesmo nível (src/)
from constantes import IMPOSTO_RENDA_VALOR, POSICAO_PRISAO
import random

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
    """Casa de Sorte ou Revés - evento aleatório com sorteio de 1 a 10"""
    def __init__(self, nome="Sorte ou Revés"):
        super().__init__(nome, 'SORTE')
    
    def sorteio_evento(self, jogador, banco):
        numero_sorteado = random.randint(1, 10)
        valor = 100
        
        if numero_sorteado % 2 == 1:  # Ímpar = paga
            # Only debit if player has sufficient balance
            if not banco.pagar(jogador.nome, valor, recebedor="Banco"):
                # If payment fails, still return the result for UI feedback
                mensagem = f"{jogador.nome} foi taxado - tentou pagar R${valor} mas não tem saldo suficiente!"
                return {"tipo": "SORTE", "mensagem": mensagem, "valor": 0, "sucesso": False}
            mensagem = f"{jogador.nome} foi taxado e pagou R${valor} ao banco"
            return {"tipo": "SORTE", "mensagem": mensagem, "valor": -valor, "sucesso": True}
        else:  # Par = recebe
            banco.depositar(jogador.nome, valor)
            mensagem = f"{jogador.nome} foi sortudo e recebeu R${valor} do banco"
            return {"tipo": "SORTE", "mensagem": mensagem, "valor": valor, "sucesso": True}
    
    def acao_ao_cair(self, jogador, banco):
        """Ação padrão ao cair - o sorteio será feito em jogo.py"""
        super().acao_ao_cair(jogador, banco)

class CasaCofre(Casa):
    """Casa do Cofre Comunitário - evento aleatório com sorteio de 1 a 10"""
    def __init__(self, nome="Cofre"):
        super().__init__(nome, 'COFRE')
    
    def sorteio_evento(self, jogador, banco):
        numero_sorteado = random.randint(1, 10)
        valor = 100
        
        if numero_sorteado % 2 == 1:  # Ímpar = paga
            # Only debit if player has sufficient balance
            if not banco.pagar(jogador.nome, valor, recebedor="Banco"):
                # If payment fails, still return the result for UI feedback
                mensagem = f"{jogador.nome} foi taxado - tentou pagar R${valor} mas não tem saldo suficiente!"
                return {"tipo": "COFRE", "mensagem": mensagem, "valor": 0, "sucesso": False}
            mensagem = f"{jogador.nome} foi taxado e pagou R${valor} ao banco"
            return {"tipo": "COFRE", "mensagem": mensagem, "valor": -valor, "sucesso": True}
        else:  # Par = recebe
            banco.depositar(jogador.nome, valor)
            mensagem = f"{jogador.nome} ganhou uma aposta e recebeu R${valor}"
            return {"tipo": "COFRE", "mensagem": mensagem, "valor": valor, "sucesso": True}
    
    def acao_ao_cair(self, jogador, banco):
        """Ação padrão ao cair - o sorteio será feito em jogo.py"""
        super().acao_ao_cair(jogador, banco)

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
