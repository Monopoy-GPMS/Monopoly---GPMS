# tabuleiro.py
# Módulo responsável por definir a estrutura do tabuleiro e as casas.

class Casa:
    """Classe base para qualquer espaço no tabuleiro (40 no total)."""
    def __init__(self, nome, tipo):
        self.nome = nome          # Nome exibido da casa
        self.tipo = tipo          # Tipo da casa: 'INICIO', 'PROPRIEDADE', 'IMPOSTO', 'SORTE', 'PRISAO', etc.

    def __str__(self):
        return f"{self.nome} ({self.tipo})"
    
    def acao_ao_cair(self, jogador, banco):
        """
        Define a ação padrão quando um jogador cai nesta casa. 
        Será implementado no módulo 'regras.py' para evitar dependência circular.
        """
        print(f"  > {jogador.nome} caiu em {self.nome} ({self.tipo}).")

class Propriedade(Casa):
    """Herda de Casa. Representa propriedades que podem ser compradas, alugadas e hipotecadas."""
    def __init__(self, nome, preco_compra, aluguel_base, grupo_cor, aluguel_passagem=200):
        super().__init__(nome, 'PROPRIEDADE') # Tipo fixo 'PROPRIEDADE'
        self.preco_compra = preco_compra
        self.aluguel_base = aluguel_base
        self.grupo_cor = grupo_cor        # Ex: "Roxo", "Ferrovia", "Serviço Público"
        self.proprietario = None          # Objeto Jogador que é o dono
        self.casas = 0                    # 0 a 4 (Hotel)
        self.hipotecada = False
        self.aluguel_passagem = aluguel_passagem # Ex: R$200 ao passar pelo INICIO

    def is_livre(self):
        """Verifica se a propriedade está disponível para compra."""
        return self.proprietario is None

    def calcular_aluguel(self):
        """Lógica simplificada para calcular o aluguel (será expandida)."""
        # Lógica inicial: apenas aluguel base se tiver proprietário.
        if self.proprietario and not self.hipotecada:
            # Em uma versão completa, usaria self.casas para calcular o aluguel exato
            return self.aluguel_base 
        return 0

    def acao_ao_cair(self, jogador, banco):
        """Ação específica de uma Propriedade ao cair."""
        super().acao_ao_cair(jogador, banco)
        
        if self.is_livre():
            print(f"  > {self.nome} custa R${self.preco_compra}. Livre para compra!")
            # A decisão de compra/venda fica no módulo 'regras'
        elif self.proprietario.nome != jogador.nome:
            aluguel = self.calcular_aluguel()
            print(f"  > Propriedade de {self.proprietario.nome}. Aluguel devido: R${aluguel}.")
            # A transação financeira também fica no módulo 'regras' (usando banco.py)
        else:
            print(f"  > Você está em sua própria propriedade ({self.nome}).")


class Tabuleiro:
    """Gerencia a coleção de todas as 40 casas do Monopoly."""
    def __init__(self):
        # Definição das 40 casas do tabuleiro clássico (Simplificado para o teste inicial)
        self.casas = [
            # 1ª Linha (4 casas para demonstração)
            Casa("Saída (GO)", "INICIO"), # Posição 0 - Início/Saída
            Propriedade("Avenida Mediterrânea", 60, 2, "Roxo"), # Posição 1
            Casa("Caixa da Comunidade", "COMUNIDADE"), # Posição 2
            Propriedade("Avenida Báltica", 60, 4, "Roxo"), # Posição 3
            Casa("Imposto de Renda", "IMPOSTO"), # Posição 4
            
            # Adicione as 35 casas restantes do Monopoly clássico aqui...
            # Para o teste, vamos adicionar um número suficiente para fechar o ciclo básico
            Propriedade("Ferrovia Reading", 200, 25, "Ferrovia"), # Posição 5
            Casa("Vá Para a Prisão", "VAPRISÃO"), # Posição 30 (importante para o ciclo)
            Casa("Prisão (Jail)", "PRISAO"), # Posição 10 (importante para o ciclo)
            # Preenche o resto com casas genéricas para chegar a 40 para o teste de movimento
        ]

        # Adiciona casas genéricas até ter 40, se o mapa não estiver completo
        while len(self.casas) < 40:
            self.casas.append(Casa(f"Casa Genérica {len(self.casas)}", "GENÉRICA"))
        
        self.casas = self.casas[:40] # Garante exatamente 40 casas

    def get_casa(self, posicao):
        """Retorna o objeto Casa na posição especificada (0 a 39)."""
        return self.casas[posicao % 40]

# --- Bloco de Teste/Demonstração para a Versão Parcial ---
if __name__ == '__main__':
    print("--- Teste do Módulo Tabuleiro e Casas ---")
    
    tabuleiro = Tabuleiro()
    
    # 1. Teste da Estrutura
    print(f"Total de casas no tabuleiro: {len(tabuleiro.casas)}")
    
    # 2. Teste de Acesso
    casa_saida = tabuleiro.get_casa(0)
    casa_propriedade = tabuleiro.get_casa(1)
    
    print(f"Casa 0: {casa_saida}")
    print(f"Casa 1: {casa_propriedade}")
    
    # 3. Teste da Lógica da Propriedade
    
    # Simulação de um jogador (Mock) e Banco (Mock)
    class JogadorMock:
        def __init__(self, nome):
            self.nome = nome
    class BancoMock:
        def pagar(self, pagador, valor, recebedor):
            print(f"[BancoMock] Pagamento simulado: {pagador} paga R${valor} para {recebedor}.")

    jogador_a = JogadorMock("Alice")
    jogador_b = JogadorMock("Bob")
    banco_mock = BancoMock()

    # Cenário 1: Propriedade Livre
    print("\n--- Cenário 1: Cai em Propriedade Livre ---")
    casa_propriedade.acao_ao_cair(jogador_a, banco_mock)
    
    # Cenário 2: Propriedade Comprada
    print("\n--- Cenário 2: Propriedade Comprada por outro jogador ---")
    casa_propriedade.proprietario = jogador_b # Bob compra a propriedade
    casa_propriedade.acao_ao_cair(jogador_a, banco_mock) # Alice cai nela
    
    # Cenário 3: Cai na Própria Propriedade
    print("\n--- Cenário 3: Cai na Própria Propriedade ---")
    casa_propriedade.acao_ao_cair(jogador_b, banco_mock)