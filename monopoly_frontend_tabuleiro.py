#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monopoly BR - Interface Principal (Frontend + Jogo)
- Mostra o tabuleiro no centro.
- Mostra os painéis de jogadores (1/3 à esquerda, 2/4 à direita).
- Gerencia o loop principal do Pygame e o estado do Jogo (backend).

Execução:
  python monopoly_frontend_tabuleiro.py

Integração de regras:
- Registre um callback com register_on_click(func) OU escute o evento Pygame SQUARE_CLICKED.
  * Callback assinatura: func(posicao: int, casa_obj: Any, board_obj: Any) -> None
  * Evento: Pygame posta USEREVENT+1 com dict {"pos": int, "casa": obj, "board": obj}
"""

import os
import sys
from typing import Callable, List, Optional, Any, Tuple

import pygame

# ========= Importa backend de ./src (se existir) =========
BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

try:
    # Importa as classes principais do backend
    from jogo import Jogo
    from banco import Banco
    from jogador import Jogador
    # Importa constantes para usar a POSICAO_PRISAO
    from constantes import POSICAO_PRISAO
    import tabuleiro as backend  # type: ignore
except ImportError as e:
    print(f"Erro ao importar módulos de 'src/': {e}")
    print("Verifique se os arquivos 'jogo.py', 'banco.py', 'jogador.py' etc. estão na pasta 'src/'.")
    sys.exit(1)
except Exception:
    backend = None

# ========= Configuração da janela / layout (MODIFICADO) =========
WINDOW_WIDTH = 1600      # 300 (painel) + 900 (tabuleiro) + 300 (painel)
WINDOW_HEIGHT = 900      # Altura máxima
PANEL_WIDTH = 200        # Largura dos painéis laterais
BOARD_SIZE = 1200         # Tabuleiro se ajusta à altura

# Definição das áreas principais
LEFT_PANEL_RECT = pygame.Rect(0, 0, PANEL_WIDTH, WINDOW_HEIGHT)
# O tabuleiro começa DEPOIS do painel esquerdo
BOARD_RECT = pygame.Rect(PANEL_WIDTH, 0, BOARD_SIZE, WINDOW_HEIGHT) 
# O painel direito começa DEPOIS do tabuleiro
RIGHT_PANEL_RECT = pygame.Rect(PANEL_WIDTH + BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT)

# Cores e Fontes
COLOR_BG = (20, 20, 20)
COLOR_PANEL_BG = (40, 40, 40)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_TITLE = (255, 255, 255)
COLOR_SALDO = (100, 255, 100)
COLOR_BUTTON = (0, 150, 0)
COLOR_BUTTON_DEBUG = (180, 0, 0) # Cor para botões de debug
COLOR_AVISO_PRISAO = (255, 100, 100) # Vermelho para aviso

# Geometria do Tabuleiro
BOARD_MARGIN = 30        
SQUARE_W = 80            
SQUARE_H = 120           
CORNER = 120             

IMG_NAME = "monopoly_board_preview.png"

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
    """Retorna o índice 0..39 da casa sob (px,py), ou None se fora das áreas."""
    for i in range(40):
        x, y, w, h = pos_to_rect(i)
        if x <= px <= x + w and y <= py <= y + h:
            return i
    return None

# ========= Funções de Desenho da UI (NOVO) =========

def draw_player_info(screen, jogador, banco, x_start, y_start, max_width, fonts):
    """(ATUALIZADO) Desenha o status de um único jogador no painel."""
    if not jogador:
        return

    # Calcula o centro X do painel (usado para Nome e Saldo)
    centro_x_painel = x_start + (max_width // 2)

    # 1. Nome (MODIFICADO: Centralizado)
    nome_txt = fonts["titulo"].render(jogador.nome, True, COLOR_TEXT_TITLE)
    nome_rect = nome_txt.get_rect(centerx=centro_x_painel, top=y_start)
    screen.blit(nome_txt, nome_rect)
    y_curr = y_start + 40 # Espaçamento após o nome

    # 2. Saldo (MODIFICADO: Formato e Centralização)
    saldo = banco.consultar_saldo(jogador.nome)
    saldo_texto = f"$ {saldo} M" 
    saldo_surf = fonts["normal"].render(saldo_texto, True, COLOR_SALDO)
    saldo_rect = saldo_surf.get_rect(centerx=centro_x_painel, top=y_curr)
    screen.blit(saldo_surf, saldo_rect)
    y_curr += 30 # Espaçamento após o saldo

    # 3. Status (Prisão) (Alinhado à esquerda)
    if jogador.em_prisao:
        # Nota: Este status não está centralizado para se destacar
        status_txt = fonts["normal"].render("Status: NA PRISÃO", True, COLOR_AVISO_PRISAO)
        screen.blit(status_txt, (x_start, y_curr))
        y_curr += 35 # Adiciona espaço SÓ SE estiver preso

    # 4. Propriedades (Alinhado à esquerda)
    props_titulo = fonts["normal"].render("Propriedades:", True, COLOR_TEXT_TITLE)
    screen.blit(props_titulo, (x_start, y_curr))
    y_curr += 25
    
    if not jogador.propriedades:
        vazio_txt = fonts["props"].render("- Nenhuma -", True, (150, 150, 150))
        screen.blit(vazio_txt, (x_start + 10, y_curr))
        y_curr += 22
    else:
        for prop in jogador.propriedades:
            prop_txt = fonts["props"].render(f"- {prop.nome}", True, COLOR_TEXT)
            screen.blit(prop_txt, (x_start + 10, y_curr))
            y_curr += 22
            # Limita a altura para não transbordar
            if y_curr > y_start + (WINDOW_HEIGHT // 2) - 50: # Ajuste para nova altura
                extra_txt = fonts["props"].render("... e mais", True, (150, 150, 150))
                screen.blit(extra_txt, (x_start + 10, y_curr))
                break

def draw_player_panels(screen, jogadores, banco, fonts):
    """Desenha os painéis da esquerda e direita com os dados dos jogadores."""
    # Desenha os fundos dos painéis
    pygame.draw.rect(screen, COLOR_PANEL_BG, LEFT_PANEL_RECT)
    pygame.draw.rect(screen, COLOR_PANEL_BG, RIGHT_PANEL_RECT)
    
    # Extrai os jogadores (lidando com menos de 4 jogadores)
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

# ========= UI principal (MODIFICADO) =========
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Monopoly BR - Interface Gráfica (com Debug)")
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
        print("Aviso: Fontes do sistema não carregadas, usando padrão.")
        fonts = {
            "titulo": pygame.font.Font(None, 36),
            "normal": pygame.font.Font(None, 28),
            "props": pygame.font.Font(None, 24),
            "debug": pygame.font.Font(None, 20),
        }

    # Carrega imagem de fundo
    img_path = os.path.join(BASE_DIR, IMG_NAME)
    if not os.path.exists(img_path):
        raise SystemExit(f"Imagem '{IMG_NAME}' não encontrada em {BASE_DIR}.")

    bg = pygame.image.load(img_path).convert_alpha()
    available = BOARD_RECT.width - 2 * BOARD_MARGIN
    # Redimensiona mantendo proporção (sem distorcer)
    img_w, img_h = bg.get_size()
    scale = min(available / img_w, available / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)
    bg = pygame.transform.smoothscale(bg, (new_w, new_h))
    board_blit_x = BOARD_RECT.x + BOARD_MARGIN + (available - new_w) // 2
    board_blit_y = BOARD_RECT.y + BOARD_MARGIN + (available - new_h) // 2
    board_blit_pos = (board_blit_x, board_blit_y)

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
    
    # Botão de Próximo Turno
    btn_turno_rect = pygame.Rect(LEFT_PANEL_RECT.x + 20, WINDOW_HEIGHT - 70, PANEL_WIDTH - 40, 50)
    
    # --- NOVOS BOTÕES DE DEBUG (Painel Direito) ---
    btn_comprar_rect = pygame.Rect(RIGHT_PANEL_RECT.x + 20, WINDOW_HEIGHT - 130, PANEL_WIDTH - 40, 50)
    btn_prisao_rect = pygame.Rect(RIGHT_PANEL_RECT.x + 20, WINDOW_HEIGHT - 70, PANEL_WIDTH - 40, 50)

    running = True
    while running:
        # --- 1. Processamento de Eventos ---
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
                
                # B. NOVO: Botão Debug Prisão
                elif btn_prisao_rect.collidepoint(event.pos):
                    jogador_atual = jogo.jogadores[jogo.indice_turno_atual]
                    jogador_atual.em_prisao = True
                    jogador_atual.posicao = POSICAO_PRISAO
                    print(f"[DEBUG] Forçando prisão do {jogador_atual.nome}")
                
                # C. NOVO: Botão Debug Compra
                elif btn_comprar_rect.collidepoint(event.pos):
                    jogador_atual = jogo.jogadores[jogo.indice_turno_atual]
                    propriedade = jogo.tabuleiro.get_casa(1) # Pega a "Avenida Sumaré"
                    
                    if propriedade.is_livre():
                        if jogo.banco.pagar(jogador_atual.nome, propriedade.preco_compra, "Banco"):
                            propriedade.proprietario = jogador_atual
                            jogador_atual.adicionar_propriedade(propriedade)
                            print(f"[DEBUG] Forçando compra da {propriedade.nome} por {jogador_atual.nome}")
                        else:
                            print(f"[DEBUG] {jogador_atual.nome} não tem saldo para comprar.")
                    else:
                        print(f"[DEBUG] {propriedade.nome} já tem dono.")

                # D. Clique no Tabuleiro
                elif BOARD_RECT.collidepoint(event.pos):
                    local_px = event.pos[0] - BOARD_RECT.x
                    local_py = event.pos[1] - BOARD_RECT.y
                    pos = find_position_at(local_px, local_py)
                    
                    if pos is not None:
                        casa = board.casas[pos] if board else None
                        nome = getattr(casa, "nome", None) if casa is not None else None
                        print(f"[CLICK TABULEIRO] posição={pos}  nome={nome}")
                        # (Callbacks e eventos customizados removidos para simplificar)

        # --- 2. Lógica de Desenho ---
        
        # Limpa a tela
        screen.fill(COLOR_BG)

        # Desenha o Tabuleiro
        screen.blit(bg, board_blit_pos)
        
        # Desenha os Painéis de Jogadores
        draw_player_panels(screen, jogo.jogadores, jogo.banco, fonts)

        # Desenha Botão "Próximo Turno"
        pygame.draw.rect(screen, COLOR_BUTTON, btn_turno_rect, border_radius=5)
        btn_txt = fonts["titulo"].render("Próximo Turno", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_turno_rect.center)
        screen.blit(btn_txt, txt_rect)
        
        # --- Desenha NOVOS BOTÕES DE DEBUG ---
        
        # Botão Prisão
        pygame.draw.rect(screen, COLOR_BUTTON_DEBUG, btn_prisao_rect, border_radius=5)
        btn_txt = fonts["debug"].render("Debug: Ir para Prisão", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_prisao_rect.center)
        screen.blit(btn_txt, txt_rect)
        
        # Botão Comprar
        pygame.draw.rect(screen, COLOR_BUTTON_DEBUG, btn_comprar_rect, border_radius=5)
        btn_txt = fonts["debug"].render("Debug: Comprar Propriedade (Av. Sumaré)", True, COLOR_TEXT_TITLE)
        txt_rect = btn_txt.get_rect(center=btn_comprar_rect.center)
        screen.blit(btn_txt, txt_rect)

        # Atualiza a tela
        pygame.display.flip()
        
        # Limita o FPS
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
