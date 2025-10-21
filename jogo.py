# regras.py
# Módulo principal que gerencia o fluxo de turnos, rolagem de dados e a aplicação das regras do jogo.

""" 
Esse regras.py está funcionando como um main.py provisório...

Para a versão parcial, podemos executá-lo e usar o console ou prints do mesmo para a evidenciar o progresso da Versão Parcial do Produto...
Esse é um backend inicial...

"""

import random
# Importação dos módulos que definem a Estrutura do Jogo:
from jogador import Jogador 
from banco import Banco
from tabuleiro import Tabuleiro 

class Jogo:
    VALOR_PASSAGEM_SAIDA = 200 # Regra clássica do Monopoly

    def __init__(self, nomes_jogadores):
        """Inicializa o Banco, o Tabuleiro e os Jogadores."""
        self.banco = Banco()
        self.tabuleiro = Tabuleiro()
        self.jogadores = []

        # Inicializa o objeto Jogador e a conta no Banco para cada nome
        for i, nome in enumerate(nomes_jogadores):
            novo_jogador = Jogador(nome, f"Peça {i+1}")
            self.jogadores.append(novo_jogador)
            self.banco.inicializar_conta(nome)
        
        # O jogo sempre começa com o primeiro jogador da lista
        self.indice_turno_atual = 0

    def rolar_dados(self):
        """Simula a rolagem de dois dados (2d6)."""
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        eh_duplo = d1 == d2
        print(f"  > Dados rolados: {d1} e {d2}. Total: {total} ({'DUPLO!' if eh_duplo else 'Simples'})")
        return total, eh_duplo

    def verificar_passagem_saida(self, jogador_obj, posicao_antiga, posicao_nova):
        """Verifica se o jogador passou pela casa 'Saída' e credita o valor."""
        # Se a posição antiga era maior que a nova, significa que ele completou uma volta
        if posicao_nova < posicao_antiga:
            print(f"  > **PASSOU PELA SAÍDA!** Recebe R${self.VALOR_PASSAGEM_SAIDA}.")
            self.banco.depositar(jogador_obj.nome, self.VALOR_PASSAGEM_SAIDA)

    def acao_compra_propriedade(self, jogador, propriedade):
        """Simula a ação de compra e o pagamento ao Banco."""
        # Esta é uma lógica SIMPLIFICADA para a Versão Parcial
        
        # Pergunta ao jogador (em um sistema real seria via interface)
        decisao = input(f"    Quer comprar {propriedade.nome} por R${propriedade.preco_compra}? (s/n): ").lower()
        
        if decisao == 's':
            # Tenta realizar a transação financeira
            if self.banco.pagar(jogador.nome, propriedade.preco_compra, recebedor="Banco"):
                # Transação bem-sucedida, atualiza o estado da propriedade
                propriedade.proprietario = jogador
                jogador.adicionar_propriedade(propriedade)
        else:
            print(f"    {jogador.nome} decide não comprar {propriedade.nome}.")
            # Em uma partida real, a propriedade iria a leilão aqui.

    def iniciar_turno(self):
        """Executa um turno completo para o jogador atual."""
        jogador = self.jogadores[self.indice_turno_atual]
        posicao_antiga = jogador.posicao
        
        print(f"\n==========================================")
        print(f"TURNO {self.indice_turno_atual + 1}: {jogador.nome} ({jogador.peca})")
        print(f"==========================================")
        
        # 1. Rolagem de Dados e Movimentação
        rolagem, eh_duplo = self.rolar_dados()
        jogador.mover(rolagem) 
        
        posicao_nova = jogador.posicao

        # 2. Verificação de Passagem pela Saída
        self.verificar_passagem_saida(jogador, posicao_antiga, posicao_nova)

        # 3. Ação da Casa (Interação entre Tabuleiro, Jogador e Banco)
        casa_atual = self.tabuleiro.get_casa(posicao_nova)
        casa_atual.acao_ao_cair(jogador, self.banco) # Chamada da ação da Casa
        
        # Ações específicas de Propriedade (Lógica de Compra)
        if casa_atual.tipo == 'PROPRIEDADE':
            propriedade = casa_atual # Casa é um objeto Propriedade
            
            if propriedade.is_livre():
                # Ação de Compra (Simulada via console)
                self.acao_compra_propriedade(jogador, propriedade)
            
            elif propriedade.proprietario.nome != jogador.nome:
                # Ação de Pagamento de Aluguel
                aluguel = propriedade.calcular_aluguel()
                print(f"  > Pagando aluguel de R${aluguel} para {propriedade.proprietario.nome}...")
                
                # O banco gerencia a transação (pagador, valor, recebedor)
                self.banco.pagar(jogador.nome, aluguel, propriedade.proprietario.nome)

        # 4. Mudar o Turno (Lógica simples: passa para o próximo, ignorando duplos por enquanto)
        self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
        
        # Exibe o status final do turno para o monitoramento
        self.status_geral()
        input("\n[Pressione Enter para ir para o próximo turno...]")


    def status_geral(self):
        """
        Exibe o status de todos os jogadores (Atende ao Requisito 04: Usabilidade/Monitoramento).
        Este é o principal dado de monitoramento para a Versão Parcial.
        """
        print("\n--- STATUS GERAL DOS JOGADORES ---")
        for jogador in self.jogadores:
            saldo = self.banco.consultar_saldo(jogador.nome)
            print(jogador.status_resumido(saldo))

# --- Bloco de Demonstração para a Versão Parcial (main.py temporário) ---
if __name__ == '__main__':
    print("--- DEMONSTRAÇÃO DA VERSÃO PARCIAL: BACKEND ---")
    
    # Simulação da Inicialização da Partida (Requisito 08: Escalabilidade)
    nomes = ["Alice (Humana)", "Bot 1 (IA)", "Carlos (Humano)"]
    
    jogo = Jogo(nomes)
    print("\n[PARTIDA INICIADA]")
    jogo.status_geral()

    # Execução de alguns turnos para demonstrar a lógica (Requisito 10: Conformidade Regras)
    for i in range(1, 4): # Simula 3 turnos (um para cada jogador)
        jogo.iniciar_turno()
        
    print("\n--- FIM DA DEMONSTRAÇÃO ---")
    print("O backend demonstrou: Transações Financeiras, Movimentação e Ações Básicas de Propriedade.")