# regras_propriedades.py
# Módulo responsável pelas regras de compra e venda de propriedades

class GestorPropriedades:
    """Gerencia compra, venda e negociação de propriedades"""
    
    def __init__(self, banco, tabuleiro):
        """
        Args:
            banco: Objeto Banco para transações
            tabuleiro: Objeto Tabuleiro para acessar propriedades
        """
        self.banco = banco
        self.tabuleiro = tabuleiro
    
    def pode_comprar(self, jogador, propriedade):
        """
        Verifica se o jogador pode comprar a propriedade.
        Regras:
        - Propriedade deve estar livre (sem dono)
        - Jogador deve ter saldo suficiente
        """
        if not hasattr(propriedade, 'preco_compra'):
            return False, "Esta casa não pode ser comprada."
        
        if propriedade.proprietario is not None:
            return False, f"Propriedade pertence a {propriedade.proprietario.nome}."
        
        saldo = self.banco.consultar_saldo(jogador.nome)
        if saldo < propriedade.preco_compra:
            return False, f"Saldo insuficiente. Preço: R${propriedade.preco_compra}, Saldo: R${saldo}"
        
        return True, f"Pode comprar por R${propriedade.preco_compra}"
    
    def comprar_propriedade(self, jogador, propriedade):
        """
        Realiza a compra de uma propriedade.
        Returns:
            bool: True se comprou com sucesso
        """
        pode, mensagem = self.pode_comprar(jogador, propriedade)
        
        if not pode:
            print(f"  > Não foi possível comprar: {mensagem}")
            return False
        
        # Realiza a transação
        sucesso = self.banco.pagar(jogador.nome, propriedade.preco_compra, "Banco")
        
        if sucesso:
            jogador.adicionar_propriedade(propriedade)
            print(f"  > {jogador.nome} comprou {propriedade.nome} por R${propriedade.preco_compra}!")
            
            # Verifica se completou monopólio
            self._verificar_monopolio(jogador, propriedade)
            
            return True
        
        return False
    
    def _verificar_monopolio(self, jogador, propriedade):
        """Verifica se o jogador completou um monopólio"""
        if not hasattr(propriedade, 'grupo_cor'):
            return
        
        grupo = propriedade.grupo_cor
        props_grupo = self.tabuleiro.listar_propriedades_por_grupo(grupo)
        
        if all(p.proprietario == jogador for p in props_grupo):
            print(f"  > 🎉 {jogador.nome} completou o MONOPÓLIO do grupo {grupo}!")
    
    def calcular_valor_hipoteca(self, propriedade):
        """Calcula o valor da hipoteca (50% do preço de compra)"""
        if hasattr(propriedade, 'preco_compra'):
            return propriedade.preco_compra // 2
        return 0
    
    def pode_hipotecar(self, jogador, propriedade):
        """Verifica se a propriedade pode ser hipotecada"""
        if propriedade.proprietario != jogador:
            return False, "Você não é o proprietário desta propriedade."
        
        if propriedade.hipotecada:
            return False, "Esta propriedade já está hipotecada."
        
        # Não pode hipotecar se tem construções
        if hasattr(propriedade, 'casas') and propriedade.casas > 0:
            return False, "Venda as construções antes de hipotecar."
        
        valor = self.calcular_valor_hipoteca(propriedade)
        return True, f"Pode hipotecar por R${valor}"
    
    def hipotecar_propriedade(self, jogador, propriedade):
        """
        Hipoteca uma propriedade.
        Returns:
            bool: True se hipotecou com sucesso
        """
        pode, mensagem = self.pode_hipotecar(jogador, propriedade)
        
        if not pode:
            print(f"  > Não foi possível hipotecar: {mensagem}")
            return False
        
        valor = self.calcular_valor_hipoteca(propriedade)
        self.banco.depositar(jogador.nome, valor)
        propriedade.hipotecada = True
        
        print(f"  > {jogador.nome} hipotecou {propriedade.nome} e recebeu R${valor}")
        return True
    
    def pode_resgatar_hipoteca(self, jogador, propriedade):
        """Verifica se pode resgatar uma hipoteca"""
        if propriedade.proprietario != jogador:
            return False, "Você não é o proprietário desta propriedade."
        
        if not propriedade.hipotecada:
            return False, "Esta propriedade não está hipotecada."
        
        # Custo = 110% do valor de hipoteca (valor original + 10% juros)
        valor_hipoteca = self.calcular_valor_hipoteca(propriedade)
        custo_resgate = int(valor_hipoteca * 1.1)
        
        saldo = self.banco.consultar_saldo(jogador.nome)
        if saldo < custo_resgate:
            return False, f"Saldo insuficiente. Custo: R${custo_resgate}, Saldo: R${saldo}"
        
        return True, f"Pode resgatar por R${custo_resgate}"
    
    def resgatar_hipoteca(self, jogador, propriedade):
        """
        Resgata uma propriedade hipotecada.
        Returns:
            bool: True se resgatou com sucesso
        """
        pode, mensagem = self.pode_resgatar_hipoteca(jogador, propriedade)
        
        if not pode:
            print(f"  > Não foi possível resgatar: {mensagem}")
            return False
        
        valor_hipoteca = self.calcular_valor_hipoteca(propriedade)
        custo_resgate = int(valor_hipoteca * 1.1)
        
        sucesso = self.banco.pagar(jogador.nome, custo_resgate, "Banco")
        
        if sucesso:
            propriedade.hipotecada = False
            print(f"  > {jogador.nome} resgatou a hipoteca de {propriedade.nome} por R${custo_resgate}")
            return True
        
        return False
    
    def calcular_aluguel(self, propriedade, rolagem_dados=0):
        """
        Calcula o aluguel de uma propriedade.
        Args:
            rolagem_dados: Valor dos dados (necessário para companhias)
        """
        if propriedade.hipotecada:
            return 0
        
        # Para propriedades com casas/hotéis
        if hasattr(propriedade, 'casas') and propriedade.casas > 0:
            # Aluguel aumenta com construções
            # Simplificado: base * (2 ^ casas)
            return propriedade.aluguel_base * (2 ** propriedade.casas)
        
        # Para companhias (usa método específico)
        if hasattr(propriedade, 'calcular_aluguel'):
            if propriedade.grupo_cor == "SERVIÇO":
                return propriedade.calcular_aluguel(rolagem_dados)
            else:
                return propriedade.calcular_aluguel()
        
        # Propriedade normal sem construções
        # Verifica se tem monopólio para dobrar aluguel
        if propriedade.proprietario and hasattr(propriedade, 'grupo_cor'):
            grupo = propriedade.grupo_cor
            props_grupo = self.tabuleiro.listar_propriedades_por_grupo(grupo)
            
            tem_monopolio = all(p.proprietario == propriedade.proprietario for p in props_grupo)
            
            if tem_monopolio and propriedade.grupo_cor not in ['METRÔ', 'SERVIÇO']:
                return propriedade.aluguel_base * 2
        
        return propriedade.aluguel_base
    
    def cobrar_aluguel(self, proprietario, inquilino, propriedade, rolagem_dados=0):
        """
        Cobra aluguel do inquilino para o proprietário.
        Returns:
            bool: True se pagou com sucesso
        """
        if propriedade.proprietario != proprietario:
            return False
        
        if proprietario.nome == inquilino.nome:
            print(f"  > {inquilino.nome} está em sua própria propriedade.")
            return True
        
        aluguel = self.calcular_aluguel(propriedade, rolagem_dados)
        
        if aluguel == 0:
            print(f"  > Propriedade hipotecada. Sem aluguel.")
            return True
        
        print(f"  > {inquilino.nome} deve pagar R${aluguel} de aluguel para {proprietario.nome}")
        sucesso = self.banco.pagar(inquilino.nome, aluguel, proprietario.nome)
        
        if not sucesso:
            print(f"  > {inquilino.nome} não tem dinheiro suficiente! (Possível falência)")
            # Aqui entraria a lógica de falência
        
        return sucesso
    
    def vender_propriedade(self, vendedor, comprador, propriedade, preco):
        """
        Realiza a venda de uma propriedade entre jogadores.
        Returns:
            bool: True se vendeu com sucesso
        """
        if propriedade.proprietario != vendedor:
            print(f"  > {vendedor.nome} não é o proprietário de {propriedade.nome}")
            return False
        
        # Não pode vender se tem construções
        if hasattr(propriedade, 'casas') and propriedade.casas > 0:
            print(f"  > Venda as construções de {propriedade.nome} antes de vendê-la.")
            return False
        
        # Verifica se comprador tem dinheiro
        saldo = self.banco.consultar_saldo(comprador.nome)
        if saldo < preco:
            print(f"  > {comprador.nome} não tem dinheiro suficiente (R${preco}).")
            return False
        
        # Realiza a transação
        sucesso = self.banco.pagar(comprador.nome, preco, vendedor.nome)
        
        if sucesso:
            vendedor.remover_propriedade(propriedade)
            comprador.adicionar_propriedade(propriedade)
            print(f"  > {vendedor.nome} vendeu {propriedade.nome} para {comprador.nome} por R${preco}!")
            
            # Verifica se completou monopólio
            self._verificar_monopolio(comprador, propriedade)
            
            return True
        
        return False

# Teste do módulo
if __name__ == '__main__':
    print("--- Teste do Módulo Regras de Propriedades ---")
    print("Este módulo requer integração completa com Tabuleiro, Banco e Jogador.")
    print("Execute os testes através do arquivo principal do jogo.")
