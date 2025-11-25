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
from casas import CasaImposto, CasaVAPrisao, CasaSorteReves, CasaCofre

from dados import Dados
from cartas import BaralhoCartas
from regras_prisao import GestorPrisao
from construcao import GestorConstrucao
from regras_propriedades import GestorPropriedades
from sistema_propostas import SistemaPropostas

class Jogo:
    
    def __init__(self, nomes_jogadores):
        """Inicializa o Banco, o Tabuleiro e os Jogadores."""
        self.banco = Banco()
        self.tabuleiro = Tabuleiro()
        
        self.dados_obj = Dados(num_dados=2)
        self.baralho_sorte = BaralhoCartas('SORTE')
        self.baralho_cofre = BaralhoCartas('COFRE')  # Renamed baralho_reves to baralho_cofre for clarity and consistency
        self.gestor_prisao = GestorPrisao(self.banco)
        self.gestor_construcao = GestorConstrucao(self.tabuleiro, self.banco)
        self.gestor_propriedades = GestorPropriedades(self.banco, self.tabuleiro)
        self.sistema_propostas = SistemaPropostas(self.banco, self.tabuleiro)
        
        self.jogadores = []
        self.ultimo_d1 = 1 
        self.ultimo_d2 = 1 
        self.eh_duplo_ultimo = False
        self.duplas_consecutivas = 0  # Track consecutive doubles

        for i, nome in enumerate(nomes_jogadores):
            novo_jogador = Jogador(nome, f"Peça {i+1}")
            self.jogadores.append(novo_jogador)
            self.banco.inicializar_conta(nome)
        
        self.indice_turno_atual = 0
        self.jogo_finalizado = False  # Track game state

    def rolar_dados(self):
        """Simula a rolagem de dois dados (2d6)."""
        total, valores, eh_duplo = self.dados_obj.rolar()
        
        print(f"  > Dados rolados: {valores[0]} e {valores[1]}. Total: {total} ({'DUPLO!' if eh_duplo else 'Simples'})")
        
        self.ultimo_d1 = valores[0]
        self.ultimo_d2 = valores[1]
        self.eh_duplo_ultimo = eh_duplo
        
        if eh_duplo:
            self.duplas_consecutivas += 1
        else:
            self.duplas_consecutivas = 0
        
        return total

    def verificar_passagem_saida(self, jogador_obj, posicao_antiga, posicao_nova):
        """Verifica se o jogador passou pela casa 'Saída' e credita o valor."""
        if posicao_nova < posicao_antiga:
            print(f"  > **PASSOU PELA SAÍDA!** Recebe R${VALOR_PASSAGEM_SAIDA}.")
            self.banco.depositar(jogador_obj.nome, VALOR_PASSAGEM_SAIDA)

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
        
        if jogador.em_prisao:
            saiu, pode_mover, valor_movimento = self.gestor_prisao.processar_turno_prisao(jogador, self.dados_obj)
            
            if not saiu:
                # Player stays in prison, end turn
                casa_atual = self.tabuleiro.get_casa(jogador.posicao)
                return casa_atual
            elif saiu and pode_mover:
                # Player got out with doubles, can move
                rolagem = valor_movimento
            else:
                # Player paid or used card, doesn't move this turn
                casa_atual = self.tabuleiro.get_casa(jogador.posicao)
                return casa_atual
        else:
            # Normal turn
            rolagem = self.rolar_dados()
            
            if self.duplas_consecutivas >= 3:
                print(f"  > {jogador.nome} tirou 3 duplas seguidas! Vai para a prisão!")
                self.gestor_prisao.enviar_prisao(jogador)
                self.duplas_consecutivas = 0
                self.eh_duplo_ultimo = False
                casa_atual = self.tabuleiro.get_casa(jogador.posicao)
                return casa_atual
        
        jogador.mover(rolagem) 
        posicao_nova = jogador.posicao

        self.verificar_passagem_saida(jogador, posicao_antiga, posicao_nova)

        casa_atual = self.tabuleiro.get_casa(posicao_nova)
        return casa_atual

    def obter_acao_para_casa(self, casa_atual):
        """
        Etapa 2 do Turno: Analisa a casa e retorna um dicionário
        com a ação que o frontend deve tomar.
        """
        jogador_atual = self.jogadores[self.indice_turno_atual]

        if isinstance(casa_atual, (CasaSorteReves, CasaCofre)):
            return {"tipo": "ACAO_AUTOMATICA", "casa": casa_atual}

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

        # 4. Nenhuma Ação
        return {"tipo": "NENHUMA_ACAO"}

    def executar_acao_automatica(self, casa_atual):
        """
        Etapa 3 (Opcional): Executa ações que não pedem input do usuário.
        Retorna uma mensagem para o frontend, se houver.
        """
        jogador_atual = self.jogadores[self.indice_turno_atual]

        if isinstance(casa_atual, (CasaSorteReves, CasaCofre)):
            resultado = casa_atual.sorteio_evento(jogador_atual, self.banco)
            print(f"  > Resultado sorteio: {resultado}")
            return resultado

        # Ação de Imposto ou Vá para Prisão
        if isinstance(casa_atual, CasaVAPrisao):
            self.gestor_prisao.enviar_prisao(jogador_atual)
            return {"tipo": "PRISAO", "mensagem": f"{jogador_atual.nome} foi para a prisão!"}
        elif isinstance(casa_atual, CasaImposto):
            casa_atual.acao_ao_cair(jogador_atual, self.banco)
            return {"tipo": "IMPOSTO", "mensagem": f"Pagou R${casa_atual.valor} de imposto"}
        
        # Ação de Pagar Aluguel
        elif (isinstance(casa_atual, Propriedade) and 
              casa_atual.proprietario and 
              casa_atual.proprietario != jogador_atual):
            
            rolagem_para_aluguel = self.ultimo_d1 + self.ultimo_d2
            aluguel = casa_atual.calcular_aluguel(rolagem_dados=rolagem_para_aluguel) 
            
            print(f"  > Pagando aluguel de R${aluguel} para {casa_atual.proprietario.nome}...")
            sucesso = self.banco.pagar(jogador_atual.nome, aluguel, casa_atual.proprietario.nome)
            
            if not sucesso:
                self.verificar_falencia(jogador_atual)
            
            return {"tipo": "ALUGUEL", "mensagem": f"Pagou R${aluguel} de aluguel"}
        
        return None

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

    def comprar_propriedade(self, jogador, propriedade):
        """
        Compra uma propriedade para o jogador.
        Compatible method for frontend calls.
        """
        return self.gestor_propriedades.comprar_propriedade(jogador, propriedade)

    def construir_na_propriedade(self, jogador, propriedade):
        """Attempts to build a house/hotel on a property"""
        return self.gestor_construcao.construir_casa(jogador, propriedade)
    
    def pode_construir_propriedade(self, jogador, propriedade):
        """Checks if player can build on property"""
        return self.gestor_construcao.pode_construir(jogador, propriedade)

    def finalizar_turno(self):
        """
        Etapa 4: Passa o turno para o próximo jogador, a menos que
        os dados tenham sido duplos.
        """
        if self.verificar_fim_jogo():
            return
        
        if not self.eh_duplo_ultimo:
            self.indice_turno_atual = (self.indice_turno_atual + 1) % len(self.jogadores)
            self.duplas_consecutivas = 0  # Reset doubles counter
            print(f"  > Turno finalizado. Próximo jogador: {self.jogadores[self.indice_turno_atual].nome}")
        else:
            print(f"  > Jogou dados duplos! Joga novamente.")
        
        self.status_geral()

    def verificar_falencia(self, jogador):
        """Verifica se o jogador está falido e o remove do jogo"""
        saldo = self.banco.consultar_saldo(jogador.nome)
        
        # Calculate property value
        valor_propriedades = sum(
            prop.valor_hipoteca for prop in jogador.propriedades 
            if hasattr(prop, 'valor_hipoteca') and not getattr(prop, 'hipotecada', False)
        )
        
        if saldo <= 0 and valor_propriedades == 0:
            print(f"\n{'='*50}")
            print(f"FALÊNCIA! {jogador.nome} está fora do jogo!")
            print(f"{'='*50}\n")
            
            jogador.declarar_falencia()
            
            # Return properties to bank
            for prop in jogador.propriedades[:]:
                jogador.remover_propriedade(prop)
                prop.proprietario = None
                if hasattr(prop, 'hipotecada'):
                    prop.hipotecada = False
                if hasattr(prop, 'casas'):
                    prop.casas = 0
            
            # Remove player
            if jogador in self.jogadores:
                self.jogadores.remove(jogador)
            
            # Adjust turn index
            if self.indice_turno_atual >= len(self.jogadores) and self.jogadores:
                self.indice_turno_atual = 0
            
            return True
        
        return False

    def verificar_fim_jogo(self):
        """Verifica se apenas 1 jogador resta (condição de vitória)"""
        if len(self.jogadores) <= 1:
            self.jogo_finalizado = True
            if self.jogadores:
                print(f"\n{'='*50}")
                print(f"FIM DE JOGO!")
                print(f"VENCEDOR: {self.jogadores[0].nome}")
                print(f"{'='*50}\n")
            return True
        return False

    def status_geral(self):
        """Exibe o status de todos os jogadores."""
        print("\n--- STATUS GERAL DOS JOGADORES ---")
        for jogador in self.jogadores:
            saldo = self.banco.consultar_saldo(jogador.nome)
            status = jogador.status_resumido(saldo)
            if jogador.em_prisao:
                status += f" [PRISÃO: {jogador.turnos_na_prisao}/3]"
            print(status)

    def propor_troca(self, jogador_ofertante, jogador_receptor, propriedades_ofertadas, propriedades_recebidas):
        """
        Propõe uma troca entre dois jogadores.
        """
        return self.sistema_propostas.propor_troca(jogador_ofertante, jogador_receptor, propriedades_ofertadas, propriedades_recebidas)

    def aceitar_troca(self, jogador_receptor, propriedades_ofertadas, propriedades_recebidas):
        """
        Aceita uma troca proposta por outro jogador.
        """
        return self.sistema_propostas.aceitar_troca(jogador_receptor, propriedades_ofertadas, propriedades_recebidas)

    def recusar_troca(self, jogador_receptor):
        """
        Recusa uma troca proposta por outro jogador.
        """
        return self.sistema_propostas.recusar_troca(jogador_receptor)

    def hipotecar_propriedade(self, jogador, propriedade):
        """Hipoteca uma propriedade do jogador."""
        return self.gestor_propriedades.hipotecar_propriedade(jogador, propriedade)

    def deshipotecar_propriedade(self, jogador, propriedade):
        """Deshipoteca uma propriedade do jogador."""
        return self.gestor_propriedades.deshipotecar_propriedade(jogador, propriedade)
