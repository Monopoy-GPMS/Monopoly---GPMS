# construcao.py
# Módulo responsável pela construção de casas e hotéis

from constantes import POSICAO_SAIDA

class GestorConstrucao:
    """Gerencia a construção de casas e hotéis nas propriedades"""
    
    # Custos padrão de construção por grupo
    CUSTO_CONSTRUCAO = {
        'Marrom': 50,
        'Azul Claro': 50,
        'Rosa': 100,
        'Laranja': 100,
        'Vermelho': 150,
        'Amarelo': 150,
        'Verde': 200,
        'Azul Escuro': 200
    }
    
    MAX_CASAS = 4  # Máximo de casas antes de poder construir hotel
    HOTEL = 5      # Representa um hotel
    
    def __init__(self, tabuleiro, banco):
        """
        Args:
            tabuleiro: Objeto Tabuleiro para acessar propriedades
            banco: Objeto Banco para transações financeiras
        """
        self.tabuleiro = tabuleiro
        self.banco = banco
    
    def pode_construir(self, jogador, propriedade):
        """
        Verifica se o jogador pode construir na propriedade.
        Regras:
        - Deve ter monopólio do grupo (todas as propriedades da mesma cor)
        - Construção deve ser uniforme (não pode ter 2+ casas de diferença)
        - Propriedade não pode estar hipotecada
        - Não pode construir em ferrovias ou companhias
        """
        # Verifica se é uma propriedade normal (não ferrovia/companhia)
        if not hasattr(propriedade, 'grupo_cor') or propriedade.grupo_cor in ['METRÔ', 'SERVIÇO']:
            return False, "Não é possível construir nesta propriedade."
        
        # Check if property has casas attribute (metro and companies don't)
        if not hasattr(propriedade, 'casas'):
            return False, "Não é possível construir nesta propriedade."
        
        # Verifica se o jogador é o proprietário
        if propriedade.proprietario != jogador:
            return False, "Você não é o proprietário desta propriedade."
        
        # Verifica se a propriedade está hipotecada
        if propriedade.hipotecada:
            return False, "Propriedade hipotecada não pode receber construções."
        
        # Verifica se tem monopólio (TODAS as propriedades do grupo)
        grupo = propriedade.grupo_cor
        props_grupo = self.tabuleiro.listar_propriedades_por_grupo(grupo)
        
        # Count how many properties the player owns in this group
        props_jogador_no_grupo = [p for p in props_grupo if p.proprietario == jogador]
        tem_monopolio = len(props_jogador_no_grupo) == len(props_grupo)
        
        if not tem_monopolio:
            return False, f"Precisa ter todas as {len(props_grupo)} propriedades do grupo {grupo}."
        
        # Verifica se alguma propriedade do grupo está hipotecada
        if any(p.hipotecada for p in props_grupo):
            return False, "Não é possível construir enquanto alguma propriedade do grupo estiver hipotecada."
        
        # Verifica construção uniforme (não pode ter mais de 1 casa de diferença)
        casas_atual = propriedade.casas
        for prop in props_grupo:
            if prop != propriedade:
                if casas_atual - prop.casas >= 1:
                    return False, "Construção deve ser uniforme. Construa nas outras propriedades primeiro."
        
        # Verifica se já tem hotel
        if propriedade.casas >= self.HOTEL:
            return False, "Esta propriedade já tem um hotel."
        
        # Verifica se tem dinheiro
        custo = self.CUSTO_CONSTRUCAO.get(grupo, 100)
        saldo = self.banco.consultar_saldo(jogador.nome)
        if saldo < custo:
            return False, f"Saldo insuficiente. Custo: R${custo}"
        
        return True, f"Pode construir por R${custo}"
    
    def construir_casa(self, jogador, propriedade):
        """
        Constrói uma casa na propriedade.
        Returns:
            bool: True se construiu com sucesso
        """
        pode, mensagem = self.pode_construir(jogador, propriedade)
        
        if not pode:
            print(f"  > Não foi possível construir: {mensagem}")
            return False
        
        # Realiza a construção
        grupo = propriedade.grupo_cor
        custo = self.CUSTO_CONSTRUCAO.get(grupo, 100)
        
        sucesso = self.banco.pagar(jogador.nome, custo, "Banco")
        if sucesso:
            propriedade.casas += 1
            
            if propriedade.casas == self.HOTEL:
                print(f"  > {jogador.nome} construiu um HOTEL em {propriedade.nome}! Custo: R${custo}")
            else:
                print(f"  > {jogador.nome} construiu a casa {propriedade.casas} em {propriedade.nome}! Custo: R${custo}")
            
            return True
        
        return False
    
    def pode_vender_construcao(self, jogador, propriedade):
        """Verifica se o jogador pode vender uma casa/hotel da propriedade"""
        if propriedade.proprietario != jogador:
            return False, "Você não é o proprietário desta propriedade."
        
        if propriedade.casas == 0:
            return False, "Esta propriedade não tem construções."
        
        # Verifica construção uniforme (deve vender das mais construídas primeiro)
        grupo = propriedade.grupo_cor
        props_grupo = self.tabuleiro.listar_propriedades_por_grupo(grupo)
        
        casas_atual = propriedade.casas
        for prop in props_grupo:
            if prop != propriedade:
                if prop.casas > casas_atual:
                    return False, "Deve vender das propriedades mais construídas primeiro."
        
        return True, "Pode vender"
    
    def vender_casa(self, jogador, propriedade):
        """
        Vende uma casa/hotel da propriedade.
        Returns:
            bool: True se vendeu com sucesso
        """
        pode, mensagem = self.pode_vender_construcao(jogador, propriedade)
        
        if not pode:
            print(f"  > Não foi possível vender: {mensagem}")
            return False
        
        # Realiza a venda (recebe metade do valor de construção)
        grupo = propriedade.grupo_cor
        custo_construcao = self.CUSTO_CONSTRUCAO.get(grupo, 100)
        valor_venda = custo_construcao // 2
        
        self.banco.depositar(jogador.nome, valor_venda)
        
        era_hotel = propriedade.casas == self.HOTEL
        propriedade.casas -= 1
        
        if era_hotel:
            print(f"  > {jogador.nome} vendeu o HOTEL de {propriedade.nome} por R${valor_venda}")
        else:
            print(f"  > {jogador.nome} vendeu 1 casa de {propriedade.nome} por R${valor_venda}")
        
        return True
    
    def get_info_construcao(self, propriedade):
        """Retorna informações sobre construção na propriedade"""
        if not hasattr(propriedade, 'casas'):
            return "Esta propriedade não permite construções."
        
        grupo = propriedade.grupo_cor
        custo = self.CUSTO_CONSTRUCAO.get(grupo, 100)
        
        if propriedade.casas == 0:
            status = "Sem construções"
        elif propriedade.casas == self.HOTEL:
            status = "HOTEL"
        else:
            status = f"{propriedade.casas} casa(s)"
        
        return f"{propriedade.nome}: {status} | Custo construção: R${custo}"

# Teste do módulo
if __name__ == '__main__':
    print("--- Teste do Módulo Construção ---")
    print("Este módulo requer integração completa com Tabuleiro, Banco e Jogador.")
    print("Execute os testes através do arquivo principal do jogo.")
