# negociador_propriedades.py
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
        
        saldo_proponente = self.banco.consultar_saldo(proponente.nome)
        if saldo_proponente < valor_ofertado:
            print(f"  > Erro: {proponente.nome} não tem R${valor_ofertado}")
            return None
        
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
        self.banco.pagar(proponente.nome, valor, receptor.nome)
        
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
    
    def obter_negociacoes_ativas(self):
        """Retorna lista de negociações ativas"""
        return self.negociacoes_ativas
    
    def obter_historico(self, nome_jogador=None):
        """Retorna histórico de negociações, opcionalmente filtrado por jogador"""
        if nome_jogador:
            return [n for n in self.historico_negociacoes 
                   if n.proponente.nome == nome_jogador or n.receptor.nome == nome_jogador]
        return self.historico_negociacoes
