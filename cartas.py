# cartas.py
# Módulo responsável pelas cartas de Sorte, Cofre e gerenciamento de baralhos
# Implementação com as 32 cartas reais do Monopoly (16 de Sorte + 16 de Cofre)

import random
from constantes import VALOR_PASSAGEM_SAIDA, POSICAO_PRISAO, POSICAO_SAIDA

class Carta:
    """Classe base para representar uma carta"""
    
    def __init__(self, descricao, tipo_carta, é_negociavel=False):
        """
        Args:
            descricao: Texto da carta
            tipo_carta: 'SORTE', 'COFRE'
            é_negociavel: Se a carta pode ser armazenada e negociada
        """
        self.descricao = descricao
        self.tipo_carta = tipo_carta
        self.é_negociavel = é_negociavel
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        """
        Executa a ação da carta.
        Returns: True se deve devolver ao baralho, False se é guardável
        """
        raise NotImplementedError("Subclasses devem implementar executar()")
    
    def __str__(self):
        return f"[{self.tipo_carta}] {self.descricao}"

class CartaDinheiro(Carta):
    """Carta que adiciona ou remove dinheiro do jogador"""
    
    def __init__(self, descricao, valor, tipo_carta='SORTE'):
        super().__init__(descricao, tipo_carta)
        self.valor = valor
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        if self.valor > 0:
            banco.depositar(jogador.nome, self.valor)
            print(f"  > {jogador.nome} recebeu R${self.valor}!")
        else:
            sucesso = banco.pagar(jogador.nome, abs(self.valor), "Banco")
            if not sucesso:
                print(f"  > {jogador.nome} não tem dinheiro suficiente!")
        return True

class CartaMovimento(Carta):
    """Carta que move o jogador para uma posição específica"""
    
    def __init__(self, descricao, posicao_destino, tipo_carta='SORTE', cobra_passagem=True):
        super().__init__(descricao, tipo_carta)
        self.posicao_destino = posicao_destino
        self.cobra_passagem = cobra_passagem
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        posicao_antiga = jogador.posicao
        jogador.mover_para(self.posicao_destino)
        
        if self.cobra_passagem and posicao_antiga > self.posicao_destino:
            banco.depositar(jogador.nome, VALOR_PASSAGEM_SAIDA)
            print(f"  > {jogador.nome} passou pela Saída e recebeu R${VALOR_PASSAGEM_SAIDA}!")
        
        return True

class CartaMovimentoRelativo(Carta):
    """Carta que move o jogador X casas para frente ou para trás"""
    
    def __init__(self, descricao, casas, tipo_carta='SORTE'):
        super().__init__(descricao, tipo_carta)
        self.casas = casas
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        posicao_antiga = jogador.posicao
        nova_posicao = (jogador.posicao + self.casas) % 40
        jogador.mover_para(nova_posicao)
        
        if self.casas > 0 and nova_posicao < posicao_antiga:
            banco.depositar(jogador.nome, VALOR_PASSAGEM_SAIDA)
            print(f"  > {jogador.nome} passou pela Saída e recebeu R${VALOR_PASSAGEM_SAIDA}!")
        
        return True

class CartaPrisao(Carta):
    """Carta que envia o jogador para a prisão"""
    
    def __init__(self, tipo_carta='SORTE'):
        super().__init__("Vá para a Cadeia. Avance diretamente. Não passe pelo Ponto de Partida. Não receba R$200.", tipo_carta)
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        jogador.entrar_prisao()
        print(f"  > {jogador.nome} foi enviado para a Cadeia!")
        return True

class CartaLivrePrisao(Carta):
    """Carta que permite sair livre da prisão - negociável"""
    
    def __init__(self, tipo_carta='SORTE'):
        super().__init__("Saia da Cadeia de Graça. Esta carta pode ser guardada até ser necessária, ou vendida", tipo_carta, é_negociavel=True)
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        jogador.adicionar_carta_livre_prisao(self)
        print(f"  > {jogador.nome} ganhou uma carta 'Saia Livre da Cadeia'! Armazenada no inventário.")
        return False

class CartaReparos(Carta):
    """Carta que cobra reparos baseados em casas e hotéis"""
    
    def __init__(self, descricao, valor_por_casa, valor_por_hotel, tipo_carta='COFRE'):
        super().__init__(descricao, tipo_carta)
        self.valor_por_casa = valor_por_casa
        self.valor_por_hotel = valor_por_hotel
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        total_casas = 0
        total_hoteis = 0
        
        for prop in jogador.propriedades:
            if hasattr(prop, 'casas'):
                if prop.casas == 5:
                    total_hoteis += 1
                else:
                    total_casas += prop.casas
        
        total_a_pagar = (total_casas * self.valor_por_casa) + (total_hoteis * self.valor_por_hotel)
        
        if total_a_pagar > 0:
            sucesso = banco.pagar(jogador.nome, total_a_pagar, "Banco")
            print(f"  > {jogador.nome} pagou R${total_a_pagar} em reparos ({total_casas} casas, {total_hoteis} hotéis)")
            if not sucesso:
                print(f"  > {jogador.nome} não tem dinheiro suficiente!")
        else:
            print(f"  > {jogador.nome} não tem casas ou hotéis para reparar.")
        
        return True

class CartaComunidade(Carta):
    """Carta que afeta todos os jogadores (transações comunitárias)"""
    
    def __init__(self, descricao, valor_por_jogador, è_recebimento=True, tipo_carta='COFRE'):
        super().__init__(descricao, tipo_carta)
        self.valor_por_jogador = valor_por_jogador
        self.è_recebimento = è_recebimento
    
    def executar(self, jogador, banco, tabuleiro, jogo=None):
        if not jogo:
            print(f"  > Aviso: Carta comunitária executada sem contexto de jogo.")
            return True
        
        jogador_atual_nome = jogador.nome
        
        if self.è_recebimento:
            print(f"  > {jogador_atual_nome} recebe R${self.valor_por_jogador} de cada jogador!")
            for j in jogo.jogadores:
                if j.nome != jogador_atual_nome:
                    banco.pagar(j.nome, self.valor_por_jogador, jogador_atual_nome)
        else:
            print(f"  > {jogador_atual_nome} paga R${self.valor_por_jogador} para cada jogador!")
            for j in jogo.jogadores:
                if j.nome != jogador_atual_nome:
                    banco.depositar(j.nome, self.valor_por_jogador)
        
        return True

class BaralhoCartas:
    """Gerencia um baralho de cartas (Sorte ou Cofre) com 16 cartas cada"""
    
    def __init__(self, tipo='SORTE'):
        """
        Args:
            tipo: 'SORTE' ou 'COFRE'
        """
        self.tipo = tipo
        self.cartas = []
        self.cartas_descartadas = []
        self._criar_baralho()
        self.embaralhar()
    
    def _criar_baralho(self):
        """Cria os 32 baralhos corretos (16 de Sorte + 16 de Cofre)"""
        if self.tipo == 'SORTE':
            self.cartas = [
                CartaMovimento("Avance para a Casa de Partida (Receba R$200)", POSICAO_SAIDA, 'SORTE', cobra_passagem=False),
                CartaMovimento("Avance para o Estacionamento (Parada livre)", 20, 'SORTE'),
                CartaMovimento("Avance para a Avenida Morumbi", 39, 'SORTE'),
                CartaMovimento("Avance para a Estação de Metrô mais próxima. Pague se necessário, ou permita a compra se possível.", 5, 'SORTE'),
                CartaMovimento("Avance para a Companhia de Água. Pague se necessário, ou permita a compra se possível.", 12, 'SORTE'),
                CartaMovimento("Avance para a Avenida Atlântica. Se passar pelo Ponto de Partida, receba R$200", 37, 'SORTE'),
                CartaMovimento("Avance para a Rua Oscar Freire", 39, 'SORTE'),
                CartaMovimentoRelativo("Volte 3 casas", -3, 'SORTE'),
                CartaPrisao('SORTE'),
                CartaLivrePrisao('SORTE'),
                CartaDinheiro("Taxa de Reparo Geral: Pague R$15", -15, 'SORTE'),
                CartaDinheiro("Multa por excesso de velocidade (Driving fine): Pague R$50", -50, 'SORTE'),
                CartaReparos("Avaliação de Ruas. Pague R$25 por casa e R$100 por hotel que você possuir", 25, 100, 'SORTE'),
                CartaDinheiro("Seu Empréstimo de Construção venceu. Receba R$150", 150, 'SORTE'),
                CartaDinheiro("Você ganhou um concurso de palavras cruzadas. Receba R$100", 100, 'SORTE'),
                CartaDinheiro("O Banco pagará a você R$50 de dividendos", 50, 'SORTE'),
            ]
        else:  # COFRE
            self.cartas = [
                CartaMovimento("Avance para a Casa de Partida (Receba R$200)", POSICAO_SAIDA, 'COFRE', cobra_passagem=False),
                CartaLivrePrisao('COFRE'),
                CartaPrisao('COFRE'),
                CartaDinheiro("Erro do Banco a seu favor. Receba R$200", 200, 'COFRE'),
                CartaDinheiro("Você herda R$100", 100, 'COFRE'),
                CartaDinheiro("Taxa de Serviço (Consulting Fee). Receba R$25", 25, 'COFRE'),
                CartaDinheiro("Restituição do Imposto de Renda (Income Tax Refund). Receba R$20", 20, 'COFRE'),
                CartaDinheiro("Fundo de Natal (Holiday Fund) é liberado. Receba R$100", 100, 'COFRE'),
                CartaDinheiro("Seu seguro de vida venceu. Receba R$100", 100, 'COFRE'),
                CartaComunidade("Taxa de Médico (Doctor's Fee). Receba R$50 de cada jogador", 50, è_recebimento=True, tipo_carta='COFRE'),
                CartaDinheiro("Pague as taxas da Escola. Pague R$50", -50, 'COFRE'),
                CartaDinheiro("Pague a conta do Hospital. Pague R$100", -100, 'COFRE'),
                CartaDinheiro("Pague a Avaliação da sua Propriedade. Pague R$150", -150, 'COFRE'),
                CartaDinheiro("Você foi eleito Presidente do Conselho. Pague R$100", -100, 'COFRE'),
                CartaReparos("Avaliação de Ruas. Pague R$40 por casa e R$115 por hotel que você possuir", 40, 115, 'COFRE'),
                CartaDinheiro("Você ganha um segundo prêmio em um concurso de beleza. Receba R$10", 10, 'COFRE'),
            ]
    
    def embaralhar(self):
        """Embaralha o baralho"""
        random.shuffle(self.cartas)
        print(f"  > Baralho de {self.tipo} embaralhado! ({len(self.cartas)} cartas)")
    
    def pegar_carta(self):
        """Pega uma carta do topo do baralho"""
        if not self.cartas:
            if self.cartas_descartadas:
                print(f"  > Reembaralhando cartas de {self.tipo}...")
                self.cartas = self.cartas_descartadas[:]
                self.cartas_descartadas = []
                self.embaralhar()
            else:
                return None
        
        if self.cartas:
            return self.cartas.pop(0)
        return None
    
    def devolver_carta(self, carta):
        """Devolve uma carta ao baralho (no final da pilha de descartadas) - exceto cartas negociáveis"""
        if not carta.é_negociavel:
            self.cartas_descartadas.append(carta)
            print(f"  > Carta '{carta.descricao[:40]}...' devolvida ao baralho de {self.tipo}.")
    
    def __str__(self):
        return f"Baralho {self.tipo}: {len(self.cartas)} cartas disponíveis, {len(self.cartas_descartadas)} descartadas"

# Teste do módulo
if __name__ == '__main__':
    print("--- Teste do Módulo Cartas ---")
    
    # Mock classes for testing
    class JogadorMock:
        def __init__(self, nome):
            self.nome = nome
            self.posicao = 0
            self.cartas_livre_prisao = []
            self.propriedades = []
            self.em_prisao = False
        
        def mover_para(self, posicao):
            self.posicao = posicao
        
        def entrar_prisao(self):
            self.em_prisao = True
            self.posicao = 10
        
        def adicionar_carta_livre_prisao(self, carta):
            self.cartas_livre_prisao.append(carta)
        
        def adicionar_item(self, tipo_item, carta):
            print(f"    [JOGADOR] Adicionando item '{tipo_item}' ao inventário de {self.nome}")
    
    class BancoMock:
        def depositar(self, jogador, valor):
            print(f"    [BANCO] Depositou R${valor} para {jogador}")
        
        def pagar(self, jogador, valor, destino):
            print(f"    [BANCO] {jogador} pagou R${valor} para {destino}")
            return True
    
    class JogoMock:
        def __init__(self):
            self.jogadores = [JogadorMock("Jogador1"), JogadorMock("Jogador2")]
    
    # Testa baralhos
    baralho_sorte = BaralhoCartas('SORTE')
    baralho_cofre = BaralhoCartas('COFRE')
    
    print(f"\n{baralho_sorte}")
    print(f"{baralho_cofre}")
    
    # Testa pegar cartas
    print("\n--- Testando 5 cartas de SORTE ---")
    jogador = JogadorMock("Teste")
    banco = BancoMock()
    
    for i in range(5):
        carta = baralho_sorte.pegar_carta()
        print(f"\nCarta {i+1}: {carta}")
        carta.executar(jogador, banco, None)

    print("\n--- Testando 5 cartas de COFRE ---")
    jogo = JogoMock()
    jogador_cofre = jogo.jogadores[0]
    
    for i in range(5):
        carta = baralho_cofre.pegar_carta()
        print(f"\nCarta {i+1}: {carta}")
        carta.executar(jogador_cofre, banco, None, jogo)
