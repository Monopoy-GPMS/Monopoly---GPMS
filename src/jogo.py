# src/jogo.py
# Módulo principal que gerencia o fluxo de turnos, rolagem de dados e a aplicação das regras do jogo.

import random

# Importação CORRIGIDA para a nova estrutura de módulos (imports relativos dentro de src/)
from jogador import Jogador 
from banco import Banco
from tabuleiro import Tabuleiro 
from constantes import VALOR_PASSAGEM_SAIDA # Usamos a constante do novo arquivo!

class Jogo:
    # A constante VALOR_PASSAGEM_SAIDA foi removida daqui e está em constantes.py

    def __init__(self, nomes_jogadores):
        """Inicializa o Banco, o Tabuleiro e os Jogadores."""
        self.banco = Banco()
        self.tabuleiro = Tabuleiro()
        self.jogadores = []
        self.ultimo_d1 = 1 # Valor inicial dado 1
        self.ultimo_d2 = 1 # Valor inicial dado 2

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
        return d1, d2, total, eh_duplo

    def verificar_passagem_saida(self, jogador_obj, posicao_antiga, posicao_nova):
        """Verifica se o jogador passou pela casa 'Saída' e credita o valor."""
        if posicao_nova < posicao_antiga:
            print(f"  > **PASSOU PELA SAÍDA!** Recebe R${VALOR_PASSAGEM_SAIDA}.")
            self.banco.depositar(jogador_obj.nome, VALOR_PASSAGEM_SAIDA)

    def acao_compra_propriedade(self, jogador, propriedade):
        """Lógica SIMPLIFICADA de compra via console."""
        decisao = input(f"    Quer comprar {propriedade.nome} por R${propriedade.preco_compra}? (s/n): ").lower()
        
        if decisao == 's':
            if self.banco.pagar(jogador.nome, propriedade.preco_compra, recebedor="Banco"):
                propriedade.proprietario = jogador
                jogador.adicionar_propriedade(propriedade)
        else:
            print(f"    {jogador.nome} decide não comprar {propriedade.nome}.")
            # Lógica de leilão seria implementada aqui.

    def iniciar_turno(self):
        """Executa um turno completo para o jogador atual."""
        jogador = self.jogadores[self.indice_turno_atual]
        posicao_antiga = jogador.posicao
        
        print(f"\n==========================================")
        print(f"TURNO DE: {jogador.nome} | Posição Inicial: {posicao_antiga}")
        print(f"==========================================")
        
        # 1. Rolagem de Dados e Movimentação
        d1, d2, rolagem, eh_duplo = self.rolar_dados()
        self.ultimo_d1 = d1
        self.ultimo_d2 = d2
        jogador.mover(rolagem) 
        
        posicao_nova = jogador.posicao

        # 2. Verificação de Passagem pela Saída
        self.verificar_passagem_saida(jogador, posicao_antiga, posicao_nova)

        # 3. Ação da Casa (Chama a lógica específica, incluindo Imposto e Prisão)
        casa_atual = self.tabuleiro.get_casa(posicao_nova)
        
        # Esta linha faz a magia da SCRUM-8 acontecer: 
        # Se cair no Imposto, o acao_ao_cair de CasaImposto cobra.
        # Se cair no Vá para a Prisão, o acao_ao_cair de CasaVAPrisao move o jogador.
        casa_atual.acao_ao_cair(jogador, self.banco) 
        
        # 4. Ações de Propriedade (Compra/Aluguel)
        if hasattr(casa_atual, 'is_livre'): 
            propriedade = casa_atual 
            
            if propriedade.is_livre():
                # ... (lógica de compra) IMPLEMENTAR...
                pass
            
            elif propriedade.proprietario and propriedade.proprietario.nome != jogador.nome:
                
                # CHAVE DA CORREÇÃO: Passar a última rolagem do jogador
                rolagem_para_aluguel = jogador.ultima_rolagem 
                
                aluguel = propriedade.calcular_aluguel(rolagem_dados=rolagem_para_aluguel) 
                
                print(f"  > Pagando aluguel de R${aluguel} para {propriedade.proprietario.nome}...")
                self.banco.pagar(jogador.nome, aluguel, propriedade.proprietario.nome)

        # 5. Mudar o Turno
        if not eh_duplo:
             self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
        
        self.status_geral()

    def status_geral(self):
        """Exibe o status de todos os jogadores (Requisito 04: Usabilidade/Monitoramento)."""
        print("\n--- STATUS GERAL DOS JOGADORES ---")
        for jogador in self.jogadores:
            saldo = self.banco.consultar_saldo(jogador.nome)
            print(jogador.status_resumido(saldo))

# O bloco de teste 'if __name__ == '__main__': ' foi movido para src/main.py