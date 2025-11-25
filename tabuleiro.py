# src/tabuleiro.py

# Importação dos novos módulos e classes
from casas import Casa, CasaImposto, CasaVAPrisao, CasaSorteReves, CasaCofre 
from propriedades import Propriedade, CasaMetro, CasaCompanhia
from constantes import IMPOSTO_RENDA_VALOR, VALOR_FERROVIA, VALOR_COMPANHIA_SERVICO, TAXA_RIQUEZA_VALOR

class Tabuleiro:
    def __init__(self):
        self.casas = []
        self._current_pos = 0 # Contador temporário de casas
        
        self._construir_tabuleiro()
        
        # Verificação final para garantir 40 casas
        if len(self.casas) != 40:
            raise Exception(f"Erro ao construir o tabuleiro: {len(self.casas)} casas encontradas, 40 esperadas.")

    def _construir_tabuleiro(self):
        """Constrói o tabuleiro com todas as 40 casas seguindo o layout clássico do Monopoly"""
        
        # Posição 0: Ponto de Partida
        self._add_casa_simples(nome="Ponto de Partida", tipo="INICIO")
        
        # Grupo 1: Marrom (Posições 1, 3)
        self._add_prop(nome="Avenida Sumaré", preco=60, aluguel=2, grupo="Marrom")
        self.casas.append(CasaCofre(nome="Cofre"))  # Changed from _add_casa_simples to CasaCofre instance
        self._add_prop(nome="Praça da Sé", preco=60, aluguel=4, grupo="Marrom")
        
        # Posição 4: Imposto de Renda
        self.casas.append(CasaImposto("Imposto de Renda", IMPOSTO_RENDA_VALOR))
        
        # Posição 5: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô Maracanã", preco=VALOR_FERROVIA))
        
        # Grupo 2: Azul Claro (Posições 6, 8, 9)
        self._add_prop(nome="Rua 25 de Março", preco=100, aluguel=6, grupo="Azul Claro")
        self.casas.append(CasaSorteReves(nome="Sorte ou Revés"))  # Changed from _add_casa_simples to CasaSorteReves instance
        self._add_prop(nome="Avenida São João", preco=100, aluguel=6, grupo="Azul Claro")
        self._add_prop(nome="Avenida Paulista", preco=120, aluguel=8, grupo="Azul Claro")
        
        # Posição 10: Cadeia/Prisão (apenas visitando)
        self._add_casa_simples(nome="Cadeia/Prisão", tipo="PRISAO")
        
        # Grupo 3: Rosa (Posições 11, 13, 14)
        self._add_prop(nome="Avenida Vieira Souto", preco=140, aluguel=10, grupo="Rosa")
        self.casas.append(CasaCompanhia(nome="Companhia Elétrica", preco=VALOR_COMPANHIA_SERVICO))
        self._add_prop(nome="Niterói", preco=140, aluguel=10, grupo="Rosa")
        self._add_prop(nome="Avenida Atlântica", preco=160, aluguel=12, grupo="Rosa")
        
        # Posição 15: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô Carioca", preco=VALOR_FERROVIA))
        
        # Grupo 4: Laranja (Posições 16, 18, 19)
        self._add_prop(nome="Avenida Presidente Juscelino Kubitschek", preco=180, aluguel=14, grupo="Laranja")
        self.casas.append(CasaCofre(nome="Cofre"))  # Changed from _add_casa_simples to CasaCofre instance
        self._add_prop(nome="Avenida Engenheiro Luis Carlos Berrini", preco=180, aluguel=14, grupo="Laranja")
        self._add_prop(nome="Avenida Brigadeiro Faria Lima", preco=200, aluguel=16, grupo="Laranja")
        
        # Posição 20: Estacionamento Grátis
        self._add_casa_simples(nome="Estacionamento Grátis", tipo="GRATIS")
        
        # Grupo 5: Vermelho (Posições 21, 23, 24)
        self._add_prop(nome="Ipanema", preco=220, aluguel=18, grupo="Vermelho")
        self.casas.append(CasaSorteReves(nome="Sorte ou Revés"))  # Changed from _add_casa_simples to CasaSorteReves instance
        self._add_prop(nome="Leblon", preco=220, aluguel=18, grupo="Vermelho")
        self._add_prop(nome="Copacabana", preco=240, aluguel=20, grupo="Vermelho")
        
        # Posição 25: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô Consolação", preco=VALOR_FERROVIA))
        
        # Grupo 6: Amarelo (Posições 26, 27, 29)
        self._add_prop(nome="Avenida Cidade Jardim", preco=260, aluguel=22, grupo="Amarelo")
        self._add_prop(nome="Pacaembu", preco=260, aluguel=22, grupo="Amarelo")
        self.casas.append(CasaCompanhia(nome="Companhia de Distribuição de Água", preco=VALOR_COMPANHIA_SERVICO))
        self._add_prop(nome="Ibirapuera", preco=280, aluguel=24, grupo="Amarelo")
        
        # Posição 30: VÁ PARA A CADEIA
        self.casas.append(CasaVAPrisao())
        
        # Grupo 7: Verde (Posições 31, 32, 34)
        self._add_prop(nome="Barra da Tijuca", preco=300, aluguel=26, grupo="Verde")
        self._add_prop(nome="Jardim Botânico", preco=300, aluguel=26, grupo="Verde")
        self.casas.append(CasaCofre(nome="Cofre"))  # Changed from _add_casa_simples to CasaCofre instance
        self._add_prop(nome="Lagoa Rodrigo de Freitas", preco=320, aluguel=28, grupo="Verde")
        
        # Posição 35: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô República", preco=VALOR_FERROVIA))
        
        # Grupo 8: Azul Escuro (Posições 37, 39)
        self.casas.append(CasaSorteReves(nome="Sorte ou Revés"))  # Changed from _add_casa_simples to CasaSorteReves instance
        self._add_prop(nome="Avenida Morumbi", preco=350, aluguel=35, grupo="Azul Escuro")
        
        # Posição 38: Taxa de Riqueza
        self.casas.append(CasaImposto("Taxa de Riqueza", TAXA_RIQUEZA_VALOR))
        
        # Posição 39: Última propriedade
        self._add_prop(nome="Rua Oscar Freire", preco=400, aluguel=50, grupo="Azul Escuro")

    def get_casa(self, posicao):
        """
        Retorna o objeto Casa na posição especificada (0 a 39).
        Usa módulo 40 para garantir que posições válidas sejam sempre retornadas.
        """
        if not isinstance(posicao, int):
            raise ValueError(f"Posição deve ser um inteiro, recebido: {type(posicao)}")
        return self.casas[posicao % 40]

    def get_tipo_casa(self, posicao):
        """Retorna o tipo da casa na posição especificada"""
        casa = self.get_casa(posicao)
        return casa.tipo

    def get_nome_casa(self, posicao):
        """Retorna o nome da casa na posição especificada"""
        casa = self.get_casa(posicao)
        return casa.nome

    def listar_propriedades_por_grupo(self, grupo):
        """
        Retorna todas as propriedades de um grupo específico.
        Útil para verificar monopólios.
        """
        propriedades_grupo = []
        for casa in self.casas:
            if isinstance(casa, Propriedade) and hasattr(casa, 'grupo_cor'):
                if casa.grupo_cor == grupo:
                    propriedades_grupo.append(casa)
        return propriedades_grupo

    def listar_todas_propriedades(self):
        """Retorna lista de todas as propriedades do tabuleiro"""
        return [casa for casa in self.casas if isinstance(casa, Propriedade)]

    def get_casas_especiais(self):
        """Retorna um dicionário com as posições das casas especiais"""
        return {
            'inicio': 0,
            'prisao': 10,
            'va_prisao': 30,
            'estacionamento': 20,
            'impostos': [4, 38],
            'sorte': [2, 7, 17, 22, 33, 36],
            'cofre': [2, 17, 33]
        }

    # --- Métodos Auxiliares para simplificar a criação ---
    def _add_prop(self, nome, preco, aluguel, grupo):
        """Adiciona uma propriedade comum ao tabuleiro"""
        self.casas.append(Propriedade(nome, preco, aluguel, grupo))
        
    def _add_casa_simples(self, nome, tipo):
        """Adiciona uma casa simples (não comprável) ao tabuleiro"""
        self.casas.append(Casa(nome, tipo))

    def __str__(self):
        """Representação em string do tabuleiro para debug"""
        return f"Tabuleiro com {len(self.casas)} casas"

    def __repr__(self):
        return self.__str__()

# Bloco de teste/demonstração (deve ser movido para src/main.py no final)
if __name__ == '__main__':
    print("--- Teste do Módulo Tabuleiro (Mapeamento) ---")
    
    # É necessário que as classes Propriedade, CasaImposto, etc. estejam definidas 
    # ou importadas com sucesso para que este teste funcione.
    
    tabuleiro = Tabuleiro()
    print(f"Total de casas: {len(tabuleiro.casas)}")
    
    print("\n--- Casas Especiais ---")
    print(f"Posição 4 (Imposto): {tabuleiro.get_casa(4)}")
    print(f"Posição 30 (Vá para a Prisão): {tabuleiro.get_casa(30)}")
    print(f"Posição 38 (Taxa): {tabuleiro.get_casa(38)}")
    
    print("\n--- Propriedades ---")
    prop_39 = tabuleiro.get_casa(39)
    print(f"Posição 39: {prop_39.nome} (Grupo: {prop_39.grupo})")
