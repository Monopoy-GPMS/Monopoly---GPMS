class SistemaPropostas:
    """Sistema para gerenciar propostas de troca entre jogadores"""
    
    def __init__(self, banco, tabuleiro):
        self.banco = banco
        self.tabuleiro = tabuleiro
        self.proposta_ativa = None
    
    def criar_proposta(self, jogador_oferente, jogador_destinatario, 
                      propriedades_oferecidas, propriedades_solicitadas,
                      dinheiro_oferecido=0, dinheiro_solicitado=0):
        """
        Cria uma proposta de troca entre jogadores
        
        Args:
            jogador_oferente: Jogador que está fazendo a proposta
            jogador_destinatario: Jogador que receberá a proposta
            propriedades_oferecidas: Lista de propriedades que o oferente dá
            propriedades_solicitadas: Lista de propriedades que o oferente quer
            dinheiro_oferecido: Quantia em dinheiro que o oferente oferece
            dinheiro_solicitado: Quantia em dinheiro que o oferente quer receber
        
        Returns:
            dict: Proposta criada ou None se inválida
        """
        # Validações básicas
        if jogador_oferente == jogador_destinatario:
            return None
        
        # Verifica se o oferente tem as propriedades que está oferecendo
        for prop in propriedades_oferecidas:
            if prop not in jogador_oferente.propriedades:
                print(f"Erro: {jogador_oferente.nome} não possui {prop.nome}")
                return None
        
        # Verifica se o destinatário tem as propriedades solicitadas
        for prop in propriedades_solicitadas:
            if prop not in jogador_destinatario.propriedades:
                print(f"Erro: {jogador_destinatario.nome} não possui {prop.nome}")
                return None
        
        # Verifica saldo do oferente se está oferecendo dinheiro
        if dinheiro_oferecido > 0:
            saldo_oferente = self.banco.consultar_saldo(jogador_oferente.nome)
            if saldo_oferente < dinheiro_oferecido:
                print(f"Erro: {jogador_oferente.nome} não tem R${dinheiro_oferecido}")
                return None
        
        # Verifica saldo do destinatário se está pedindo dinheiro dele
        if dinheiro_solicitado > 0:
            saldo_destinatario = self.banco.consultar_saldo(jogador_destinatario.nome)
            if saldo_destinatario < dinheiro_solicitado:
                print(f"Erro: {jogador_destinatario.nome} não tem R${dinheiro_solicitado}")
                return None
        
        self.proposta_ativa = {
            "oferente": jogador_oferente,
            "destinatario": jogador_destinatario,
            "props_oferecidas": propriedades_oferecidas,
            "props_solicitadas": propriedades_solicitadas,
            "dinheiro_oferecido": dinheiro_oferecido,
            "dinheiro_solicitado": dinheiro_solicitado
        }
        
        return self.proposta_ativa
    
    def aceitar_proposta(self):
        """Executa a troca se a proposta for aceita"""
        if not self.proposta_ativa:
            return False
        
        proposta = self.proposta_ativa
        oferente = proposta["oferente"]
        destinatario = proposta["destinatario"]
        
        # Transferir propriedades oferecidas
        for prop in proposta["props_oferecidas"]:
            oferente.remover_propriedade(prop)
            destinatario.adicionar_propriedade(prop)
            prop.proprietario = destinatario
            print(f"  > {prop.nome}: {oferente.nome} → {destinatario.nome}")
        
        # Transferir propriedades solicitadas
        for prop in proposta["props_solicitadas"]:
            destinatario.remover_propriedade(prop)
            oferente.adicionar_propriedade(prop)
            prop.proprietario = oferente
            print(f"  > {prop.nome}: {destinatario.nome} → {oferente.nome}")
        
        # Transferir dinheiro oferecido (oferente → destinatário)
        if proposta["dinheiro_oferecido"] > 0:
            self.banco.transferir(oferente.nome, destinatario.nome, 
                                 proposta["dinheiro_oferecido"])
            print(f"  > R${proposta['dinheiro_oferecido']}: {oferente.nome} → {destinatario.nome}")
        
        # Transferir dinheiro solicitado (destinatário → oferente)
        if proposta["dinheiro_solicitado"] > 0:
            self.banco.transferir(destinatario.nome, oferente.nome, 
                                 proposta["dinheiro_solicitado"])
            print(f"  > R${proposta['dinheiro_solicitado']}: {destinatario.nome} → {oferente.nome}")
        
        print(f"\n✓ Proposta aceita e executada!")
        self.proposta_ativa = None
        return True
    
    def recusar_proposta(self):
        """Recusa a proposta ativa"""
        if not self.proposta_ativa:
            return False
        
        print(f"\n✗ Proposta recusada por {self.proposta_ativa['destinatario'].nome}")
        self.proposta_ativa = None
        return True
    
    def cancelar_proposta(self):
        """Cancela a proposta ativa"""
        if not self.proposta_ativa:
            return False
        
        print(f"\n✗ Proposta cancelada por {self.proposta_ativa['oferente'].nome}")
        self.proposta_ativa = None
        return True
    
    def obter_resumo_proposta(self):
        """Retorna um resumo legível da proposta ativa"""
        if not self.proposta_ativa:
            return None
        
        p = self.proposta_ativa
        resumo = f"\n{'='*50}\n"
        resumo += f"PROPOSTA: {p['oferente'].nome} → {p['destinatario'].nome}\n"
        resumo += f"{'='*50}\n"
        
        resumo += f"\n{p['oferente'].nome} oferece:\n"
        if p['props_oferecidas']:
            for prop in p['props_oferecidas']:
                resumo += f"  • {prop.nome}\n"
        if p['dinheiro_oferecido'] > 0:
            resumo += f"  • R${p['dinheiro_oferecido']}\n"
        if not p['props_oferecidas'] and p['dinheiro_oferecido'] == 0:
            resumo += "  • Nada\n"
        
        resumo += f"\n{p['oferente'].nome} quer receber:\n"
        if p['props_solicitadas']:
            for prop in p['props_solicitadas']:
                resumo += f"  • {prop.nome}\n"
        if p['dinheiro_solicitado'] > 0:
            resumo += f"  • R${p['dinheiro_solicitado']}\n"
        if not p['props_solicitadas'] and p['dinheiro_solicitado'] == 0:
            resumo += "  • Nada\n"
        
        return resumo
