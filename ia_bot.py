# ia_bot.py
# Módulo responsável pela IA dos bots para jogadas automáticas

import random
from propriedades import Propriedade, CasaCompanhia, CasaMetro

class IIABot:
    """
    Classe que implementa a IA para bots jogarem automaticamente.
    Toma decisões estratégicas sobre compra de propriedades, construção e outros movimentos.
    """
    
    def __init__(self, dificuldade='medio'):
        """
        Args:
            dificuldade: 'facil', 'medio', 'dificil'
        """
        self.dificuldade = dificuldade
        self.historico_decisoes = []
    
    def decidir_compra_propriedade(self, jogador, propriedade, banco):
        """
        Decide se o bot deve comprar uma propriedade.
        
        Args:
            jogador: Objeto do jogador (bot)
            propriedade: Propriedade onde o jogador parou
            banco: Objeto banco para consultar saldo
            
        Returns:
            bool: True se deve comprar, False caso contrário
        """
        saldo = banco.consultar_saldo(jogador.nome)
        
        if self.dificuldade == 'facil':
            # Bot fácil compra 30% das propriedades que pode pagar
            if saldo >= propriedade.preco_compra:
                return random.random() < 0.3
        
        elif self.dificuldade == 'medio':
            # Bot médio é mais estratégico
            if saldo >= propriedade.preco_compra:
                # Verifica se é parte de um grupo valioso
                valor_compra = self._calcular_valor_compra_estrategica(jogador, propriedade)
                return valor_compra > 0
        
        elif self.dificuldade == 'dificil':
            # Bot difícil otimiza compras para monopólios e propriedades com potencial
            if saldo >= propriedade.preco_compra:
                valor_compra = self._calcular_valor_compra_estrategica(jogador, propriedade)
                return valor_compra > 0 and saldo - propriedade.preco_compra >= 200
        
        return False
    
    def _calcular_valor_compra_estrategica(self, jogador, propriedade):
        """
        Calcula o valor estratégico de comprar uma propriedade.
        
        Returns:
            int: Score de valor (quanto maior, mais desejável a compra)
        """
        score = 0
        
        # 1. Propriedades de alto potencial de aluguel (cores)
        cores_estrategicas = ['Azul Escuro', 'Vermelho', 'Amarelo', 'Verde']
        if propriedade.grupo_cor in cores_estrategicas:
            score += 3
        
        # 2. Propriedades que completam monopólios
        monopolio_progress = jogador.contar_propriedades_grupo(propriedade.grupo_cor)
        if monopolio_progress > 0:
            score += monopolio_progress * 2
        
        # 3. Ferrovias e companhias (renda passiva boa)
        if propriedade.grupo_cor in ['METRÔ', 'SERVIÇO']:
            score += 2
        
        return score
    
    def decidir_construcao(self, jogador, tabuleiro, banco):
        """
        Decide quais propriedades construir casas/hotéis.
        
        Args:
            jogador: Objeto do jogador (bot)
            tabuleiro: Objeto tabuleiro
            banco: Objeto banco
            
        Returns:
            list: Lista de propriedades para construir
        """
        propriedades_para_construir = []
        saldo = banco.consultar_saldo(jogador.nome)
        
        grupos_propriedades = {}
        for prop in jogador.propriedades:
            if isinstance(prop, Propriedade) and not isinstance(prop, (CasaCompanhia, CasaMetro)):
                grupo = prop.grupo_cor
                if grupo not in grupos_propriedades:
                    grupos_propriedades[grupo] = []
                grupos_propriedades[grupo].append(prop)
        
        # Construir em grupos onde tem monopólio
        for grupo, props in grupos_propriedades.items():
            # Verifica se tem todas as propriedades do grupo
            if len(props) == self._contar_total_grupo(grupo):
                # Ordena por menor número de casas
                props.sort(key=lambda p: p.casas)
                
                for prop in props:
                    if prop.casas < 5 and saldo >= 100:  # Assume custo padrão de construção
                        # Construir uniformemente
                        if prop.casas < props[0].casas + 1:
                            propriedades_para_construir.append(prop)
                            saldo -= 100
        
        return propriedades_para_construir
    
    def _contar_total_grupo(self, grupo):
        """Retorna o número total de propriedades de um grupo"""
        # Grupos padrão do Monopoly
        grupos_totais = {
            'Marrom': 2,
            'Azul Claro': 3,
            'Rosa': 3,
            'Laranja': 3,
            'Vermelho': 3,
            'Amarelo': 3,
            'Verde': 3,
            'Azul Escuro': 2,
            'METRÔ': 4,
            'SERVIÇO': 2
        }
        return grupos_totais.get(grupo, 0)
    
    def decidir_hipoteca(self, jogador, banco, valor_necessario):
        """
        Decide quais propriedades hipotecar quando falta saldo.
        
        Args:
            jogador: Objeto do jogador (bot)
            banco: Objeto banco
            valor_necessario: Valor que precisa levantar
            
        Returns:
            list: Propriedades para hipotecar
        """
        propriedades_hipoteca = []
        valor_levantado = 0
        
        # Ordena propriedades por valor de hipoteca (menor primeiro)
        props_disponiveis = [
            p for p in jogador.propriedades 
            if not p.hipotecada and hasattr(p, 'valor_hipoteca')
        ]
        props_disponiveis.sort(key=lambda p: p.valor_hipoteca)
        
        for prop in props_disponiveis:
            if valor_levantado >= valor_necessario:
                break
            propriedades_hipoteca.append(prop)
            valor_levantado += prop.valor_hipoteca
        
        return propriedades_hipoteca
    
    def _registrar_decisao(self, tipo, decisao, resultado):
        """Registra decisão da IA para análise"""
        self.historico_decisoes.append({
            'tipo': tipo,
            'decisao': decisao,
            'resultado': resultado
        })
    
    def pode_negociar_propriedade(self, jogador, propriedade_alvo, valor_maximo_oferta, banco):
        """
        Decide se o bot quer negociar uma propriedade com outro jogador.
        
        Returns:
            (bool, int): (quer_negociar, valor_sugerido_compra)
        """
        saldo = banco.consultar_saldo(jogador.nome)
        
        # Valida se o bot tem saldo suficiente
        if saldo < valor_maximo_oferta:
            return False, 0
        
        # Analisa valor estratégico
        importancia = self._calcular_importancia_propriedade_para_bot(jogador, propriedade_alvo)
        
        if self.dificuldade == 'facil':
            # Bot fácil negocia se o preço for razoável
            valor_proposto = int(propriedade_alvo.preco_compra * 1.1)
            return valor_proposto <= valor_maximo_oferta, valor_proposto
        
        elif self.dificuldade == 'medio':
            # Bot médio só negocia se for estratégico
            if importancia < 1:
                return False, 0
            valor_proposto = int(propriedade_alvo.preco_compra * 1.15)
            return valor_proposto <= valor_maximo_oferta, valor_proposto
        
        elif self.dificuldade == 'dificil':
            # Bot difícil negocia apenas se muito estratégico e mantém segurança
            if importancia < 2 or saldo - valor_maximo_oferta < 300:
                return False, 0
            valor_proposto = int(propriedade_alvo.preco_compra * 1.25)
            return valor_proposto <= valor_maximo_oferta, valor_proposto
        
        return False, 0
    
    def _calcular_importancia_propriedade_para_bot(self, jogador, propriedade):
        """Calcula quão importante é uma propriedade para o bot"""
        score = 0
        
        # Propriedades que completam monopólios são muito valiosas
        if hasattr(propriedade, 'grupo_cor'):
            progresso = jogador.contar_propriedades_grupo(propriedade.grupo_cor)
            if progresso > 0:
                score += progresso * 3
        
        # Cores estratégicas têm mais valor
        cores_premium = ['Azul Escuro', 'Vermelho', 'Amarelo']
        if hasattr(propriedade, 'grupo_cor') and propriedade.grupo_cor in cores_premium:
            score += 2
        
        return score

class GerenciadorBots:
    """
    Gerencia todos os bots do jogo.
    Coordena suas ações e decisões.
    """
    
    def __init__(self):
        self.bots = {}
        self.tempo_resposta_ms = 500  # Delay para parecer mais natural
    
    def criar_bot(self, nome_jogador, dificuldade='medio'):
        """
        Cria uma IA para um jogador específico.
        
        Args:
            nome_jogador: Nome do jogador
            dificuldade: Nível de dificuldade da IA
        """
        self.bots[nome_jogador] = IIABot(dificuldade)
        print(f"  > Bot criado para {nome_jogador} (dificuldade: {dificuldade})")
    
    def executar_turno_bot(self, jogador, jogo):
        """
        Executa um turno completo para um bot.
        
        Args:
            jogador: Objeto do jogador (bot)
            jogo: Objeto jogo para acessar estado do jogo
            
        Returns:
            dict: Resultado das ações do bot
        """
        if jogador.nome not in self.bots:
            return {"sucesso": False, "mensagem": "Bot não encontrado"}
        
        bot = self.bots[jogador.nome]
        resultado = {"jogador": jogador.nome, "acoes": []}
        
        print(f"\n  [BOT] Executando turno para {jogador.nome}...")
        
        import time
        time.sleep(self.tempo_resposta_ms / 1000)
        
        # Pega a casa atual onde o bot parou
        casa_atual = jogo.tabuleiro.get_casa(jogador.posicao)
        
        # Toma decisões baseadas na casa
        if isinstance(casa_atual, Propriedade) and casa_atual.is_livre():
            # Decide se compra
            deve_comprar = bot.decidir_compra_propriedade(jogador, casa_atual, jogo.banco)
            if deve_comprar:
                sucesso = jogo.executar_compra()
                resultado["acoes"].append({
                    "tipo": "COMPRA",
                    "propriedade": casa_atual.nome,
                    "sucesso": sucesso
                })
        
        # Decide construções se for seu turno
        propriedades_construir = bot.decidir_construcao(jogador, jogo.tabuleiro, jogo.banco)
        for prop in propriedades_construir:
            resultado["acoes"].append({
                "tipo": "CONSTRUCAO",
                "propriedade": prop.nome
            })
        
        resultado["sucesso"] = True
        return resultado
