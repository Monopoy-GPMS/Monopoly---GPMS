# Sistema avançado para negociação de propriedades entre jogadores

from enum import Enum

class StatusNegociacaoEnum(Enum):
    PENDENTE = "pendente"
    ACEITA = "aceita"
    RECUSADA = "recusada"
    CANCELADA = "cancelada"

class NegociacaoProposta:
    """Representa uma proposta de negociação de propriedade"""
    
    def __init__(self, proponente, receptor, propriedade, valor_ofertado):
        self.proponente = proponente
        self.receptor = receptor
        self.propriedade = propriedade
        self.valor_ofertado = valor_ofertado
        self.status = StatusNegociacaoEnum.PENDENTE
        self.data_criacao = None
        self.resposta_receptor = None
    
    def obter_resumo(self):
        """Retorna resumo da negociação"""
        return {
            "proponente": self.proponente.nome,
            "receptor": self.receptor.nome,
            "propriedade": self.propriedade.nome,
            "valor_ofertado": f"R${self.valor_ofertado}",
            "status": self.status.value
        }

class NegociadorPropriedades:
    """
    Gerencia negociações de propriedades entre jogadores.
    """
    
    def __init__(self, banco):
        self.banco = banco
        self.negociacoes_ativas = []
        self.historico_negociacoes = []
    
    def propor_negociacao(self, proponente, receptor, propriedade, valor_ofertado):
        """
        Propõe uma negociação de propriedade.
        
        Args:
            proponente: Jogador que quer comprar
            receptor: Jogador dono da propriedade
            propriedade: Propriedade a negociar
            valor_ofertado: Valor oferecido pelo proponente
            
        Returns:
            NegociacaoProposta ou None se inválida
        """
        # Validações
        if propriedade not in receptor.propriedades:
            print(f"  > Erro: {receptor.nome} não possui {propriedade.nome}")
            return None
        
        if propriedade in proponente.propriedades:
            print(f"  > Erro: {proponente.nome} já possui {propriedade.nome}")
            return None
        
        if hasattr(propriedade, 'hipotecada') and propriedade.hipotecada:
            print(f"  > Erro: {propriedade.nome} está hipotecada e não pode ser negociada")
            return None
        
        saldo_proponente = self.banco.consultar_saldo(proponente.nome)
        if saldo_proponente < valor_ofertado:
            print(f"  > Erro: {proponente.nome} não tem R${valor_ofertado}")
            return None
        
        # Additional check: if property is part of a monopoly with buildings, special consideration
        if hasattr(propriedade, 'casas') and propriedade.casas > 0:
            print(f"  > Aviso: {propriedade.nome} possui construções que serão perdidas na venda")
        
        # Cria proposta
        negociacao = NegociacaoProposta(proponente, receptor, propriedade, valor_ofertado)
        self.negociacoes_ativas.append(negociacao)
        
        print(f"  > [NEGOCIAÇÃO] {proponente.nome} ofereceu R${valor_ofertado} por {propriedade.nome}")
        
        return negociacao
    
    def aceitar_negociacao(self, negociacao):
        """Aceita uma negociação e transfere propriedade"""
        if negociacao not in self.negociacoes_ativas:
            return False
        
        proponente = negociacao.proponente
        receptor = negociacao.receptor
        propriedade = negociacao.propriedade
        valor = negociacao.valor_ofertado
        
        # Transfere dinheiro
        sucesso_pagamento = self.banco.pagar(proponente.nome, valor, receptor.nome)
        
        if not sucesso_pagamento:
            print(f"  > Erro: Falha na transferência de dinheiro")
            return False
        
        # Transfere propriedade
        receptor.remover_propriedade(propriedade)
        proponente.adicionar_propriedade(propriedade)
        propriedade.proprietario = proponente
        
        negociacao.status = StatusNegociacaoEnum.ACEITA
        self.historico_negociacoes.append(negociacao)
        self.negociacoes_ativas.remove(negociacao)
        
        print(f"  > [NEGOCIAÇÃO ACEITA] {propriedade.nome} vendida de {receptor.nome} para {proponente.nome} por R${valor}")
        
        return True
    
    def recusar_negociacao(self, negociacao):
        """Recusa uma negociação"""
        if negociacao not in self.negociacoes_ativas:
            return False
        
        negociacao.status = StatusNegociacaoEnum.RECUSADA
        self.historico_negociacoes.append(negociacao)
        self.negociacoes_ativas.remove(negociacao)
        
        print(f"  > [NEGOCIAÇÃO RECUSADA] {negociacao.receptor.nome} recusou a oferta de {negociacao.proponente.nome}")
        
        return True
    
    def cancelar_negociacao(self, negociacao):
        """Cancela uma negociação pendente"""
        if negociacao not in self.negociacoes_ativas:
            return False
        
        negociacao.status = StatusNegociacaoEnum.CANCELADA
        self.historico_negociacoes.append(negociacao)
        self.negociacoes_ativas.remove(negociacao)
        
        print(f"  > [NEGOCIAÇÃO CANCELADA]")
        
        return True
    
    def propor_troca_propriedades(self, proponente, receptor, propriedade_oferecida, propriedade_desejada, valor_adicional=0):
        """
        Propõe uma troca de propriedades entre dois jogadores (com ou sem dinheiro adicional).
        
        Args:
            proponente: Jogador que inicia a negociação
            receptor: Outro jogador
            propriedade_oferecida: Propriedade que proponente quer dar
            propriedade_desejada: Propriedade que proponente quer receber
            valor_adicional: Dinheiro adicional que proponente quer adicionar
            
        Returns:
            NegociacaoProposta ou None se inválida
        """
        # Validações de ambas as propriedades
        if propriedade_oferecida not in proponente.propriedades:
            print(f"  > Erro: {proponente.nome} não possui {propriedade_oferecida.nome}")
            return None
        
        if propriedade_desejada not in receptor.propriedades:
            print(f"  > Erro: {receptor.nome} não possui {propriedade_desejada.nome}")
            return None
        
        # Validações de hipoteca
        if hasattr(propriedade_oferecida, 'hipotecada') and propriedade_oferecida.hipotecada:
            print(f"  > Erro: {propriedade_oferecida.nome} está hipotecada")
            return None
        
        if hasattr(propriedade_desejada, 'hipotecada') and propriedade_desejada.hipotecada:
            print(f"  > Erro: {propriedade_desejada.nome} está hipotecada")
            return None
        
        saldo_proponente = self.banco.consultar_saldo(proponente.nome)
        if valor_adicional > 0 and saldo_proponente < valor_adicional:
            print(f"  > Erro: {proponente.nome} não tem R${valor_adicional} para adicionar")
            return None
        
        # Cria proposta de troca
        negociacao = NegociacaoProposta(proponente, receptor, propriedade_desejada, valor_adicional)
        negociacao.propriedade_oferecida = propriedade_oferecida
        negociacao.é_troca = True
        self.negociacoes_ativas.append(negociacao)
        
        print(f"  > [TROCA] {proponente.nome} ofereceu {propriedade_oferecida.nome} + R${valor_adicional} por {propriedade_desejada.nome}")
        
        return negociacao
    
    def aceitar_troca(self, negociacao):
        """Aceita uma troca de propriedades"""
        if negociacao not in self.negociacoes_ativas or not hasattr(negociacao, 'é_troca'):
            return False
        
        proponente = negociacao.proponente
        receptor = negociacao.receptor
        prop_oferecida = negociacao.propriedade_oferecida
        prop_desejada = negociacao.propriedade
        valor_adicional = negociacao.valor_ofertado
        
        # Transfere dinheiro se houver
        if valor_adicional > 0:
            sucesso = self.banco.pagar(proponente.nome, valor_adicional, receptor.nome)
            if not sucesso:
                print(f"  > Erro: Falha na transferência de dinheiro")
                return False
        
        # Transfere propriedades
        proponente.remover_propriedade(prop_oferecida)
        proponente.adicionar_propriedade(prop_desejada)
        prop_desejada.proprietario = proponente
        
        receptor.remover_propriedade(prop_desejada)
        receptor.adicionar_propriedade(prop_oferecida)
        prop_oferecida.proprietario = receptor
        
        negociacao.status = StatusNegociacaoEnum.ACEITA
        self.historico_negociacoes.append(negociacao)
        self.negociacoes_ativas.remove(negociacao)
        
        msg = f"  > [TROCA ACEITA] {proponente.nome} trocou {prop_oferecida.nome} por {prop_desejada.nome}"
        if valor_adicional > 0:
            msg += f" (+ R${valor_adicional})"
        print(msg)
        
        return True
    
    def obter_negociacoes_ativas(self):
        """Retorna lista de negociações ativas"""
        return self.negociacoes_ativas
    
    def obter_historico(self, nome_jogador=None):
        """Retorna histórico de negociações, opcionalmente filtrado por jogador"""
        if nome_jogador:
            return [n for n in self.historico_negociacoes 
                   if n.proponente.nome == nome_jogador or n.receptor.nome == nome_jogador]
        return self.historico_negociacoes
