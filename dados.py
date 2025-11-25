# dados.py
# Módulo responsável pela rolagem de dados

import random

class Dados:
    """Classe para gerenciar a rolagem de dados do jogo"""
    
    def __init__(self, num_dados=2):
        """
        Inicializa o sistema de dados.
        Args:
            num_dados: Número de dados a serem rolados (padrão: 2)
        """
        self.num_dados = num_dados
        self.ultima_rolagem = []
        self.ultimo_total = 0
        
    def rolar(self):
        """
        Rola os dados e retorna o resultado.
        Returns:
            tuple: (total, lista_valores, eh_dupla)
        """
        self.ultima_rolagem = [random.randint(1, 6) for _ in range(self.num_dados)]
        self.ultimo_total = sum(self.ultima_rolagem)
        
        # Verifica se é uma dupla (ambos dados com o mesmo valor)
        eh_dupla = len(set(self.ultima_rolagem)) == 1 if self.num_dados > 1 else False
        
        return self.ultimo_total, self.ultima_rolagem, eh_dupla
    
    def obter_ultima_rolagem(self):
        """Retorna informações da última rolagem"""
        return {
            'total': self.ultimo_total,
            'valores': self.ultima_rolagem,
            'eh_dupla': len(set(self.ultima_rolagem)) == 1 if len(self.ultima_rolagem) > 1 else False
        }
    
    def __str__(self):
        if self.ultima_rolagem:
            return f"Dados: {self.ultima_rolagem} = {self.ultimo_total}"
        return "Dados: Ainda não foram rolados"

# Teste do módulo
if __name__ == '__main__':
    print("--- Teste do Módulo Dados ---")
    
    dados = Dados()
    
    print("\n--- Simulando 10 rolagens ---")
    duplas_count = 0
    for i in range(10):
        total, valores, eh_dupla = dados.rolar()
        dupla_str = " [DUPLA!]" if eh_dupla else ""
        print(f"Rolagem {i+1}: {valores[0]} + {valores[1]} = {total}{dupla_str}")
        if eh_dupla:
            duplas_count += 1
    
    print(f"\nTotal de duplas: {duplas_count}/10")
