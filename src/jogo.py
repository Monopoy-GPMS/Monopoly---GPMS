# src/jogo.py
# Módulo principal que gerencia o fluxo de turnos, rolagem de dados e a aplicação das regras do jogo.

import random

# Importação CORRIGIDA para a nova estrutura de módulos (imports relativos dentro de src/)
from jogador import Jogador 
from banco import Banco
from tabuleiro import Tabuleiro 
from constantes import VALOR_PASSAGEM_SAIDA, POSICAO_PRISAO # Usamos a constante do novo arquivo!

class Jogo:
    # A constante VALOR_PASSAGEM_SAIDA foi removida daqui e está em constantes.py

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
        if posicao_nova < posicao_antiga:
            print(f"  > **PASSOU PELA SAÍDA!** Recebe R${VALOR_PASSAGEM_SAIDA}.")
            self.banco.depositar(jogador_obj.nome, VALOR_PASSAGEM_SAIDA)

    def acao_compra_propriedade(self, jogador, propriedade):
        """Lógica SIMPLIFICADA de compra via console."""
        saldo_jogador = self.banco.consultar_saldo(jogador.nome)

        if saldo_jogador < propriedade.preco_compra:
             print(f"O jodador {jogador.nome} não possui saldo suficiente para comprar a propriedade {propriedade.nome}")
             return
        else:
             
            decisao = input(f"    Quer comprar {propriedade.nome} por R${propriedade.preco_compra}? (s/n): ").lower()
            
            if decisao == 's':
                if self.banco.pagar(jogador.nome, propriedade.preco_compra, recebedor="Banco"):
                    propriedade.proprietario = jogador
                    jogador.adicionar_propriedade(propriedade)
            else:
                print(f"    {jogador.nome} decide não comprar {propriedade.nome}.")
                # Lógica de leilão seria implementada aqui.

    def gerenciar_propriedades(self, jogador):
         while True:
              print("(1)Hipotecar Propriedede")
              print("(2)Pagar Hipoteca")
              print("(3)Sair")
              decisao_hipoteca = input()

              if decisao_hipoteca == '1':
                   propriedades_disp_hipoteca = []
                   for propriedade in jogador.propriedades:
                        if propriedade.hipotecada == False:
                             
                             propriedades_disp_hipoteca.append(propriedade)
                   if not propriedades_disp_hipoteca:
                     print("Você não tem propriedades disponíveis para hipoteca")
                     continue
                   else:
                      print("Qual propriedade deseja Hipotecar?")  
                      for i, prop in enumerate(propriedades_disp_hipoteca):
                          valor_hipoteca = prop.preco_compra/2
                          print(f"{i+1} - {prop.nome} - Valor da Hipoteca = {valor_hipoteca}")
                      try:
                        escolha_prop_hip = int(input("Digite o numero da propriedade (OU 0 PARA CANCELAR A AÇÃO)"))
                        if escolha_prop_hip == 0:
                            continue
                        indice_prop_esc = escolha_prop_hip - 1
                        if  0 <= indice_prop_esc < len(propriedades_disp_hipoteca):
                            prop_hipotecada = propriedades_disp_hipoteca[indice_prop_esc]
                            valor_hipoteca = prop_hipotecada /2
                            prop_hipotecada.hipotecada = True
                            self.banco.depositar(jogador.nome, valor_hipoteca)
                            print(f"  > Você hipotecou {prop_hipotecada.nome} e recebeu R${valor_hipoteca}.")
                        else:
                            print("Digite um valor válido")
                      except ValueError:
                        print("Digite um valor válido")
    

                   
                             

        

         
    def iniciar_turno(self):
        """Executa um turno completo para o jogador atual."""
        jogador = self.jogadores[self.indice_turno_atual]
        posicao_antiga = jogador.posicao

        
        print(f"\n==========================================")
        print(f"TURNO DE: {jogador.nome} | Posição Inicial: {posicao_antiga}")
        print(f"==========================================")
            
            # 1. Rolagem de Dados e Movimentação
        rolagem, eh_duplo = self.rolar_dados()
        jogador.ultima_rolagem = rolagem
            
        if eh_duplo:
            jogador.contagem_duplos +=1
            print(f"  > Rolagem dupla! (Contagem: {jogador.contagem_duplos})")

            if jogador.contagem_duplos ==3 :
                    print(f"  > **{jogador.nome} rolou 3 duplos e FOI PRESO!**")
                    jogador.posicao = POSICAO_PRISAO
                    jogador.em_prisao = True
                    jogador.contagem_duplos = 0

                    ##passa o turno apos a prisao
                    self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
                    self.status_geral()
                    return
            else:
                    jogador.contagem_duplos = 0

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
            ##alteracao feita por VINICIUS
            if jogador.em_prisao: # Se a acao_ao_cair o prendeu
                # Passa o turno
                self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
                self.status_geral()
                return
            # 4. Ações de Propriedade (Compra/Aluguel)
            if hasattr(casa_atual, 'is_livre'): 
                propriedade = casa_atual 
                
                if propriedade.is_livre():
                        self.acao_compra_propriedade(jogador, propriedade)
                
                elif propriedade.proprietario and propriedade.proprietario.nome != jogador.nome and not propriedade.hipotecada:
                    
                    # CHAVE DA CORREÇÃO: Passar a última rolagem do jogador
                    rolagem_para_aluguel = jogador.ultima_rolagem 
                    
                    aluguel = propriedade.calcular_aluguel(rolagem_dados=rolagem_para_aluguel) 
                    
                    print(f"  > Pagando aluguel de R${aluguel} para {propriedade.proprietario.nome}...")
                    self.banco.pagar(jogador.nome, aluguel, propriedade.proprietario.nome)

            # 5. Mudar o Turno
            if not eh_duplo:
                self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
                
            else:
                print(f"  > {jogador.nome} rolou um duplo e joga novamente!")
            
            self.status_geral()

    def status_geral(self):
        """Exibe o status de todos os jogadores (Requisito 04: Usabilidade/Monitoramento)."""
        print("\n--- STATUS GERAL DOS JOGADORES ---")
        for jogador in self.jogadores:
            saldo = self.banco.consultar_saldo(jogador.nome)
            print(jogador.status_resumido(saldo))

# O bloco de teste 'if __name__ == '__main__': ' foi movido para src/main.py