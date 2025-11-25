# regras_prisao.py
# Módulo responsável pelas regras da prisão

from constantes import POSICAO_PRISAO

class GestorPrisao:
    """Gerencia todas as regras relacionadas à prisão"""
    
    MULTA_SAIDA = 50  # Valor para pagar e sair da prisão
    MAX_TURNOS_PRISAO = 3  # Máximo de turnos antes de ser forçado a pagar
    
    def __init__(self, banco):
        """
        Args:
            banco: Objeto Banco para transações financeiras
        """
        self.banco = banco
    
    def enviar_prisao(self, jogador):
        """
        Envia o jogador para a prisão.
        Usado quando:
        - Cai na casa "Vá para a Prisão"
        - Pega carta que envia para prisão
        - Tira 3 duplas seguidas
        """
        jogador.entrar_prisao()
        print(f"  > {jogador.nome} foi enviado para a prisão!")
        return True
    
    def pode_sair_prisao_com_carta(self, jogador):
        """Verifica se o jogador tem carta 'Saia Livre da Prisão'"""
        return jogador.cartas_livre_prisao > 0
    
    def sair_prisao_com_carta(self, jogador):
        """
        Usa uma carta 'Saia Livre da Prisão' para sair.
        Returns:
            bool: True se conseguiu sair
        """
        if not jogador.em_prisao:
            print(f"  > {jogador.nome} não está na prisão.")
            return False
        
        if jogador.cartas_livre_prisao > 0:
            jogador.cartas_livre_prisao -= 1
            jogador.sair_prisao()
            print(f"  > {jogador.nome} usou uma carta 'Saia Livre da Prisão'!")
            return True
        else:
            print(f"  > {jogador.nome} não tem carta 'Saia Livre da Prisão'.")
            return False
    
    def pode_pagar_fianca(self, jogador):
        """Verifica se o jogador tem dinheiro para pagar a fiança"""
        if not jogador.em_prisao:
            return False
        
        saldo = self.banco.consultar_saldo(jogador.nome)
        return saldo >= self.MULTA_SAIDA
    
    def pagar_fianca(self, jogador):
        """
        Paga a fiança para sair da prisão.
        Returns:
            bool: True se pagou e saiu
        """
        if not jogador.em_prisao:
            print(f"  > {jogador.nome} não está na prisão.")
            return False
        
        sucesso = self.banco.pagar(jogador.nome, self.MULTA_SAIDA, "Banco")
        
        if sucesso:
            jogador.sair_prisao()
            print(f"  > {jogador.nome} pagou R${self.MULTA_SAIDA} e saiu da prisão!")
            return True
        else:
            print(f"  > {jogador.nome} não tem dinheiro suficiente para pagar a fiança.")
            return False
    
    def tentar_sair_com_dupla(self, jogador, eh_dupla):
        """
        Tenta sair da prisão tirando dupla nos dados.
        Returns:
            bool: True se conseguiu sair com dupla
        """
        if not jogador.em_prisao:
            return False
        
        if eh_dupla:
            jogador.sair_prisao()
            print(f"  > {jogador.nome} tirou dupla e saiu da prisão!")
            return True
        else:
            turnos = jogador.incrementar_turno_prisao()
            print(f"  > {jogador.nome} não tirou dupla. Turno {turnos}/{self.MAX_TURNOS_PRISAO} na prisão.")
            
            # Após 3 turnos, é forçado a pagar
            if turnos >= self.MAX_TURNOS_PRISAO:
                print(f"  > {jogador.nome} completou {self.MAX_TURNOS_PRISAO} turnos e DEVE pagar a fiança!")
                return self.pagar_fianca(jogador)
            
            return False
    
    def processar_turno_prisao(self, jogador, dados_obj):
        """
        Processa o turno de um jogador na prisão.
        O jogador pode:
        1. Pagar a fiança
        2. Usar carta 'Saia Livre da Prisão'
        3. Tentar tirar dupla nos dados
        
        Returns:
            tuple: (saiu_prisao: bool, pode_mover: bool, valor_dados: int)
        """
        if not jogador.em_prisao:
            return False, False, 0
        
        print(f"\n  > {jogador.nome} está na prisão (Turno {jogador.turnos_na_prisao + 1}/{self.MAX_TURNOS_PRISAO})")
        print(f"    Opções: 1) Rolar dados (tentar dupla)  2) Pagar R${self.MULTA_SAIDA}  3) Usar carta")
        
        # Para fins de demonstração automática, tentamos sair com dupla
        total, valores, eh_dupla = dados_obj.rolar()
        print(f"    > Rolou dados: {valores[0]} + {valores[1]} = {total}")
        
        saiu = self.tentar_sair_com_dupla(jogador, eh_dupla)
        
        # Se saiu com dupla, pode mover normalmente
        if saiu:
            return True, True, total
        
        # Se não saiu, fica na prisão
        return False, False, 0
    
    def get_opcoes_prisao(self, jogador):
        """
        Retorna as opções disponíveis para o jogador sair da prisão.
        Returns:
            dict: Dicionário com opções disponíveis
        """
        if not jogador.em_prisao:
            return {}
        
        opcoes = {
            'pode_pagar': self.pode_pagar_fianca(jogador),
            'tem_carta': self.pode_sair_prisao_com_carta(jogador),
            'turnos_restantes': self.MAX_TURNOS_PRISAO - jogador.turnos_na_prisao,
            'valor_fianca': self.MULTA_SAIDA
        }
        
        return opcoes

# Teste do módulo
if __name__ == '__main__':
    print("--- Teste do Módulo Regras da Prisão ---")
    
    # Mock classes
    class JogadorMock:
        def __init__(self, nome):
            self.nome = nome
            self.posicao = 0
            self.em_prisao = False
            self.turnos_na_prisao = 0
            self.cartas_livre_prisao = 0
        
        def entrar_prisao(self):
            self.em_prisao = True
            self.posicao = POSICAO_PRISAO
            self.turnos_na_prisao = 0
        
        def sair_prisao(self):
            self.em_prisao = False
            self.turnos_na_prisao = 0
        
        def incrementar_turno_prisao(self):
            if self.em_prisao:
                self.turnos_na_prisao += 1
            return self.turnos_na_prisao
    
    class BancoMock:
        def __init__(self):
            self.contas = {}
        
        def inicializar_conta(self, nome):
            self.contas[nome] = 1500
        
        def consultar_saldo(self, nome):
            return self.contas.get(nome, 0)
        
        def pagar(self, pagador, valor, destino):
            if self.contas.get(pagador, 0) >= valor:
                self.contas[pagador] -= valor
                print(f"    [BANCO] {pagador} pagou R${valor}")
                return True
            return False
    
    # Testa o gestor
    banco = BancoMock()
    banco.inicializar_conta("Jogador1")
    
    gestor = GestorPrisao(banco)
    jogador = JogadorMock("Jogador1")
    
    print("\n--- Teste 1: Enviar para prisão ---")
    gestor.enviar_prisao(jogador)
    print(f"Jogador na prisão: {jogador.em_prisao}")
    
    print("\n--- Teste 2: Tentar sair com carta (sem ter carta) ---")
    gestor.sair_prisao_com_carta(jogador)
    
    print("\n--- Teste 3: Dar carta e sair ---")
    jogador.cartas_livre_prisao = 1
    gestor.sair_prisao_com_carta(jogador)
    print(f"Jogador na prisão: {jogador.em_prisao}")
    
    print("\n--- Teste 4: Enviar novamente e pagar fiança ---")
    gestor.enviar_prisao(jogador)
    gestor.pagar_fianca(jogador)
    print(f"Saldo restante: R${banco.consultar_saldo('Jogador1')}")
