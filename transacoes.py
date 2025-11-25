# transacoes.py
# Módulo responsável por gerenciar todas as transações financeiras do jogo

from constantes import (
    VALOR_PASSAGEM_SAIDA,
    IMPOSTO_RENDA_VALOR,
    TAXA_RIQUEZA_VALOR,
    MULTA_SAIDA_PRISAO
)

class GerenciadorTransacoes:
    """
    Classe responsável por gerenciar todas as transações financeiras entre jogadores,
    banco, pagamentos de impostos, aluguéis e recebimentos.
    """
    
    def __init__(self, banco):
        """
        Inicializa o gerenciador de transações com referência ao banco.
        
        Args:
            banco: Instância da classe Banco que gerencia as contas
        """
        self.banco = banco
        self.historico_transacoes = []  # Log de todas as transações
        
    def _registrar_transacao(self, tipo, origem, destino, valor, descricao=""):
        """
        Registra uma transação no histórico para auditoria.
        
        Args:
            tipo: Tipo da transação (PAGAMENTO, RECEBIMENTO, IMPOSTO, ALUGUEL)
            origem: Nome do jogador ou entidade que pagou
            destino: Nome do jogador ou entidade que recebeu
            valor: Valor da transação
            descricao: Descrição adicional da transação
        """
        transacao = {
            'tipo': tipo,
            'origem': origem,
            'destino': destino,
            'valor': valor,
            'descricao': descricao
        }
        self.historico_transacoes.append(transacao)
    
    # ===== TRANSAÇÕES ENTRE JOGADORES =====
    
    def pagar_aluguel(self, inquilino, proprietario, valor_aluguel):
        """
        Realiza o pagamento de aluguel de um jogador para outro.
        
        Args:
            inquilino: Jogador que deve pagar o aluguel
            proprietario: Jogador que receberá o aluguel
            valor_aluguel: Valor do aluguel a ser pago
            
        Returns:
            bool: True se o pagamento foi bem-sucedido, False caso contrário
        """
        if inquilino.nome == proprietario.nome:
            print(f"  > {inquilino.nome} caiu em sua própria propriedade. Sem cobrança.")
            return True
            
        print(f"\n--- PAGAMENTO DE ALUGUEL ---")
        print(f"  Inquilino: {inquilino.nome}")
        print(f"  Proprietário: {proprietario.nome}")
        print(f"  Valor: R${valor_aluguel}")
        
        sucesso = self.banco.pagar(inquilino.nome, valor_aluguel, proprietario.nome)
        
        if sucesso:
            self._registrar_transacao(
                'ALUGUEL',
                inquilino.nome,
                proprietario.nome,
                valor_aluguel,
                f"Pagamento de aluguel"
            )
            print(f"  ✓ Aluguel pago com sucesso!")
            return True
        else:
            print(f"  ✗ {inquilino.nome} não tem saldo suficiente para pagar o aluguel!")
            # Aqui seria acionada a lógica de falência/negociação
            return False
    
    def transferir_entre_jogadores(self, pagador, recebedor, valor, motivo=""):
        """
        Realiza transferência genérica entre dois jogadores.
        Útil para negociações, acordos e compra/venda de propriedades.
        
        Args:
            pagador: Jogador que fará o pagamento
            recebedor: Jogador que receberá o valor
            valor: Quantia a ser transferida
            motivo: Descrição do motivo da transferência
            
        Returns:
            bool: True se a transferência foi bem-sucedida
        """
        print(f"\n--- TRANSFERÊNCIA ENTRE JOGADORES ---")
        print(f"  De: {pagador.nome}")
        print(f"  Para: {recebedor.nome}")
        print(f"  Valor: R${valor}")
        if motivo:
            print(f"  Motivo: {motivo}")
        
        sucesso = self.banco.pagar(pagador.nome, valor, recebedor.nome)
        
        if sucesso:
            self._registrar_transacao(
                'TRANSFERENCIA',
                pagador.nome,
                recebedor.nome,
                valor,
                motivo
            )
            print(f"  ✓ Transferência realizada com sucesso!")
            return True
        else:
            print(f"  ✗ Transferência falhou - saldo insuficiente!")
            return False
    
    # ===== PAGAMENTOS AO BANCO (IMPOSTOS E TAXAS) =====
    
    def pagar_imposto(self, jogador, valor_imposto, tipo_imposto="Imposto"):
        """
        Realiza o pagamento de impostos e taxas ao banco.
        
        Args:
            jogador: Jogador que deve pagar o imposto
            valor_imposto: Valor do imposto
            tipo_imposto: Tipo do imposto (ex: "Imposto de Renda", "Taxa de Riqueza")
            
        Returns:
            bool: True se o pagamento foi bem-sucedido
        """
        print(f"\n--- PAGAMENTO DE IMPOSTO ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Tipo: {tipo_imposto}")
        print(f"  Valor: R${valor_imposto}")
        
        sucesso = self.banco.pagar(jogador.nome, valor_imposto, "Banco")
        
        if sucesso:
            self._registrar_transacao(
                'IMPOSTO',
                jogador.nome,
                'Banco',
                valor_imposto,
                tipo_imposto
            )
            print(f"  ✓ Imposto pago ao banco!")
            return True
        else:
            print(f"  ✗ Saldo insuficiente para pagar o imposto!")
            return False
    
    def pagar_taxa_construcao(self, jogador, valor_total, quantidade_casas=0, quantidade_hoteis=0):
        """
        Cobra taxa especial para reparos em propriedades (carta de Sorte/Revés).
        
        Args:
            jogador: Jogador que deve pagar a taxa
            valor_total: Valor total a ser pago
            quantidade_casas: Número de casas que o jogador possui
            quantidade_hoteis: Número de hotéis que o jogador possui
            
        Returns:
            bool: True se o pagamento foi bem-sucedido
        """
        print(f"\n--- TAXA DE REPAROS ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Casas: {quantidade_casas} | Hotéis: {quantidade_hoteis}")
        print(f"  Valor Total: R${valor_total}")
        
        sucesso = self.banco.pagar(jogador.nome, valor_total, "Banco")
        
        if sucesso:
            self._registrar_transacao(
                'TAXA',
                jogador.nome,
                'Banco',
                valor_total,
                f"Taxa de reparos ({quantidade_casas} casas, {quantidade_hoteis} hotéis)"
            )
            return True
        else:
            print(f"  ✗ Saldo insuficiente para pagar a taxa de reparos!")
            return False
    
    def pagar_multa_prisao(self, jogador):
        """
        Cobra a multa para sair da prisão.
        
        Args:
            jogador: Jogador que pagará a multa
            
        Returns:
            bool: True se o pagamento foi bem-sucedido
        """
        print(f"\n--- PAGAMENTO DE MULTA DA PRISÃO ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Valor: R${MULTA_SAIDA_PRISAO}")
        
        sucesso = self.banco.pagar(jogador.nome, MULTA_SAIDA_PRISAO, "Banco")
        
        if sucesso:
            self._registrar_transacao(
                'MULTA',
                jogador.nome,
                'Banco',
                MULTA_SAIDA_PRISAO,
                "Multa para sair da prisão"
            )
            jogador.sair_prisao()
            print(f"  ✓ {jogador.nome} pagou a multa e saiu da prisão!")
            return True
        else:
            print(f"  ✗ Saldo insuficiente para pagar a multa!")
            return False
    
    def pagar_compra_propriedade(self, jogador, propriedade):
        """
        Processa o pagamento da compra de uma propriedade.
        
        Args:
            jogador: Jogador que está comprando
            propriedade: Propriedade a ser comprada
            
        Returns:
            bool: True se a compra foi bem-sucedida
        """
        print(f"\n--- COMPRA DE PROPRIEDADE ---")
        print(f"  Comprador: {jogador.nome}")
        print(f"  Propriedade: {propriedade.nome}")
        print(f"  Valor: R${propriedade.preco_compra}")
        
        sucesso = self.banco.pagar(jogador.nome, propriedade.preco_compra, "Banco")
        
        if sucesso:
            self._registrar_transacao(
                'COMPRA',
                jogador.nome,
                'Banco',
                propriedade.preco_compra,
                f"Compra de {propriedade.nome}"
            )
            jogador.adicionar_propriedade(propriedade)
            print(f"  ✓ Propriedade comprada com sucesso!")
            return True
        else:
            print(f"  ✗ Saldo insuficiente para comprar a propriedade!")
            return False
    
    # ===== RECEBIMENTOS =====
    
    def receber_salario_saida(self, jogador):
        """
        Credita o salário ao jogador por passar pela casa de saída.
        
        Args:
            jogador: Jogador que passará pela saída
            
        Returns:
            bool: True sempre (não há como falhar em receber)
        """
        print(f"\n--- PASSOU PELA SAÍDA ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Bônus: R${VALOR_PASSAGEM_SAIDA}")
        
        sucesso = self.banco.depositar(jogador.nome, VALOR_PASSAGEM_SAIDA)
        
        if sucesso:
            self._registrar_transacao(
                'SALARIO',
                'Banco',
                jogador.nome,
                VALOR_PASSAGEM_SAIDA,
                "Passou pela saída"
            )
            print(f"  ✓ Salário recebido!")
        
        return sucesso
    
    def receber_premio(self, jogador, valor, descricao="Prêmio"):
        """
        Credita um valor ao jogador (ex: cartas de Sorte/Revés).
        
        Args:
            jogador: Jogador que receberá o prêmio
            valor: Quantia a ser recebida
            descricao: Descrição do prêmio
            
        Returns:
            bool: True sempre
        """
        print(f"\n--- PRÊMIO RECEBIDO ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Valor: R${valor}")
        print(f"  Motivo: {descricao}")
        
        sucesso = self.banco.depositar(jogador.nome, valor)
        
        if sucesso:
            self._registrar_transacao(
                'PREMIO',
                'Banco',
                jogador.nome,
                valor,
                descricao
            )
            print(f"  ✓ Prêmio creditado!")
        
        return sucesso
    
    def receber_venda_propriedade(self, jogador, valor, propriedade_nome):
        """
        Credita o valor da venda de uma propriedade ao jogador.
        
        Args:
            jogador: Jogador que vendeu a propriedade
            valor: Valor recebido pela venda
            propriedade_nome: Nome da propriedade vendida
            
        Returns:
            bool: True sempre
        """
        print(f"\n--- VENDA DE PROPRIEDADE ---")
        print(f"  Vendedor: {jogador.nome}")
        print(f"  Propriedade: {propriedade_nome}")
        print(f"  Valor: R${valor}")
        
        sucesso = self.banco.depositar(jogador.nome, valor)
        
        if sucesso:
            self._registrar_transacao(
                'VENDA',
                'Banco',
                jogador.nome,
                valor,
                f"Venda de {propriedade_nome}"
            )
            print(f"  ✓ Valor da venda creditado!")
        
        return sucesso
    
    def hipotecar_propriedade(self, jogador, propriedade):
        """
        Credita o valor da hipoteca de uma propriedade.
        
        Args:
            jogador: Jogador que está hipotecando
            propriedade: Propriedade a ser hipotecada
            
        Returns:
            bool: True se a hipoteca foi realizada
        """
        if propriedade.hipotecada:
            print(f"  ✗ {propriedade.nome} já está hipotecada!")
            return False
        
        valor_hipoteca = propriedade.preco_compra // 2  # Metade do valor de compra
        
        print(f"\n--- HIPOTECA DE PROPRIEDADE ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Propriedade: {propriedade.nome}")
        print(f"  Valor: R${valor_hipoteca}")
        
        propriedade.hipotecada = True
        sucesso = self.banco.depositar(jogador.nome, valor_hipoteca)
        
        if sucesso:
            self._registrar_transacao(
                'HIPOTECA',
                'Banco',
                jogador.nome,
                valor_hipoteca,
                f"Hipoteca de {propriedade.nome}"
            )
            print(f"  ✓ Hipoteca realizada!")
        
        return sucesso
    
    def pagar_deshipoteca(self, jogador, propriedade):
        """
        Remove a hipoteca de uma propriedade pagando o valor + juros.
        
        Args:
            jogador: Jogador que está removendo a hipoteca
            propriedade: Propriedade a ser deshipotecada
            
        Returns:
            bool: True se o pagamento foi bem-sucedido
        """
        if not propriedade.hipotecada:
            print(f"  ✗ {propriedade.nome} não está hipotecada!")
            return False
        
        valor_base = propriedade.preco_compra // 2
        valor_total = int(valor_base * 1.1)  # Valor + 10% de juros
        
        print(f"\n--- DESHIPOTECAR PROPRIEDADE ---")
        print(f"  Jogador: {jogador.nome}")
        print(f"  Propriedade: {propriedade.nome}")
        print(f"  Valor: R${valor_total} (com 10% de juros)")
        
        sucesso = self.banco.pagar(jogador.nome, valor_total, "Banco")
        
        if sucesso:
            propriedade.hipotecada = False
            self._registrar_transacao(
                'DESHIPOTECA',
                jogador.nome,
                'Banco',
                valor_total,
                f"Deshipoteca de {propriedade.nome}"
            )
            print(f"  ✓ Propriedade deshipotecada!")
            return True
        else:
            print(f"  ✗ Saldo insuficiente para deshipotecar!")
            return False
    
    # ===== RELATÓRIOS E CONSULTAS =====
    
    def obter_historico(self, jogador_nome=None, limite=10):
        """
        Retorna o histórico de transações.
        
        Args:
            jogador_nome: Nome do jogador para filtrar (None = todas)
            limite: Número máximo de transações a retornar
            
        Returns:
            list: Lista de transações
        """
        if jogador_nome:
            filtradas = [
                t for t in self.historico_transacoes
                if t['origem'] == jogador_nome or t['destino'] == jogador_nome
            ]
            return filtradas[-limite:]
        else:
            return self.historico_transacoes[-limite:]
    
    def imprimir_historico(self, jogador_nome=None, limite=10):
        """
        Imprime o histórico de transações de forma formatada.
        
        Args:
            jogador_nome: Nome do jogador para filtrar (None = todas)
            limite: Número máximo de transações a mostrar
        """
        transacoes = self.obter_historico(jogador_nome, limite)
        
        print("\n" + "="*60)
        print("HISTÓRICO DE TRANSAÇÕES")
        if jogador_nome:
            print(f"Jogador: {jogador_nome}")
        print("="*60)
        
        if not transacoes:
            print("  Nenhuma transação registrada.")
        else:
            for i, t in enumerate(transacoes, 1):
                print(f"\n{i}. {t['tipo']}")
                print(f"   De: {t['origem']} → Para: {t['destino']}")
                print(f"   Valor: R${t['valor']}")
                if t['descricao']:
                    print(f"   Descrição: {t['descricao']}")
        
        print("="*60 + "\n")
    
    def obter_total_pago(self, jogador_nome):
        """
        Calcula o total de dinheiro pago por um jogador.
        
        Args:
            jogador_nome: Nome do jogador
            
        Returns:
            int: Total pago
        """
        total = sum(
            t['valor'] for t in self.historico_transacoes
            if t['origem'] == jogador_nome
        )
        return total
    
    def obter_total_recebido(self, jogador_nome):
        """
        Calcula o total de dinheiro recebido por um jogador.
        
        Args:
            jogador_nome: Nome do jogador
            
        Returns:
            int: Total recebido
        """
        total = sum(
            t['valor'] for t in self.historico_transacoes
            if t['destino'] == jogador_nome
        )
        return total


# ===== TESTE DO MÓDULO =====
if __name__ == '__main__':
    from banco import Banco
    from jogador import Jogador
    
    print("="*60)
    print("TESTE DO SISTEMA DE TRANSAÇÕES")
    print("="*60)
    
    # Configuração inicial
    banco = Banco()
    transacoes = GerenciadorTransacoes(banco)
    
    # Criar jogadores
    banco.inicializar_conta("Alice")
    banco.inicializar_conta("Bob")
    
    jogador1 = Jogador("Alice", "Chapéu")
    jogador2 = Jogador("Bob", "Carro")
    
    print("\n--- SALDO INICIAL ---")
    banco.status_contas()
    
    # Teste 1: Passar pela saída
    print("\n" + "="*60)
    print("TESTE 1: PASSAR PELA SAÍDA")
    print("="*60)
    transacoes.receber_salario_saida(jogador1)
    
    # Teste 2: Pagamento de aluguel
    print("\n" + "="*60)
    print("TESTE 2: PAGAMENTO DE ALUGUEL")
    print("="*60)
    transacoes.pagar_aluguel(jogador2, jogador1, 150)
    
    # Teste 3: Pagamento de imposto
    print("\n" + "="*60)
    print("TESTE 3: PAGAMENTO DE IMPOSTO")
    print("="*60)
    transacoes.pagar_imposto(jogador1, IMPOSTO_RENDA_VALOR, "Imposto de Renda")
    
    # Teste 4: Receber prêmio
    print("\n" + "="*60)
    print("TESTE 4: RECEBER PRÊMIO")
    print("="*60)
    transacoes.receber_premio(jogador2, 50, "Carta de Sorte - Prêmio de concurso de beleza")
    
    # Teste 5: Transferência entre jogadores
    print("\n" + "="*60)
    print("TESTE 5: TRANSFERÊNCIA ENTRE JOGADORES")
    print("="*60)
    transacoes.transferir_entre_jogadores(jogador1, jogador2, 100, "Acordo de negociação")
    
    # Teste 6: Multa da prisão
    print("\n" + "="*60)
    print("TESTE 6: MULTA DA PRISÃO")
    print("="*60)
    jogador2.entrar_prisao()
    transacoes.pagar_multa_prisao(jogador2)
    
    # Saldo final
    print("\n--- SALDO FINAL ---")
    banco.status_contas()
    
    # Histórico de transações
    transacoes.imprimir_historico()
    
    # Estatísticas
    print("\n--- ESTATÍSTICAS ---")
    print(f"Alice - Total Pago: R${transacoes.obter_total_pago('Alice')} | Total Recebido: R${transacoes.obter_total_recebido('Alice')}")
    print(f"Bob - Total Pago: R${transacoes.obter_total_pago('Bob')} | Total Recebido: R${transacoes.obter_total_recebido('Bob')}")
