# src/propriedades.py
# Importação relativa para usar a classe Casa base
from casas import Casa 

class Propriedade(Casa):
    """Herda de Casa. Representa propriedades compráveis."""
    def __init__(self, nome, preco_compra, aluguel_base, grupo_cor, aluguel_passagem=200):
        super().__init__(nome, 'PROPRIEDADE') # Agora herda de Casa em casas.py
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

    def calcular_aluguel(self, rolagem_dados=0):
        """
        Calcula o aluguel baseado no número de casas/hotel.
        """
        if self.proprietario and not self.hipotecada:
            # Se tem casas ou hotel, calcular aluguel progressivo
            if self.casas == 0:
                # Sem construções, usar aluguel base
                return self.aluguel_base
            elif self.casas == 1:
                # 1 casa: 5x aluguel base
                return self.aluguel_base * 5
            elif self.casas == 2:
                # 2 casas: 15x aluguel base
                return self.aluguel_base * 15
            elif self.casas == 3:
                # 3 casas: 45x aluguel base
                return self.aluguel_base * 45
            elif self.casas == 4:
                # 4 casas: 80x aluguel base
                return self.aluguel_base * 80
            elif self.casas == 5:
                # Hotel: 100x aluguel base
                return self.aluguel_base * 100
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

# Classe especializada para Metrô (Ferrovia)
class CasaMetro(Propriedade):
    def __init__(self, nome, preco, grupo="METRÔ"):
        # Aluguel base não é usado, mas mantemos 25 para herança
        super().__init__(nome, preco, aluguel_base=25, grupo_cor=grupo)
        # Metro stations cannot have houses
        del self.casas
        
    def calcular_aluguel(self, rolagem_dados=0):
        # O aluguel do metrô depende do número de metrôs que o proprietário possui.
        if not self.proprietario: return 0

        # Contar quantos Metrôs o proprietário tem
        num_metros = sum(1 for prop in self.proprietario.propriedades if prop.grupo_cor == "METRÔ")
        
        # Regra do Monopoly (25, 50, 100, 200)
        alugueis = {1: 25, 2: 50, 3: 100, 4: 200}
        return alugueis.get(num_metros, 25)
        

# Classe especializada para Companhia de Serviço
class CasaCompanhia(Propriedade):
    def __init__(self, nome, preco, grupo="SERVIÇO"):
        # Aluguel base não é usado
        super().__init__(nome, preco, aluguel_base=0, grupo_cor=grupo)
        # Companies cannot have houses
        del self.casas
        
    def calcular_aluguel(self, rolagem_dados):
        if not self.proprietario: return 0

        num_companhias = sum(1 for prop in self.proprietario.propriedades if prop.grupo_cor == "SERVIÇO")
        
        # Regra do Monopoly (4x ou 10x a rolagem dos dados)
        if num_companhias == 1:
            return 4 * rolagem_dados
        elif num_companhias >= 2:
            return 10 * rolagem_dados
        return 0
