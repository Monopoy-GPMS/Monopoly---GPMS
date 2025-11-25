# movimentacao.py

from constantes import POSICAO_SAIDA, VALOR_PASSAGEM_SAIDA, POSICAO_PRISAO

class GerenciadorMovimentacao:
    """
    Classe responsável por gerenciar toda a lógica de movimentação dos jogadores no tabuleiro.
    Inclui movimentação normal, passagem pela saída, e movimentação especial (cartas, prisão, etc).
    """
    
    def __init__(self, tabuleiro, banco):
        """
        Inicializa o gerenciador de movimentação.
        
        Args:
            tabuleiro: Instância do Tabuleiro
            banco: Instância do Banco para gerenciar transações
        """
        self.tabuleiro = tabuleiro
        self.banco = banco
    
    def mover_jogador(self, jogador, quantidade_casas):
        """
        Move o jogador uma quantidade específica de casas.
        Verifica se passou pela saída e credita o bônus.
        
        Args:
            jogador: Objeto Jogador a ser movido
            quantidade_casas: Número de casas a avançar
            
        Returns:
            tuple: (casa_destino, passou_pela_saida)
        """
        posicao_antiga = jogador.posicao
        jogador.mover(quantidade_casas)
        posicao_nova = jogador.posicao
        
        # Verifica se passou pela saída
        passou_pela_saida = self._verificar_passagem_saida(posicao_antiga, posicao_nova)
        
        if passou_pela_saida:
            self._creditar_passagem_saida(jogador)
        
        # Retorna a casa onde o jogador parou
        casa_destino = self.tabuleiro.get_casa(posicao_nova)
        return casa_destino, passou_pela_saida
    
    def mover_jogador_para_posicao(self, jogador, posicao_destino, creditar_saida=True):
        """
        Move o jogador diretamente para uma posição específica.
        Usado para cartas de Sorte/Revés que movem o jogador para locais específicos.
        
        Args:
            jogador: Objeto Jogador a ser movido
            posicao_destino: Posição de destino (0-39)
            creditar_saida: Se deve creditar ao passar pela saída
            
        Returns:
            Casa objeto da posição de destino
        """
        posicao_antiga = jogador.posicao
        jogador.mover_para(posicao_destino)
        
        # Verifica passagem pela saída se habilitado
        if creditar_saida:
            passou_pela_saida = self._verificar_passagem_saida(posicao_antiga, posicao_destino)
            if passou_pela_saida:
                self._creditar_passagem_saida(jogador)
        
        casa_destino = self.tabuleiro.get_casa(posicao_destino)
        return casa_destino
    
    def enviar_para_prisao(self, jogador):
        """
        Envia o jogador diretamente para a prisão.
        Não credita passagem pela saída.
        
        Args:
            jogador: Objeto Jogador a ser enviado
        """
        jogador.entrar_prisao()
        jogador.posicao = POSICAO_PRISAO
        print(f"  > {jogador.nome} foi enviado para a prisão na posição {POSICAO_PRISAO}!")
    
    def voltar_casas(self, jogador, quantidade_casas):
        """
        Move o jogador para trás uma quantidade de casas.
        Usado para algumas cartas de Sorte/Revés.
        
        Args:
            jogador: Objeto Jogador a ser movido
            quantidade_casas: Número de casas a voltar (positivo)
            
        Returns:
            Casa objeto da posição de destino
        """
        posicao_antiga = jogador.posicao
        nova_posicao = (posicao_antiga - quantidade_casas) % 40
        jogador.mover_para(nova_posicao)
        
        casa_destino = self.tabuleiro.get_casa(nova_posicao)
        return casa_destino
    
    def avancar_ate_proxima_casa_tipo(self, jogador, tipo_casa):
        """
        Move o jogador para a próxima casa de um tipo específico.
        Útil para cartas que dizem "Vá para a próxima Ferrovia" ou "Vá para a próxima Companhia".
        
        Args:
            jogador: Objeto Jogador a ser movido
            tipo_casa: Tipo de casa procurado (ex: "METRÔ", "SERVIÇO")
            
        Returns:
            Casa objeto encontrada ou None se não encontrar
        """
        posicao_atual = jogador.posicao
        
        # Procura a próxima casa do tipo especificado
        for i in range(1, 40):  # Percorre o tabuleiro uma vez
            posicao_teste = (posicao_atual + i) % 40
            casa = self.tabuleiro.get_casa(posicao_teste)
            
            # Verifica se é uma propriedade com o grupo correto
            if hasattr(casa, 'grupo_cor') and casa.grupo_cor == tipo_casa:
                return self.mover_jogador_para_posicao(jogador, posicao_teste)
        
        return None
    
    def calcular_distancia(self, posicao_origem, posicao_destino):
        """
        Calcula a distância em casas entre duas posições.
        
        Args:
            posicao_origem: Posição inicial (0-39)
            posicao_destino: Posição final (0-39)
            
        Returns:
            int: Número de casas de distância
        """
        if posicao_destino >= posicao_origem:
            return posicao_destino - posicao_origem
        else:
            return 40 - posicao_origem + posicao_destino
    
    def _verificar_passagem_saida(self, posicao_antiga, posicao_nova):
        """
        Verifica se o jogador passou pela saída durante o movimento.
        
        Args:
            posicao_antiga: Posição antes do movimento
            posicao_nova: Posição depois do movimento
            
        Returns:
            bool: True se passou pela saída, False caso contrário
        """
        # Se a posição nova for menor que a antiga, deu a volta no tabuleiro
        if posicao_nova < posicao_antiga:
            return True
        # Se parou exatamente na saída vindo de outra posição
        elif posicao_nova == POSICAO_SAIDA and posicao_antiga != POSICAO_SAIDA:
            return True
        return False
    
    def _creditar_passagem_saida(self, jogador):
        """
        Credita o bônus de passagem pela saída ao jogador.
        
        Args:
            jogador: Objeto Jogador que passou pela saída
        """
        self.banco.depositar(jogador.nome, VALOR_PASSAGEM_SAIDA)
        print(f"  > {jogador.nome} passou pela saída e recebeu R${VALOR_PASSAGEM_SAIDA}!")
    
    def obter_info_posicao(self, posicao):
        """
        Retorna informações detalhadas sobre uma posição do tabuleiro.
        
        Args:
            posicao: Posição a ser consultada (0-39)
            
        Returns:
            dict: Dicionário com informações da casa
        """
        casa = self.tabuleiro.get_casa(posicao)
        
        info = {
            'posicao': posicao,
            'nome': casa.nome,
            'tipo': casa.tipo,
        }
        
        # Adiciona informações específicas se for propriedade
        if hasattr(casa, 'preco_compra'):
            info['preco'] = casa.preco_compra
            info['aluguel_base'] = casa.aluguel_base
            info['grupo'] = casa.grupo_cor if hasattr(casa, 'grupo_cor') else None
            info['proprietario'] = casa.proprietario.nome if casa.proprietario else None
        
        # Adiciona valor se for imposto
        if hasattr(casa, 'valor'):
            info['valor_imposto'] = casa.valor
        
        return info
    
    def __str__(self):
        return f"GerenciadorMovimentacao(Tabuleiro: {self.tabuleiro})"
    
    def __repr__(self):
        return self.__str__()
