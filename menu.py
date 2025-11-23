# menu.py
# Módulo responsável pelas telas de Menu e Fim de Jogo

import pygame
import sys
import math

class CampoTexto:
    """Classe para campo de entrada de texto com design melhorado"""
    def __init__(self, x, y, largura, altura, texto_placeholder=""):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_borda_inativa = (100, 100, 120)
        self.cor_borda_ativa = (255, 215, 0)
        self.cor_fundo = (40, 42, 54)
        self.cor_atual = self.cor_borda_inativa
        self.texto = ""
        self.placeholder = texto_placeholder
        self.ativo = False
        self.fonte = pygame.font.SysFont('Arial', 22)
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        """Processa eventos de mouse e teclado"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.ativo = True
                self.cor_atual = self.cor_borda_ativa
            else:
                self.ativo = False
                self.cor_atual = self.cor_borda_inativa
                
        if event.type == pygame.KEYDOWN and self.ativo:
            if event.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                self.ativo = False
                self.cor_atual = self.cor_borda_inativa
            elif len(self.texto) < 15:
                if event.unicode.isprintable():
                    self.texto += event.unicode
                
    def update(self):
        """Atualiza animação do cursor"""
        if self.ativo:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False
            
    def draw(self, screen):
        """Desenha o campo de texto na tela"""
        # Desenha o fundo
        pygame.draw.rect(screen, self.cor_fundo, self.rect, border_radius=8)
        
        # Desenha a borda
        pygame.draw.rect(screen, self.cor_atual, self.rect, 3, border_radius=8)
        
        # Desenha o texto ou placeholder
        texto_display = self.texto if self.texto else self.placeholder
        cor_texto = (255, 255, 255) if self.texto else (120, 120, 140)
        
        texto_surface = self.fonte.render(texto_display, True, cor_texto)
        texto_rect = texto_surface.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        screen.blit(texto_surface, texto_rect)
        
        # Desenha o cursor piscante
        if self.ativo and self.cursor_visible and self.texto:
            cursor_x = texto_rect.right + 2
            cursor_y = self.rect.centery - 12
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + 24), 2)


class Botao:
    """Classe para botões clicáveis com efeitos visuais"""
    def __init__(self, x, y, largura, altura, texto, cor_normal=(70, 130, 180), cor_hover=(100, 160, 210), tamanho_fonte=24):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_normal = cor_normal
        self.cor_hover = cor_hover
        self.cor_atual = cor_normal
        self.fonte = pygame.font.SysFont('Arial', tamanho_fonte, bold=True)
        self.pressionado = False
        self.escala = 1.0
        
    def draw(self, screen):
        """Desenha o botão na tela com efeito de sombra"""
        # Sombra
        sombra_rect = self.rect.copy()
        sombra_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 100), sombra_rect, border_radius=12)
        
        # Botão principal
        rect_atual = self.rect.copy()
        if self.pressionado:
            rect_atual.y += 2
        
        pygame.draw.rect(screen, self.cor_atual, rect_atual, border_radius=12)
        
        # Brilho no topo
        brilho_rect = pygame.Rect(rect_atual.x, rect_atual.y, rect_atual.width, rect_atual.height // 3)
        brilho_surface = pygame.Surface((brilho_rect.width, brilho_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(brilho_surface, (255, 255, 255, 30), brilho_surface.get_rect(), border_radius=12)
        screen.blit(brilho_surface, brilho_rect)
        
        # Texto centralizado
        texto_surface = self.fonte.render(self.texto, True, (255, 255, 255))
        texto_rect = texto_surface.get_rect(center=rect_atual.center)
        screen.blit(texto_surface, texto_rect)
        
    def handle_event(self, event):
        """Detecta clique no botão"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressionado = True
        
        if event.type == pygame.MOUSEBUTTONUP:
            if self.pressionado and self.rect.collidepoint(event.pos):
                self.pressionado = False
                return True
            self.pressionado = False
            
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.cor_atual = self.cor_hover
            else:
                self.cor_atual = self.cor_normal
        
        return False


class MenuInicial:
    """Tela de Menu Inicial do jogo com design aprimorado"""
    def __init__(self, screen):
        self.screen = screen
        self.largura = screen.get_width()
        self.altura = screen.get_height()
        
        # Fontes
        self.fonte_titulo = pygame.font.SysFont('Arial', 88, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont('Arial', 30)
        self.fonte_texto = pygame.font.SysFont('Arial', 22)
        
        # Número de jogadores selecionado
        self.num_jogadores = 2
        
        # Animação do título
        self.titulo_offset = 0
        self.titulo_direction = 1
        
        # Campos de texto para nomes dos jogadores
        self.campos_texto = []
        self.criar_campos_texto()
        
        # Botões de seleção de jogadores (2 a 6 jogadores)
        self.botoes_num_jogadores = []
        for i in range(2, 7):  # 2, 3, 4, 5, 6 jogadores
            x = self.largura // 2 - 275 + (i - 2) * 110
            y = 240
            botao = BotaoCircular(x, y, 45, str(i))
            self.botoes_num_jogadores.append(botao)
        
        # Botão Iniciar Jogo
        self.botao_iniciar = Botao(
            self.largura // 2 - 120,
            self.altura - 120,
            240,
            70,
            "INICIAR JOGO",
            cor_normal=(46, 204, 113),
            cor_hover=(39, 174, 96),
            tamanho_fonte=26
        )
        
        # Partículas de fundo (efeito visual)
        self.particulas = []
        for _ in range(30):
            self.particulas.append({
                'x': pygame.math.Vector2(
                    random.uniform(0, self.largura),
                    random.uniform(0, self.altura)
                ),
                'vel': pygame.math.Vector2(
                    random.uniform(-0.5, 0.5),
                    random.uniform(-0.5, 0.5)
                ),
                'tamanho': random.uniform(1, 3)
            })
        
    def criar_campos_texto(self):
        """Cria campos de texto baseado no número de jogadores"""
        self.campos_texto = []
        
        # Ajusta o layout baseado no número de jogadores
        if self.num_jogadores <= 3:
            # Layout de 1 coluna
            espacamento = 75
            inicio_y = 340
            for i in range(self.num_jogadores):
                campo = CampoTexto(
                    self.largura // 2 - 180,
                    inicio_y + i * espacamento,
                    360,
                    60,
                    f"Jogador {i + 1}"
                )
                self.campos_texto.append(campo)
        else:
            # Layout de 2 colunas
            espacamento = 75
            inicio_y = 320
            coluna_esquerda_x = self.largura // 2 - 380
            coluna_direita_x = self.largura // 2 + 20
            
            for i in range(self.num_jogadores):
                if i < 3:
                    # Primeira coluna
                    campo = CampoTexto(
                        coluna_esquerda_x,
                        inicio_y + i * espacamento,
                        360,
                        60,
                        f"Jogador {i + 1}"
                    )
                else:
                    # Segunda coluna
                    campo = CampoTexto(
                        coluna_direita_x,
                        inicio_y + (i - 3) * espacamento,
                        360,
                        60,
                        f"Jogador {i + 1}"
                    )
                self.campos_texto.append(campo)
    
    def update(self):
        """Atualiza animações"""
        # Animação do título
        self.titulo_offset += 0.3 * self.titulo_direction
        if abs(self.titulo_offset) > 5:
            self.titulo_direction *= -1
        
        # Atualiza partículas
        for p in self.particulas:
            p['x'] += p['vel']
            if p['x'][0] < 0:
                p['x'][0] = self.largura
            if p['x'][0] > self.largura:
                p['x'][0] = 0
            if p['x'][1] < 0:
                p['x'][1] = self.altura
            if p['x'][1] > self.altura:
                p['x'][1] = 0
        
        # Atualiza campos de texto
        for campo in self.campos_texto:
            campo.update()
    
    def handle_events(self, event):
        """Processa eventos do menu"""
        # Eventos dos campos de texto
        for campo in self.campos_texto:
            campo.handle_event(event)
        
        # Eventos dos botões de número de jogadores
        for i, botao in enumerate(self.botoes_num_jogadores):
            if botao.handle_event(event):
                self.num_jogadores = i + 2
                self.criar_campos_texto()
        
        # Evento do botão iniciar
        if self.botao_iniciar.handle_event(event):
            nomes = []
            for i, campo in enumerate(self.campos_texto):
                nome = campo.texto.strip()
                if not nome:
                    nome = f"Jogador {i + 1}"
                nomes.append(nome)
            return ("INICIAR_JOGO", nomes)
        
        return None
    
    def draw(self):
        """Desenha o menu na tela"""
        # Gradiente de fundo
        for y in range(self.altura):
            progresso = y / self.altura
            cor = (
                int(25 + progresso * 10),
                int(25 + progresso * 15),
                int(50 + progresso * 20)
            )
            pygame.draw.line(self.screen, cor, (0, y), (self.largura, y))
        
        # Desenha partículas
        for p in self.particulas:
            pygame.draw.circle(self.screen, (100, 100, 150, 50), (int(p['x'][0]), int(p['x'][1])), int(p['tamanho']))
        
        # Título com efeito de sombra e brilho
        titulo_texto = "MONOPOLY"
        
        # Sombra do título
        sombra_titulo = self.fonte_titulo.render(titulo_texto, True, (0, 0, 0))
        sombra_rect = sombra_titulo.get_rect(center=(self.largura // 2 + 5, 90 + self.titulo_offset + 5))
        self.screen.blit(sombra_titulo, sombra_rect)
        
        # Título principal
        titulo = self.fonte_titulo.render(titulo_texto, True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(self.largura // 2, 90 + self.titulo_offset))
        self.screen.blit(titulo, titulo_rect)
        
        # Brilho do título
        brilho_titulo = self.fonte_titulo.render(titulo_texto, True, (255, 255, 200, 100))
        brilho_rect = brilho_titulo.get_rect(center=(self.largura // 2 - 2, 88 + self.titulo_offset))
        self.screen.blit(brilho_titulo, brilho_rect)
        
        # Linha decorativa
        pygame.draw.line(self.screen, (255, 215, 0), 
                        (self.largura // 2 - 200, 150), 
                        (self.largura // 2 + 200, 150), 3)
        
        # Subtítulo - Número de Jogadores
        subtitulo = self.fonte_subtitulo.render("Selecione o número de jogadores:", True, (220, 220, 240))
        subtitulo_rect = subtitulo.get_rect(center=(self.largura // 2, 195))
        self.screen.blit(subtitulo, subtitulo_rect)
        
        # Botões de número de jogadores
        for i, botao in enumerate(self.botoes_num_jogadores):
            botao.selecionado = (i + 2 == self.num_jogadores)
            botao.draw(self.screen)
        
        # Texto - Digite os nomes
        texto_nomes = self.fonte_subtitulo.render("Digite os nomes dos jogadores:", True, (220, 220, 240))
        texto_nomes_rect = texto_nomes.get_rect(center=(self.largura // 2, 285))
        self.screen.blit(texto_nomes, texto_nomes_rect)
        
        # Campos de texto
        for campo in self.campos_texto:
            campo.draw(self.screen)
        
        # Botão Iniciar
        self.botao_iniciar.draw(self.screen)


class BotaoCircular:
    """Botão circular para seleção de número de jogadores"""
    def __init__(self, x, y, raio, texto):
        self.x = x
        self.y = y
        self.raio = raio
        self.texto = texto
        self.selecionado = False
        self.hover = False
        self.fonte = pygame.font.SysFont('Arial', 32, bold=True)
        
    def handle_event(self, event):
        """Detecta clique no botão"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            distancia = math.sqrt((event.pos[0] - self.x)**2 + (event.pos[1] - self.y)**2)
            if distancia <= self.raio:
                return True
        
        if event.type == pygame.MOUSEMOTION:
            distancia = math.sqrt((event.pos[0] - self.x)**2 + (event.pos[1] - self.y)**2)
            self.hover = distancia <= self.raio
        
        return False
    
    def draw(self, screen):
        """Desenha o botão circular"""
        # Sombra
        pygame.draw.circle(screen, (0, 0, 0, 100), (self.x + 3, self.y + 3), self.raio)
        
        # Cor do botão
        if self.selecionado:
            cor = (255, 215, 0)
            cor_borda = (255, 235, 50)
        elif self.hover:
            cor = (100, 160, 210)
            cor_borda = (120, 180, 230)
        else:
            cor = (70, 130, 180)
            cor_borda = (90, 150, 200)
        
        # Círculo principal
        pygame.draw.circle(screen, cor, (self.x, self.y), self.raio)
        
        # Borda
        pygame.draw.circle(screen, cor_borda, (self.x, self.y), self.raio, 4)
        
        # Texto
        texto_surface = self.fonte.render(self.texto, True, (255, 255, 255))
        texto_rect = texto_surface.get_rect(center=(self.x, self.y))
        screen.blit(texto_surface, texto_rect)


class TelaFimDeJogo:
    """Tela de Fim de Jogo com estatísticas aprimorada"""
    def __init__(self, screen, jogo_backend):
        self.screen = screen
        self.largura = screen.get_width()
        self.altura = screen.get_height()
        self.jogo_backend = jogo_backend
        
        # Fontes
        self.fonte_titulo = pygame.font.SysFont('Arial', 70, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont('Arial', 36, bold=True)
        self.fonte_texto = pygame.font.SysFont('Arial', 20)
        self.fonte_grande = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Determina o vencedor
        self.vencedor = self.determinar_vencedor()
        
        # Animação
        self.animacao_offset = 0
        self.particulas_confete = []
        for _ in range(50):
            self.particulas_confete.append({
                'x': random.uniform(0, self.largura),
                'y': -random.uniform(0, 200),
                'vel_y': random.uniform(2, 5),
                'vel_x': random.uniform(-1, 1),
                'cor': [
                    (255, 215, 0),
                    (255, 100, 100),
                    (100, 255, 100),
                    (100, 100, 255),
                    (255, 100, 255)
                ][int(random.uniform(0, 5))]
            })
        
        # Botões
        self.botao_novo_jogo = Botao(
            self.largura // 2 - 250,
            self.altura - 100,
            220,
            65,
            "NOVO JOGO",
            cor_normal=(46, 204, 113),
            cor_hover=(39, 174, 96),
            tamanho_fonte=24
        )
        
        self.botao_sair = Botao(
            self.largura // 2 + 30,
            self.altura - 100,
            220,
            65,
            "SAIR",
            cor_normal=(231, 76, 60),
            cor_hover=(192, 57, 43),
            tamanho_fonte=24
        )
    
    def determinar_vencedor(self):
        """Determina o vencedor baseado no patrimônio total"""
        jogadores_ativos = [j for j in self.jogo_backend.jogadores]
        
        if not jogadores_ativos:
            return None
        
        patrimonios = []
        for jogador in jogadores_ativos:
            saldo = self.jogo_backend.banco.consultar_saldo(jogador.nome)
            valor_propriedades = sum(prop.preco_compra for prop in jogador.propriedades)
            patrimonio_total = saldo + valor_propriedades
            patrimonios.append((jogador, patrimonio_total, saldo, valor_propriedades))
        
        patrimonios.sort(key=lambda x: x[1], reverse=True)
        return patrimonios
    
    def update(self):
        """Atualiza animações"""
        self.animacao_offset = (self.animacao_offset + 1) % 360
        
        # Atualiza confetes
        for p in self.particulas_confete:
            p['y'] += p['vel_y']
            p['x'] += p['vel_x']
            if p['y'] > self.altura:
                p['y'] = -10
                p['x'] = random.uniform(0, self.largura)
    
    def handle_events(self, event):
        """Processa eventos da tela de fim de jogo"""
        if self.botao_novo_jogo.handle_event(event):
            return "NOVO_JOGO"
        
        if self.botao_sair.handle_event(event):
            return "SAIR"
        
        return None
    
    def draw(self):
        """Desenha a tela de fim de jogo"""
        # Gradiente de fundo
        for y in range(self.altura):
            progresso = y / self.altura
            cor = (
                int(20 + progresso * 30),
                int(20 + progresso * 25),
                int(40 + progresso * 30)
            )
            pygame.draw.line(self.screen, cor, (0, y), (self.largura, y))
        
        # Desenha confetes
        for p in self.particulas_confete:
            pygame.draw.circle(self.screen, p['cor'], (int(p['x']), int(p['y'])), 4)
        
        # Título com animação
        brilho = abs(math.sin(self.animacao_offset * 0.05)) * 50 + 205
        titulo = self.fonte_titulo.render("FIM DE JOGO!", True, (255, int(brilho), 0))
        titulo_rect = titulo.get_rect(center=(self.largura // 2, 60))
        
        # Sombra do título
        sombra = self.fonte_titulo.render("FIM DE JOGO!", True, (0, 0, 0))
        sombra_rect = sombra.get_rect(center=(self.largura // 2 + 4, 64))
        self.screen.blit(sombra, sombra_rect)
        self.screen.blit(titulo, titulo_rect)
        
        if self.vencedor and len(self.vencedor) > 0:
            # Vencedor
            vencedor_obj, patrimonio, saldo, props = self.vencedor[0]
            
            # Troféu
            trofeu = self.fonte_grande.render("🏆", True, (255, 215, 0))
            trofeu_rect = trofeu.get_rect(center=(self.largura // 2, 135))
            self.screen.blit(trofeu, trofeu_rect)
            
            texto_vencedor = self.fonte_subtitulo.render(
                f"VENCEDOR: {vencedor_obj.nome.upper()}",
                True,
                (255, 215, 0)
            )
            texto_vencedor_rect = texto_vencedor.get_rect(center=(self.largura // 2, 180))
            
            # Sombra
            sombra_venc = self.fonte_subtitulo.render(
                f"VENCEDOR: {vencedor_obj.nome.upper()}",
                True,
                (0, 0, 0)
            )
            sombra_venc_rect = sombra_venc.get_rect(center=(self.largura // 2 + 2, 182))
            self.screen.blit(sombra_venc, sombra_venc_rect)
            self.screen.blit(texto_vencedor, texto_vencedor_rect)
            
            # Patrimônio do vencedor
            texto_patrimonio = self.fonte_texto.render(
                f"Patrimônio Total: R$ {patrimonio:,.2f}",
                True,
                (200, 255, 200)
            )
            texto_patrimonio_rect = texto_patrimonio.get_rect(center=(self.largura // 2, 215))
            self.screen.blit(texto_patrimonio, texto_patrimonio_rect)
        
        # Painel de estatísticas
        num_jogadores = len(self.vencedor)
        
        # Ajusta layout baseado no número de jogadores
        if num_jogadores <= 3:
            # Layout de 1 coluna
            self._desenhar_ranking_coluna_unica()
        else:
            # Layout de 2 colunas
            self._desenhar_ranking_duas_colunas()
        
        # Botões
        self.botao_novo_jogo.draw(self.screen)
        self.botao_sair.draw(self.screen)
    
    def _desenhar_ranking_coluna_unica(self):
        """Desenha ranking em uma coluna (até 3 jogadores)"""
        painel_y = 260
        painel_altura = min(450, len(self.vencedor) * 120 + 80)
        painel_rect = pygame.Rect(self.largura // 2 - 400, painel_y, 800, painel_altura)
        
        # Fundo do painel
        painel_surface = pygame.Surface((painel_rect.width, painel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(painel_surface, (30, 35, 50, 230), painel_surface.get_rect(), border_radius=15)
        self.screen.blit(painel_surface, painel_rect)
        pygame.draw.rect(self.screen, (100, 120, 150), painel_rect, 3, border_radius=15)
        
        # Título
        titulo_stats = self.fonte_subtitulo.render("ESTATÍSTICAS FINAIS", True, (220, 220, 240))
        titulo_stats_rect = titulo_stats.get_rect(center=(self.largura // 2, painel_y + 30))
        self.screen.blit(titulo_stats, titulo_stats_rect)
        
        # Jogadores
        y_atual = painel_y + 75
        espacamento = 110
        
        for i, (jogador, patrimonio, saldo, valor_props) in enumerate(self.vencedor):
            self._desenhar_jogador_stats(i, jogador, patrimonio, saldo, valor_props, 
                                        self.largura // 2 - 360, y_atual, True)
            y_atual += espacamento
    
    def _desenhar_ranking_duas_colunas(self):
        """Desenha ranking em duas colunas (4-6 jogadores)"""
        num_jogadores = len(self.vencedor)
        painel_y = 250
        
        # Calcula altura do painel
        jogadores_por_coluna = (num_jogadores + 1) // 2
        painel_altura = min(500, jogadores_por_coluna * 100 + 80)
        painel_rect = pygame.Rect(self.largura // 2 - 500, painel_y, 1000, painel_altura)
        
        # Fundo do painel
        painel_surface = pygame.Surface((painel_rect.width, painel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(painel_surface, (30, 35, 50, 230), painel_surface.get_rect(), border_radius=15)
        self.screen.blit(painel_surface, painel_rect)
        pygame.draw.rect(self.screen, (100, 120, 150), painel_rect, 3, border_radius=15)
        
        # Título
        titulo_stats = self.fonte_subtitulo.render("ESTATÍSTICAS FINAIS", True, (220, 220, 240))
        titulo_stats_rect = titulo_stats.get_rect(center=(self.largura // 2, painel_y + 30))
        self.screen.blit(titulo_stats, titulo_stats_rect)
        
        # Desenha jogadores em duas colunas
        y_inicial = painel_y + 75
        espacamento = 100
        coluna_esquerda_x = self.largura // 2 - 470
        coluna_direita_x = self.largura // 2 + 30
        
        for i, (jogador, patrimonio, saldo, valor_props) in enumerate(self.vencedor):
            if i < jogadores_por_coluna:
                # Coluna esquerda
                x_base = coluna_esquerda_x
                y_atual = y_inicial + i * espacamento
            else:
                # Coluna direita
                x_base = coluna_direita_x
                y_atual = y_inicial + (i - jogadores_por_coluna) * espacamento
            
            self._desenhar_jogador_stats(i, jogador, patrimonio, saldo, valor_props, 
                                        x_base, y_atual, False)
    
    def _desenhar_jogador_stats(self, posicao, jogador, patrimonio, saldo, valor_props, x_base, y_base, compacto):
        """Desenha as estatísticas de um jogador"""
        # Medalhas/Posição
        if posicao == 0:
            medalha = "🥇"
            cor_posicao = (255, 215, 0)
        elif posicao == 1:
            medalha = "🥈"
            cor_posicao = (192, 192, 192)
        elif posicao == 2:
            medalha = "🥉"
            cor_posicao = (205, 127, 50)
        else:
            medalha = f"{posicao+1}º"
            cor_posicao = (200, 200, 200)
        
        fonte_medalha = self.fonte_grande if compacto else self.fonte_texto
        
        # Medalha
        texto_medalha = fonte_medalha.render(medalha, True, cor_posicao)
        self.screen.blit(texto_medalha, (x_base, y_base - 5))
        
        # Nome
        texto_nome = self.fonte_grande.render(jogador.nome, True, cor_posicao)
        self.screen.blit(texto_nome, (x_base + 50, y_base))
        
        # Saldo
        texto_saldo = self.fonte_texto.render(
            f"💰 Saldo: R$ {saldo:,.2f}",
            True,
            (150, 255, 150)
        )
        self.screen.blit(texto_saldo, (x_base + 50, y_base + 28))
        
        # Propriedades
        texto_props = self.fonte_texto.render(
            f"🏠 Propriedades: {len(jogador.propriedades)} (R$ {valor_props:,.2f})",
            True,
            (150, 200, 255)
        )
        self.screen.blit(texto_props, (x_base + 50, y_base + 50))


# Importação do random para as partículas
import random