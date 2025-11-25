# jogador.py
# Módulo responsável pela classe Jogador, que armazena o estado e as ações de cada participante.

class Jogador:
    def __init__(self, nome, peca, is_ia=False):
        """
        Inicializa o jogador. O saldo será gerenciado pelo módulo 'banco'.
        """
        self.nome = nome          # Nome do jogador (identificador)
        self.peca = peca          # Peça escolhida (ex: "Carro", "Chapéu")
        self.posicao = 0          # Posição inicial: Casa "Saída" (0)
        self.propriedades = []    # Lista de objetos Propriedade que o jogador possui
        self.em_prisao = False    # Flag que indica se o jogador está na prisão
        self.is_ia = is_ia        # Flag para Escalabilidade (Requisito 08): Define se é um bot
        self.cartas_livre_prisao = []  # Lista de cartas "Saia Livre da Prisão" (negociáveis)
        self.ultima_rolagem = 0 # Armazena o valor total dos dados para Aluguel de Companhias
        self.turnos_na_prisao = 0
        self.falido = False       # Flag que indica se o jogador está falido
        self.inventario_itens = {}  # Dicionário para armazenar itens especiais

    def mover(self, dados_rolados):
        """
        Atualiza a posição do jogador no tabuleiro.
        Retorna a posição antiga para verificação de passagem pela saída.
        """
        posicao_antiga = self.posicao
        self.posicao = (self.posicao + dados_rolados) % 40
        
        print(f"  > {self.nome} rolou {dados_rolados} e moveu de {posicao_antiga} para a Casa {self.posicao}.")
        
        return posicao_antiga

    def mover_para(self, posicao_destino):
        """
        Move o jogador diretamente para uma posição específica.
        Útil para cartas de sorte/revés e para enviar à prisão.
        """
        posicao_antiga = self.posicao
        self.posicao = posicao_destino % 40
        print(f"  > {self.nome} foi movido de {posicao_antiga} para a Casa {self.posicao}.")
        return posicao_antiga

    def pode_mover(self):
        """
        Verifica se o jogador pode se mover neste turno.
        Jogadores presos não podem se mover até pagar fiança ou tirar dupla.
        """
        return not self.em_prisao

    def entrar_prisao(self):
        """Coloca o jogador na prisão"""
        self.em_prisao = True
        self.turnos_na_prisao = 0
        self.posicao = 10  # Posição da prisão
        print(f"  > {self.nome} entrou na prisão!")

    def sair_prisao(self):
        """Libera o jogador da prisão"""
        self.em_prisao = False
        self.turnos_na_prisao = 0
        print(f"  > {self.nome} saiu da prisão!")

    def incrementar_turno_prisao(self):
        """Incrementa o contador de turnos na prisão"""
        if self.em_prisao:
            self.turnos_na_prisao += 1
            return self.turnos_na_prisao
        return 0

    def adicionar_propriedade(self, propriedade):
        """Adiciona uma propriedade comprada ou recebida à lista do jogador."""
        self.propriedades.append(propriedade)
        propriedade.proprietario = self
        print(f"  > {self.nome} adquiriu a propriedade: {propriedade.nome}.")
        
    def remover_propriedade(self, propriedade):
        """Remove uma propriedade (em caso de venda/hipoteca/falência)."""
        if propriedade in self.propriedades:
            self.propriedades.remove(propriedade)
            propriedade.proprietario = None
            print(f"  > {self.nome} perdeu a propriedade: {propriedade.nome}.")
            return True
        return False

    def tem_propriedade(self, propriedade):
        """Verifica se o jogador possui uma propriedade específica"""
        return propriedade in self.propriedades

    def contar_propriedades_grupo(self, grupo):
        """Conta quantas propriedades de um grupo específico o jogador possui"""
        return sum(1 for prop in self.propriedades if hasattr(prop, 'grupo_cor') and prop.grupo_cor == grupo)

    def tem_monopolio(self, grupo, total_grupo):
        """Verifica se o jogador tem todas as propriedades de um grupo (monopólio)"""
        return self.contar_propriedades_grupo(grupo) == total_grupo

    def status_resumido(self, saldo):
        """
        Gera um resumo do estado do jogador para a Interface do Jogador (Requisito 04: Usabilidade).
        Note que o SALDO vem do módulo Banco, mas a posição e propriedades vêm desta classe.
        """
        prop_count = len(self.propriedades)
        
        status = (
            f"--- {self.nome} ({'IA' if self.is_ia else 'Humano'}) ---\n"
            f"  Peça: {self.peca}\n"
            f"  **SALDO**: R${saldo}\n"
            f"  **POSIÇÃO**: Casa {self.posicao} ({'NA PRISÃO' if self.em_prisao else 'Livre'})\n"
            f"  **PROPRIEDADES**: {prop_count} compradas"
        )
        return status

    def declarar_falencia(self):
        """Marca o jogador como falido"""
        self.falido = True
        print(f"  > {self.nome} declarou falência!")

    def adicionar_carta_livre_prisao(self, carta):
        """Adiciona uma carta 'Saia Livre da Prisão' ao inventário negociável"""
        self.cartas_livre_prisao.append(carta)
        print(f"  > {self.nome} agora possui {len(self.cartas_livre_prisao)} carta(s) de 'Saia Livre da Prisão'")

    def usar_carta_livre_prisao(self):
        """Remove uma carta de 'Saia Livre da Prisão' do inventário ao usá-la"""
        if self.cartas_livre_prisao:
            carta = self.cartas_livre_prisao.pop(0)
            print(f"  > {self.nome} usou a carta 'Saia Livre da Prisão'!")
            return carta
        return None

    def tem_carta_livre_prisao(self):
        """Verifica se o jogador possui alguma carta de 'Saia Livre da Prisão'"""
        return len(self.cartas_livre_prisao) > 0

    def adicionar_item(self, tipo_item, item=None):
        """Adiciona um item especial ao inventário"""
        if tipo_item not in self.inventario_itens:
            self.inventario_itens[tipo_item] = []
        self.inventario_itens[tipo_item].append(item)
        print(f"  > {self.nome} adicionou ao inventário: {tipo_item}")

    def usar_item(self, tipo_item):
        """Remove e retorna um item do inventário"""
        if tipo_item in self.inventario_itens and self.inventario_itens[tipo_item]:
            item = self.inventario_itens[tipo_item].pop(0)
            print(f"  > {self.nome} usou o item: {tipo_item}")
            return item
        return None

    def tem_item(self, tipo_item):
        """Verifica se o jogador possui um item específico"""
        return tipo_item in self.inventario_itens and len(self.inventario_itens[tipo_item]) > 0

    def listar_inventario(self):
        """Retorna uma descrição do inventário"""
        inventario = "Inventário:\n"
        if self.cartas_livre_prisao:
            inventario += f"  - Cartas Saia Livre da Prisão: {len(self.cartas_livre_prisao)}\n"
        for tipo_item, items in self.inventario_itens.items():
            if items:
                inventario += f"  - {tipo_item}: {len(items)}\n"
        return inventario if inventario != "Inventário:\n" else "Inventário vazio"

    def __str__(self):
        return f"Jogador {self.nome} (Peça: {self.peca}, Posição: {self.posicao})"

    def __repr__(self):
        return self.__str__()
        
# --- Bloco de Teste/Demonstração para a Versão Parcial ---
if __name__ == '__main__':
    print("--- Teste do Módulo Jogador ---")
    
    # Simulação de objetos simples para a lista de propriedades
    class PropriedadeMock:
        def __init__(self, nome, grupo_cor=None):
            self.nome = nome
            self.grupo_cor = grupo_cor

    # 1. Inicialização de jogadores (Humano e Bot)
    jogador1 = Jogador("Patrícia", "Chapéu")
    jogador2 = Jogador("Bot Monopólio", "Bota", is_ia=True)
    
    # 2. Simulação de ações
    print("\n--- Simulação de Ações ---")
    
    # Movimentação
    jogador1.mover(7)
    jogador2.mover(15)
    
    # Compra de Propriedade
    prop1 = PropriedadeMock("Avenida Atlântica", "Amarelo")
    prop2 = PropriedadeMock("Ferrovia Reading", "Amarelo")
    
    jogador1.adicionar_propriedade(prop1)
    jogador1.adicionar_propriedade(prop2)
    
    # Adição de Carta Saia Livre da Prisão
    jogador1.adicionar_carta_livre_prisao("Carta 1")
    jogador1.adicionar_carta_livre_prisao("Carta 2")
    
    # Uso de Carta Saia Livre da Prisão
    jogador1.usar_carta_livre_prisao()
    
    # Adição de Item Especial
    jogador1.adicionar_item("Item Especial 1")
    jogador1.adicionar_item("Item Especial 2")
    
    # Uso de Item Especial
    jogador1.usar_item("Item Especial 1")
    
    # 3. Exibição do Status (Requisito 04)
    print("\n--- Status do Jogador (Simulando Saldo de R$1000) ---")
    
    # O saldo R$1000 é um mock (valor temporário para simular um cenário), pois o Banco não foi importado neste arquivo.
    print(jogador1.status_resumido(saldo=1000)) 
    print(jogador2.status_resumido(saldo=1500))

    # 4. Simulação de Entrada e Saída da Prisão
    print("\n--- Simulação de Entrada e Saída da Prisão ---")
    jogador1.entrar_prisao()
    jogador1.incrementar_turno_prisao()
    jogador1.sair_prisao()

    # 5. Listagem do Inventário
    print("\n--- Listagem do Inventário ---")
    print(jogador1.listar_inventario())
