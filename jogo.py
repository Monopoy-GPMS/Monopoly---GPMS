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
from cartas import BaralhoCartas, CartaDinheiro, CartaMovimento

from dados import Dados
from sistema_propostas import SistemaPropostas
from construcao import GestorConstrucao
from regras_propriedades import GestorPropriedades
from regras_prisao import GestorPrisao
from ia_bot import GerenciadorBots
from sistema_eventos import SistemaEventos, TipoEvento
from integracao_cartas import GerenciadorCartasAvancado
from gerenciador_inicializacao import GerenciadorInicializacao
from exibidor_cartas import ExibidorCartas
from negociador_propriedades import NegociadorPropriedades
from ia_bot_negociacao import IIABotNegociacao

class Jogo:
    
    def __init__(self, nomes_jogadores, num_humanos=None):
        """Inicializa o Banco, o Tabuleiro e os Jogadores."""
        if num_humanos is None:
            num_humanos = len(nomes_jogadores)
        
        GerenciadorInicializacao.validar_numero_jogadores(num_humanos)
        lista_jogadores = GerenciadorInicializacao.gerar_lista_jogadores(num_humanos, nomes_jogadores)
        
        self.banco = Banco()
        self.tabuleiro = Tabuleiro()
        
        self.dados_obj = Dados(num_dados=2)
        self.baralho_sorte = BaralhoCartas('SORTE')
        self.baralho_cofre = BaralhoCartas('COFRE')
        self.gestor_prisao = GestorPrisao(self.banco)
        self.gestor_construcao = GestorConstrucao(self.tabuleiro, self.banco)
        self.gestor_propriedades = GestorPropriedades(self.banco, self.tabuleiro)
        self.sistema_propostas = SistemaPropostas(self.banco, self.tabuleiro)
        self.indice_turno_atual = 0
        self.jogo_finalizado = False
        
        self.jogadores = []
        self.ultimo_d1 = 1 
        self.ultimo_d2 = 1 
        self.eh_duplo_ultimo = False
        self.duplas_consecutivas = 0

        self.sistema_eventos = SistemaEventos()
        self.gerenciador_bots = GerenciadorBots()
        self.exibidor_cartas = ExibidorCartas(tempo_exibicao=2.0)
        self.negociador_propriedades = NegociadorPropriedades(self.banco)
        self.ia_bot_negociacao = IIABotNegociacao()
        self.gerenciador_cartas_avancado = GerenciadorCartasAvancado(self.sistema_eventos)
        
        for info in lista_jogadores:
            novo_jogador = Jogador(info["nome"], info["peca"], is_ia=info["eh_bot"])
            self.jogadores.append(novo_jogador)
            self.banco.inicializar_conta(info["nome"])
            
            if info["eh_bot"]:
                self.gerenciador_bots.criar_bot(info["nome"], info["dificuldade"])
        
        self._registrar_callbacks_eventos()

    def _registrar_callbacks_eventos(self):
        """Registra callbacks para eventos importantes do jogo"""
        # Monitora saldo crítico
        self.sistema_eventos.registrar_callback(
            TipoEvento.SALDO_CRITICO,
            lambda e: print(f"  [ALERTA] {e.jogador} com saldo crítico!")
        )
        
        # Monitora monopólios
        self.sistema_eventos.registrar_callback(
            TipoEvento.MONOPÓLIO_COMPLETADO,
            lambda e: print(f"  [MONOPÓLIO] {e.jogador} completou monopólio!")
        )

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
        
        if jogador.is_ia:
            print(f"  [BOT] {jogador.nome} está jogando...")
        
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
            return {"tipo": "PEGAR_CARTA", "casa": casa_atual}

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
            casa_atual.acao_ao_cair(jogador_atual, self.banco)
            
            # Se tiver sistema de cartas, executar aqui
            print(f"\n  > ===== ACIONANDO BARALHO DE CARTAS =====")
            
            if isinstance(casa_atual, CasaSorteReves):
                carta = self.baralho_sorte.pegar_carta()
                tipo_baralho = 'SORTE'
            else:
                carta = self.baralho_cofre.pegar_carta()
                tipo_baralho = 'COFRE'
            
            if carta:
                # Exibe carta por 2 segundos antes de executar
                resultado = self.exibidor_cartas.executar_carta_apos_delay(
                    carta, jogador_atual, self.banco, self
                )
                
                # Devolve carta ao baralho se aplicável
                if isinstance(carta, CartaDinheiro) or isinstance(carta, CartaMovimento):
                    self.baralho_sorte.devolver_carta(carta) if tipo_baralho == 'SORTE' else self.baralho_cofre.devolver_carta(carta)
                
                return {
                    "tipo": "CARTA",
                    "mensagem": carta.descricao,
                    "tipo_baralho": tipo_baralho,
                    "tempo_exibicao": 2.0
                }
            else:
                return {"tipo": "CARTA", "mensagem": "Erro ao puxar carta"}

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
        
        if self.jogadores:
            proximo_jogador = self.jogadores[self.indice_turno_atual]
            if proximo_jogador.is_ia and not self.jogo_finalizado:
                self._executar_turno_automatico_bot(proximo_jogador)
        
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

    def propor_negociacao_propriedade(self, proponente, receptor, propriedade, valor_ofertado):
        """Propõe negociação de propriedade específica"""
        return self.negociador_propriedades.propor_negociacao(
            proponente, receptor, propriedade, valor_ofertado
        )
    
    def aceitar_negociacao(self, negociacao):
        """Aceita negociação de propriedade"""
        return self.negociador_propriedades.aceitar_negociacao(negociacao)
    
    def recusar_negociacao(self, negociacao):
        """Recusa negociação de propriedade"""
        return self.negociador_propriedades.recusar_negociacao(negociacao)
    
    def obter_propriedades_para_negociacao(self, jogador):
        """Retorna propriedades de um jogador organizadas por categoria"""
        propriedades_por_categoria = {
            'cores': [],
            'estacoes': [],
            'servicos': [],
            'hipotecadas': []
        }
        
        for prop in jogador.propriedades:
            if hasattr(prop, 'hipotecada') and prop.hipotecada:
                propriedades_por_categoria['hipotecadas'].append(prop)
            elif hasattr(prop, 'grupo_cor'):
                if prop.grupo_cor == 'METRÔ':
                    propriedades_por_categoria['estacoes'].append(prop)
                elif prop.grupo_cor == 'SERVIÇO':
                    propriedades_por_categoria['servicos'].append(prop)
                else:
                    propriedades_por_categoria['cores'].append(prop)
        
        return propriedades_por_categoria
    
    def bot_responder_negociacao(self, bot, negociacao):
        """Bot decide se aceita negociação"""
        aceita = self.ia_bot_negociacao.decidir_venda_propriedade(
            bot, 
            negociacao.propriedade, 
            negociacao.valor_ofertado, 
            self.banco
        )
        
        if aceita:
            return self.negociador_propriedades.aceitar_negociacao(negociacao)
        else:
            return self.negociador_propriedades.recusar_negociacao(negociacao)

    def hipotecar_propriedade(self, jogador, propriedade):
        """Hipoteca uma propriedade do jogador."""
        return self.gestor_propriedades.hipotecar_propriedade(jogador, propriedade)

    def deshipotecar_propriedade(self, jogador, propriedade):
        """Deshipoteca uma propriedade do jogador."""
        return self.gestor_propriedades.deshipotecar_propriedade(jogador, propriedade)

    def _executar_turno_automatico_bot(self, jogador_bot):
        """
        Executa turno do bot com delays usando threading para evitar travamento.
        Permite que o jogo continue respondendo normalmente enquanto o bot joga.
        """
        import threading
        import time
        
        def executar_bot_thread():
            """Executa o turno do bot em thread separada"""
            global turno_bot_em_execucao
            
            print(f"\n  [BOT AUTO] Iniciando turno automático para {jogador_bot.nome}...")
            turno_bot_em_execucao = True  # Desabilita HUD durante bot turn
            
            try:
                time.sleep(0.5)
                
                # 1. Rolar dados e mover
                casa_atual = self.rolar_dados_e_mover()
                time.sleep(0.3)
                
                # 2. Obter ação necessária
                acao = self.obter_acao_para_casa(casa_atual)
                
                # 3. Executar ações automáticas
                if acao["tipo"] == "ACAO_AUTOMATICA":
                    self.executar_acao_automatica(casa_atual)
                    time.sleep(0.3)
                
                # 4. Para decisões de compra, usar bot
                elif acao["tipo"] == "DECISAO_COMPRA":
                    resultado_bot = self.gerenciador_bots.executar_turno_bot(jogador_bot, self)
                    if resultado_bot.get("sucesso"):
                        for acao_bot in resultado_bot.get("acoes", []):
                            print(f"    [BOT AÇÃO] {acao_bot}")
                            time.sleep(0.3)
                            self.sistema_eventos.disparar_evento(
                                TipoEvento.COMPRA_PROPRIEDADE,
                                jogador_bot.nome,
                                f"Bot comprou {acao_bot.get('propriedade')}",
                                {'propriedade': acao_bot.get('propriedade')}
                            )
                
                # 5. Finalizar turno com delay
                time.sleep(0.3)
                self.finalizar_turno()
            finally:
                turno_bot_em_execucao = False  # Reabilita HUD após bot terminar
        
        thread = threading.Thread(target=executar_bot_thread, daemon=True)
        thread.start()

    def executar_turno_bot_nao_bloqueante(self, jogador_bot):
        """
        Executa o turno de um bot de forma não-bloqueante com delays entre ações.
        Permite que o jogo continue respondendo enquanto o bot joga.
        """
        import time
        
        # Delay inicial antes de iniciar o turno do bot
        time.sleep(0.5)
        
        # 1. Rolar dados e mover
        casa_atual = self.rolar_dados_e_mover()
        time.sleep(0.3)  # Reduzido para 300ms para animação dos dados
        
        # 2. Obter ação necessária
        acao = self.obter_acao_para_casa(casa_atual)
        
        # 3. Executar ações automáticas (Sorte, Cofre, Imposto, etc)
        if acao["tipo"] == "ACAO_AUTOMATICA":
            resultado = self.executar_acao_automatica(casa_atual)
            time.sleep(0.3)
        
        # 4. Para decisões de compra, usar bot
        elif acao["tipo"] == "DECISAO_COMPRA":
            resultado_bot = self.gerenciador_bots.executar_turno_bot(jogador_bot, self)
            if resultado_bot.get("sucesso"):
                for acao_bot in resultado_bot.get("acoes", []):
                    print(f"    [BOT AÇÃO] {acao_bot}")
                    time.sleep(0.3)
                    self.sistema_eventos.disparar_evento(
                        TipoEvento.COMPRA_PROPRIEDADE,
                        jogador_bot.nome,
                        f"Bot comprou {acao_bot.get('propriedade')}",
                        {'propriedade': acao_bot.get('propriedade')}
                    )
        
        # 5. Finalizar turno com delay
        time.sleep(0.3)
        self.finalizar_turno()

    def obter_estatisticas_eventos(self, nome_jogador=None):
        """Retorna estatísticas baseadas em eventos"""
        if nome_jogador:
            return self.sistema_eventos.obter_estatisticas_jogador(nome_jogador)
        else:
            return {
                'total_eventos': len(self.sistema_eventos.eventos),
                'tipos_eventos': list(set(e.tipo.value for e in self.sistema_eventos.eventos))
            }
