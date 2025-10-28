# src/main.py
# Ponto de entrada do sistema

from src.jogo import Jogo 

if __name__ == '__main__':
    print("--- DEMONSTRAÇÃO DA VERSÃO PARCIAL: BACKEND ---")
    
    # Simulação da Inicialização da Partida (Requisito 08: Escalabilidade)
    nomes = ["Alice (Humana)", "Bot 1 (IA)", "Carlos (Humano)"]
    
    jogo = Jogo(nomes)
    print("\n[PARTIDA INICIADA]")
    jogo.status_geral()

    # Execução de turnos para testar a Mecânica da SCRUM-8
    for i in range(1, 6): # Rodar 5 turnos
        jogo.iniciar_turno()
        
    print("\n--- FIM DA DEMONSTRAÇÃO ---")
    print("O backend demonstrou: Transações, Movimentação e as novas regras de Imposto/Prisão.")