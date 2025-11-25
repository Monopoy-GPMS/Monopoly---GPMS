import pygame
import sys
import os
import random
from jogo import Jogo
from propriedades import Propriedade
from menu import MenuInicial, TelaFimDeJogo
from posicoes_board import POSICOES_CASAS_PRECISAS, OFFSETS_POR_JOGADOR

# --- 1. Inicialização e Configurações ---
pygame.init()
pygame.font.init()

try:
    FONTE_PADRAO = pygame.font.SysFont('Arial', 18)
    FONTE_PEQUENA = pygame.font.SysFont('Arial', 13)
    FONTE_GRANDE = pygame.font.SysFont('Arial', 26)
    FONTE_MEDIA = pygame.font.SysFont('Arial', 18)
except Exception as e:
    print(f"Erro ao carregar fonte: {e}. Usando fonte padrão.")
    FONTE_PADRAO = pygame.font.Font(None, 18)
    FONTE_PEQUENA = pygame.font.Font(None, 13)
    FONTE_GRANDE = pygame.font.Font(None, 26)
    FONTE_MEDIA = pygame.font.Font(None, 18)

LARGURA_TELA = 1600
ALTURA_TELA = 900
flags = pygame.FULLSCREEN | pygame.SCALED

screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), flags)
pygame.display.set_caption("Monopoly")
COR_FUNDO = (10, 10, 20)

# --- Carregamento de Assets ---
def carregar_imagem(nome_arquivo, alpha=False):
    """Carrega uma imagem da pasta 'assets'."""
    caminho_completo = os.path.join(os.path.dirname(__file__), 'assets', nome_arquivo)
    try:
        imagem = pygame.image.load(caminho_completo)
    except pygame.error as e:
        print(f"Erro ao carregar imagem '{nome_arquivo}': {e}")
        sys.exit()
    
    if alpha:
        return imagem.convert_alpha()
    else:
        return imagem.convert()

# --- Carregando as imagens ---
tabuleiro_img = carregar_imagem('tabuleiro.png')

BOARD_IMG_WIDTH = 768
BOARD_IMG_HEIGHT = 768

# ====================================================================
# VARIÁVEIS DE AJUSTE GLOBAL - Modifique aqui para corrigir posições
# ====================================================================

X_TABULEIRO = 320  # Posição X do tabuleiro (já correto)
Y_TABULEIRO = 0    # Posição Y do tabuleiro (já correto)

# AJUSTE GLOBAL PARA PEÕES - Modifique estes valores para corrigir posicionamento
# Estes valores são SOMADOS a todas as posições dos peões
AJUSTE_GLOBAL_PEOES_X = -300
AJUSTE_GLOBAL_PEOES_Y = 0      # Aumentar para mover peões para BAIXO, diminuir para CIMA

# OFFSETS INDIVIDUAIS DOS PEÕES - Controla a distribuição dentro de cada casa
# Valores pequenos (±10 a ±15 pixels) para não ficar muito espalhado
# OFFSETS_PEOES = [
#     (-8, -8),    # Jogador 1 (top-left)
#     (8, -8),     # Jogador 2 (top-right)
#     (-8, 4),     # Jogador 3 (middle-left)
#     (8, 4),      # Jogador 4 (middle-right)
#     (-8, 16),    # Jogador 5 (bottom-left)
#     (8, 16),     # Jogador 6 (bottom-right)
# ]

MOSTRAR_HUD_MENU = True  # Enable menu display
# POSIÇÃO BASE DO MENU DE TURNO (HUD PRINCIPAL) - MODIFICADA PARA MELHOR LAYOUT
HUD_MENU_X = 10                # Posição X base (esquerda)
AJUSTE_HUD_Y = 135
HUD_MENU_Y = 480 + AJUSTE_HUD_Y # Posição Y base (abaixo do histórico)
HUD_MENU_WIDTH = 215
HUD_MENU_HEIGHT = 260  # Increased from 210 to accommodate "Passar a Vez" button

# AJUSTE GLOBAL PARA CONSTRUÇÕES - Modifique para corrigir casas/hotéis
AJUSTE_CONSTRUCOES_X = 200     # Aumentado de 0 para 200 - move menus popups para DIREITA
AJUSTE_CONSTRUCOES_Y = 0       # Aumentar para mover construções para BAIXO

AJUSTE_HUD_X = 0
# AJUSTE_HUD_Y = 0 # Removed and replaced by the above

print(f"[v0] Board image size: {BOARD_IMG_WIDTH}x{BOARD_IMG_HEIGHT}")
print(f"[v0] Board position on screen: ({X_TABULEIRO}, {Y_TABULEIRO})")
print(f"[v0] Pawn adjustment: ({AJUSTE_GLOBAL_PEOES_X}, {AJUSTE_GLOBAL_PEOES_Y})")
print(f"[v0] HUD adjustment: ({HUD_MENU_X}, {HUD_MENU_Y})")
print(f"[v0] Construction adjustment: ({AJUSTE_CONSTRUCOES_X}, {AJUSTE_CONSTRUCOES_Y})")

# The board has 40 squares: 11 on each side (including corners)
# Bottom row: positions 0-10 (right to left)
# Left row: positions 11-19 (bottom to top) 
# Top row: positions 20-30 (left to right)
# Right row: positions 31-39 (top to bottom)

# Square dimensions
CORNER_SIZE = 90  # Corner squares are larger
REGULAR_SIZE = 63  # Regular property squares

# Board is 755x755, squares are 63 pixels except corners which are 90 pixels
# Simply use POSICOES_CASAS_PRECISAS from the imported file
# POSICOES_CASAS_XY = [
#     # Bottom row (0-10): Starting from bottom-right corner, going left
#     (690, 690),   # 0: Ponto de Partida (bottom-right corner)
#     (627, 690),   # 1: Avenida Sumaré
#     (564, 690),   # 2: Cofre
#     (501, 690),   # 3: Praça da Sé
#     (438, 690),   # 4: Imposto de Renda
#     (375, 690),   # 5: Estação Metrô Maracanã
#     (312, 690),   # 6: Rua 25 de Março
#     (249, 690),   # 7: Sorte
#     (186, 690),   # 8: Av São João
#     (123, 690),   # 9: Av Paulista
#     (25, 690),    # 10: Cadeia/Prisão (bottom-left corner)
    
#     # Left row (11-19): Going up from bottom-left
#     (25, 627),    # 11: Av Vieira Souto
#     (25, 564),    # 12: Cia Elétrica
#     (25, 501),    # 13: Niterói
#     (25, 438),    # 14: Av Atlântica
#     (25, 375),    # 15: Estação Metrô Carioca
#     (25, 312),    # 16: Av Juscelino
#     (25, 249),    # 17: Cofre
#     (25, 186),    # 18: Av Berrini
#     (25, 123),    # 19: Av Faria Lima
#     (25, 25),     # 20: Estacionamento (top-left corner)
    
#     # Top row (21-30): Going right from top-left
#     (123, 25),    # 21: Ipanema
#     (186, 25),    # 22: Sorte
#     (249, 25),    # 23: Leblon
#     (312, 25),    # 24: Copacabana
#     (375, 25),    # 25: Estação Metrô Consolação
#     (438, 25),    # 26: Av Cidade Jardim
#     (501, 25),    # 27: Pacaembu
#     (564, 25),    # 28: Cia Água
#     (627, 25),    # 29: Ibirapuera
#     (690, 25),    # 30: Vá Para Cadeia (top-right corner)
    
#     # Right row (31-39): Going down from top-right
#     (690, 123),   # 31: Barra da Tijuca
#     (690, 186),   # 32: Jardim Botânico
#     (690, 249),   # 33: Cofre
#     (690, 312),   # 34: Lagoa Rodrigo
#     (690, 375),   # 35: Estação Metrô República
#     (690, 438),   # 36: Sorte
#     (690, 501),   # 37: Av Morumbi
#     (690, 564),   # 38: Taxa Riqueza
#     (690, 627),   # 39: Rua Oscar Freire
# ]

print(f"[v0] Generated {len(POSICOES_CASAS_PRECISAS)} position coordinates")
print(f"[v0] Position 0 (Start): {POSICOES_CASAS_PRECISAS[0]}")
print(f"[v0] Position 10 (Jail): {POSICOES_CASAS_PRECISAS[10]}")
print(f"[v0] Position 20 (Free Parking): {POSICOES_CASAS_PRECISAS[20]}")
print(f"[v0] Position 30 (Go to Jail): {POSICOES_CASAS_PRECISAS[30]}")


# Carregando peões (6 jogadores)
PEOES_IMG = [] # Renamed from 'peoes' to avoid confusion with player's pawn list
for i in range(1, 7):
    try:
        peao_img = pygame.transform.scale(carregar_imagem(f'peao{i}.png', alpha=True), (28, 28))
        PEOES_IMG.append(peao_img)
    except:
        # Fallback: criar círculo colorido se imagem não existir
        peao_surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        cores_fallback = [(0, 100, 255), (255, 200, 0), (255, 100, 200), (255, 50, 50), (50, 50, 50), (0, 200, 100)]
        pygame.draw.circle(peao_surf, cores_fallback[i-1], (14, 14), 14)
        PEOES_IMG.append(peao_surf)

# Carregando imagens dos dados (usadas na renderização dos dados)
imagens_dados = []
for i in range(1, 7):
    try:
        dado_img = carregar_imagem(f'dado_{i}.png', alpha=True)
        imagens_dados.append(dado_img)
    except:
        # Fallback: criar representação numérica do dado se imagem não existir
        dado_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.rect(dado_surf, (255, 255, 255), (2, 2, 56, 56))
        pygame.draw.rect(dado_surf, (0, 0, 0), (2, 2, 56, 56), 2)
        texto_dado = FONTE_GRANDE.render(str(i), True, (0, 0, 0))
        texto_rect = texto_dado.get_rect(center=(30, 30))
        dado_surf.blit(texto_dado, texto_rect)
        imagens_dados.append(dado_surf)

# --- Player info display positions (right side) ---
POSICOES_TEXTO_JOGADOR = [
    (LARGURA_TELA - 240, 20),    # Player 1
    (LARGURA_TELA - 240, 130),   # Player 2
    (LARGURA_TELA - 240, 240),   # Player 3
    (LARGURA_TELA - 240, 350),   # Player 4
    (LARGURA_TELA - 240, 460),   # Player 5
    (LARGURA_TELA - 240, 570)    # Player 6
]

BOARD_CENTER_X = BOARD_IMG_WIDTH // 2
BOARD_CENTER_Y = BOARD_IMG_HEIGHT // 2

CORES_JOGADORES_MENU = {
    'a': (80, 120, 200),   # Azul
    'b': (200, 180, 60),   # Amarelo
    'c': (200, 100, 150),  # Rosa
    'd': (200, 60, 60),    # Vermelho
    'e': (60, 60, 60),     # Preto
    'f': (60, 180, 100),   # Verde
}

AJUSTE_POSICAO_PEOES = 0   # Volta para 0 - posição correta sem offset adicional

def calcular_offsets_peoes_dinamicos(jogador_indice, jogadores):
    """
    Calcula o offset dinâmico para uma peça com base na posição e quantos jogadores estão lá.
    Distribui as peças em um padrão baseado no índice do jogador.
    """
    posicao = jogadores[jogador_indice].posicao
    jogadores_na_posicao = [j for j in jogadores if j.posicao == posicao and not j.falido]
    
    if len(jogadores_na_posicao) == 0:
        return OFFSETS_POR_JOGADOR[jogador_indice % len(OFFSETS_POR_JOGADOR)]
    
    # Índice deste jogador dentro dos jogadores na mesma posição
    indice_na_casa = jogadores_na_posicao.index(jogadores[jogador_indice])
    
    offset_x, offset_y = OFFSETS_POR_JOGADOR[indice_na_casa % len(OFFSETS_POR_JOGADOR)]
    
    return (offset_x, offset_y)

# --- Define all game functions BEFORE the main loop ---
def calcular_posicao_construcao(indice_casa):
    """Calcula a posição onde desenhar as construções no tabuleiro"""
    if indice_casa < len(POSICOES_CASAS_PRECISAS): # Use precise positions
        pos_x_board, pos_y_board = POSICOES_CASAS_PRECISAS[indice_casa]
        pos_x = X_TABULEIRO + pos_x_board + AJUSTE_CONSTRUCOES_X
        pos_y = Y_TABULEIRO + pos_y_board + AJUSTE_CONSTRUCOES_Y
        
        # Adjust positions to fit houses/hotels better
        if indice_casa in [0, 10, 20, 30]: # Corners
            return (pos_x - 15, pos_y - 15)
        elif indice_casa in list(range(1, 10)) + list(range(11, 20)) + list(range(21, 30)) + list(range(31, 40)): # Regular squares
             # Determine if it's a horizontal or vertical edge for better offset
            if indice_casa in list(range(1, 10)): # Bottom row
                return (pos_x + 5, pos_y - 25)
            elif indice_casa in list(range(11, 20)): # Left column
                return (pos_x - 30, pos_y + 5)
            elif indice_casa in list(range(21, 30)): # Top row
                return (pos_x + 5, pos_y - 30)
            elif indice_casa in list(range(31, 40)): # Right column
                return (pos_x - 25, pos_y + 5)
    return (0, 0) # Default if out of bounds

def desenhar_construcoes_no_tabuleiro():
    """Draws houses and hotels on properties"""
    if not jogo_backend:
        return
    
    for i, casa in enumerate(jogo_backend.tabuleiro.casas):
        if isinstance(casa, Propriedade) and hasattr(casa, 'casas') and casa.casas > 0:
            pos_x, pos_y = calcular_posicao_construcao(i)
            
            if casa.casas == 5:  # Hotel
                # Draw a red square for the hotel
                pygame.draw.rect(screen, (255, 0, 0), (pos_x, pos_y, 20, 20))
                # Render 'H' for hotel
                texto_hotel = FONTE_PEQUENA.render("H", True, (255, 255, 255))
                screen.blit(texto_hotel, (pos_x + 5, pos_y + 2))
            else:  # Houses
                largura_casa = 4
                espacamento = 1
                for j in range(casa.casas):
                    pygame.draw.rect(screen, (0, 200, 0), 
                                   (pos_x + j * (largura_casa + espacamento), pos_y, largura_casa, 10))

def desenhar_menu_construcao():
    """Desenha o menu de construção (casas/hotéis)"""
    if not mostrar_menu_construcao:
        return
    
    jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
    
    menu_width = 700
    menu_height = 550
    # </CHANGE> Usando AJUSTE_CONSTRUCOES para reposicionar menu à direita
    menu_x = BOARD_CENTER_X - menu_width // 2 + AJUSTE_CONSTRUCOES_X
    menu_y = BOARD_CENTER_Y - menu_height // 2 + AJUSTE_CONSTRUCOES_Y
    
    pygame.draw.rect(screen, CORES_JOGADORES_MENU.get(jogador_atual.nome, (120, 80, 80)), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (200, 200, 255), (menu_x, menu_y, menu_width, menu_height), 3)
    
    titulo = FONTE_GRANDE.render("Construir", True, (255, 255, 255))
    screen.blit(titulo, (menu_x + menu_width // 2 - 60, menu_y + 15))
    
    botao_fechar_rect = pygame.Rect(menu_x + menu_width - 40, menu_y + 10, 35, 35)
    pygame.draw.rect(screen, (150, 50, 50), botao_fechar_rect)
    pygame.draw.rect(screen, (255, 100, 100), botao_fechar_rect, 2)
    texto_fechar = FONTE_MEDIA.render("X", True, (255, 255, 255))
    screen.blit(texto_fechar, (botao_fechar_rect.x + 10, botao_fechar_rect.y + 5))
    desenhar_menu_construcao.botao_fechar_rect = botao_fechar_rect
    
    # List properties where player can build
    y_offset = menu_y + 60
    desenhar_menu_construcao.botoes_construir = []
    
    # Group properties by color group
    grupos_monopolio = {}
    for prop in jogador_atual.propriedades:
        if hasattr(prop, 'grupo_cor') and prop.grupo_cor not in ['METRÔ', 'SERVIÇO']:
            if prop.grupo_cor not in grupos_monopolio:
                grupos_monopolio[prop.grupo_cor] = []
            grupos_monopolio[prop.grupo_cor].append(prop)
    
    # Check which groups are monopolies
    propriedades_construiveis = []
    for grupo, props in grupos_monopolio.items():
        props_grupo_total = jogo_backend.tabuleiro.listar_propriedades_por_grupo(grupo)
        tem_monopolio = len(props) == len(props_grupo_total)
        
        if tem_monopolio:
            propriedades_construiveis.extend(props)
    
    if not propriedades_construiveis:
        texto_aviso = FONTE_MEDIA.render("Você precisa ter o monopólio", True, (255, 200, 100))
        screen.blit(texto_aviso, (menu_x + 100, y_offset))
        texto_aviso2 = FONTE_MEDIA.render("de um grupo para construir!", True, (255, 200, 100))
        screen.blit(texto_aviso2, (menu_x + 100, y_offset + 25))
        return
    
    for prop in propriedades_construiveis:
        pode, mensagem = jogo_backend.gestor_construcao.pode_construir(jogador_atual, prop)
        
        # Property name and status
        casas_txt = ""
        if prop.casas == 0:
            casas_txt = "Sem casas"
        elif prop.casas == 5:
            casas_txt = "Hotel"
        else:
            casas_txt = f"{prop.casas} casa(s)"
        
        cor_texto = (255, 255, 255) if pode else (150, 150, 150)
        texto_prop = FONTE_PEQUENA.render(f"{prop.nome}: {casas_txt}", True, cor_texto)
        screen.blit(texto_prop, (menu_x + 25, y_offset))
        
        if pode and prop.casas < 5:
            botao_rect = pygame.Rect(menu_x + menu_width - 160, y_offset - 5, 140, 32)
            
            mouse_pos = pygame.mouse.get_pos()
            cor_botao = (50, 150, 50) if botao_rect.collidepoint(mouse_pos) else (30, 100, 30)
            
            pygame.draw.rect(screen, cor_botao, botao_rect)
            pygame.draw.rect(screen, (100, 255, 100), botao_rect, 2)
            
            custo = jogo_backend.gestor_construcao.CUSTO_CONSTRUCAO.get(prop.grupo_cor, 100)
            texto_construir = FONTE_PEQUENA.render(f"Construir R${custo}", True, (255, 255, 255))
            screen.blit(texto_construir, (botao_rect.x + 8, botao_rect.y + 8))
            
            desenhar_menu_construcao.botoes_construir.append((botao_rect, prop))
        elif not pode:
            texto_status = FONTE_PEQUENA.render(mensagem[:30], True, (255, 100, 100))
            screen.blit(texto_status, (menu_x + 25, y_offset + 18))
        
        y_offset += 50
        
        if y_offset > menu_y + menu_height - 60:
            break

def desenhar_menu_propostas():
    """Desenha o menu de propostas de troca"""
    if not mostrar_menu_proposta:
        return
    menu_width = 700
    menu_height = 550
    # </CHANGE> Usando AJUSTE_CONSTRUCOES para reposicionar menu à direita
    menu_x = BOARD_CENTER_X - menu_width // 2 + AJUSTE_CONSTRUCOES_X
    menu_y = BOARD_CENTER_Y - menu_height // 2 + AJUSTE_CONSTRUCOES_Y
    
    pygame.draw.rect(screen, CORES_JOGADORES_MENU.get(jogo_backend.jogadores[jogo_backend.indice_turno_atual].nome, (120, 80, 80)), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (255, 200, 200), (menu_x, menu_y, menu_width, menu_height), 3)
    
    titulo = FONTE_GRANDE.render("Gerenciar Propriedades", True, (255, 255, 255))
    screen.blit(titulo, (menu_x + 50, menu_y + 10))
    
    botao_fechar_rect = pygame.Rect(menu_x + menu_width - 40, menu_y + 10, 35, 35)
    pygame.draw.rect(screen, (150, 50, 50), botao_fechar_rect)
    pygame.draw.rect(screen, (255, 100, 100), botao_fechar_rect, 2)
    texto_fechar = FONTE_MEDIA.render("X", True, (255, 255, 255))
    screen.blit(texto_fechar, (botao_fechar_rect.x + 10, botao_fechar_rect.y + 5))
    desenhar_menu_propostas.botao_fechar_rect = botao_fechar_rect
    
    jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
    y_offset = menu_y + 60
    
    if not jogador_atual.propriedades:
        texto_sem_props = FONTE_MEDIA.render("Você não possui propriedades", True, (255, 200, 100))
        screen.blit(texto_sem_props, (menu_x + 60, y_offset))
        return
    
    desenhar_menu_propostas.botoes_jogadores = []
    
    texto_info = FONTE_PEQUENA.render("Suas propriedades:", True, (255, 255, 255))
    screen.blit(texto_info, (menu_x + 15, y_offset))
    y_offset += 30
    
    for prop in jogador_atual.propriedades:
        # Property name
        texto_prop = FONTE_PEQUENA.render(f"• {prop.nome}", True, (200, 200, 255))
        screen.blit(texto_prop, (menu_x + 20, y_offset))
        
        # Property value
        if hasattr(prop, 'preco_compra'):
            texto_valor = FONTE_PEQUENA.render(f"R${prop.preco_compra}", True, (150, 255, 150))
            screen.blit(texto_valor, (menu_x + menu_width - 100, y_offset))
        
        y_offset += 25
        
        if y_offset > menu_y + menu_height - 60:
            break
    
    y_offset = menu_y + menu_height - 100
    texto_trocar = FONTE_MEDIA.render("Propor troca com:", True, (255, 255, 255))
    screen.blit(texto_trocar, (menu_x + 15, y_offset))
    y_offset += 30
    
    x_botao = menu_x + 15
    for i, jogador in enumerate(jogo_backend.jogadores):
        if i == jogo_backend.indice_turno_atual or jogador.falido:
            continue
        
        botao_rect = pygame.Rect(x_botao, y_offset, 90, 30)
        
        mouse_pos = pygame.mouse.get_pos()
        cor_botao = (80, 120, 200) if botao_rect.collidepoint(mouse_pos) else (50, 80, 150)
        
        pygame.draw.rect(screen, cor_botao, botao_rect)
        pygame.draw.rect(screen, (150, 200, 255), botao_rect, 2)
        
        texto_jogador = FONTE_PEQUENA.render(jogador.nome, True, (255, 255, 255))
        screen.blit(texto_jogador, (botao_rect.x + 15, botao_rect.y + 8))
        
        desenhar_menu_propostas.botoes_jogadores.append((botao_rect, jogador))
        
        x_botao += 100
        if x_botao > menu_x + menu_width - 90:
            x_botao = menu_x + 15
            y_offset += 35

def desenhar_menu_compra():
    """Desenha o menu de compra de propriedades"""
    menu_width = 550
    menu_height = 400
    # </CHANGE> Usando AJUSTE_CONSTRUCOES para reposicionar menu à direita
    menu_x = BOARD_CENTER_X - menu_width // 2 + AJUSTE_CONSTRUCOES_X
    menu_y = BOARD_CENTER_Y - menu_height // 2 + AJUSTE_CONSTRUCOES_Y
    
    # Draw background
    pygame.draw.rect(screen, CORES_JOGADORES_MENU.get(jogo_backend.jogadores[jogo_backend.indice_turno_atual].nome, (120, 80, 80)), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (150, 100, 100), (menu_x, menu_y, menu_width, menu_height), 3)
    
    # Title
    texto_titulo = FONTE_GRANDE.render("Comprar Propriedade", True, (255, 255, 255))
    text_rect = texto_titulo.get_rect()
    text_rect.center = (menu_x + menu_width // 2, menu_y + 30)
    screen.blit(texto_titulo, text_rect)
    
    fechar_rect = pygame.Rect(menu_x + menu_width - 40, menu_y + 5, 35, 35)
    mouse_pos = pygame.mouse.get_pos()
    cor_fechar = (255, 100, 100) if fechar_rect.collidepoint(mouse_pos) else (200, 80, 80)
    pygame.draw.rect(screen, cor_fechar, fechar_rect)
    pygame.draw.rect(screen, (255, 150, 150), fechar_rect, 2)
    texto_x = FONTE_MEDIA.render("X", True, (255, 255, 255))
    texto_x_rect = texto_x.get_rect()
    texto_x_rect.center = fechar_rect.center
    screen.blit(texto_x, texto_x_rect)
    desenhar_menu_compra.fechar_rect = fechar_rect
    
    jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
    casa_atual = jogo_backend.tabuleiro.casas[jogador_atual.posicao]
    
    # Property info
    y_offset = menu_y + 60
    
    if isinstance(casa_atual, Propriedade):
        texto_nome = FONTE_MEDIA.render(casa_atual.nome, True, (255, 255, 255))
        screen.blit(texto_nome, (menu_x + 20, y_offset))
        y_offset += 35
        
        if hasattr(casa_atual, 'proprietario') and casa_atual.proprietario:
            texto_dono = FONTE_MEDIA.render(f"Proprietário: {casa_atual.proprietario.nome}", True, (255, 200, 100))
            screen.blit(texto_dono, (menu_x + 20, y_offset))
            y_offset += 30
            texto_info = FONTE_PEQUENA.render("Esta propriedade já tem dono!", True, (255, 100, 100))
            screen.blit(texto_info, (menu_x + 20, y_offset))
        else:
            texto_preco = FONTE_MEDIA.render(f"Preço: R${casa_atual.preco_compra}", True, (150, 255, 150))
            screen.blit(texto_preco, (menu_x + 20, y_offset))
            y_offset += 35
            
            saldo_jogador = jogo_backend.banco.consultar_saldo(jogador_atual.nome)
            texto_saldo = FONTE_PEQUENA.render(f"Seu saldo: R${saldo_jogador}", True, (200, 200, 255))
            screen.blit(texto_saldo, (menu_x + 20, y_offset))
            y_offset += 50
            
            if saldo_jogador >= casa_atual.preco_compra:
                botao_comprar_rect = pygame.Rect(menu_x + (menu_width - 220) // 2, y_offset, 220, 45)
                
                mouse_pos = pygame.mouse.get_pos()
                cor_botao = (50, 200, 50) if botao_comprar_rect.collidepoint(mouse_pos) else (30, 150, 30)
                
                pygame.draw.rect(screen, cor_botao, botao_comprar_rect)
                pygame.draw.rect(screen, (100, 255, 100), botao_comprar_rect, 2)
                
                texto_comprar = FONTE_MEDIA.render(f"COMPRAR R${casa_atual.preco_compra}", True, (255, 255, 255))
                texto_rect = texto_comprar.get_rect()
                texto_rect.center = (botao_comprar_rect.centerx, botao_comprar_rect.centery)
                screen.blit(texto_comprar, texto_rect)
                
                desenhar_menu_compra.botao_comprar_rect = botao_comprar_rect
            else:
                texto_sem_saldo = FONTE_MEDIA.render("Saldo insuficiente!", True, (255, 100, 100))
                screen.blit(texto_sem_saldo, (menu_x + 80, y_offset))
    else:
        texto_nao_propriedade = FONTE_MEDIA.render("Esta casa não pode ser comprada", True, (255, 200, 100))
        screen.blit(texto_nao_propriedade, (menu_x + 40, y_offset))

def desenhar_painel_feedback():
    """Desenha o painel lateral de feedback com histórico de rodadas"""
    pygame.draw.rect(screen, (20, 30, 60), (10, 80, 240, 420))
    pygame.draw.rect(screen, (100, 150, 255), (10, 80, 240, 420), 2)
    
    titulo = FONTE_PEQUENA.render("Historico", True, (100, 200, 255))
    screen.blit(titulo, (15, 85))
    
    y_offset = 110
    max_visible = 13
    start_index = max(0, len(mensagens_feedback) - max_visible - scroll_feedback)
    
    for i, msg in enumerate(mensagens_feedback[start_index:start_index + max_visible]):
        cor = (150, 200, 255) if i % 2 == 0 else (100, 150, 200)
        texto_msg = FONTE_PEQUENA.render(msg[:26], True, cor)
        screen.blit(texto_msg, (15, y_offset))
        y_offset += 22
    
    if len(mensagens_feedback) > max_visible:
        pygame.draw.rect(screen, (150, 150, 200), (245, 110, 3, 360))
        scroll_pos = int((scroll_feedback / len(mensagens_feedback)) * 360)
        pygame.draw.rect(screen, (200, 200, 255), (245, 110 + scroll_pos, 3, 40))

def adicionar_mensagem_log(mensagem):
    """Adiciona uma mensagem ao log de mensagens"""
    global mensagens_log
    mensagens_log.append(mensagem)
    if len(mensagens_log) > MAX_MENSAGENS_LOG:
        mensagens_log.pop(0)

def adicionar_mensagem_feedback(mensagem):
    """Adiciona uma mensagem ao feedback da rodada"""
    global mensagens_feedback
    mensagens_feedback.append(mensagem)
    if len(mensagens_feedback) > MAX_MENSAGENS_FEEDBACK:
        mensagens_feedback.pop(0)

def desenhar_menu_turno():
    """Desenha menu de opções de turno com botões de texto"""
    if not MOSTRAR_HUD_MENU:
        return
    
    menu_x = HUD_MENU_X + AJUSTE_HUD_X
    menu_y = HUD_MENU_Y + AJUSTE_HUD_Y
    
    # Clamp position to screen boundaries
    menu_x = max(10, min(menu_x, 1600 - HUD_MENU_WIDTH - 10))
    menu_y = max(10, min(menu_y, 900 - HUD_MENU_HEIGHT - 10))
    
    menu_width = HUD_MENU_WIDTH
    menu_height = HUD_MENU_HEIGHT
    
    jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
    cor_fundo = CORES_JOGADORES_MENU.get(jogador_atual.nome, (40, 60, 100))
    cor_borda = tuple(min(255, c + 50) for c in cor_fundo)
    
    pygame.draw.rect(screen, cor_fundo, (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, cor_borda, (menu_x, menu_y, menu_width, menu_height), 2)
    
    turno_texto = FONTE_MEDIA.render(f"Turno: {jogador_atual.nome}", True, (255, 255, 255))
    text_rect = turno_texto.get_rect()
    text_rect.center = (menu_x + menu_width // 2, menu_y + 15)
    screen.blit(turno_texto, text_rect)
    
    y_botao = menu_y + 40
    altura_botao = 35
    largura_botao = 195
    x_botao = menu_x + 10
    
    # Botão Lançar Dados - ativo apenas se é turno do jogador e não é turno de bot
    if estado_turno == "ANTES_LANCAR_DADOS" and not turno_bot_em_execucao:
        desenhar_menu_turno.botao_lancar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        # Colorido se não bloqueado, cinza se bloqueado
        cor_fundo = (50, 120, 50) if not botoes_bloqueados else (80, 80, 80)
        cor_borda = (100, 200, 100) if not botoes_bloqueados else (120, 120, 120)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_lancar = FONTE_PEQUENA.render("LANÇAR DADOS", True, (255, 255, 255))
        screen.blit(texto_lancar, (x_botao + 40, y_botao + 8))
        y_botao += 50
    else:
        # Botão Lançar Dados - sempre desenhado mas cinza quando desabilitado
        desenhar_menu_turno.botao_lancar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (80, 80, 80)
        cor_borda = (120, 120, 120)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_lancar = FONTE_PEQUENA.render("LANÇAR DADOS", True, (150, 150, 150))
        screen.blit(texto_lancar, (x_botao + 40, y_botao + 8))
        y_botao += 50
    
    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao:
        casa_atual = jogo_backend.tabuleiro.casas[jogador_atual.posicao]
        
        if isinstance(casa_atual, Propriedade) and not casa_atual.proprietario:
            desenhar_menu_turno.botao_comprar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
            cor_fundo = (100, 150, 50) if not botoes_bloqueados else (100, 100, 50)
            cor_borda = (200, 200, 100) if not botoes_bloqueados else (150, 150, 100)
            pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
            pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
            texto_comprar = FONTE_PEQUENA.render("COMPRAR", True, (255, 255, 255))
            screen.blit(texto_comprar, (x_botao + 60, y_botao + 8))
            y_botao += 50
        else:
            # Botão Comprar desabilitado (cinza)
            desenhar_menu_turno.botao_comprar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
            cor_fundo = (80, 80, 80)
            cor_borda = (120, 120, 120)
            pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
            pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
            texto_comprar = FONTE_PEQUENA.render("COMPRAR", True, (150, 150, 150))
            screen.blit(texto_comprar, (x_botao + 60, y_botao + 8))
            y_botao += 50
    elif estado_turno == "APOS_LANCAR_DADOS" or turno_bot_em_execucao:
        # Botão Comprar desabilitado durante turno de bot
        desenhar_menu_turno.botao_comprar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (80, 80, 80)
        cor_borda = (120, 120, 120)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_comprar = FONTE_PEQUENA.render("COMPRAR", True, (150, 150, 150))
        screen.blit(texto_comprar, (x_botao + 60, y_botao + 8))
        y_botao += 50
    
    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao and len(jogador_atual.propriedades) > 0:
        desenhar_menu_turno.botao_propriedades_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (100, 80, 50) if not botoes_bloqueados else (100, 80, 50)
        cor_borda = (200, 150, 100) if not botoes_bloqueados else (150, 120, 80)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_propriedades = FONTE_PEQUENA.render("PROPRIEDADES", True, (255, 255, 255))
        screen.blit(texto_propriedades, (x_botao + 35, y_botao + 8))
        y_botao += 50
    elif estado_turno == "APOS_LANCAR_DADOS" and len(jogador_atual.propriedades) > 0:
        # Propriedades desabilitado durante bot turn
        desenhar_menu_turno.botao_propriedades_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (80, 80, 80)
        cor_borda = (120, 120, 120)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_propriedades = FONTE_PEQUENA.render("PROPRIEDADES", True, (150, 150, 150))
        screen.blit(texto_propriedades, (x_botao + 35, y_botao + 8))
        y_botao += 50
    
    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao and len(jogador_atual.propriedades) > 0:
        desenhar_menu_turno.botao_negociar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (100, 50, 100) if not botoes_bloqueados else (100, 50, 100)
        cor_borda = (200, 100, 200) if not botoes_bloqueados else (150, 80, 150)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_negociar = FONTE_PEQUENA.render("NEGOCIAR", True, (255, 255, 255))
        screen.blit(texto_negociar, (x_botao + 50, y_botao + 8))
        y_botao += 50
    elif estado_turno == "APOS_LANCAR_DADOS" and len(jogador_atual.propriedades) > 0:
        # Negociar desabilitado durante bot turn
        desenhar_menu_turno.botao_negociar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (80, 80, 80)
        cor_borda = (120, 120, 120)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_negociar = FONTE_PEQUENA.render("NEGOCIAR", True, (150, 150, 150))
        screen.blit(texto_negociar, (x_botao + 50, y_botao + 8))
        y_botao += 50
    
    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao:
        desenhar_menu_turno.botao_passar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (150, 50, 50) if not botoes_bloqueados else (100, 50, 50)
        cor_borda = (200, 100, 100) if not botoes_bloqueados else (150, 80, 80)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_passar = FONTE_PEQUENA.render("PASSAR A VEZ", True, (255, 255, 255))
        screen.blit(texto_passar, (x_botao + 50, y_botao + 8))
    else:
        # Passar desabilitado durante turno de bot
        desenhar_menu_turno.botao_passar_rect = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        cor_fundo = (80, 80, 80)
        cor_borda = (120, 120, 120)
        pygame.draw.rect(screen, cor_fundo, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(screen, cor_borda, (x_botao, y_botao, largura_botao, altura_botao), 2)
        texto_passar = FONTE_PEQUENA.render("PASSAR A VEZ", True, (150, 150, 150))
        screen.blit(texto_passar, (x_botao + 50, y_botao + 8))

def desenhar_popup_carta():
    """Desenha um pop-up com a carta puxada"""
    global tempo_mensagem_carta, mostrar_popup_carta
    
    if not mostrar_popup_carta or tempo_mensagem_carta <= 0:
        mostrar_popup_carta = False
        return
    
    # Dimensões do pop-up
    popup_width = 600
    popup_height = 250
    popup_x = (LARGURA_TELA - popup_width) // 2
    popup_y = (ALTURA_TELA - popup_height) // 2
    
    # Fundo do pop-up com transparência
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
    overlay.set_alpha(100)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Caixa do pop-up
    pygame.draw.rect(screen, (40, 60, 100), (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(screen, (100, 200, 255), (popup_x, popup_y, popup_width, popup_height), 3)
    
    # Título
    titulo = FONTE_GRANDE.render("INTERAÇÃO EM ANDAMENTO!", True, (255, 200, 50))
    titulo_rect = titulo.get_rect()
    titulo_rect.center = (LARGURA_TELA // 2, popup_y + 25)
    screen.blit(titulo, titulo_rect)
    
    # Mensagem da carta (quebra em múltiplas linhas)
    linhas = []
    palavras = mensagem_carta_atual.split()
    linha_atual = ""
    
    for palavra in palavras:
        if len(linha_atual + " " + palavra) > 50:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
        else:
            linha_atual = (linha_atual + " " + palavra).strip()
    
    if linha_atual:
        linhas.append(linha_atual)
    
    y_texto = popup_y + 70
    for linha in linhas:
        texto = FONTE_MEDIA.render(linha, True, (200, 220, 255))
        texto_rect = texto.get_rect()
        texto_rect.center = (LARGURA_TELA // 2, y_texto)
        screen.blit(texto, texto_rect)
        y_texto += 35
    
    # Barra de progresso
    barra_width = 500
    barra_height = 8
    barra_x = (LARGURA_TELA - barra_width) // 2
    barra_y = popup_y + popup_height - 30
    
    pygame.draw.rect(screen, (100, 100, 100), (barra_x, barra_y, barra_width, barra_height))
    
    if tempo_mensagem_carta > 0:
        progresso = (tempo_mensagem_carta / 300) * barra_width
        pygame.draw.rect(screen, (100, 200, 255), (barra_x, barra_y, max(0, progresso), barra_height))
    
    tempo_mensagem_carta -= 1

# --- Início das atualizações para desenhar_painel_propriedades_jogador ---
def desenhar_painel_propriedades_jogador(jogador):
    """
    Renderiza um painel com as propriedades do jogador ao clicar em seu nome.
    Propriedades agrupadas por cor com ícones coloridos.
    """
    if not jogador or not jogador.propriedades:
        return
    
    CORES_PROPRIEDADES = {
        "Marrom": (139, 69, 19),
        "Azul Claro": (100, 149, 237),
        "Rosa": (255, 192, 203),
        "Laranja": (255, 165, 0),
        "Vermelho": (220, 20, 60),
        "Amarelo": (255, 255, 0),
        "Verde": (34, 139, 34),
        "Azul Escuro": (25, 25, 112),
        "METRÔ": (128, 128, 128),
        "SERVIÇO": (200, 100, 50),
    }
    
    propriedades_por_grupo = {}
    for prop in jogador.propriedades:
        grupo = getattr(prop, 'grupo_cor', 'Sem Grupo')
        if grupo not in propriedades_por_grupo:
            propriedades_por_grupo[grupo] = []
        propriedades_por_grupo[grupo].append(prop)
    
    # Calcular altura do painel
    altura_estimada = 60  # Header
    for grupo, props in propriedades_por_grupo.items():
        altura_estimada += 30 + (len(props) * 28)  # Group header + properties
    
    painel_height = min(600, max(200, altura_estimada))
    painel_width = 400
    painel_x = (LARGURA_TELA - painel_width) // 2
    painel_y = (ALTURA_TELA - painel_height) // 2
    
    # Draw background with transparency
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
    overlay.set_alpha(100)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Draw panel
    pygame.draw.rect(screen, (40, 40, 80), (painel_x, painel_y, painel_width, painel_height))
    pygame.draw.rect(screen, (150, 150, 200), (painel_x, painel_y, painel_width, painel_height), 3)
    
    # Title
    titulo = FONTE_GRANDE.render(f"Propriedades de {jogador.nome}", True, (200, 255, 200))
    titulo_rect = titulo.get_rect()
    titulo_rect.center = (painel_x + painel_width // 2, painel_y + 15)
    screen.blit(titulo, titulo_rect)
    
    # Close button
    fechar_rect = pygame.Rect(painel_x + painel_width - 35, painel_y + 5, 30, 30)
    mouse_pos = pygame.mouse.get_pos()
    cor_fechar = (255, 100, 100) if fechar_rect.collidepoint(mouse_pos) else (200, 80, 80)
    pygame.draw.rect(screen, cor_fechar, fechar_rect)
    texto_x = FONTE_PEQUENA.render("X", True, (255, 255, 255))
    texto_x_rect = texto_x.get_rect()
    texto_x_rect.center = fechar_rect.center
    screen.blit(texto_x, texto_x_rect)
    desenhar_painel_propriedades_jogador.fechar_rect = fechar_rect
    
    y_offset = painel_y + 45
    
    # Draw properties grouped by color
    for grupo, props in sorted(propriedades_por_grupo.items()):
        cor_grupo = CORES_PROPRIEDADES.get(grupo, (128, 128, 128))
        
        # Group title with colored background
        pygame.draw.rect(screen, cor_grupo, (painel_x + 10, y_offset, painel_width - 20, 25))
        texto_grupo = FONTE_PEQUENA.render(grupo, True, (255, 255, 255))
        screen.blit(texto_grupo, (painel_x + 15, y_offset + 5))
        y_offset += 28
        
        for prop in props:
            # Draw colored dot icon
            pygame.draw.circle(screen, cor_grupo, (painel_x + 20, y_offset + 10), 6)
            
            # Property name
            texto_prop = FONTE_PEQUENA.render(prop.nome, True, (200, 220, 255))
            screen.blit(texto_prop, (painel_x + 35, y_offset + 4))
            
            y_offset += 28
# --- Fim das atualizações para desenhar_painel_propriedades_jogador ---

def desenhar_menu_negociacao():
    """Desenha o menu para negociação de propriedades"""
    if not mostrar_menu_negociacao:
        return
    
    menu_width = 700
    menu_height = 550
    menu_x = BOARD_CENTER_X - menu_width // 2 + AJUSTE_CONSTRUCOES_X
    menu_y = BOARD_CENTER_Y - menu_height // 2 + AJUSTE_CONSTRUCOES_Y
    
    pygame.draw.rect(screen, (50, 50, 100), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (150, 150, 200), (menu_x, menu_y, menu_width, menu_height), 3)
    
    titulo = FONTE_GRANDE.render("Negociar Propriedades", True, (200, 255, 200))
    screen.blit(titulo, (menu_x + 30, menu_y + 10))
    
    botao_fechar_rect = pygame.Rect(menu_x + menu_width - 40, menu_y + 10, 35, 35)
    pygame.draw.rect(screen, (150, 50, 50), botao_fechar_rect)
    pygame.draw.rect(screen, (255, 100, 100), botao_fechar_rect, 2)
    texto_fechar = FONTE_MEDIA.render("X", True, (255, 255, 255))
    screen.blit(texto_fechar, (botao_fechar_rect.x + 10, botao_fechar_rect.y + 5))
    desenhar_menu_negociacao.fechar_rect = botao_fechar_rect
    
    # Players to negotiate with
    jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
    desenhar_menu_negociacao.player_buttons = []
    x_player_btn = menu_x + 20
    y_player_btn = menu_y + 55
    
    screen.blit(FONTE_MEDIA.render("Negociar com:", True, (255, 255, 255)), (menu_x + 20, y_player_btn - 20))
    
    for i, jogador in enumerate(jogo_backend.jogadores):
        if jogador == jogador_atual or jogador.falido:
            continue
        
        btn_rect = pygame.Rect(x_player_btn, y_player_btn, 90, 30)
        mouse_pos = pygame.mouse.get_pos()
        cor_btn = (80, 120, 200) if btn_rect.collidepoint(mouse_pos) else (50, 80, 150)
        pygame.draw.rect(screen, cor_btn, btn_rect)
        pygame.draw.rect(screen, (150, 200, 255), btn_rect, 2)
        
        txt = FONTE_PEQUENA.render(jogador.nome, True, (255, 255, 255))
        screen.blit(txt, (btn_rect.x + 10, btn_rect.y + 5))
        desenhar_menu_negociacao.player_buttons.append((btn_rect, jogador))
        
        x_player_btn += 100
        if x_player_btn > menu_x + menu_width - 90:
            x_player_btn = menu_x + 20
            y_player_btn += 35
    
    # If a player is selected, show their properties and yours
    if hasattr(desenhar_menu_negociacao, 'jogador_selecionado_para_negociacao'):
        jogador_a_trocar = desenhar_menu_negociacao.jogador_selecionado_para_negociacao
        
        y_offset = y_player_btn + 45
        
        # Your properties
        screen.blit(FONTE_MEDIA.render("Suas Propriedades:", True, (255, 255, 255)), (menu_x + 20, y_offset))
        y_offset += 30
        
        desenhar_menu_negociacao.sua_propriedades_buttons = []
        for i, prop in enumerate(jogador_atual.propriedades):
            prop_rect = pygame.Rect(menu_x + 25, y_offset + i * 28, menu_width - 70, 25)
            mouse_pos = pygame.mouse.get_pos()
            cor_prop = (100, 150, 100) if prop_rect.collidepoint(mouse_pos) else (50, 80, 50)
            
            if hasattr(desenhar_menu_negociacao, 'sua_prop_selecionada') and desenhar_menu_negociacao.sua_prop_selecionada == prop:
                cor_prop = (150, 200, 100) # Highlight selected
            
            pygame.draw.rect(screen, cor_prop, prop_rect)
            pygame.draw.rect(screen, (150, 255, 150), prop_rect, 2)
            txt = FONTE_PEQUENA.render(f"{prop.nome} (R${prop.preco_compra})", True, (255, 255, 255))
            screen.blit(txt, (prop_rect.x + 5, prop_rect.y + 5))
            desenhar_menu_negociacao.sua_propriedades_buttons.append((prop_rect, prop))
        
        y_offset += len(jogador_atual.propriedades) * 28 + 30
        
        # Other player's properties
        screen.blit(FONTE_MEDIA.render(f"{jogador_a_trocar.nome}'s Propriedades:", True, (255, 255, 255)), (menu_x + 20, y_offset))
        y_offset += 30
        
        desenhar_menu_negociacao.outra_propriedades_buttons = []
        for i, prop in enumerate(jogador_a_trocar.propriedades):
            prop_rect = pygame.Rect(menu_x + 25, y_offset + i * 28, menu_width - 70, 25)
            mouse_pos = pygame.mouse.get_pos()
            cor_prop = (100, 100, 150) if prop_rect.collidepoint(mouse_pos) else (50, 50, 80)
            pygame.draw.rect(screen, cor_prop, prop_rect)
            pygame.draw.rect(screen, (150, 150, 255), prop_rect, 2)
            txt = FONTE_PEQUENA.render(f"{prop.nome} (R${prop.preco_compra})", True, (255, 255, 255))
            screen.blit(txt, (prop_rect.x + 5, prop_rect.y + 5))
            desenhar_menu_negociacao.outra_propriedades_buttons.append((prop_rect, prop))
        
        # Button to propose trade (currently directly trades if clicked)
        x_trade_btn = menu_x + menu_width - 160
        y_trade_btn = menu_y + menu_height - 50
        
        if hasattr(desenhar_menu_negociacao, 'sua_prop_selecionada') and desenhar_menu_negociacao.sua_prop_selecionada:
            trade_btn_rect = pygame.Rect(x_trade_btn, y_trade_btn, 140, 35)
            mouse_pos = pygame.mouse.get_pos()
            cor_trade_btn = (150, 100, 50) if trade_btn_rect.collidepoint(mouse_pos) else (100, 80, 40)
            pygame.draw.rect(screen, cor_trade_btn, trade_btn_rect)
            pygame.draw.rect(screen, (200, 150, 100), trade_btn_rect, 2)
            
            txt_trade = FONTE_PEQUENA.render("Propor Troca", True, (255, 255, 255))
            screen.blit(txt_trade, (trade_btn_rect.x + 15, trade_btn_rect.y + 8))
            desenhar_menu_negociacao.propor_troca_rect = trade_btn_rect

def mouse_sobre_botao(x, y, largura, altura):
    """Verifica se o mouse está sobre um botão retangular"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return x < mouse_x < x + largura and y < mouse_y < y + altura

# --- Variáveis Globais do Jogo ---
running = True
jogo_backend = None
estado_jogo = "MENU" # MENU, INICIO_TURNO, FIM_JOGO
estado_turno = "ANTES_LANCAR_DADOS"
mostrar_menu_compra = False
mostrar_menu_proposta = False
mostrar_menu_construcao = False
tempo_bloqueio_botoes = 0  # Timer to block buttons for 1 second (60 frames at 60fps)
botoes_bloqueados = False
turno_bot_em_execucao = False  # Flag to disable HUD during bot turns

mostrar_menu_negociacao = False
jogador_negociacao_selecionado = None # Player to negotiate with
proposta_negociacao_ativa = None # Not implemented yet

mostrar_painel_propriedades = False
jogador_selecionado_para_info = None
mostrar_popup_carta = False
mensagem_carta_atual = ""
tempo_mensagem_carta = 0
mensagens_log = []
mensagens_feedback = []
MAX_MENSAGENS_LOG = 100
MAX_MENSAGENS_FEEDBACK = 30
scroll_feedback = 0
dado1_valor = None
dado2_valor = None
dados_lancados = False
# botoes_desabilitados = False # Removed based on updates
# tempo_desabilitacao = 0     # Removed based on updates

clock = pygame.time.Clock()

menu_inicial = MenuInicial(screen)
tela_fim_jogo = None

def atualizar_bloqueio_botoes():
    """
    Atualiza o estado de bloqueio dos botões.
    Desabilita por 1 segundo após o jogador clicar em LANÇAR DADOS.
    """
    global tempo_bloqueio_botoes, botoes_bloqueados
    
    if tempo_bloqueio_botoes > 0:
        tempo_bloqueio_botoes -= 1
        botoes_bloqueados = True
    else:
        botoes_bloqueados = False

# --- MAIN GAME LOOP ---
while running:
    # Removed botoes_desabilitados check from event handling
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        # --- PROCESSAMENTO POR ESTADO ---
        if estado_jogo == "MENU":
            resultado = menu_inicial.handle_events(event)
            if resultado:
                acao, nomes_jogadores = resultado
                if acao == "INICIAR_JOGO":
                    jogo_backend = Jogo(nomes_jogadores)
                    estado_jogo = "INICIO_TURNO"
                    scroll_feedback = 0
                    mensagens_feedback = []
                    mensagens_log = []
        
        elif estado_jogo == "FIM_JOGO":
            resultado = tela_fim_jogo.handle_events(event)
            if resultado == "NOVO_JOGO":
                menu_inicial = MenuInicial(screen)
                estado_jogo = "MENU"
                mensagens_log = []
                mensagens_feedback = []
                scroll_feedback = 0
            elif resultado == "SAIR":
                running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f"Clique do mouse em: {event.pos}")
            
            if estado_jogo == "INICIO_TURNO" and not mostrar_menu_compra and not mostrar_menu_proposta and not mostrar_menu_construcao and not mostrar_menu_negociacao:
                for i, (pos_x, pos_y) in enumerate(POSICOES_TEXTO_JOGADOR):
                    if i < len(jogo_backend.jogadores):
                        rect_jogador = pygame.Rect(pos_x, pos_y, 220, 100)
                        if rect_jogador.collidepoint(event.pos):
                            jogador_selecionado_para_info = jogo_backend.jogadores[i]
                            mostrar_painel_propriedades = True
                            break
            
            if mostrar_painel_propriedades and hasattr(desenhar_painel_propriedades_jogador, 'fechar_rect'):
                if desenhar_painel_propriedades_jogador.fechar_rect.collidepoint(event.pos):
                    mostrar_painel_propriedades = False
                    jogador_selecionado_para_info = None
            
            if MOSTRAR_HUD_MENU and estado_jogo == "INICIO_TURNO":
                if hasattr(desenhar_menu_turno, 'botao_lancar_rect') and \
                   desenhar_menu_turno.botao_lancar_rect.collidepoint(event.pos):
                    
                    if estado_turno == "ANTES_LANCAR_DADOS" and not turno_bot_em_execucao:
                        tempo_bloqueio_botoes = 60
                        estado_turno = "LANCANDO_DADOS"
                        
                        jogador_antes = jogo_backend.jogadores[jogo_backend.indice_turno_atual].nome
                        
                        casa_onde_parei = jogo_backend.rolar_dados_e_mover()
                        print(f"Backend moveu jogador para: {casa_onde_parei.nome}")
                        
                        dado1_valor = jogo_backend.ultimo_d1
                        dado2_valor = jogo_backend.ultimo_d2
                        dados_lancados = True
                        
                        adicionar_mensagem_log(f"{jogador_antes}: {dado1_valor}+{dado2_valor} -> {casa_onde_parei.nome}")
                        adicionar_mensagem_feedback(f"{jogador_antes}: {dado1_valor}+{dado2_valor} -> {casa_onde_parei.nome}")
                        
                        acao_necessaria = jogo_backend.obter_acao_para_casa(casa_onde_parei)
                        
                        estado_turno_acao = acao_necessaria["tipo"]
                        posicao_para_decisao = jogo_backend.jogadores[jogo_backend.indice_turno_atual].posicao
                        
                        if acao_necessaria["tipo"] == "PEGAR_CARTA":
                            print(f"[v0] Acionando PEGAR_CARTA para jogador {jogador_antes}")
                            casa_atual = jogo_backend.tabuleiro.get_casa(jogo_backend.jogadores[jogo_backend.indice_turno_atual].posicao)
                            resultado = jogo_backend.executar_acao_automatica(casa_atual)
                            print(f"[v0] Resultado de executar_acao_automatica: {resultado}")
                            
                            if resultado is not None and isinstance(resultado, dict) and "mensagem" in resultado:
                                mensagem_carta_atual = resultado["mensagem"]
                                tempo_mensagem_carta = 300  # 5 seconds at 60fps
                                mostrar_popup_carta = True
                                print(f"[v0] Adicionando ao log: {resultado['mensagem']}")
                                adicionar_mensagem_log(f"CARTA: {resultado['mensagem']}")
                                adicionar_mensagem_feedback(f"CARTA: {resultado['mensagem']}")
                            else:
                                print(f"[v0] AVISO: Resultado vazio ou inválido de executar_acao_automatica")
                            
                            jogo_backend.finalizar_turno()
                            if jogo_backend.jogo_finalizado:
                                tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                                estado_jogo = "FIM_JOGO"
                            else:
                                estado_turno = "ANTES_LANCAR_DADOS"
                        
                        elif acao_necessaria["tipo"] in ["ACAO_AUTOMATICA", "PAGAR_ALUGUEL"]:
                            if acao_necessaria["tipo"] == "PAGAR_ALUGUEL":
                                adicionar_mensagem_log(f"Pagando aluguel...")
                                adicionar_mensagem_feedback(f"Pagando aluguel...")
                            
                            resultado = jogo_backend.executar_acao_automatica(casa_atual)
                            if resultado and "mensagem" in resultado:
                                tempo_mensagem_carta = 200
                                mensagem_carta_atual = resultado["mensagem"]
                                mostrar_popup_carta = True
                                adicionar_mensagem_log(resultado["mensagem"])
                                adicionar_mensagem_feedback(resultado["mensagem"])
                            
                            jogo_backend.finalizar_turno()
                            if jogo_backend.jogo_finalizado:
                                tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                                estado_jogo = "FIM_JOGO"
                            else:
                                estado_turno = "ANTES_LANCAR_DADOS"
                        
                        elif acao_necessaria["tipo"] == "NENHUMA_ACAO":
                            jogo_backend.finalizar_turno()
                            if jogo_backend.jogo_finalizado:
                                tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                                estado_jogo = "FIM_JOGO"
                            else:
                                estado_turno = "ANTES_LANCAR_DADOS"
                        
                        else:
                            estado_turno = "APOS_LANCAR_DADOS"
                    continue
                
                elif hasattr(desenhar_menu_turno, 'botao_comprar_rect') and \
                     desenhar_menu_turno.botao_comprar_rect.collidepoint(event.pos):
                    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao:
                        # Direct purchase logic without disabling buttons
                        jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
                        casa_atual = jogo_backend.tabuleiro.casas[jogador_atual.posicao]
                        
                        if isinstance(casa_atual, Propriedade) and not casa_atual.proprietario:
                            sucesso = jogo_backend.executar_compra()
                            if sucesso:
                                adicionar_mensagem_log(f"{jogador_atual.nome} comprou {casa_atual.nome}")
                                adicionar_mensagem_feedback(f"{jogador_atual.nome} comprou {casa_atual.nome}")
                                mostrar_menu_compra = False # Close the purchase menu
                                # Auto-pass turn after buying
                                jogo_backend.finalizar_turno()
                                if jogo_backend.jogo_finalizado:
                                    tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                                    estado_jogo = "FIM_JOGO"
                                else:
                                    estado_turno = "ANTES_LANCAR_DADOS"
                                    dados_lancados = False
                            else:
                                adicionar_mensagem_log("Não foi possível comprar a propriedade")
                                adicionar_mensagem_feedback("Não foi possível comprar a propriedade")
                        continue
                
                elif hasattr(desenhar_menu_turno, 'botao_propriedades_rect') and \
                     desenhar_menu_turno.botao_propriedades_rect.collidepoint(event.pos):
                    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao:
                        mostrar_menu_proposta = True
                        adicionar_mensagem_log("Abrindo gerenciador de propriedades")
                        adicionar_mensagem_feedback("Abrindo gerenciador de propriedades")
                    continue
                
                elif hasattr(desenhar_menu_turno, 'botao_negociar_rect') and \
                     desenhar_menu_turno.botao_negociar_rect.collidepoint(event.pos):
                    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao:
                        mostrar_menu_negociacao = True
                    continue
                
                elif hasattr(desenhar_menu_turno, 'botao_passar_rect') and \
                     desenhar_menu_turno.botao_passar_rect.collidepoint(event.pos):
                    if estado_turno == "APOS_LANCAR_DADOS" and not turno_bot_em_execucao:
                        jogo_backend.finalizar_turno()
                        if jogo_backend.jogo_finalizado:
                            tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                            estado_jogo = "FIM_JOGO"
                        else:
                            estado_turno = "ANTES_LANCAR_DADOS"
                            dados_lancados = False
                        adicionar_mensagem_log("Passou a vez")
                        adicionar_mensagem_feedback("Passou a vez")
                    continue
            
            if mostrar_menu_construcao:
                # Check close button
                if hasattr(desenhar_menu_construcao, 'botao_fechar_rect') and \
                   desenhar_menu_construcao.botao_fechar_rect.collidepoint(event.pos):
                    mostrar_menu_construcao = False
                    continue
                
                # Check construction buttons
                if hasattr(desenhar_menu_construcao, 'botoes_construir'):
                    for botao_rect, propriedade in desenhar_menu_construcao.botoes_construir:
                        if botao_rect.collidepoint(event.pos):
                            jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
                            sucesso = jogo_backend.construir_na_propriedade(jogador_atual, propriedade)
                            if sucesso:
                                casas_txt = "Hotel" if propriedade.casas == 5 else f"{propriedade.casas} casas"
                                adicionar_mensagem_log(f"Construiu em {propriedade.nome}: {casas_txt}")
                                adicionar_mensagem_feedback(f"Construiu em {propriedade.nome}: {casas_txt}")
                                # No change in state here, construction menu stays open until closed
                            break
                continue
            
            if mostrar_menu_proposta:
                # Check close button
                if hasattr(desenhar_menu_propostas, 'botao_fechar_rect') and \
                   desenhar_menu_propostas.botao_fechar_rect.collidepoint(event.pos):
                    mostrar_menu_proposta = False
                    continue
                
                # Check player selection buttons
                if hasattr(desenhar_menu_propostas, 'botoes_jogadores'):
                    for botao_rect, jogador in desenhar_menu_propostas.botoes_jogadores:
                        if botao_rect.collidepoint(event.pos):
                            adicionar_mensagem_log(f"Sistema de proposta em desenvolvimento")
                            adicionar_mensagem_log(f"Negociar com {jogador.nome}")
                            adicionar_mensagem_feedback(f"Sistema de proposta em desenvolvimento")
                            adicionar_mensagem_feedback(f"Negociar com {jogador.nome}")
                            mostrar_menu_proposta = False
                            break
                continue
            
            if mostrar_menu_compra:
                # Check close button
                if hasattr(desenhar_menu_compra, 'fechar_rect') and \
                   desenhar_menu_compra.fechar_rect.collidepoint(event.pos):
                    mostrar_menu_compra = False
                    continue
                
                # Check buy button
                if hasattr(desenhar_menu_compra, 'botao_comprar_rect') and \
                   desenhar_menu_compra.botao_comprar_rect.collidepoint(event.pos):
                    jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
                    casa_atual = jogo_backend.tabuleiro.casas[jogador_atual.posicao]
                    
                    if isinstance(casa_atual, Propriedade) and not casa_atual.proprietario:
                        sucesso = jogo_backend.executar_compra()
                        if sucesso:
                            adicionar_mensagem_log(f"{jogador_atual.nome} comprou {casa_atual.nome}")
                            adicionar_mensagem_feedback(f"{jogador_atual.nome} comprou {casa_atual.nome}")
                            mostrar_menu_compra = False # Close the purchase menu
                            # Auto-pass turn after buying
                            jogo_backend.finalizar_turno()
                            if jogo_backend.jogo_finalizado:
                                tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                                estado_jogo = "FIM_JOGO"
                            else:
                                estado_turno = "ANTES_LANCAR_DADOS"
                                dados_lancados = False
                        else:
                            adicionar_mensagem_log("Não foi possível comprar a propriedade")
                            adicionar_mensagem_feedback("Não foi possível comprar a propriedade")
                continue

            if mostrar_menu_negociacao and hasattr(desenhar_menu_negociacao, 'fechar_rect'):
                if desenhar_menu_negociacao.fechar_rect.collidepoint(event.pos):
                    mostrar_menu_negociacao = False
                    desenhar_menu_negociacao.jogador_selecionado_para_negociacao = None # Reset selected player
                    continue
                
                # Player selection
                if hasattr(desenhar_menu_negociacao, 'player_buttons'):
                    for player_button, jogador in desenhar_menu_negociacao.player_buttons:
                        if player_button.collidepoint(event.pos):
                            desenhar_menu_negociacao.jogador_selecionado_para_negociacao = jogador # Store selected player
                            # Clear previous selections
                            if hasattr(desenhar_menu_negociacao, 'sua_prop_selecionada'):
                                del desenhar_menu_negociacao.sua_prop_selecionada
                            continue
                
                # Your properties selection
                if hasattr(desenhar_menu_negociacao, 'sua_propriedades_buttons') and hasattr(desenhar_menu_negociacao, 'jogador_selecionado_para_negociacao'):
                    for prop_button, prop_sua in desenhar_menu_negociacao.sua_propriedades_buttons:
                        if prop_button.collidepoint(event.pos):
                            desenhar_menu_negociacao.sua_prop_selecionada = prop_sua
                            adicionar_mensagem_feedback(f"Selecionou {prop_sua.nome} para oferecer")
                            continue
                
                # Other player's properties selection and trade proposal
                if hasattr(desenhar_menu_negociacao, 'outra_propriedades_buttons') and hasattr(desenhar_menu_negociacao, 'sua_prop_selecionada') and desenhar_menu_negociacao.sua_prop_selecionada:
                    for prop_button, prop_deles in desenhar_menu_negociacao.outra_propriedades_buttons:
                        if prop_button.collidepoint(event.pos):
                            # Execute trade proposal
                            jogador_atual = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
                            jogador_a_trocar = desenhar_menu_negociacao.jogador_selecionado_para_negociacao
                            
                            # Note: The trade proposal function currently acts as an immediate trade for simplicity.
                            # A full implementation would involve waiting for the other player's response.
                            sucesso = jogo_backend.negociador_propriedades.propor_troca_propriedades(
                                jogador_atual,
                                jogador_a_trocar,
                                desenhar_menu_negociacao.sua_prop_selecionada,
                                prop_deles,
                                0 # Money component not implemented
                            )
                            
                            if sucesso:
                                # Currently, accepting the trade immediately
                                jogo_backend.negociador_propriedades.aceitar_troca(sucesso)
                                adicionar_mensagem_log(f"Troca realizada: {desenhar_menu_negociacao.sua_prop_selecionada.nome} por {prop_deles.nome}")
                                adicionar_mensagem_feedback(f"Troca realizada com {jogador_a_trocar.nome}")
                                mostrar_menu_negociacao = False
                                desenhar_menu_negociacao.jogador_selecionado_para_negociacao = None
                                del desenhar_menu_negociacao.sua_prop_selecionada
                            else:
                                adicionar_mensagem_log("Falha na negociação.")
                                adicionar_mensagem_feedback("Falha na negociação.")
                            continue
            
    # --- ATUALIZAÇÃO DAS ANIMAÇÕES ---
    if estado_jogo == "MENU":
        menu_inicial.update()
    elif estado_jogo == "FIM_JOGO":
        tela_fim_jogo.update()
    
    # --- RENDERIZAÇÃO POR ESTADO ---
    if estado_jogo == "MENU":
        menu_inicial.draw()
    
    elif estado_jogo == "FIM_JOGO":
        tela_fim_jogo.draw()
    
    else:  # Estados de jogo (INICIO_TURNO, OPCAO_COMPRA)
        screen.fill(COR_FUNDO)
        screen.blit(tabuleiro_img, (X_TABULEIRO, Y_TABULEIRO))
        
        desenhar_construcoes_no_tabuleiro()
        
        # In the rendering loop where pieces are drawn:
        for i, jogador in enumerate(jogo_backend.jogadores):
            if jogador.falido:
                continue
            
            # Use precise positions from the POSICOES_CASAS_PRECISAS
            if jogador.posicao < len(POSICOES_CASAS_PRECISAS):
                pos_x, pos_y = POSICOES_CASAS_PRECISAS[jogador.posicao]
                
                # Use dynamic offsets based on how many players are in the same square
                offset_x, offset_y = calcular_offsets_peoes_dinamicos(i, jogo_backend.jogadores)
                
                if i < len(PEOES_IMG):
                    peao_img = PEOES_IMG[i]
                    # Apply global adjustments and center the pawn
                    screen_x = X_TABULEIRO + pos_x + offset_x - peao_img.get_width() // 2 + AJUSTE_GLOBAL_PEOES_X
                    screen_y = Y_TABULEIRO + pos_y + offset_y - peao_img.get_height() // 2 + AJUSTE_GLOBAL_PEOES_Y
                    screen.blit(peao_img, (screen_x, screen_y))
        
        
        # Renderizando informações dos jogadores com propriedades (LADO DIREITO)
        for i, jogador in enumerate(jogo_backend.jogadores):
            pos_texto_x, pos_texto_y = POSICOES_TEXTO_JOGADOR[i % len(POSICOES_TEXTO_JOGADOR)]
            
            cor_nome = (255, 215, 0) if i == jogo_backend.indice_turno_atual else (255, 255, 255)
            
            if jogador.falido:
                texto_nome = FONTE_PADRAO.render(f"{jogador.nome} (FALIDO)", True, (150, 150, 150))
            else:
                texto_nome = FONTE_PADRAO.render(jogador.nome, True, cor_nome)
            
            saldo_jogador = jogo_backend.banco.consultar_saldo(jogador.nome)
            texto_saldo = FONTE_PEQUENA.render(f"${saldo_jogador}", True, (150, 255, 150))
            
            screen.blit(texto_nome, (pos_texto_x, pos_texto_y))
            screen.blit(texto_saldo, (pos_texto_x, pos_texto_y + 20))
            
            num_props = len(jogador.propriedades)
            if num_props > 0:
                texto_props_info = FONTE_PEQUENA.render(f"Propriedades: {num_props} [clique]", True, (200, 200, 100))
                screen.blit(texto_props_info, (pos_texto_x, pos_texto_y + 35))
        
        if mostrar_painel_propriedades and jogador_selecionado_para_info:
            desenhar_painel_propriedades_jogador(jogador_selecionado_para_info)
        
        # Draw dados if they were rolled
        if dados_lancados and dado1_valor and dado2_valor:
            # Draw white background for dice
            pygame.draw.rect(screen, (255, 255, 255), (20, 530, 140, 60))
            pygame.draw.rect(screen, (0, 0, 0), (20, 530, 140, 60), 2)
            
            # Draw dice images
            dado1_img = pygame.transform.scale(imagens_dados[dado1_valor - 1], (50, 50))
            dado2_img = pygame.transform.scale(imagens_dados[dado2_valor - 1], (50, 50))
            screen.blit(dado1_img, (30, 535))
            screen.blit(dado2_img, (90, 535))
            
            # Draw text below
            texto_dados = FONTE_PEQUENA.render(f"Dados: {dado1_valor} + {dado2_valor}", True, (255, 255, 255))
            screen.blit(texto_dados, (25, 595))

        if mostrar_menu_compra:
            desenhar_menu_compra()
        
        if mostrar_menu_proposta:
            desenhar_menu_propostas()
        
        if mostrar_menu_construcao:
            desenhar_menu_construcao()
        
        if mostrar_menu_negociacao:
            desenhar_menu_negociacao()
        
        desenhar_painel_feedback()
        desenhar_menu_turno() # Draw the turn menu on the left - ONLY HUD
        
        if mostrar_popup_carta:
            desenhar_popup_carta()
    
    atualizar_bloqueio_botoes()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
