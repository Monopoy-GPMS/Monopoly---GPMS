# Arquivo de mapeamento das posições precisas de cada casa/propriedade
# Coordenadas capturadas manualmente para posicionamento exato dos peões
# O sistema usará esses pontos como centro de cada casa com pequenos offsets por jogador

POSICOES_CASAS_PRECISAS = [
    (1162, 843),   # 0: Ponto de Partida
    (1067, 841),   # 1: Avenida Sumaré
    (994, 839),    # 2: Cofre
    (920, 844),    # 3: Praça da Sé
    (844, 835),    # 4: Imposto de Renda
    (772, 832),    # 5: Estação Metrô Maracanã
    (695, 839),    # 6: Rua 25 de Março
    (620, 840),    # 7: Sorte
    (543, 842),    # 8: Av São João
    (466, 842),    # 9: Av Paulista
    (379, 837),    # 10: Cadeia/Prisão
    (372, 754),    # 11: Av Vieira Souto
    (373, 674),    # 12: Cia Elétrica
    (370, 602),    # 13: Niterói
    (365, 532),    # 14: Av Atlântica
    (368, 459),    # 15: Estação Metrô Carioca
    (360, 380),    # 16: Av Juscelino
    (365, 300),    # 17: Cofre
    (360, 228),    # 18: Av Berrini
    (362, 153),    # 19: Av Faria Lima
    (369, 59),     # 20: Estacionamento
    (475, 62),     # 21: Ipanema
    (549, 61),     # 22: Sorte
    (620, 62),     # 23: Leblon
    (695, 67),     # 24: Copacabana
    (770, 62),     # 25: Estação Metrô Consolação
    (847, 65),     # 26: Av Cidade Jardim
    (924, 65),     # 27: Pacaembu
    (997, 64),     # 28: Cia Água
    (1065, 63),    # 29: Ibirapuera
    (1159, 61),    # 30: Vá Para Cadeia
    (1164, 149),   # 31: Barra da Tijuca
    (1167, 226),   # 32: Jardim Botânico
    (1167, 299),   # 33: Cofre
    (1169, 381),   # 34: Lagoa Rodrigo
    (1165, 446),   # 35: Estação Metrô República
    (1162, 526),   # 36: Sorte
    (1168, 599),   # 37: Av Morumbi
    (1170, 678),   # 38: Taxa Riqueza
    (1165, 750),   # 39: Rua Oscar Freire
]

# Offsets pequenos por jogador para evitar sobreposição
# Cada jogador terá um offset único baseado em seu índice
OFFSETS_POR_JOGADOR = [
    (-8, -8),      # Jogador 0 (top-left)
    (8, -8),       # Jogador 1 (top-right)
    (-8, 8),       # Jogador 2 (bottom-left)
    (8, 8),        # Jogador 3 (bottom-right)
    (-4, 0),       # Jogador 4 (middle-left)
    (4, 0),        # Jogador 5 (middle-right)
]
