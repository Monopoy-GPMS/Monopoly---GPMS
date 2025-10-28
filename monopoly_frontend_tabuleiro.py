#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monopoly BR - Interface Principal (Frontend + Jogo)
- Layout LADO A LADO (1800x1200)
- Painéis opacos de 300px nas laterais.
- Tabuleiro de 1200x1200 no meio.
- Exibe imagens dos dados no centro.

Execução:
  python monopoly_frontend_tabuleiro.py
"""

import os
import sys
from typing import Callable, List, Optional, Any, Tuple

import pygame

# ========= Importa backend de ./src =========
BASE_DIR = os.path.dirname(__file__) or "." # Garante que BASE_DIR não seja vazio
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

try:
    # Importa as classes principais do backend
    from jogo import Jogo
    from banco import Banco
    from jogador import Jogador
    from constantes import POSICAO_PRISAO
    import tabuleiro as backend  # type: ignore
except ImportError as e:
    print(f"Erro ao importar módulos de 'src/': {e}")
    print(f"Verifique se a pasta 'src/' existe em: {os.path.abspath(BASE_DIR)}")
    sys.exit(1)
except Exception:
    backend = None

# ========= Configuração da janela / layout (MODIFICADO) =========
WINDOW_WIDTH = 1800      # 300 (painel) + 1200 (tabuleiro) + 300 (painel)
WINDOW_HEIGHT = 1200     # Altura total
PANEL_WIDTH = 300
BOARD_SIZE = 1200

# Definição das áreas principais (LADO A LADO)
LEFT_PANEL_RECT = pygame.Rect(0, 0, PANEL_WIDTH, WINDOW_HEIGHT)
BOARD_RECT = pygame.Rect(PANEL_WIDTH, 0, BOARD_SIZE, WINDOW_HEIGHT) 
RIGHT_PANEL_RECT = pygame.Rect(PANEL_WIDTH + BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT)

# ========= Cores e Fontes (MODIFICADO) =========
COLOR_BG = (20, 20, 20)
COLOR_PANEL_BG = (40, 40, 40) # Fundo OPACO para os painéis
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_TITLE = (255, 255, 255)
COLOR_SALDO = (100, 255, 100)
COLOR_BUTTON = (0, 150, 0)
COLOR_BUTTON_DEBUG = (180, 0, 0) 
COLOR_AVISO_PRISAO = (255, 100, 100) 

# ========= Geometria do Tabuleiro (A que você pediu) =========
BOARD_MARGIN = 30        
SQUARE_W = 80            
SQUARE_H = 120           
CORNER = 120             

IMG_NAME = "monopoly_board_preview.png"

# ========= Configuração dos Dados =========
DICE_SIZE = 80  # Tamanho de cada imagem de dado (80x80)
DICE_GAP = 20   # Espaço entre os dados

# ========= Callbacks =========
_ON_CLICK: List[Callable[[int, Any, Any], None]] = []
SQUARE_CLICKED = pygame.USEREVENT + 1    

def register_on_click(func: Callable[[int, Any, Any], None]) -> None:
    _ON_CLICK.append(func)

# ========= Geometria =========
def pos_to_rect(pos: int) -> Tuple[int, int, int, int]:
    """Converte a posição 0..39 para (x, y, w, h) LOCAL (0,0 é o canto do tabuleiro)."""
    left = BOARD_MARGIN
    top = BOARD_MARGIN

    if 0 <= pos <= 10:
        if pos in (0, 10): 
            x, y = (left, top) if pos == 0 else (left + CORNER + 9 * SQUARE_W, top)
            return (x, y, CORNER, CORNER)
        x = left + CORNER + (pos - 1) * SQUARE_W
        y = top
        return (x, y, SQUARE_W, SQUARE_H)

    if 11 <= pos <= 19:
        x = left + CORNER + 9 * SQUARE_W
        y = top + CORNER + (pos - 11) * SQUARE_W
        return (x, y, SQUARE_H, SQUARE_W)

    if 20 <= pos <= 30:
        if pos in (20, 30):
            x, y = (
                (left + CORNER + 9 * SQUARE_W, top + CORNER + 9 * SQUARE_W)
                if pos == 20 else
                (left, top + CORNER + 9 * SQUARE_W)
            )
            return (x, y, CORNER, CORNER)
        x = left + CORNER + (30 - pos - 1) * SQUARE_W
        y = top + CORNER + 9 * SQUARE_W
        return (x, y, SQUARE_W, SQUARE_H)

    x = left
    y = top + CORNER + (39 - pos) * SQUARE_W
    return (x, y, SQUARE_H, SQUARE_W)


def find_position_at(px: int, py: int) -> Optional[int]:
    """Retorna o índice 0..39 da casa sob (px,py) LOCAL, ou None."""
    for i in range(40):
        x, y, w, h = pos_to_rect(i)
        if x <= px <= x + w and y <= py <= y + h:
            return i
    return None

# ========= Funções de Desenho da UI =========

def draw_player_info(screen, jogador, banco, x_start, y_start, max_width, fonts):
    """Desenha o status de um único jogador no painel."""
    if not jogador:
        return

    centro_x_painel = x_start + (max_width // 2)

    # 1. Nome (Centralizado)
    nome_txt = fonts["titulo"].render(jogador.nome, True, COLOR_TEXT_TITLE)
    nome_rect = nome_txt.get_rect(centerx=centro_x_painel, top=y_start)
    screen.blit(nome_txt, nome_rect)
    y_curr = y_start + 40 

    # 2. Saldo (Centralizado)
    saldo = banco.consultar_saldo(jogador.nome)
    saldo_texto = f"$ {saldo} M" 
    saldo_surf = fonts["normal"].render(saldo_texto, True, COLOR_SALDO)
    saldo_rect = saldo_surf.get_rect(centerx=centro_x_painel, top=y_curr)
    screen.blit(saldo_surf, saldo_rect)
    y_curr += 30 

    # 3. Status (Prisão) (Alinhado à esquerda)
    if jogador.em_prisao:
        status_txt = fonts["normal"].render("Status: NA PRISÃO", True, COLOR_AVISO_PRISAO)
        screen.blit(status_txt, (x_start, y_curr)) 
        y_curr += 35 

    # 4. Propriedades (Alinhado à esquerda)
    props_titulo = fonts["normal"].render("Propriedades:", True, COLOR_TEXT_TITLE)
    screen.blit(props_titulo, (x_start, y_curr))
    y_curr += 25
    
    if not jogador.propriedades:
        vazio_txt = fonts["props"].render("- Nenhuma -", True, (150, 150, 150))
        screen.blit(vazio_txt, (x_start + 10, y_curr))
    else:
        for prop in jogador.propriedades:
            prop_txt = fonts["props"].render(f"- {prop.nome}", True, COLOR_TEXT)
            screen.blit(prop_txt, (x_start + 10, y_curr))
            y_curr += 22
            if y_curr > y_start + (WINDOW_HEIGHT // 2) - 50: 
                extra_txt = fonts["props"].render("... e mais", True, (150, 150, 150))
                screen.blit(extra_txt, (x_start + 10, y_curr))
                break

def draw_player_panels(screen, jogadores, banco, fonts):
    """(ATUALIZADO) Desenha os painéis com fundo opaco."""
    
    # --- NOVO: Desenha fundos opacos ---
    pygame.draw.rect(screen, COLOR_PANEL_BG, LEFT_PANEL_RECT)
    pygame.draw.rect(screen, COLOR_PANEL_BG, RIGHT_PANEL_RECT)
    
    # --- O restante da lógica (desenhar texto) é o mesmo ---
    
    j1 = jogadores[0] if len(jogadores) > 0 else None
    j2 = jogadores[1] if len(jogadores) > 1 else None
    j3 = jogadores[2] if len(jogadores) > 2 else None
    j4 = jogadores[3] if len(jogadores) > 3 else None # Corrigido índice

    info_width = PANEL_WIDTH - 20 
    
    # --- Painel Esquerdo ---
    draw_player_info(screen, j1, banco, 10, 10, info_width, fonts)
    draw_player_info(screen, j3, banco, 10, WINDOW_HEIGHT // 2, info_width, fonts)

    # --- Painel Direito ---
    draw_player_info(screen, j2, banco, RIGHT_PANEL_RECT.x + 10, 10, info_width, fonts)
    draw_player_info(screen, j4, banco, RIGHT_PANEL_RECT.x + 10, WINDOW_HEIGHT // 2, info_width, fonts)


# ========= UI principal =========
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Monopoly BR - Interface Gráfica (1800x1200)")
    clock = pygame.time.Clock()

    # Inicializa fontes
    try:
        fonts = {
            "titulo": pygame.font.SysFont(None, 36),
            "normal": pygame.font.SysFont(None, 28),
            "props": pygame.font.SysFont(None, 24),
            "debug": pygame.font.SysFont(None, 20),
        }
    except Exception:
        fonts = {
            "titulo": pygame.font.Font(None, 36),
            "normal": pygame.font.Font(None, 28),
            "props": pygame.font.Font(None, 24),
            "debug": pygame.font.Font(None, 20),
        }

    # Carregar Imagens dos Dados
    dice_images = []
    try:
        for i in range(1, 7):
            path = os.path.join(BASE_DIR, f"dado{i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (DICE_SIZE, DICE_SIZE))
            dice_images.append(img)
    except Exception as e:
        print(f"Erro ao carregar imagens dos dados (ex: 'dado1.png'): {e}")
        pygame.quit()
        sys.exit(1)


    # Carrega imagem de fundo
    img_path = os.path.join(BASE_DIR, IMG_NAME)
    if not os.path.exists(img_path):
        raise SystemExit(f"Imagem '{IMG_NAME}' não encontrada em {BASE_DIR}.")

    bg = pygame.image.load(img_path).convert_alpha()
    try:
        bg = pygame.transform.smoothscale(bg, (BOARD_SIZE, BOARD_SIZE))
    except Exception:
        bg = pygame.transform.scale(bg, (BOARD_SIZE, BOARD_SIZE))

    
    # Posição de blit do tabuleiro (MODIFICADO: Lado a Lado)
    board_blit_x = PANEL_WIDTH  # Começa depois do painel esquerdo
    board_blit_y = 0
    board_blit_pos = (board_blit_x, board_blit_y)

    # Área de Clique do Tabuleiro
    BOARD_AREA_RECT = pygame.Rect(board_blit_pos[0], board_blit_pos[1], BOARD_SIZE, BOARD_SIZE)

    # Calcular Posições dos Dados
    # (Esta lógica ainda funciona, pois BOARD_AREA_RECT está correto)
    board_center_x = BOARD_AREA_RECT.centerx
    board_center_y = BOARD_AREA_RECT.centery
    
    DICE_POS_1 = (
        board_center_x - DICE_SIZE - (DICE_GAP // 2),
        board_center_y - (DICE_SIZE // 2)
    )
    DICE_POS_2 = (
        board_center_x + (DICE_GAP // 2),
        board_center_y - (DICE_SIZE // 2)
    )

    # Instancia o Jogo (Backend)
    try:
        nomes_jogadores = ["Jogador 1", "Jogador 2", "Jogador 3", "Jogador 4"]
        jogo = Jogo(nomes_jogadores)
        board = jogo.tabuleiro 
    except Exception as e:
        print(f"[Erro Fatal] Falha ao instanciar Jogo(): {e}")
        pygame.quit()
        sys.exit(1)

    # --- Definição dos Botões ---
    btn_turno_rect = pygame.Rect(LEFT_PANEL_RECT.x + 20, WINDOW_HEIGHT - 70, PANEL_WIDTH - 40, 50)
    btn_comprar_rect = pygame.Rect(RIGHT_PANEL_RECT.x + 20, WINDOW_HEIGHT - 130, PANEL_WIDTH - 40, 50)
    btn_prisao_rect = pygame.Rect(RIGHT_PANEL_RECT.x + 20, WINDOW_HEIGHT - 70, PANEL_WIDTH - 40, 50)

    running = True
    while running:
        # --- 1. Processamento de Eventos (MODIFICADO) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                # A. Botão de Próximo Turno
                if btn_turno_rect.collidepoint(event.pos):
                    print("[AÇÃO] Próximo Turno...")
                    jogo.iniciar_turno() 
                
                # B. Botão Debug Prisão
                elif btn_prisao_rect.collidepoint(event.pos):
                    jogador_atual = jogo.jogadores[jogo.indice_turno_atual]
                    jogador_atual.em_prisao = True
                    jogador_atual.posicao = POSICAO_PRISAO
                    print(f"[DEBUG] Forçando prisão do {jogador_atual.nome}")
                
                # C. Botão Debug Compra
                elif btn_comprar_rect.collidepoint(event.pos):
                    jogador_atual = jogo.jogadores[jogo.indice_turno_atual]
                    propriedade = jogo.tabuleiro.get_casa(1) # Av. Sumaré
                    
                    if propriedade and hasattr(propriedade, 'is_livre'):
                        if propriedade.is_livre():
                            if jogo.banco.pagar(jogador_atual.nome, propriedade.preco_compra, "Banco"):
                                propriedade.proprietario = jogador_atual
                                jogador_atual.adicionar_propriedade(propriedade)
                            else:
                                print(f"[DEBUG] {jogador_atual.nome} não tem saldo para comprar.")
                        else:
                            print(f"[DEBUG] {propriedade.nome} já tem dono.")
                    else:
                        print(f"[DEBUG] Posição 1 não é uma propriedade comprável.")


                # D. Clique no Tabuleiro (Lógica simplificada, sem sobreposição)
                elif BOARD_AREA_RECT.collidepoint(event.pos):
                    local_px = event.pos[0] - BOARD_AREA_RECT.x
                    local_py = event.pos[1] - BOARD_AREA_RECT.y
                    pos = find_position_at(local_px, local_py)
                    
                    if pos is not None:
                        casa = board.casas[pos] if board else None
                        nome = getattr(casa, "nome", None) if casa is not None else None
                        print(f"[CLICK TABULEIRO] posição={pos}  nome={nome}")
                        
                        for cb in list(_ON_CLICK):
                            cb(pos, casa, board)
                        pygame.event.post(pygame.event.Event(SQUARE_CLICKED, {"pos": pos, "casa": casa, "board": board}))


        # --- 2. Lógica de Desenho (MODIFICADA) ---
        
        screen.fill(COLOR_BG)

        # 1. Desenha o Tabuleiro (Fundo)
        screen.blit(bg, board_blit_pos)
        
        # 2. Desenha os Dados
        d1_img = dice_images[jogo.ultimo_d1 - 1]
        d2_img = dice_images[jogo.ultimo_d2 - 1]
        screen.blit(d1_img, DICE_POS_1)
        screen.blit(d2_img, DICE_POS_2)
        
        # 3. Desenha os Painéis (Opaques, nas laterais)
        draw_player_panels(screen, jogo.jogadores, jogo.banco, fonts)

        # 4. Desenha os Botões
        pygame.draw.rect(screen, COLOR_BUTTON, btn_turno_rect, border_radius=5)
        btn_txt = fonts["titulo"].render("Próximo Turno", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_turno_rect.center)
        screen.blit(btn_txt, txt_rect)
        
        pygame.draw.rect(screen, COLOR_BUTTON_DEBUG, btn_prisao_rect, border_radius=5)
        btn_txt = fonts["debug"].render("Debug: Ir para Prisão", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_prisao_rect.center)
        screen.blit(btn_txt, txt_rect)
        
        pygame.draw.rect(screen, COLOR_BUTTON_DEBUG, btn_comprar_rect, border_radius=5)
        btn_txt = fonts["debug"].render("Debug: Comprar Propriedade", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_comprar_rect.center)
        screen.blit(btn_txt, txt_rect)

        # Atualiza a tela
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()