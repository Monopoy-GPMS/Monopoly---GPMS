#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monopoly Board Frontend - PyGame Implementation
Tabuleiro do Monopoly com visualização completa usando PyGame
"""

import pygame
import sys
import math

# ==================== CONSTANTES E CONFIGURAÇÕES ====================

# Dimensões da janela e casas
WINDOW_SIZE = 1200
SQUARE_WIDTH = 80
SQUARE_HEIGHT = 120
CORNER_SIZE = 120

# Cores do jogo
COLORS = {
    'red': (220, 0, 0),
    'dark_red': (180, 0, 0),
    'dark_green': (0, 128, 0),
    'light_green': (144, 238, 144),
    'light_yellow_green': (180, 220, 100),
    'blue': (100, 150, 255),
    'dark_blue': (0, 0, 139),
    'orange': (255, 165, 0),
    'pink': (255, 105, 180),
    'magenta': (220, 20, 130),
    'brown': (139, 69, 19),
    'dark_brown': (101, 45, 11),
    'yellow': (255, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'background': (220, 220, 200),
    'light_gray': (240, 240, 230),
    'gray': (180, 180, 180),
    'gold': (255, 215, 0),
}

# ==================== CLASSE BASE: SQUARE ====================

class Square:
    """Classe base para uma casa do tabuleiro"""
    
    def __init__(self, name, position, square_type):
        self.name = name
        self.position = position
        self.square_type = square_type
        self.rect = None
        
    def draw(self, screen):
        """Método base para desenhar a casa"""
        pass
    
    def get_coordinates(self, board_offset, corner_size, square_width, square_height):
        """Calcula as coordenadas da casa baseado na posição"""
        x, y = 0, 0
        
        # Posição 0-10: Lado superior (esquerda → direita)
        if 0 <= self.position <= 10:
            if self.position == 0:  # Canto superior esquerdo
                x = board_offset
                y = board_offset
                return (x, y, corner_size, corner_size)
            elif self.position == 10:  # Canto superior direito
                x = board_offset + corner_size + (9 * square_width)
                y = board_offset
                return (x, y, corner_size, corner_size)
            else:
                x = board_offset + corner_size + ((self.position - 1) * square_width)
                y = board_offset
                return (x, y, square_width, square_height)
        
        # Posição 11-19: Lado direito (cima → baixo)
        elif 11 <= self.position <= 19:
            x = board_offset + corner_size + (9 * square_width)
            y = board_offset + corner_size + ((self.position - 11) * square_width)
            return (x, y, square_height, square_width)
        
        # Posição 20-30: Lado inferior (direita → esquerda)
        elif 20 <= self.position <= 30:
            if self.position == 20:  # Canto inferior direito
                x = board_offset + corner_size + (9 * square_width)
                y = board_offset + corner_size + (9 * square_width)
                return (x, y, corner_size, corner_size)
            elif self.position == 30:  # Canto inferior esquerdo
                x = board_offset
                y = board_offset + corner_size + (9 * square_width)
                return (x, y, corner_size, corner_size)
            else:
                x = board_offset + corner_size + ((30 - self.position - 1) * square_width)
                y = board_offset + corner_size + (9 * square_width)
                return (x, y, square_width, square_height)
        
        # Posição 31-39: Lado esquerdo (baixo → cima)
        else:  # 31-39
            x = board_offset
            y = board_offset + corner_size + ((39 - self.position) * square_width)
            return (x, y, square_height, square_width)


# ==================== CLASSE: PROPERTY ====================

class Property(Square):
    """Propriedade com cor e valor"""
    
    def __init__(self, name, position, price, color):
        super().__init__(name, position, 'PROPERTY')
        self.price = price
        self.color = color
        
    def draw(self, screen, rect):
        """Desenha a propriedade com faixa colorida no topo"""
        x, y, w, h = rect
        
        # Fundo claro
        pygame.draw.rect(screen, COLORS['light_gray'], rect)
        pygame.draw.rect(screen, COLORS['black'], rect, 2)
        
        # Determina orientação baseado na posição
        if 1 <= self.position <= 9:  # Lado superior
            color_rect = (x, y, w, 20)
            text_y = y + 25
            is_vertical = False
        elif 11 <= self.position <= 19:  # Lado direito
            color_rect = (x, y, 20, h)
            text_y = y + 25
            is_vertical = True
        elif 21 <= self.position <= 29:  # Lado inferior
            color_rect = (x, y + h - 20, w, 20)
            text_y = y + 5
            is_vertical = False
        else:  # Lado esquerdo (31-39)
            color_rect = (x + w - 20, y, 20, h)
            text_y = y + 25
            is_vertical = True
        
        # Desenha faixa colorida
        pygame.draw.rect(screen, self.color, color_rect)
        
        # Texto do nome (ajustado para tamanho menor)
        font_name = pygame.font.Font(None, 16)
        font_price = pygame.font.Font(None, 14)
        
        # Renderiza nome em múltiplas linhas se necessário
        words = self.name.split()
        line_height = 14
        
        if is_vertical:
            # Para casas verticais, rotacionar texto
            for i, word in enumerate(words):
                text_surface = font_name.render(word, True, COLORS['black'])
                text_surface = pygame.transform.rotate(text_surface, -90)
                text_rect = text_surface.get_rect(center=(x + w//2, text_y + i * line_height))
                screen.blit(text_surface, text_rect)
            
            # Preço
            price_text = f"${self.price}m"
            price_surface = font_price.render(price_text, True, COLORS['black'])
            price_surface = pygame.transform.rotate(price_surface, -90)
            price_rect = price_surface.get_rect(center=(x + w//2, y + h - 20))
            screen.blit(price_surface, price_rect)
        else:
            # Para casas horizontais
            for i, word in enumerate(words):
                text_surface = font_name.render(word, True, COLORS['black'])
                text_rect = text_surface.get_rect(center=(x + w//2, text_y + i * line_height))
                screen.blit(text_surface, text_rect)
            
            # Preço
            price_text = f"${self.price}m"
            price_surface = font_price.render(price_text, True, COLORS['black'])
            if 1 <= self.position <= 9:
                price_rect = price_surface.get_rect(center=(x + w//2, y + h - 15))
            else:
                price_rect = price_surface.get_rect(center=(x + w//2, y + h - 25))
            screen.blit(price_surface, price_rect)


# ==================== CLASSE: SPECIAL SQUARE ====================

class SpecialSquare(Square):
    """Casas especiais: Sorte, Cofre, Estação, etc"""
    
    def __init__(self, name, position, icon_type, price=None):
        super().__init__(name, position, 'SPECIAL')
        self.icon_type = icon_type
        self.price = price
        
    def draw(self, screen, rect):
        """Desenha casa especial com ícone"""
        x, y, w, h = rect
        
        # Fundo claro
        pygame.draw.rect(screen, COLORS['light_gray'], rect)
        pygame.draw.rect(screen, COLORS['black'], rect, 2)
        
        # Determina orientação
        is_vertical = 11 <= self.position <= 19 or 31 <= self.position <= 39
        
        # Desenha ícone baseado no tipo
        icon_center_x = x + w // 2
        icon_center_y = y + h // 2 - 10 if not is_vertical else y + h // 2
        
        if self.icon_type == 'SORTE':
            self._draw_luck_icon(screen, icon_center_x, icon_center_y)
        elif self.icon_type == 'COFRE':
            self._draw_chest_icon(screen, icon_center_x, icon_center_y)
        elif self.icon_type == 'ESTACAO':
            self._draw_train_icon(screen, icon_center_x, icon_center_y)
        elif self.icon_type == 'COMPANHIA':
            self._draw_company_icon(screen, icon_center_x, icon_center_y)
        elif self.icon_type == 'IMPOSTO':
            self._draw_tax_icon(screen, icon_center_x, icon_center_y)
        
        # Texto do nome
        font_name = pygame.font.Font(None, 14)
        words = self.name.split()
        line_height = 12
        
        if is_vertical:
            for i, word in enumerate(words):
                text_surface = font_name.render(word, True, COLORS['black'])
                text_surface = pygame.transform.rotate(text_surface, -90)
                text_rect = text_surface.get_rect(center=(x + w//2, y + 20 + i * line_height))
                screen.blit(text_surface, text_rect)
        else:
            text_y = y + h - 25 if 1 <= self.position <= 9 else y + 5
            for i, word in enumerate(words):
                text_surface = font_name.render(word, True, COLORS['black'])
                text_rect = text_surface.get_rect(center=(x + w//2, text_y + i * line_height))
                screen.blit(text_surface, text_rect)
        
        # Preço se houver
        if self.price:
            font_price = pygame.font.Font(None, 13)
            price_text = f"${self.price}m"
            price_surface = font_price.render(price_text, True, COLORS['black'])
            
            if is_vertical:
                price_surface = pygame.transform.rotate(price_surface, -90)
                price_rect = price_surface.get_rect(center=(x + w//2, y + h - 15))
            else:
                if 1 <= self.position <= 9:
                    price_rect = price_surface.get_rect(center=(x + w//2, y + h - 10))
                else:
                    price_rect = price_surface.get_rect(center=(x + w//2, y + h - 10))
            screen.blit(price_surface, price_rect)
    
    def _draw_luck_icon(self, screen, x, y):
        """Desenha ícone de interrogação (?)"""
        font = pygame.font.Font(None, 40)
        text = font.render('?', True, COLORS['dark_red'])
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)
    
    def _draw_chest_icon(self, screen, x, y):
        """Desenha ícone de baú/cofre"""
        # Corpo do baú
        pygame.draw.rect(screen, COLORS['gold'], (x-15, y-5, 30, 20))
        pygame.draw.rect(screen, COLORS['black'], (x-15, y-5, 30, 20), 2)
        # Tampa
        pygame.draw.rect(screen, COLORS['gold'], (x-15, y-15, 30, 12))
        pygame.draw.rect(screen, COLORS['black'], (x-15, y-15, 30, 12), 2)
        # Fechadura
        pygame.draw.circle(screen, COLORS['black'], (x, y), 3)
    
    def _draw_train_icon(self, screen, x, y):
        """Desenha ícone de trem"""
        # Corpo do trem
        pygame.draw.rect(screen, COLORS['black'], (x-15, y-8, 30, 16))
        # Janelas
        pygame.draw.rect(screen, COLORS['white'], (x-10, y-5, 6, 6))
        pygame.draw.rect(screen, COLORS['white'], (x+4, y-5, 6, 6))
        # Rodas
        pygame.draw.circle(screen, COLORS['black'], (x-8, y+10), 4)
        pygame.draw.circle(screen, COLORS['black'], (x+8, y+10), 4)
        pygame.draw.circle(screen, COLORS['white'], (x-8, y+10), 2)
        pygame.draw.circle(screen, COLORS['white'], (x+8, y+10), 2)
    
    def _draw_company_icon(self, screen, x, y):
        """Desenha ícone de companhia (torneira/água)"""
        # Base da torneira
        pygame.draw.rect(screen, COLORS['blue'], (x-3, y-15, 6, 15))
        # Saída
        pygame.draw.circle(screen, COLORS['blue'], (x, y+5), 8)
        # Gotas
        pygame.draw.circle(screen, COLORS['blue'], (x-3, y+15), 3)
        pygame.draw.circle(screen, COLORS['blue'], (x+3, y+18), 2)
    
    def _draw_tax_icon(self, screen, x, y):
        """Desenha ícone de imposto (cifrão)"""
        font = pygame.font.Font(None, 36)
        text = font.render('$', True, COLORS['blue'])
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)


# ==================== CLASSE: CORNER SQUARE ====================

class CornerSquare(Square):
    """Casas dos cantos (maiores)"""
    
    def __init__(self, name, position, corner_type):
        super().__init__(name, position, 'CORNER')
        self.corner_type = corner_type
        
    def draw(self, screen, rect):
        """Desenha casa de canto especial"""
        x, y, w, h = rect
        
        # Fundo especial para cantos
        if self.corner_type == 'GRATIS':
            pygame.draw.rect(screen, COLORS['light_gray'], rect)
        elif self.corner_type == 'PRISAO_VAI':
            pygame.draw.rect(screen, COLORS['orange'], rect)
        elif self.corner_type == 'INICIO':
            pygame.draw.rect(screen, COLORS['light_green'], rect)
        elif self.corner_type == 'PRISAO':
            pygame.draw.rect(screen, COLORS['gray'], rect)
        
        pygame.draw.rect(screen, COLORS['black'], rect, 3)
        
        # Desenha ícone e texto baseado no tipo
        if self.corner_type == 'GRATIS':
            self._draw_free_parking(screen, x, y, w, h)
        elif self.corner_type == 'PRISAO_VAI':
            self._draw_go_to_jail(screen, x, y, w, h)
        elif self.corner_type == 'INICIO':
            self._draw_start(screen, x, y, w, h)
        elif self.corner_type == 'PRISAO':
            self._draw_jail(screen, x, y, w, h)
    
    def _draw_free_parking(self, screen, x, y, w, h):
        """Desenha canto GRÁTIS"""
        font = pygame.font.Font(None, 28)
        text = font.render('GRÁTIS', True, COLORS['black'])
        rect = text.get_rect(center=(x + w//2, y + h//2 - 10))
        screen.blit(text, rect)
        
        # Ícone de carro simplificado
        car_x, car_y = x + w//2, y + h//2 + 20
        pygame.draw.rect(screen, COLORS['red'], (car_x-15, car_y-8, 30, 16), 0)
        pygame.draw.circle(screen, COLORS['black'], (car_x-8, car_y+10), 5)
        pygame.draw.circle(screen, COLORS['black'], (car_x+8, car_y+10), 5)
    
    def _draw_go_to_jail(self, screen, x, y, w, h):
        """Desenha canto VÁ PARA A CADEIA"""
        font_big = pygame.font.Font(None, 22)
        font_small = pygame.font.Font(None, 18)
        
        text1 = font_big.render('VÁ PARA', True, COLORS['black'])
        text2 = font_big.render('A CADEIA', True, COLORS['black'])
        
        rect1 = text1.get_rect(center=(x + w//2, y + h//2 - 15))
        rect2 = text2.get_rect(center=(x + w//2, y + h//2 + 5))
        
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)
        
        # Ícone de pessoa indo para cadeia (seta)
        arrow_y = y + h//2 + 30
        pygame.draw.polygon(screen, COLORS['black'], [
            (x + w//2, arrow_y),
            (x + w//2 - 10, arrow_y + 15),
            (x + w//2 + 10, arrow_y + 15)
        ])
    
    def _draw_start(self, screen, x, y, w, h):
        """Desenha canto PONTO DE PARTIDA"""
        # Seta vermelha grande
        pygame.draw.polygon(screen, COLORS['red'], [
            (x + w//2, y + h//2 - 20),
            (x + w//2 - 20, y + h//2 + 10),
            (x + w//2 + 20, y + h//2 + 10)
        ])
        
        font_big = pygame.font.Font(None, 20)
        font_small = pygame.font.Font(None, 14)
        
        text1 = font_big.render('PONTO DE', True, COLORS['black'])
        text2 = font_big.render('PARTIDA', True, COLORS['black'])
        text3 = font_small.render('SALÁRIO SEMPRE', True, COLORS['black'])
        text4 = font_small.render('QUE PASSAR', True, COLORS['black'])
        
        screen.blit(text1, text1.get_rect(center=(x + w//2, y + 20)))
        screen.blit(text2, text2.get_rect(center=(x + w//2, y + 35)))
        screen.blit(text3, text3.get_rect(center=(x + w//2, y + h - 30)))
        screen.blit(text4, text4.get_rect(center=(x + w//2, y + h - 15)))
    
    def _draw_jail(self, screen, x, y, w, h):
        """Desenha canto NA CADEIA/VISITANTE"""
        font = pygame.font.Font(None, 18)
        
        text1 = font.render('NA CADEIA', True, COLORS['black'])
        text2 = font.render('VISITANTE', True, COLORS['black'])
        
        screen.blit(text1, text1.get_rect(center=(x + w//2, y + h//2 - 10)))
        screen.blit(text2, text2.get_rect(center=(x + w//2, y + h//2 + 10)))
        
        # Barras da cadeia
        for i in range(5):
            bar_x = x + 20 + i * 15
            pygame.draw.line(screen, COLORS['black'], (bar_x, y + h - 40), (bar_x, y + h - 15), 3)


# ==================== CLASSE: BOARD ====================

class Board:
    """Tabuleiro principal do Monopoly"""
    
    def __init__(self):
        self.squares = []
        self.board_offset = 50
        self.create_squares()
    
    def create_squares(self):
        """Cria todas as 40 casas do tabuleiro"""
        
        # Posição 0: GRÁTIS
        self.squares.append(CornerSquare("GRÁTIS", 0, "GRATIS"))
        
        # Lado Superior (posições 1-9)
        self.squares.append(Property("IPANEMA", 1, 220, COLORS['red']))
        self.squares.append(SpecialSquare("SORTE", 2, "SORTE"))
        self.squares.append(Property("LEBLON", 3, 220, COLORS['red']))
        self.squares.append(Property("COPACABANA", 4, 120, COLORS['red']))
        self.squares.append(SpecialSquare("ESTAÇÃO DE METRÔ CONSOLAÇÃO", 5, "ESTACAO", 200))
        self.squares.append(Property("AVENIDA COPACABANA", 6, 240, COLORS['light_yellow_green']))
        self.squares.append(Property("PACAEMBU", 7, 260, COLORS['light_yellow_green']))
        self.squares.append(SpecialSquare("COMPANHIA DE DISTRIBUIÇÃO DE ENERGIA", 8, "COMPANHIA", 150))
        self.squares.append(Property("IBIRAPUERA", 9, 280, COLORS['dark_green']))
        
        # Posição 10: VÁ PARA A CADEIA
        self.squares.append(CornerSquare("VÁ PARA A CADEIA", 10, "PRISAO_VAI"))
        
        # Lado Direito (posições 11-19)
        self.squares.append(Property("FÉRIAS NA TAILÂNDIA", 11, 300, COLORS['dark_green']))
        self.squares.append(Property("COMPRAR DE CHEFE", 12, 300, COLORS['dark_green']))
        self.squares.append(SpecialSquare("COFRE", 13, "COFRE"))
        self.squares.append(Property("JOGO ARCADE TETRIS", 14, 320, COLORS['dark_green']))
        self.squares.append(SpecialSquare("ESTAÇÃO DE METRO RIO DE JANEIRO", 15, "ESTACAO", 400))
        self.squares.append(SpecialSquare("SORTE", 16, "SORTE"))
        self.squares.append(Property("FAQUEI A PROVA I", 17, 350, COLORS['dark_blue']))
        self.squares.append(Property("FAQUEI A PROVA II", 18, 400, COLORS['dark_blue']))
        self.squares.append(SpecialSquare("SORTE", 19, "SORTE"))
        
        # Posição 20: PONTO DE PARTIDA
        self.squares.append(CornerSquare("PONTO DE PARTIDA", 20, "INICIO"))
        
        # Lado Inferior (posições 21-29)
        self.squares.append(Property("AVENIDA SUMARÉ", 21, 60, COLORS['dark_brown']))
        self.squares.append(SpecialSquare("COFRE", 22, "COFRE"))
        self.squares.append(SpecialSquare("PRAÇA DA SÉ", 23, "COFRE", 60))
        self.squares.append(SpecialSquare("IMPOSTO DE RENDA", 24, "IMPOSTO", 200))
        self.squares.append(SpecialSquare("ESTAÇÃO MARACANÃ", 25, "ESTACAO", 200))
        self.squares.append(SpecialSquare("SORTE", 26, "SORTE"))
        self.squares.append(Property("RUA 25 DE MARÇO", 27, 100, COLORS['blue']))
        self.squares.append(Property("AVENIDA SÃO JOÃO", 28, 100, COLORS['blue']))
        self.squares.append(Property("AVENIDA PAULISTA", 29, 120, COLORS['orange']))
        
        # Posição 30: NA CADEIA/VISITANTE
        self.squares.append(CornerSquare("NA CADEIA / VISITANTE", 30, "PRISAO"))
        
        # Lado Esquerdo (posições 31-39)
        self.squares.append(Property("AVENIDA DO OUVIDOR", 31, 140, COLORS['orange']))
        self.squares.append(Property("FLAMINGO", 32, 140, COLORS['pink']))
        self.squares.append(SpecialSquare("COFRE", 33, "COFRE"))
        self.squares.append(Property("BOTAFOGO", 34, 160, COLORS['magenta']))
        self.squares.append(SpecialSquare("SORTE", 35, "SORTE"))
        self.squares.append(Property("AVENIDA ATLÂNTICA", 36, 180, COLORS['magenta']))
        self.squares.append(SpecialSquare("ESTAÇÃO DE METRÔ", 37, "ESTACAO", 200))
        self.squares.append(Property("AVENIDA VIEIRA SOUTO", 38, 200, COLORS['orange']))
        self.squares.append(SpecialSquare("SORTE", 39, "SORTE"))
    
    def draw(self, screen):
        """Desenha o tabuleiro completo"""
        # Fundo
        screen.fill(COLORS['background'])
        
        # Desenha centro com logo
        self.draw_center_logo(screen)
        
        # Desenha todas as casas
        for square in self.squares:
            coords = square.get_coordinates(self.board_offset, CORNER_SIZE, SQUARE_WIDTH, SQUARE_HEIGHT)
            square.draw(screen, coords)
    
    def draw_center_logo(self, screen):
        """Desenha o logo MONOPOLY no centro do tabuleiro em diagonal"""
        # Área central
        center_size = CORNER_SIZE + (9 * SQUARE_WIDTH)
        center_x = self.board_offset + CORNER_SIZE
        center_y = self.board_offset + CORNER_SIZE
        
        # Fundo do centro
        pygame.draw.rect(screen, COLORS['background'], (center_x, center_y, center_size, center_size))
        
        # Texto MONOPOLY em diagonal
        font = pygame.font.Font(None, 80)
        text = font.render('MONOPOLY', True, COLORS['red'])
        
        # Rotaciona o texto 45 graus (diagonal)
        text = pygame.transform.rotate(text, -45)
        
        # Centraliza
        text_rect = text.get_rect(center=(center_x + center_size//2, center_y + center_size//2))
        screen.blit(text, text_rect)
        
        # Adiciona contorno decorativo
        border_padding = 10
        pygame.draw.rect(screen, COLORS['black'], 
                        (center_x + border_padding, center_y + border_padding, 
                         center_size - 2*border_padding, center_size - 2*border_padding), 3)


# ==================== FUNÇÃO PRINCIPAL ====================

def main():
    """Função principal do jogo"""
    # Inicializa PyGame
    pygame.init()
    
    # Cria janela
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('Monopoly - Tabuleiro do Jogo')
    
    # Cria o tabuleiro
    board = Board()
    
    # Clock para controlar FPS
    clock = pygame.time.Clock()
    
    # Loop principal
    running = True
    while running:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Desenha o tabuleiro
        board.draw(screen)
        
        # Atualiza a tela
        pygame.display.flip()
        
        # Controla FPS
        clock.tick(30)
    
    # Encerra PyGame
    pygame.quit()
    sys.exit()


# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    main()
