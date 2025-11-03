# banco.py
# Módulo responsável por gerenciar as contas, saldos e transações financeiras.

class Banco:
    SALDO_INICIAL_PADRAO = 1500  # Saldo padrão do Monopoly

    def __init__(self):
        """Inicializa o Banco com um dicionário vazio para armazenar as contas."""
        # Estrutura: {nome_jogador: saldo_atual}
        self.contas = {}
    
    def inicializar_conta(self, nome_jogador):
        """
        Cria a conta para um novo jogador com o saldo inicial padrão.
        Usado no início de cada partida.
        """
        if nome_jogador not in self.contas:
            self.contas[nome_jogador] = self.SALDO_INICIAL_PADRAO
            print(f"Conta de {nome_jogador} criada. Saldo: R${self.SALDO_INICIAL_PADRAO}")
        else:
            print(f"A conta de {nome_jogador} já existe.")

    def pagar(self, pagador, valor, recebedor="Banco"):
        """
        Transfere 'valor' de 'pagador' para 'recebedor'.
        Retorna True se a transação for bem-sucedida, False caso contrário (falta de saldo).
        """
        # Garante que o valor a pagar é positivo
        if valor <= 0:
            print("Erro: O valor da transação deve ser positivo.")
            return False

        # Validação do Requisito 05 (Confiabilidade): Verifica se o pagador tem saldo
        if self.contas.get(pagador, 0) < valor:
            print(f"!!! Transação Negada: {pagador} não tem saldo suficiente (R${self.contas.get(pagador, 0)}) para pagar R${valor}.")
            # Lógica de falência ou hipoteca seria implementada aqui
            return False
        
        # 1. Debitar do pagador
        self.contas[pagador] -= valor
        
        # 2. Creditar no recebedor (se não for o "Banco" - dinheiro que sai de circulação)
        if recebedor != "Banco":
            # Se o recebedor não for um jogador existente (ex: um imposto pago ao banco
            # que é registrado temporariamente), ele deve ser um nome válido.
            if recebedor not in self.contas:
                 # Cria a conta do recebedor (se for um jogador) ou ignora se for o Banco
                pass # O dinheiro pago ao "Banco" desaparece da circulação (imposto, etc.)
            else:
                self.contas[recebedor] += valor
        
        print(f"  [SUCESSO] {pagador} pagou R${valor} para {recebedor}.")
        return True

    def depositar(self, recebedor, valor):
        """Adiciona 'valor' ao saldo do 'recebedor' (ex: passar pela Saída)."""
        if valor > 0:
            if recebedor in self.contas:
                self.contas[recebedor] += valor
                print(f"  [DEPÓSITO] {recebedor} recebeu R${valor}. Novo Saldo: R${self.contas[recebedor]}")
                return True
            else:
                print(f"Erro: Jogador {recebedor} não encontrado para depósito.")
                return False
        return False

    def consultar_saldo(self, nome_jogador):
        """Permite consultar o saldo (Parte do Requisito 04: Usabilidade)."""
        return self.contas.get(nome_jogador, 0)
    
    def status_contas(self):
        """Imprime o status de todas as contas para monitoramento."""
        print("\n--- Status Atual do Banco ---")
        for jogador, saldo in self.contas.items():
            print(f"  {jogador}: R${saldo}")
        print("----------------------------\n")

# --- Bloco de Teste/Demonstração para a Versão Parcial ---
if __name__ == '__main__':
    print("--- Teste do Módulo Banco Virtual ---")
    
    banco_do_jogo = Banco()
    
    # Simulação da inicialização da partida (Requisito 08: Escalabilidade)
    banco_do_jogo.inicializar_conta("Alice")
    banco_do_jogo.inicializar_conta("Bob")
    
    banco_do_jogo.status_contas()
    
    # 1. Simulação de transação bem-sucedida (Alice compra uma propriedade)
    print("\n--- Transação: Alice compra Propriedade (R$200) ---")
    banco_do_jogo.pagar("Alice", 200) # Pagando ao Banco
    
    # 2. Simulação de pagamento de aluguel (Bob paga Alice)
    print("\n--- Transação: Bob paga Aluguel (R$150) para Alice ---")
    banco_do_jogo.pagar("Bob", 150, "Alice")
    
    # 3. Simulação de depósito (Alice passa pela Saída)
    print("\n--- Transação: Alice passa pela Saída (R$200) ---")
    banco_do_jogo.depositar("Alice", 200)
    
    # 4. Simulação de transação inválida (Requisito 05: Confiabilidade)
    print("\n--- Transação: Bob tenta pagar R$5000 ---")
    banco_do_jogo.pagar("Bob", 5000, "Banco")
    
    banco_do_jogo.status_contas()