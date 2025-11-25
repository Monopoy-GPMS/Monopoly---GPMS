# ia_bot_negociacao.py
# Módulo de IA avançada para bots tomarem decisões em negociações

class IIABotNegociacao:
    """
    Aprimoramento da IA dos bots para negociações de propriedades.
    Toma decisões inteligentes baseadas em estratégia, saldo e monopólios.
    """
    
    def __init__(self, dificuldade='medio'):
        self.dificuldade = dificuldade
    
    def decidir_venda_propriedade(self, bot_receptor, propriedade, valor_ofertado, banco):
        """
        Decide se o bot deve vender uma propriedade oferecida.
        
        Args:
            bot_receptor: Bot que recebe a proposta
            propriedade: Propriedade em questão
            valor_ofertado: Valor oferecido
            banco: Objeto banco
            
        Returns:
            bool: True para aceitar, False para recusar
        """
        valor_mercado = self._calcular_valor_mercado_propriedade(propriedade)
        saldo_bot = banco.consultar_saldo(bot_receptor.nome)
        
        print(f"  > [BOT IA] {bot_receptor.nome} analisando proposta...")
        print(f"    Valor de mercado: R${valor_mercado}")
        print(f"    Valor ofertado: R${valor_ofertado}")
        print(f"    Saldo do bot: R${saldo_bot}")
        
        if self.dificuldade == 'facil':
            # Bot fácil aceita qualquer oferta acima de 50% do valor de mercado
            return valor_ofertado >= valor_mercado * 0.5
        
        elif self.dificuldade == 'medio':
            # Bot médio analisa importância da propriedade
            importancia = self._calcular_importancia_propriedade(bot_receptor, propriedade)
            
            # Aceita se oferta for 30% acima do valor de mercado
            if valor_ofertado >= valor_mercado * 1.3:
                return True
            
            # Recusa propriedades estratégicas (monopólios)
            if importancia > 2:
                return False
            
            # Aceita se está em situação difícil financeiramente
            if saldo_bot < 500:
                return valor_ofertado >= valor_mercado * 0.8
            
            return False
        
        elif self.dificuldade == 'dificil':
            # Bot difícil é muito estratégico
            importancia = self._calcular_importancia_propriedade(bot_receptor, propriedade)
            
            # Nunca vende monopólios completos ou quase completos
            if importancia >= 3:
                return False
            
            # Só aceita por valor bem acima do mercado
            if valor_ofertado < valor_mercado * 1.5:
                return False
            
            # Mesmo com oferta boa, considera saldo
            if saldo_bot > 1000:
                return valor_ofertado >= valor_mercado * 1.8
            
            return valor_ofertado >= valor_mercado * 1.5
        
        return False
    
    def _calcular_valor_mercado_propriedade(self, propriedade):
        """Calcula o valor de mercado de uma propriedade"""
        if hasattr(propriedade, 'preco_compra'):
            preco_base = propriedade.preco_compra
        else:
            preco_base = 200  # Valor padrão
        
        # Ajusta baseado em casas/hotéis
        if hasattr(propriedade, 'casas'):
            if propriedade.casas > 0:
                preco_base *= (1 + propriedade.casas * 0.3)
            if propriedade.casas == 5:
                preco_base *= 2
        
        return int(preco_base)
    
    def _calcular_importancia_propriedade(self, jogador, propriedade):
        """
        Calcula a importância estratégica de uma propriedade para o bot.
        
        Returns:
            int: Score de importância (0-5)
        """
        score = 0
        
        # 1. Faz parte de um monopólio?
        if hasattr(propriedade, 'grupo_cor'):
            progresso_monopolio = jogador.contar_propriedades_grupo(propriedade.grupo_cor)
            score += progresso_monopolio
        
        # 2. Tem casas/hotéis?
        if hasattr(propriedade, 'casas') and propriedade.casas > 0:
            score += 2
        
        # 3. É uma estação/serviço?
        if hasattr(propriedade, 'grupo_cor'):
            if propriedade.grupo_cor in ['METRÔ', 'SERVIÇO']:
                score += 1
        
        return score
    
    def decidir_compra_inteligente(self, bot_comprador, propriedade, preco_sugerido, banco):
        """
        Decide inteligentemente se o bot quer comprar uma propriedade.
        
        Returns:
            (bool, int): (quer_comprar, valor_maximo_a_pagar)
        """
        saldo = banco.consultar_saldo(bot_comprador.nome)
        valor_mercado = self._calcular_valor_mercado_propriedade(propriedade)
        
        if self.dificuldade == 'facil':
            # Bot fácil oferece até 10% acima do preço sugerido
            valor_max = int(preco_sugerido * 1.1)
            return (saldo >= valor_max and preco_sugerido < 500), valor_max
        
        elif self.dificuldade == 'medio':
            # Bot médio oferece até 20% acima se for estratégico
            importancia = self._calcular_importancia_propriedade(bot_comprador, propriedade)
            valor_max = int(preco_sugerido * (1.0 + importancia * 0.1))
            
            # Protege saldo mínimo
            if saldo - valor_max < 200:
                return False, 0
            
            return True, valor_max
        
        elif self.dificuldade == 'dificil':
            # Bot difícil é calculista
            importancia = self._calcular_importancia_propriedade(bot_comprador, propriedade)
            
            # Não quer a menos que seja estratégico
            if importancia < 2:
                return False, 0
            
            # Calcula valor máximo mantendo saldo de segurança
            valor_max = int(valor_mercado * 1.2)
            
            if saldo - valor_max < 500:
                return False, 0
            
            return True, valor_max
        
        return False, 0
