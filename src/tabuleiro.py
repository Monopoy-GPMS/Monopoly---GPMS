# src/tabuleiro.py

# Importação dos novos módulos e classes
from casas import Casa, CasaImposto, CasaVAPrisao 
from propriedades import Propriedade, CasaMetro, CasaCompanhia
from constantes import IMPOSTO_RENDA_VALOR, VALOR_FERROVIA, VALOR_COMPANHIA_SERVICO, TAXA_RIQUEZA_VALOR

class Tabuleiro:
    def __init__(self):
        self.casas = []
        self._current_pos = 0 # Contador temporário de casas
        
        # --- Configurações Simplificadas para Propriedades (Serão detalhadas em constantes.py) ---
        # Usando preços e grupos genéricos por enquanto, o ajuste fino de aluguéis fica no propriedades.py

        self._add_casa_simples(nome="Ponto de Partida", tipo="INICIO") # 0 - Esta é a casa 0 (Ponto de partida)
        
        # Grupo 1: Marrom (Rua Sumaré, Praça da Sé)
        self._add_prop(nome="Avenida Sumaré", preco=60, aluguel=6, grupo="Marrom") # 1
        
        # 2: Cofre
        self._add_casa_simples(nome="Cofre", tipo="COFRE") # 2
        
        # Grupo 1: Marrom
        self._add_prop(nome="Praça da Sé", preco=60, aluguel=6, grupo="Marrom") # 3
        
        # 4: Imposto de Renda
        self.casas.append(CasaImposto("Imposto de Renda", IMPOSTO_RENDA_VALOR)) # 4
        
        # Grupo 2: Metrô/Ferrovia (Estação de Metrô Maracanã)
        self.casas.append(CasaMetro(nome="Estação de Metrô Maracanã", preco=VALOR_FERROVIA)) # 5 - AGORA USA CASA METRO
        
        # Grupo 3: Azul Claro (Rua 25 de Março, Av. São João, Av. Paulista)
        self._add_prop(nome="Rua 25 de Março", preco=100, aluguel=10, grupo="Azul Claro") # 6
        
        # 7: Sorte ou Revés
        self._add_casa_simples(nome="Sorte ou Revés", tipo="SORTE") # 7
        
        # Grupo 3: Azul Claro
        self._add_prop(nome="Avenida São João", preco=100, aluguel=10, grupo="Azul Claro") # 8
        self._add_prop(nome="Avenida Paulista", preco=120, aluguel=12, grupo="Azul Claro") # 9
        
        # 10: Cadeia/Prisão
        self._add_casa_simples(nome="Cadeia/Prisão", tipo="PRISAO") # 10 (Casa "normal" de parada)
        
        # Grupo 4: Rosa (Av. Vieira Souto, Niterói, Av. Atlântica)
        self._add_prop(nome="Avenida Vieira Souto", preco=140, aluguel=14, grupo="Rosa") # 11
        
        # 12: Companhia Elétrica
        self.casas.append(CasaCompanhia(nome="Companhia Elétrica", preco=VALOR_COMPANHIA_SERVICO)) # 12 - AGORA USA CASA COMPANHIA
        
        # Grupo 4: Rosa
        self._add_prop(nome="Niterói", preco=140, aluguel=14, grupo="Rosa") # 13
        self._add_prop(nome="Avenida Atlântica", preco=160, aluguel=16, grupo="Rosa") # 14
        
        # Grupo 2: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô Carioca", preco=VALOR_FERROVIA)) # 15
        
        # Grupo 5: Laranja (Av. Pres. Juscelino Kubitschek, Av. Eng. Luís Carlos Berrini, Av. Brig. Faria Lima)
        self._add_prop(nome="Avenida Presidente Juscelino Kubitschek", preco=180, aluguel=18, grupo="Laranja") # 16
        
        # 17: Cofre
        self._add_casa_simples(nome="Cofre", tipo="COFRE") # 17
        
        # Grupo 5: Laranja
        self._add_prop(nome="Avenida Engenheiro Luis Carlos Berrini", preco=180, aluguel=18, grupo="Laranja") # 18
        self._add_prop(nome="Avenida Brigadeiro Faria Lima", preco=200, aluguel=20, grupo="Laranja") # 19
        
        # 20: Estacionamento Grátis
        self._add_casa_simples(nome="Estacionamento Grátis", tipo="GRATIS") # 20
        
        # Grupo 6: Vermelho (Ipanema, Leblon, Copacabana)
        self._add_prop(nome="Ipanema", preco=220, aluguel=22, grupo="Vermelho") # 21
        
        # 22: Sorte ou Revés
        self._add_casa_simples(nome="Sorte ou Revés", tipo="SORTE") # 22
        
        # Grupo 6: Vermelho
        self._add_prop(nome="Leblon", preco=220, aluguel=22, grupo="Vermelho") # 23
        self._add_prop(nome="Copacabana", preco=120, aluguel=12, grupo="Vermelho") # 24
        
        # Grupo 2: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô Consolação", preco=VALOR_FERROVIA)) # 25
        
        # Grupo 7: Amarelo (Av. Cidade Jardim, Pacaembu, Ibirapuera)
        self._add_prop(nome="Avenida Cidade Jardim", preco=240, aluguel=24, grupo="Amarelo") # 26
        self._add_prop(nome="Pacaembu", preco=260, aluguel=26, grupo="Amarelo") # 27
        
        # 28: Companhia de Distribuição de Água
        self.casas.append(CasaCompanhia(nome="Companhia de Distribuição de Água", preco=VALOR_COMPANHIA_SERVICO)) # 28
        
        # Grupo 7: Amarelo
        self._add_prop(nome="Ibirapuera", preco=280, aluguel=28, grupo="Amarelo") # 29
        
        # 30: VÁ PARA A CADEIA (Foco da SCRUM-8)
        self.casas.append(CasaVAPrisao()) # 30
        
        # Grupo 8: Verde (Barra da Tijuca, Jardim Botânico, Lagoa Rodrigo de Freitas)
        self._add_prop(nome="Barra da Tijuca", preco=300, aluguel=30, grupo="Verde") # 31
        self._add_prop(nome="Jardim Botânico", preco=300, aluguel=30, grupo="Verde") # 32
        
        # 33: Cofre
        self._add_casa_simples(nome="Cofre", tipo="COFRE") # 33
        
        # Grupo 8: Verde
        self._add_prop(nome="Lagoa Rodrigo de Freitas", preco=320, aluguel=32, grupo="Verde") # 34
        
        # Grupo 2: Metrô/Ferrovia
        self.casas.append(CasaMetro(nome="Estação de Metrô República", preco=VALOR_FERROVIA)) # 35
        
        # 36: Sorte ou Revés
        self._add_casa_simples(nome="Sorte ou Revés", tipo="SORTE") # 36
        
        # Grupo 9: Azul Escuro (Av. Morumbi, Rua Oscar Freire)
        self._add_prop(nome="Avenida Morumbi", preco=350, aluguel=35, grupo="Azul Escuro") # 37
        
        # 38: Taxa de Riqueza (pague 100)
        self.casas.append(CasaImposto("Taxa de Riqueza", TAXA_RIQUEZA_VALOR)) # 38
        
        # Grupo 9: Azul Escuro
        self._add_prop(nome="Rua Oscar Freire", preco=400, aluguel=40, grupo="Azul Escuro") # 39
        
        # O Ponto de Partida (Posição 0) é a Casa[0] (Saída/GO).
        
        # Verificação final para garantir 40 casas
        if len(self.casas) != 40:
            raise Exception(f"Erro ao construir o tabuleiro: {len(self.casas)} casas encontradas, 40 esperadas.")

    def get_casa(self, posicao):
        """Retorna o objeto Casa na posição especificada (0 a 39)."""
        return self.casas[posicao % 40]

    # --- Métodos Auxiliares para simplificar a criação ---
    def _add_prop(self, nome, preco, aluguel, grupo): # AGORA ACEITA 4 ARGUMENTOS
        # Passa os 4 argumentos obrigatórios para Propriedade
        self.casas.append(Propriedade(nome, preco, aluguel, grupo))
        
    def _add_casa_simples(self, nome, tipo):
        self.casas.append(Casa(nome, tipo))
        self._current_pos += 1 # Incrementa após adicionar
        print(f"DEBUG: Casa {self._current_pos - 1} - {nome}") # Opcional, para debug

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