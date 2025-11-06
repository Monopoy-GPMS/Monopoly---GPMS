# src/jogo.py
# Módulo principal que gerencia o fluxo de turnos, rolagem de dados e a aplicação das regras do jogo.

import random

# Importação CORRIGIDA para a nova estrutura de módulos (imports relativos dentro de src/)
from jogador import Jogador 
from banco import Banco
from tabuleiro import Tabuleiro 
from constantes import VALOR_PASSAGEM_SAIDA
# Importações novas necessárias
from propriedades import Propriedade, CasaCompanhia
from casas import CasaImposto, CasaVAPrisao

class Jogo:
    
    def __init__(self, nomes_jogadores):
        """Inicializa o Banco, o Tabuleiro e os Jogadores."""
        self.banco = Banco()
        self.tabuleiro = Tabuleiro()
        self.jogadores = []
        self.ultimo_d1 = 1 
        self.ultimo_d2 = 1 
        self.eh_duplo_ultimo = False # Novo: para controlar o turno

        for i, nome in enumerate(nomes_jogadores):
            novo_jogador = Jogador(nome, f"Peça {i+1}")
            self.jogadores.append(novo_jogador)
            self.banco.inicializar_conta(nome)
        
        self.indice_turno_atual = 0

    def rolar_dados(self):
        """Simula a rolagem de dois dados (2d6)."""
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        eh_duplo = d1 == d2
        print(f"  > Dados rolados: {d1} e {d2}. Total: {total} ({'DUPLO!' if eh_duplo else 'Simples'})")
        
        # Armazena os resultados na instância
        self.ultimo_d1 = d1
        self.ultimo_d2 = d2
        self.eh_duplo_ultimo = eh_duplo
        return total

    def verificar_passagem_saida(self, jogador_obj, posicao_antiga, posicao_nova):
        """Verifica se o jogador passou pela casa 'Saída' e credita o valor."""
        if posicao_nova < posicao_antiga:
            print(f"  > **PASSOU PELA SAÍDA!** Recebe R${VALOR_PASSAGEM_SAIDA}.")
            self.banco.depositar(jogador_obj.nome, VALOR_PASSAGEM_SAIDA)

    # REMOVIDO: acao_compra_propriedade (a lógica de input() não funciona com Pygame)
    # def acao_compra_propriedade(self, jogador, propriedade):
    #     ...

    def rolar_dados_e_mover(self):
        """
        Etapa 1 do Turno: Rola os dados, move o jogador e retorna a casa
        onde ele parou. Nenhuma ação é executada aqui.
        """
        jogador = self.jogadores[self.indice_turno_atual]
        posicao_antiga = jogador.posicao
        
        print(f"\n==========================================")
        print(f"TURNO DE: {jogador.nome} | Posição Inicial: {posicao_antiga}")
        print(f"==========================================")
        
        # 1. Rolagem de Dados e Movimentação
        rolagem = self.rolar_dados() # Agora usa o método self.rolar_dados()
        jogador.mover(rolagem) 
        posicao_nova = jogador.posicao

        # 2. Verificação de Passagem pela Saída
        self.verificar_passagem_saida(jogador, posicao_antiga, posicao_nova)

        # 3. Retorna a casa onde parou
        casa_atual = self.tabuleiro.get_casa(posicao_nova)
        return casa_atual

    def obter_acao_para_casa(self, casa_atual):
        """
        Etapa 2 do Turno: Analisa a casa e retorna um dicionário
        com a ação que o frontend deve tomar.
        """
        jogador_atual = self.jogadores[self.indice_turno_atual]

        # 1. Opção de Compra
        if isinstance(casa_atual, Propriedade) and casa_atual.is_livre():
            return {"tipo": "DECISAO_COMPRA", "casa": casa_atual}
        
        # 2. Ações Automáticas (Imposto, Vá para Prisão)
        if isinstance(casa_atual, (CasaImposto, CasaVAPrisao)):
            return {"tipo": "ACAO_AUTOMATICA", "casa": casa_atual}

        # 3. Pagar Aluguel
        if (isinstance(casa_atual, Propriedade) and 
            casa_atual.proprietario and 
            casa_atual.proprietario != jogador_atual):
            
            return {"tipo": "PAGAR_ALUGUEL", "casa": casa_atual}

        # 4. Nenhuma Ação (Estacionamento Grátis, Prisão (visitante), propriedade própria)
        return {"tipo": "NENHUMA_ACAO"}

    def executar_acao_automatica(self, casa_atual):
        """
        Etapa 3 (Opcional): Executa ações que não pedem input do usuário,
        como pagar aluguel ou ir para a prisão.
        """
        jogador_atual = self.jogadores[self.indice_turno_atual]

        # 1. Ação de Imposto ou Vá para Prisão
        if isinstance(casa_atual, (CasaImposto, CasaVAPrisao)):
            casa_atual.acao_ao_cair(jogador_atual, self.banco)
        
        # 2. Ação de Pagar Aluguel
        elif (isinstance(casa_atual, Propriedade) and 
              casa_atual.proprietario and 
              casa_atual.proprietario != jogador_atual):
            
            # Lógica de aluguel (movemos de iniciar_turno para cá)
            rolagem_para_aluguel = self.ultimo_d1 + self.ultimo_d2
            
            # Passa a rolagem, crucial para Companhias
            aluguel = casa_atual.calcular_aluguel(rolagem_dados=rolagem_para_aluguel) 
            
            print(f"  > Pagando aluguel de R${aluguel} para {casa_atual.proprietario.nome}...")
            self.banco.pagar(jogador_atual.nome, aluguel, casa_atual.proprietario.nome)

    def executar_compra(self):
        """
        Etapa 3 (Opcional): Chamado pelo frontend quando o jogador
        clica em "Comprar".
        """
        jogador_atual = self.jogadores[self.indice_turno_atual]
        propriedade = self.tabuleiro.get_casa(jogador_atual.posicao)
        
        if not isinstance(propriedade, Propriedade):
            return False # Segurança

        # Tenta pagar ao banco
        if self.banco.pagar(jogador_atual.nome, propriedade.preco_compra, recebedor="Banco"):
            propriedade.proprietario = jogador_atual
            jogador_atual.adicionar_propriedade(propriedade)
            print(f"  > {jogador_atual.nome} comprou {propriedade.nome}!")
            return True
        else:
            print(f"  > {jogador_atual.nome} não tem saldo para comprar {propriedade.nome}.")
            return False # Saldo insuficiente

    def finalizar_turno(self):
        """
        Etapa 4: Passa o turno para o próximo jogador, a menos que
        os dados tenham sido duplos.
        """
        if not self.eh_duplo_ultimo:
             self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
             print(f"  > Turno finalizado. Próximo jogador: {self.jogadores[self.indice_turno_atual].nome}")
        else:
            print(f"  > Jogou dados duplos! Joga novamente.")
        
        self.status_geral()

    def status_geral(self):
        """Exibe o status de todos os jogadores (Requisito 04: Usabilidade/Monitoramento)."""
        print("\n--- STATUS GERAL DOS JOGADORES ---")
        for jogador in self.jogadores:
            saldo = self.banco.consultar_saldo(jogador.nome)
            print(jogador.status_resumido(saldo))