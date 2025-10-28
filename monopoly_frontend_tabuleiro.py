#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monopoly BR - Interface Principal (Frontend + Jogo)
- Layout LADO A LADO (1800x1200)
- Painéis opacos de 300px nas laterais.
- Tabuleiro de 1200x1200 no meio.
- Painel central com "Vez de:", dados e botões de ação.

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

# ========= Configuração da janela / layout =========
WINDOW_WIDTH = 1500     # Largura da janela
WINDOW_HEIGHT = 900     # Altura da janela
PANEL_WIDTH = 300
BOARD_SIZE = 900

# Definição das áreas principais (LADO A LADO)
LEFT_PANEL_RECT = pygame.Rect(0, 0, PANEL_WIDTH, WINDOW_HEIGHT)
BOARD_RECT = pygame.Rect(PANEL_WIDTH, 0, BOARD_SIZE, BOARD_SIZE) 
RIGHT_PANEL_RECT = pygame.Rect(PANEL_WIDTH + BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT)

# ========= Cores e Fontes =========
COLOR_BG = (20, 20, 20)
COLOR_PANEL_BG = (40, 40, 40) 
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_TITLE = (255, 255, 255)
COLOR_SALDO = (100, 255, 100)
COLOR_BUTTON_LANCAR = (255, 0, 0) # Vermelho para Lançar Dados
COLOR_BUTTON_PROPOSTA = (255, 165, 0) # Laranja para Proposta
COLOR_AVISO_PRISAO = (255, 100, 100) 
COLOR_CENTRAL_PANEL_BG = (80, 80, 80) # Cinza um pouco mais claro
COLOR_DICE_BG = (120, 120, 120)       # Fundo dos dados

# --- Geometria do Tabuleiro (para cliques) ---
BOARD_MARGIN = 30        
SQUARE_W = 71            
SQUARE_H = 100           
CORNER = 100             

IMG_NAME = "monopoly_board_preview.png"

# ========= Configuração dos Dados =========
DICE_SIZE = 60  # Tamanho de cada imagem de dado
DICE_GAP = 30   # Espaço entre os dados
CENTRAL_PANEL_WIDTH = 400
CENTRAL_PANEL_HEIGHT = 150

# ========= Configuração dos Peões =========
PEAO_SIZE = 25 
PEAO_FILENAMES = ["peao1.png", "peao2.png", "peao3.png", "peao4.png"]
# offsets para os peões não se sobreporem
PEAO_OFFSETS = [
    (-PEAO_SIZE // 2, -PEAO_SIZE // 2), # Canto Superior Esquerdo
    ( PEAO_SIZE // 2, -PEAO_SIZE // 2), # Canto Superior Direito
    (-PEAO_SIZE // 2,  PEAO_SIZE // 2), # Canto Inferior Esquerdo
    ( PEAO_SIZE // 2,  PEAO_SIZE // 2), # Canto Inferior Direito
]

# ========= Callbacks =========
_ON_CLICK: List[Callable[[int, Any, Any], None]] = []
SQUARE_CLICKED = pygame.USEREVENT + 1    

def register_on_click(func: Callable[[int, Any, Any], None]) -> None:
    _ON_CLICK.append(func)

# ========= Geometria =========
def pos_to_rect(pos: int) -> Tuple[int, int, int, int]:
    """Converte a posição 0..39 para (x, y, w, h) LOCAL (0,0 é o canto do tabuleiro).
    --- ATENÇÃO: Esta lógica assume que a Posição 0 é o Canto Inferior Direito ---
    Caminho: Inferior-Direito (0) -> Inferior-Esquerdo (10) -> 
             Superior-Esquerdo (20) -> Superior-Direito (30) -> Inferior-Direito (39)
    """
    left = BOARD_MARGIN
    top = BOARD_MARGIN
    right = BOARD_SIZE - BOARD_MARGIN  # Coordenada X da parte da direita
    bottom = BOARD_SIZE - BOARD_MARGIN # Coordenada Y da parte de baixo

    # Lado Inferior (Pos 0 a 10) -  para a esquerda
    if 0 <= pos <= 10:
        if pos == 0: # Canto Inferior Direito Inicio)
            return (right - CORNER, bottom - CORNER, CORNER, CORNER)
        if pos == 10: # Canto Inferior Esquerdo (Prisão)
            return (left, bottom - CORNER, CORNER, CORNER)
        # Casas 1-9 (invertido, pois 1 está à esquerda do 0)
        x = right - CORNER - (pos * SQUARE_W)
        return (x, bottom - SQUARE_H, SQUARE_W, SQUARE_H)

    # Lado Esquerdo (Pos 11 a 20) - para cima
    if 11 <= pos <= 20:
        if pos == 20: # Canto Superior Esquerdo (Estacionamento)
            return (left, top, CORNER, CORNER)
        # Casas 11-19
        y = bottom - CORNER - ((pos - 10) * SQUARE_W)
        return (left, y, SQUARE_H, SQUARE_W)

    # Lado Superior (Pos 21 a 30) - para a direita
    if 21 <= pos <= 30:
        if pos == 30: # Canto Superior Direito (Vá para Prisão)
            return (right - CORNER, top, CORNER, CORNER)
        # Casas 21-29
        x = left + CORNER + ((pos - 21) * SQUARE_W)
        return (x, top, SQUARE_W, SQUARE_H)

    # Lado Direito (Pos 31 a 39) - para baixo
    if 31 <= pos <= 39:
        # Casas 31-39
        y = top + CORNER + ((pos - 31) * SQUARE_W)
        return (right - SQUARE_H, y, SQUARE_H, SQUARE_W)

    # Fallback, não deve acontecer
    return (0, 0, 10, 10)


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
    y_curr = y_start + 25 

    # 2. Saldo (Centralizado)
    saldo = banco.consultar_saldo(jogador.nome)
    saldo_texto = f"${saldo}M" 
    saldo_surf = fonts["normal"].render(saldo_texto, True, COLOR_SALDO)
    saldo_rect = saldo_surf.get_rect(centerx=centro_x_painel, top=y_curr)
    screen.blit(saldo_surf, saldo_rect)
    y_curr += 30 

    # 3. Status (Prisão) (Alinhado à esquerda)
    if jogador.em_prisao:
        status_txt = fonts["status"].render("Status: NA PRISÃO", True, COLOR_AVISO_PRISAO)
        screen.blit(status_txt, (x_start, y_curr)) 
        y_curr += 35 

    # 4. Propriedades (Alinhado à esquerda)
    props_titulo = fonts["status"].render("Propriedades:", True, COLOR_TEXT_TITLE)
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
    
    # Desenha painéis laterais
    pygame.draw.rect(screen, COLOR_PANEL_BG, LEFT_PANEL_RECT)
    pygame.draw.rect(screen, COLOR_PANEL_BG, RIGHT_PANEL_RECT)
    
    j1 = jogadores[0] if len(jogadores) > 0 else None
    j2 = jogadores[1] if len(jogadores) > 1 else None
    j3 = jogadores[2] if len(jogadores) > 2 else None
    j4 = jogadores[3] if len(jogadores) > 3 else None

    info_width = PANEL_WIDTH - 20 
    
    # --- Painel Esquerdo ---
    draw_player_info(screen, j1, banco, 10, 10, info_width, fonts)
    draw_player_info(screen, j3, banco, 10, WINDOW_HEIGHT // 2, info_width, fonts)

    # --- Painel Direito ---
    draw_player_info(screen, j2, banco, RIGHT_PANEL_RECT.x + 10, 10, info_width, fonts)
    draw_player_info(screen, j4, banco, RIGHT_PANEL_RECT.x + 10, WINDOW_HEIGHT // 2, info_width, fonts)


# ========= Funções de Desenho do Peão =========

def draw_peoes(screen, jogo_obj, peao_images, board_offset):
    """
    Desenha todos os peões no tabuleiro com base em suas posições.
    """
    board_x_offset, board_y_offset = board_offset
    
    for i, jogador in enumerate(jogo_obj.jogadores):
        
        # 1. Determinar a Posição Lógica (0-39)
        # Se estiver na prisão, a posição visual é SEMPRE a da prisão (10)
        posicao_logica = POSICAO_PRISAO if jogador.em_prisao else jogador.posicao

        # 2. Obter a Imagem do Peão
        peao_img = peao_images[i % len(peao_images)]

        # 3. Converter Posição Lógica para Coordenadas
        try:
            # Pega o retângulo LOCAL (relativo ao tabuleiro)
            local_rect = pos_to_rect(posicao_logica)
            lx, ly, lw, lh = local_rect
            
            # Calcula o CENTRO da casa
            centro_x_local = lx + lw // 2
            centro_y_local = ly + lh // 2
            
            # 4. Aplicar Offset do Peão (para não sobrepor)
            offset_x, offset_y = PEAO_OFFSETS[i % len(PEAO_OFFSETS)]
            
            # 5. Calcular Posição Final (Global)
            draw_x = board_x_offset + centro_x_local + offset_x - (PEAO_SIZE // 2)
            draw_y = board_y_offset + centro_y_local + offset_y - (PEAO_SIZE // 2)
            
            # 6. Desenhar o peão na tela
            screen.blit(peao_img, (draw_x, draw_y))
            
        except Exception as e:
            print(f"Erro ao desenhar peão para {jogador.nome} na pos {posicao_logica}: {e}")

# ========= UI principal =========
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Monopoly BR")
    clock = pygame.time.Clock()

    # Inicializa fontes
    try:
        fonts = {
            "titulo": pygame.font.SysFont(None, 36),
            "normal": pygame.font.SysFont(None, 28),
            "props": pygame.font.SysFont(None, 24),
            "status": pygame.font.SysFont(None, 20),
        }
    except Exception:
        fonts = {
            "titulo": pygame.font.Font(None, 36),
            "normal": pygame.font.Font(None, 28),
            "props": pygame.font.Font(None, 24),
            "status": pygame.font.Font(None, 20),
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
        
    # --- Carregar Imagens dos Peões ---
    peao_images = []
    try:
        print(f"Carregando peões de: {os.path.abspath(BASE_DIR)}")
        for i, filename in enumerate(PEAO_FILENAMES):
            path = os.path.join(BASE_DIR, filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Arquivo do peão não encontrado: {filename}")
                
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (PEAO_SIZE, PEAO_SIZE))
            peao_images.append(img)
            
    except Exception as e:
        print(f"Erro ao carregar imagens dos peões (ex: 'peao1.png'): {e}")
        pygame.quit()
        sys.exit(1)

    # Carregar Tabuleiro
    img_path = os.path.join(BASE_DIR, IMG_NAME)
    if not os.path.exists(img_path):
        raise SystemExit(f"Imagem '{IMG_NAME}' não encontrada em {BASE_DIR}.")

    bg = pygame.image.load(img_path).convert_alpha()
    try:
        bg = pygame.transform.smoothscale(bg, (BOARD_SIZE, BOARD_SIZE))
    except Exception:
        bg = pygame.transform.scale(bg, (BOARD_SIZE, BOARD_SIZE))

    
    # --- 4. Calcular Posições e Áreas ---
    # Posição do Tabuleiro
    board_blit_x = PANEL_WIDTH  # Começa depois do painel esquerdo
    board_blit_y = 0
    board_blit_pos = (board_blit_x, board_blit_y)

    # Área de Clique do Tabuleiro
    BOARD_AREA_RECT = pygame.Rect(board_blit_pos[0], board_blit_pos[1], BOARD_SIZE, BOARD_SIZE)

    # Posição do Painel com os dados
    original_center_x = BOARD_AREA_RECT.centerx
    original_center_y = BOARD_AREA_RECT.centery

    new_center_x = original_center_x - 120
    new_center_y = original_center_y + 250
    
    CENTRAL_PANEL_RECT = pygame.Rect(
        new_center_x - (CENTRAL_PANEL_WIDTH // 2),
        new_center_y - (CENTRAL_PANEL_HEIGHT // 2),
        CENTRAL_PANEL_WIDTH,
        CENTRAL_PANEL_HEIGHT
    )

    # Posição dos Dados (relativo ao Painel Central)
    total_dice_display_width = (DICE_SIZE * 2) + DICE_GAP
    dice_area_x = CENTRAL_PANEL_RECT.x + CENTRAL_PANEL_RECT.width - total_dice_display_width - 35 # margem direita da imagem dos dados

    DICE_POS_1 = (
        dice_area_x,
        CENTRAL_PANEL_RECT.centery - (DICE_SIZE // 2)
    )
    DICE_POS_2 = (
        dice_area_x + DICE_SIZE + DICE_GAP,
        CENTRAL_PANEL_RECT.centery - (DICE_SIZE // 2)
    )
    
    # --- 5. Inicialização do Backend (Jogo) ---
    try:
        nomes_jogadores = ["Jogador 1", "Jogador 2", "Jogador 3", "Jogador 4"]
        jogo = Jogo(nomes_jogadores)
        board = jogo.tabuleiro 
    except Exception as e:
        print(f"[Erro Fatal] Falha ao instanciar Jogo(): {e}")
        pygame.quit()
        sys.exit(1)

    # --- 6. Definição dos Botões da UI (no Painel Central) ---
    btn_proposta_rect = pygame.Rect(
        CENTRAL_PANEL_RECT.x + 10, # Margem esquerda
        CENTRAL_PANEL_RECT.y + 70, # Margem superior relativa"
        130, # Largura do botão
        30   # Altura do botão
    )
    btn_lancar_dados_rect = pygame.Rect(
        CENTRAL_PANEL_RECT.x + 10, # Margem esquerda
        CENTRAL_PANEL_RECT.y + 110, # Margem superior relativa
        130, # Largura do botão
        30   # Altura do botão
    )

    # --- 7. Loop Principal do Jogo ---
    running = True
    while running:
        # --- 1. Processamento de Eventos (TESTE DOS DADOS) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                # A. Clique no Botão "Lançar Dados"
                if btn_lancar_dados_rect.collidepoint(event.pos):
                    print("[AÇÃO] Lançar Dados / Próximo Turno...")
                    jogo.iniciar_turno() 
                
                # B. Clique no Botão "Fazer uma proposta"
                elif btn_proposta_rect.collidepoint(event.pos):
                    print("[AÇÃO] Fazer uma proposta (Funcionalidade a ser implementada)...")
                    # (Lógica futura aqui)

                # C. Clique no Tabuleiro
                elif BOARD_AREA_RECT.collidepoint(event.pos):
                    # Converte coordenada global (tela) para local (tabuleiro)
                    local_px = event.pos[0] - BOARD_AREA_RECT.x
                    local_py = event.pos[1] - BOARD_AREA_RECT.y
                    pos = find_position_at(local_px, local_py)
                    
                    if pos is not None:
                        casa = board.casas[pos] if board else None
                        nome = getattr(casa, "nome", None) if casa is not None else None
                        print(f"[CLICK TABULEIRO] posição={pos}  nome={nome}")
                        
                        # Dispara callbacks (se houver)
                        for cb in list(_ON_CLICK):
                            cb(pos, casa, board)
                        pygame.event.post(pygame.event.Event(SQUARE_CLICKED, {"pos": pos, "casa": casa, "board": board}))


        # --- Lógica de Desenho ---
        
        screen.fill(COLOR_BG)

        # Desenha o Tabuleiro (Fundo)
        screen.blit(bg, board_blit_pos)
        
        # Desenha os Peões
        draw_peoes(screen, jogo, peao_images, board_blit_pos)
        
        # Desenha os Painéis Laterais
        draw_player_panels(screen, jogo.jogadores, jogo.banco, fonts)

        # Desenha o Painel Central (sobre o tabuleiro)
        pygame.draw.rect(screen, COLOR_CENTRAL_PANEL_BG, CENTRAL_PANEL_RECT, border_radius=10)

        # Texto "Vez de:"
        jogador_atual = jogo.jogadores[jogo.indice_turno_atual]
        vez_de_txt = fonts["normal"].render("Vez de:", True, COLOR_TEXT_TITLE)
        screen.blit(vez_de_txt, (CENTRAL_PANEL_RECT.x + 15, CENTRAL_PANEL_RECT.y + 15))
        
        jogador_nome_txt = fonts["props"].render(jogador_atual.nome, True, COLOR_TEXT_TITLE)
        screen.blit(jogador_nome_txt, (CENTRAL_PANEL_RECT.x + 15, CENTRAL_PANEL_RECT.y + 35)) # Abaixo de "Vez de:"

        # Fundo da Área dos Dados
        dice_bg_rect_x = CENTRAL_PANEL_RECT.x + CENTRAL_PANEL_RECT.width - 200 - 10
        dice_bg_rect_y = CENTRAL_PANEL_RECT.y + 10
        dice_bg_rect_width = 200 
        dice_bg_rect_height = CENTRAL_PANEL_RECT.height - 20 

        pygame.draw.rect(screen, COLOR_DICE_BG, 
                         (dice_bg_rect_x, dice_bg_rect_y, dice_bg_rect_width, dice_bg_rect_height), 
                         border_radius=5)
        
        # Imagens dos Dados
        d1_img = dice_images[jogo.ultimo_d1 - 1]
        d2_img = dice_images[jogo.ultimo_d2 - 1]
        screen.blit(d1_img, DICE_POS_1)
        screen.blit(d2_img, DICE_POS_2)
        
        # Desenha os Botões
        pygame.draw.rect(screen, COLOR_BUTTON_PROPOSTA, btn_proposta_rect, border_radius=5)
        btn_txt = fonts["status"].render("Fazer uma proposta", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_proposta_rect.center)
        screen.blit(btn_txt, txt_rect)
        
        pygame.draw.rect(screen, COLOR_BUTTON_LANCAR, btn_lancar_dados_rect, border_radius=5)
        btn_txt = fonts["status"].render("Lançar Dados", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_lancar_dados_rect.center)
        screen.blit(btn_txt, txt_rect)

        # Atualiza a tela
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()