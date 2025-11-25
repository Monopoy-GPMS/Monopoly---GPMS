"""
Validador de Regras Oficiais do Monopoly
Garante que todas as ações dos jogadores sigam as regras oficiais do jogo.
"""

from propriedades import Propriedade, CasaMetro, CasaCompanhia


class ValidadorRegras:
    """
    Classe responsável por validar todas as ações do jogo
    conforme as regras oficiais do Monopoly.
    """
    
    @staticmethod
    def validar_compra_propriedade(jogador, propriedade, banco):
        """
        Valida se um jogador pode comprar uma propriedade.
        
        Regras:
        1. A propriedade deve estar livre (sem dono)
        2. O jogador deve ter saldo suficiente
        3. O jogador deve estar na posição da propriedade
        
        Returns:
            tuple: (bool válido, str mensagem_erro)
        """
        # Regra 1: Propriedade deve estar livre
        if not isinstance(propriedade, (Propriedade, CasaMetro, CasaCompanhia)):
            return False, "Casa não é uma propriedade comprável"
        
        if propriedade.proprietario is not None:
            return False, f"Propriedade já pertence a {propriedade.proprietario.nome}"
        
        # Regra 2: Jogador deve ter saldo suficiente
        saldo = banco.consultar_saldo(jogador.nome)
        if saldo < propriedade.preco_compra:
            return False, f"Saldo insuficiente (R${saldo} < R${propriedade.preco_compra})"
        
        return True, "Compra válida"

    @staticmethod
    def validar_construcao_casa(jogador, propriedade, banco):
        """
        Valida se um jogador pode construir uma casa em uma propriedade.
        
        Regras:
        1. Jogador deve ser dono da propriedade
        2. Jogador deve ter monopólio do grupo
        3. Construção deve ser uniforme (diferença máxima de 1 casa entre propriedades do grupo)
        4. Não pode ter mais de 4 casas
        5. Jogador deve ter saldo suficiente
        6. Propriedade não pode estar hipotecada
        
        Returns:
            tuple: (bool válido, str mensagem_erro)
        """
        # Regra 1: Jogador deve ser dono
        if propriedade.proprietario != jogador:
            return False, "Você não é dono desta propriedade"
        
        # Só propriedades comuns podem ter casas (não ferrovias/companhias)
        if not isinstance(propriedade, Propriedade) or not hasattr(propriedade, 'casas'):
            return False, "Esta propriedade não aceita construções"
        
        # Regra 6: Não pode estar hipotecada
        if propriedade.hipotecada:
            return False, "Não pode construir em propriedade hipotecada"
        
        # Regra 2: Deve ter monopólio
        if not hasattr(propriedade, 'grupo_cor'):
            return False, "Propriedade sem grupo definido"
        
        grupo = propriedade.grupo_cor
        propriedades_grupo = [p for p in jogador.propriedades 
                             if hasattr(p, 'grupo_cor') and p.grupo_cor == grupo]
        
        # Contar total de propriedades no grupo (do tabuleiro)
        total_grupo = ValidadorRegras._contar_propriedades_grupo_tabuleiro(grupo)
        
        if len(propriedades_grupo) < total_grupo:
            return False, f"Você precisa ter monopólio do grupo {grupo} (tem {len(propriedades_grupo)}/{total_grupo})"
        
        # Regra 3: Construção uniforme
        casas_no_grupo = [p.casas for p in propriedades_grupo if hasattr(p, 'casas')]
        casas_minimas = min(casas_no_grupo) if casas_no_grupo else 0
        
        if propriedade.casas > casas_minimas:
            return False, f"Construção deve ser uniforme. Construa em outras propriedades do grupo primeiro"
        
        # Regra 4: Máximo de 4 casas
        if propriedade.casas >= 4:
            return False, "Máximo de 4 casas. Use construir_hotel() para adicionar hotel"
        
        # Regra 5: Saldo suficiente
        preco_casa = propriedade.preco_casa if hasattr(propriedade, 'preco_casa') else 50
        saldo = banco.consultar_saldo(jogador.nome)
        if saldo < preco_casa:
            return False, f"Saldo insuficiente (R${saldo} < R${preco_casa})"
        
        return True, "Construção válida"

    @staticmethod
    def validar_construcao_hotel(jogador, propriedade, banco):
        """
        Valida se um jogador pode construir um hotel.
        
        Regras:
        1. Mesmas regras de construção de casas
        2. Deve ter exatamente 4 casas na propriedade
        3. Não pode ter hotel já construído
        
        Returns:
            tuple: (bool válido, str mensagem_erro)
        """
        # Validações básicas de construção
        valido, msg = ValidadorRegras.validar_construcao_casa(jogador, propriedade, banco)
        if not valido and "Máximo de 4 casas" not in msg:
            return False, msg
        
        # Regra 2: Deve ter exatamente 4 casas
        if propriedade.casas != 4:
            return False, "Precisa ter exatamente 4 casas para construir hotel"
        
        # Regra 3: Não pode ter hotel
        if hasattr(propriedade, 'tem_hotel') and propriedade.tem_hotel:
            return False, "Hotel já construído nesta propriedade"
        
        # Verificar saldo
        preco_hotel = propriedade.preco_hotel if hasattr(propriedade, 'preco_hotel') else 100
        saldo = banco.consultar_saldo(jogador.nome)
        if saldo < preco_hotel:
            return False, f"Saldo insuficiente para hotel (R${saldo} < R${preco_hotel})"
        
        return True, "Construção de hotel válida"

    @staticmethod
    def validar_hipoteca(jogador, propriedade):
        """
        Valida se uma propriedade pode ser hipotecada.
        
        Regras:
        1. Jogador deve ser dono
        2. Propriedade não pode estar já hipotecada
        3. Não pode ter construções (casas/hotéis)
        
        Returns:
            tuple: (bool válido, str mensagem_erro)
        """
        # Regra 1: Deve ser dono
        if propriedade.proprietario != jogador:
            return False, "Você não é dono desta propriedade"
        
        # Regra 2: Não pode estar hipotecada
        if propriedade.hipotecada:
            return False, "Propriedade já está hipotecada"
        
        # Regra 3: Não pode ter construções
        if hasattr(propriedade, 'casas') and propriedade.casas > 0:
            return False, "Remova todas as casas antes de hipotecar"
        
        if hasattr(propriedade, 'tem_hotel') and propriedade.tem_hotel:
            return False, "Remova o hotel antes de hipotecar"
        
        return True, "Hipoteca válida"

    @staticmethod
    def validar_deshipoteca(jogador, propriedade, banco):
        """
        Valida se uma propriedade pode ser deshipotecada.
        
        Regras:
        1. Jogador deve ser dono
        2. Propriedade deve estar hipotecada
        3. Jogador deve ter saldo suficiente (valor hipoteca + 10% juros)
        
        Returns:
            tuple: (bool válido, str mensagem_erro)
        """
        # Regra 1: Deve ser dono
        if propriedade.proprietario != jogador:
            return False, "Você não é dono desta propriedade"
        
        # Regra 2: Deve estar hipotecada
        if not propriedade.hipotecada:
            return False, "Propriedade não está hipotecada"
        
        # Regra 3: Saldo suficiente (valor + 10%)
        if hasattr(propriedade, 'valor_hipoteca'):
            custo_total = int(propriedade.valor_hipoteca * 1.1)
            saldo = banco.consultar_saldo(jogador.nome)
            if saldo < custo_total:
                return False, f"Saldo insuficiente (R${saldo} < R${custo_total})"
        
        return True, "Deshipoteca válida"

    @staticmethod
    def validar_pagamento_aluguel(jogador, propriedade, banco):
        """
        Valida pagamento de aluguel.
        
        Regras:
        1. Propriedade deve ter dono
        2. Dono não pode ser o próprio jogador
        3. Propriedade não pode estar hipotecada
        4. Jogador deve ter saldo suficiente (ou falir)
        
        Returns:
            tuple: (bool deve_pagar, int valor_aluguel, str mensagem)
        """
        # Regra 1: Deve ter dono
        if not propriedade.proprietario:
            return False, 0, "Propriedade sem dono"
        
        # Regra 2: Não paga para si mesmo
        if propriedade.proprietario == jogador:
            return False, 0, "É sua propriedade"
        
        # Regra 3: Não paga se hipotecada
        if propriedade.hipotecada:
            return False, 0, "Propriedade hipotecada não cobra aluguel"
        
        # Calcular aluguel
        aluguel = propriedade.calcular_aluguel() if hasattr(propriedade, 'calcular_aluguel') else 0
        
        return True, aluguel, "Deve pagar aluguel"

    @staticmethod
    def validar_saida_prisao(jogador, metodo, banco=None):
        """
        Valida tentativa de sair da prisão.
        
        Métodos válidos:
        - "pagar": Pagar R$50
        - "carta": Usar carta "Saia Livre da Prisão"
        - "dupla": Tirar dupla nos dados (validado externamente)
        - "tres_turnos": Após 3 turnos presos, sai automaticamente
        
        Returns:
            tuple: (bool válido, str mensagem_erro)
        """
        # Deve estar preso
        if not jogador.em_prisao:
            return False, "Jogador não está na prisão"
        
        if metodo == "pagar":
            if banco and not banco.tem_saldo_suficiente(jogador.nome, 50):
                return False, "Saldo insuficiente para pagar fiança (R$50)"
            return True, "Pode pagar fiança"
        
        elif metodo == "carta":
            if jogador.cartas_livre_prisao <= 0:
                return False, "Não possui carta 'Saia Livre da Prisão'"
            return True, "Pode usar carta"
        
        elif metodo == "tres_turnos":
            if jogador.turnos_na_prisao >= 3:
                return True, "Deve sair após 3 turnos"
            return False, f"Ainda faltam {3 - jogador.turnos_na_prisao} turnos"
        
        return False, "Método inválido"

    @staticmethod
    def _contar_propriedades_grupo_tabuleiro(grupo):
        """
        Conta quantas propriedades existem em um grupo no tabuleiro.
        Usado para verificar monopólios.
        """
        # Mapeamento dos grupos e quantidades
        grupos_monopoly = {
            'Marrom': 2,
            'Azul Claro': 3,
            'Rosa': 3,
            'Laranja': 3,
            'Vermelho': 3,
            'Amarelo': 3,
            'Verde': 3,
            'Azul Escuro': 2,
            'Ferrovia': 4,
            'Companhia': 2
        }
        return grupos_monopoly.get(grupo, 3)

    @staticmethod
    def validar_turno_jogador(jogador, gerenciador_partida):
        """
        Valida se é o turno do jogador.
        
        Returns:
            tuple: (bool válido, str mensagem)
        """
        jogador_atual = gerenciador_partida.obter_jogador_atual()
        if jogador != jogador_atual:
            return False, f"Não é seu turno! Turno de: {jogador_atual.nome}"
        return True, "Turno válido"
