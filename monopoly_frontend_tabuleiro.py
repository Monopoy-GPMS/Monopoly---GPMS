#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monopoly BR - Frontend "Imagem-Click"
- Mostra apenas a IMAGEM do tabuleiro.
- Define as 40 áreas clicáveis (0..39) e dispara callbacks/eventos de clique.
- Compatível com backend em ./src/tabuleiro.py (opcional).

Estrutura sugerida:
  projeto/
    monopoly_frontend_tabuleiro.py   <-- este arquivo
    monopoly_board_preview.png       <-- imagem do tabuleiro (quadrada)
    src/
      tabuleiro.py                   <-- backend (opcional)

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
    import tabuleiro as backend  # type: ignore
except Exception:
    backend = None  # backend opcional

# ========= Configuração da janela / layout =========
WINDOW_SIZE = 1200
BOARD_MARGIN = 30        # margem externa (imagem centralizada com esta borda)
SQUARE_W = 80            # largura de casas retangulares (top/bottom)
SQUARE_H = 120           # altura de casas retangulares (top/bottom)
CORNER = 120             # tamanho dos cantos

IMG_NAME = "monopoly_board_preview.png"  # nome do arquivo da imagem

# ========= Callbacks =========
_ON_CLICK: List[Callable[[int, Any, Any], None]] = []
SQUARE_CLICKED = pygame.USEREVENT + 1    # evento customizado postado em cada clique válido


def register_on_click(func: Callable[[int, Any, Any], None]) -> None:
    """Registra um callback invocado quando o usuário clica em uma casa (0..39)."""
    _ON_CLICK.append(func)


# ========= Geometria =========
def pos_to_rect(pos: int) -> Tuple[int, int, int, int]:
    """
    Converte a posição 0..39 para (x, y, w, h) na janela.
    Layout estilo Monopoly, começando no canto superior esquerdo e seguindo horário.
    """
    left = BOARD_MARGIN
    top = BOARD_MARGIN

    if 0 <= pos <= 10:
        if pos in (0, 10):  # cantos
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

    # esquerda (31..39)
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


# ========= UI principal =========
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Monopoly BR - Imagem com Áreas Clicáveis")
    clock = pygame.time.Clock()

    # Carrega imagem de fundo
    img_path = os.path.join(BASE_DIR, IMG_NAME)
    if not os.path.exists(img_path):
        raise SystemExit(f"Imagem '{IMG_NAME}' não encontrada em {BASE_DIR}. Coloque o arquivo e tente novamente.")

    bg = pygame.image.load(img_path).convert_alpha()
    available = WINDOW_SIZE - 2 * BOARD_MARGIN
    # Redimensiona mantendo proporção (sem distorcer)
    img_w, img_h = bg.get_size()
    scale = min(available / img_w, available / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)
    bg = pygame.transform.smoothscale(bg, (new_w, new_h))
    x = BOARD_MARGIN + (available - new_w) // 2
    y = BOARD_MARGIN + (available - new_h) // 2
    screen.blit(bg, (x, y))

    # Instancia backend.Tabuleiro() se disponível
    board = None
    if backend and hasattr(backend, "Tabuleiro"):
        try:
            board = backend.Tabuleiro()
        except Exception as e:
            print("[Aviso] Falha ao instanciar Tabuleiro():", e)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = find_position_at(*event.pos)
                if pos is not None:
                    casa = None
                    if board and hasattr(board, "casas") and 0 <= pos < len(board.casas):
                        try:
                            casa = board.casas[pos]
                        except Exception:
                            casa = None

                    # Dispara evento customizado
                    pygame.event.post(pygame.event.Event(SQUARE_CLICKED, {"pos": pos, "casa": casa, "board": board}))

                    # Executa callbacks registrados
                    for cb in list(_ON_CLICK):
                        try:
                            cb(pos, casa, board)
                        except Exception as e:
                            print("[Callback erro]", e)

                    # Fallback: imprime no console (útil para depurar)
                    nome = getattr(casa, "nome", None) if casa is not None else None
                    print(f"[CLICK] posição={pos}  nome={nome}")

        # Desenha somente a IMAGEM (sem overlays)
        screen.fill((0, 0, 0))
        screen.blit(bg, (BOARD_MARGIN, BOARD_MARGIN))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
