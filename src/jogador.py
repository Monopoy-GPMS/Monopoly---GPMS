# jogador.py
# Módulo responsável pela classe Jogador, que armazena o estado e as ações de cada participante.

class Jogador:
    def __init__(self, nome, peca, is_ia=False):
        """
        Inicializa o jogador. O saldo será gerenciado pelo módulo 'banco'.
        """
        self.nome = nome          # Nome do jogador (identificador)
        self.peca = peca          # Peça escolhida (ex: "Carro", "Chapéu")
        self.posicao = 0          # Posição inicial: Casa "Saída" (0)
        self.propriedades = []    # Lista de objetos Propriedade que o jogador possui
        self.em_prisao = False    # Flag que indica se o jogador está na prisão
        self.is_ia = is_ia        # Flag para Escalabilidade (Requisito 08): Define se é um bot
        self.cartas_livre_prisao = 0 # Contagem de cartas "Saia Livre da Prisão"
        self.ultima_rolagem = 0 # Armazena o valor total dos dados para Aluguel de Companhias

    def mover(self, dados_rolados):
        """
        Atualiza a posição do jogador no tabuleiro.
        Lógica de "passar pela saída" (ganhar 200) será implementada no módulo 'regras', 
        que coordena a interação entre Jogador, Tabuleiro e Banco.
        """
        posicao_antiga = self.posicao
        self.posicao = (self.posicao + dados_rolados) % 40 # O tabuleiro tem 40 casas (0 a 39)
        
        print(f"  > {self.nome} rolou {dados_rolados} e moveu de {posicao_antiga} para a Casa {self.posicao}.")

    def adicionar_propriedade(self, propriedade):
        """Adiciona uma propriedade comprada ou recebida à lista do jogador."""
        self.propriedades.append(propriedade)
        print(f"  > {self.nome} adquiriu a propriedade: {propriedade.nome}.")
        
    def remover_propriedade(self, propriedade):
        """Remove uma propriedade (em caso de venda/hipoteca/falência)."""
        if propriedade in self.propriedades:
            self.propriedades.remove(propriedade)
            return True
        return False

    def status_resumido(self, saldo):
        """
        Gera um resumo do estado do jogador para a Interface do Jogador (Requisito 04: Usabilidade).
        Note que o SALDO vem do módulo Banco, mas a posição e propriedades vêm desta classe.
        """
        prop_count = len(self.propriedades)
        
        status = (
            f"--- {self.nome} ({'IA' if self.is_ia else 'Humano'}) ---\n"
            f"  Peça: {self.peca}\n"
            f"  **SALDO**: R${saldo}\n"
            f"  **POSIÇÃO**: Casa {self.posicao} ({'NA PRISÃO' if self.em_prisao else 'Livre'})\n"
            f"  **PROPRIEDADES**: {prop_count} compradas"
        )
        return status
        
# --- Bloco de Teste/Demonstração para a Versão Parcial ---
if __name__ == '__main__':
    print("--- Teste do Módulo Jogador ---")
    
    # Simulação de objetos simples para a lista de propriedades
    class PropriedadeMock:
        def __init__(self, nome):
            self.nome = nome

    # 1. Inicialização de jogadores (Humano e Bot)
    jogador1 = Jogador("Patrícia", "Chapéu")
    jogador2 = Jogador("Bot Monopólio", "Bota", is_ia=True)
    
    # 2. Simulação de ações
    print("\n--- Simulação de Ações ---")
    
    # Movimentação
    jogador1.mover(7)
    jogador2.mover(15)
    
    # Compra de Propriedade
    prop1 = PropriedadeMock("Avenida Atlântica")
    prop2 = PropriedadeMock("Ferrovia Reading")
    
    jogador1.adicionar_propriedade(prop1)
    jogador1.adicionar_propriedade(prop2)
    
    # 3. Exibição do Status (Requisito 04)
    print("\n--- Status do Jogador (Simulando Saldo de R$1000) ---")
    
    # O saldo R$1000 é um mock (valor temporário para simular um cenário), pois o Banco não foi importado neste arquivo.
    print(jogador1.status_resumido(saldo=1000)) 
    print(jogador2.status_resumido(saldo=1500))