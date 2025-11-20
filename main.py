import pygame
import sys
import os
import random
from jogo import Jogo
from propriedades import Propriedade
from menu import MenuInicial, TelaFimDeJogo

# --- 1. Inicialização e Configurações ---
pygame.init()
pygame.font.init()

try:
    FONTE_PADRAO = pygame.font.SysFont('Arial', 15)
    FONTE_PEQUENA = pygame.font.SysFont('Arial', 10)
except Exception as e:
    print(f"Erro ao carregar fonte: {e}. Usando fonte padrão.")
    FONTE_PADRAO = pygame.font.Font(None, 15)
    FONTE_PEQUENA = pygame.font.Font(None, 10)

LARGURA_JANELA = 1440
ALTURA_JANELA = 1000
screen = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
pygame.display.set_caption("Monopoly")
COR_FUNDO = (0, 0, 0)

# --- 2. Carregamento de Assets ---
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
botao_lancar_img = carregar_imagem('botao_lancar.png', alpha=True)
painel_ui_img = carregar_imagem('painel_ui.png', alpha=True)
fazar_proposta_img = carregar_imagem('fazer_proposta.png', alpha=True)
fundo_interativo_img = carregar_imagem('fundo_interativos.png', alpha=True)

# --- Carregando Peões (até 6 jogadores) ---
peao_jogador_1_img = carregar_imagem('peao_1.png', alpha=True)
peao_jogador_2_img = carregar_imagem('peao_2.png', alpha=True)
peao_jogador_3_img = carregar_imagem('peao_3.png', alpha=True)
peao_jogador_4_img = carregar_imagem('peao_4.png', alpha=True)

# Para jogadores 5 e 6, se não tiver imagens específicas, reutiliza as primeiras
try:
    peao_jogador_5_img = carregar_imagem('peao_5.png', alpha=True)
except:
    peao_jogador_5_img = peao_jogador_1_img  # Reutiliza peão 1
    
try:
    peao_jogador_6_img = carregar_imagem('peao_6.png', alpha=True)
except:
    peao_jogador_6_img = peao_jogador_2_img  # Reutiliza peão 2

# --- Carregando os Dados ---
imagens_dados = []
for i in range(1, 7):
    nome_arquivo = f'dado_{i}.png'
    imagens_dados.append(carregar_imagem(nome_arquivo, alpha=True))

botao_comprar_img = carregar_imagem('comprar.png', alpha=True)
botao_passar_img = carregar_imagem('passar_vez.png', alpha=True)

# --- VARIÁVEIS GLOBAIS DO JOGO ---
jogo_backend = None
nomes_dos_jogadores = []
dado1_valor = 6
dado2_valor = 6
estado_jogo = "MENU"
posicao_para_decisao = 0

# --- Constantes de posicionamento (EXPANDIDO PARA 6 JOGADORES) ---
OFFSETS_PEOES = [
    (10, 10),   # Jogador 1
    (45, 10),   # Jogador 2
    (10, 45),   # Jogador 3
    (45, 45),   # Jogador 4
    (25, 10),   # Jogador 5 (centralizado no topo)
    (25, 45)    # Jogador 6 (centralizado embaixo)
]

IMAGENS_PEOES = [
    peao_jogador_1_img,
    peao_jogador_2_img,
    peao_jogador_3_img,
    peao_jogador_4_img,
    peao_jogador_5_img,
    peao_jogador_6_img
]

# Posições para exibir informações dos jogadores (EXPANDIDO PARA 6)
POSICOES_TEXTO_JOGADOR = [
    (33, 85),     # Jogador 1 - Superior Esquerdo
    (1211, 85),   # Jogador 2 - Superior Direito
    (33, 400),    # Jogador 3 - Meio Esquerdo
    (1211, 400),  # Jogador 4 - Meio Direito
    (30, 677),    # Jogador 5 - Inferior Esquerdo
    (1210, 677)   # Jogador 6 - Inferior Direito
]

POSICOES_CASAS_XY = [
    (1048, 837.37), (972, 837.37), (899, 837.37), (823, 837.37),
    (748, 837.37), (672, 837.37), (599, 837.37), (523, 837.37),
    (449, 837.37), (374, 837.37), (262, 837.37), (262, 762.37),
    (262, 687.37), (262, 613.37), (262, 538.37), (262, 464.37),
    (262, 388.37), (262, 313.37), (262, 240.37), (262, 164.37),
    (262, 49.37), (374, 49.37), (449, 49.37), (523, 49.37),
    (598, 49.37), (671, 49.37), (747, 49.37), (822, 49.37),
    (898, 49.37), (973, 49.37), (1048, 49.37), (1048, 165.37),
    (1048, 241.37), (1048, 319.37), (1048, 389.37), (1048, 464.37),
    (1048, 539.37), (1048, 613.37), (1048, 688.37), (1048, 762.37),
]

# --- Posições e Rects ---
X_TABULEIRO = 260
Y_TABULEIRO = 49
TAMANHO_TABULEIRO = 924
tabuleiro_img = pygame.transform.scale(tabuleiro_img, (TAMANHO_TABULEIRO, TAMANHO_TABULEIRO))

X_PAINEL_UI = 397
Y_PAINEL_UI = 670
X_FUNDO_INTERA = 561
Y_FUNDO_INTERA = 690

X_BOTAO_PROPOSTA = 408
Y_BOTAO_PROPOSTA = 743
LARGURA_BOTAO_PROPOSTA = 128
ALTURA_BOTAO_PROPOSTA = 29
botao_proposta_rect = pygame.Rect(X_BOTAO_PROPOSTA, Y_BOTAO_PROPOSTA, LARGURA_BOTAO_PROPOSTA, ALTURA_BOTAO_PROPOSTA)

X_BOTAO_LANCAR = 408
Y_BOTAO_LANCAR = 777
LARGURA_BOTAO_LANCAR = 128
ALTURA_BOTAO_LANCAR = 29
botao_lancar_rect = pygame.Rect(X_BOTAO_LANCAR, Y_BOTAO_LANCAR, LARGURA_BOTAO_LANCAR, ALTURA_BOTAO_LANCAR)

X_BOTAO_COMPRAR = 640
Y_BOTAO_COMPRAR = 714
LARGURA_BOTAO_COMPRAR = 125
ALTURA_BOTAO_COMPRAR = 29
botao_comprar_rect = pygame.Rect(X_BOTAO_COMPRAR, Y_BOTAO_COMPRAR, LARGURA_BOTAO_COMPRAR, ALTURA_BOTAO_COMPRAR)

X_BOTAO_PASSAR = 640
Y_BOTAO_PASSAR = 748
LARGURA_BOTAO_PASSAR = 125
ALTURA_BOTAO_PASSAR = 29
botao_passar_rect = pygame.Rect(X_BOTAO_PASSAR, Y_BOTAO_PASSAR, LARGURA_BOTAO_PASSAR, ALTURA_BOTAO_PASSAR)

X_DADO_1, Y_DADO_1 = 593, 718
X_DADO_2, Y_DADO_2 = 685, 718
X_TEXTO_TURNO, Y_TEXTO_TURNO = 410, 691
COR_TEXTO_BRANCO = (255, 255, 255)
X_TEXTO_CARTA, Y_TEXTO_CARTA = 576, 689

# --- INICIALIZA AS TELAS ---
menu_inicial = MenuInicial(screen)
tela_fim_jogo = None

# --- Game Loop Principal ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- PROCESSAMENTO POR ESTADO ---
        if estado_jogo == "MENU":
            resultado = menu_inicial.handle_events(event)
            if resultado:
                acao, nomes = resultado
                if acao == "INICIAR_JOGO":
                    nomes_dos_jogadores = nomes
                    jogo_backend = Jogo(nomes_dos_jogadores)
                    estado_jogo = "INICIO_TURNO"
                    print(f"Jogo iniciado com {len(nomes)} jogadores: {nomes_dos_jogadores}")
        
        elif estado_jogo == "FIM_JOGO":
            resultado = tela_fim_jogo.handle_events(event)
            if resultado == "NOVO_JOGO":
                menu_inicial = MenuInicial(screen)
                estado_jogo = "MENU"
            elif resultado == "SAIR":
                running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f"Clique do mouse em: {event.pos}")
            
            if estado_jogo == "INICIO_TURNO":
                if botao_lancar_rect.collidepoint(event.pos):
                    casa_onde_parei = jogo_backend.rolar_dados_e_mover()
                    print(f"Backend moveu jogador para: {casa_onde_parei.nome}")
                    
                    dado1_valor = jogo_backend.ultimo_d1
                    dado2_valor = jogo_backend.ultimo_d2
                    
                    acao_necessaria = jogo_backend.obter_acao_para_casa(casa_onde_parei)
                    
                    if acao_necessaria["tipo"] == "DECISAO_COMPRA":
                        print("Backend: 'DECISAO_COMPRA'. Mudando estado da UI.")
                        jogador_que_moveu = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
                        posicao_para_decisao = jogador_que_moveu.posicao
                        estado_jogo = "OPCAO_COMPRA"
                    
                    elif acao_necessaria["tipo"] in ["ACAO_AUTOMATICA", "PAGAR_ALUGUEL"]:
                        print(f"Backend: '{acao_necessaria['tipo']}'. Executando e finalizando turno.")
                        jogo_backend.executar_acao_automatica(casa_onde_parei)
                        jogo_backend.finalizar_turno()
                    
                    else:
                        print("Backend: 'NENHUMA_ACAO'. Finalizando turno.")
                        jogo_backend.finalizar_turno()
                
                if botao_proposta_rect.collidepoint(event.pos):
                    print("AÇÃO: Fazer uma proposta!")
            
            elif estado_jogo == "OPCAO_COMPRA":
                if botao_comprar_rect.collidepoint(event.pos):
                    print("UI: Clicou 'Comprar'. Chamando backend...")
                    jogo_backend.executar_compra()
                    jogo_backend.finalizar_turno()
                    estado_jogo = "INICIO_TURNO"
                
                if botao_passar_rect.collidepoint(event.pos):
                    print("UI: Clicou 'Passar'. Chamando backend...")
                    jogo_backend.finalizar_turno()
                    estado_jogo = "INICIO_TURNO"
        
        # Tecla ESC para acionar fim de jogo (para teste)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if estado_jogo not in ["MENU", "FIM_JOGO"] and jogo_backend:
                tela_fim_jogo = TelaFimDeJogo(screen, jogo_backend)
                estado_jogo = "FIM_JOGO"
    
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
        screen.blit(painel_ui_img, (X_PAINEL_UI, Y_PAINEL_UI))
        screen.blit(fundo_interativo_img, (X_FUNDO_INTERA, Y_FUNDO_INTERA))
        
        ALTURA_LINHA_TEXTO = 20
        
        # Desenha informações de todos os jogadores
        for i in range(len(jogo_backend.jogadores)):
            jogador_obj = jogo_backend.jogadores[i]
            posicao_base = POSICOES_TEXTO_JOGADOR[i]
            
            saldo = jogo_backend.banco.consultar_saldo(jogador_obj.nome)
            texto_status = f"{jogador_obj.nome}: R$ {saldo}"
            img_status = FONTE_PADRAO.render(texto_status, True, COR_TEXTO_BRANCO)
            screen.blit(img_status, posicao_base)
            
            linha_atual = 1
            # Limita a quantidade de propriedades mostradas para não sobrecarregar a tela
            max_props_visiveis = 8
            for idx, prop in enumerate(jogador_obj.propriedades):
                if idx >= max_props_visiveis:
                    texto_prop = f"  + {len(jogador_obj.propriedades) - max_props_visiveis} mais..."
                    img_prop = FONTE_PEQUENA.render(texto_prop, True, COR_TEXTO_BRANCO)
                    posicao_y = posicao_base[1] + (linha_atual * ALTURA_LINHA_TEXTO)
                    posicao_prop = (posicao_base[0], posicao_y)
                    screen.blit(img_prop, posicao_prop)
                    break
                    
                nome_prop = prop.nome
                # Trunca nomes muito longos
                if len(nome_prop) > 20:
                    nome_prop = nome_prop[:17] + "..."
                texto_prop = f"  - {nome_prop}"
                img_prop = FONTE_PEQUENA.render(texto_prop, True, COR_TEXTO_BRANCO)
                posicao_y = posicao_base[1] + (linha_atual * ALTURA_LINHA_TEXTO)
                posicao_prop = (posicao_base[0], posicao_y)
                screen.blit(img_prop, posicao_prop)
                linha_atual += 1
        
        indice_jogador = jogo_backend.indice_turno_atual
        jogador_obj_atual = jogo_backend.jogadores[indice_jogador]
        texto_do_turno = f"Vez de: {jogador_obj_atual.nome}"
        img_texto_turno = FONTE_PADRAO.render(texto_do_turno, True, COR_TEXTO_BRANCO)
        screen.blit(img_texto_turno, (X_TEXTO_TURNO, Y_TEXTO_TURNO))
        
        if estado_jogo == "INICIO_TURNO":
            screen.blit(fazar_proposta_img, (X_BOTAO_PROPOSTA, Y_BOTAO_PROPOSTA))
            screen.blit(botao_lancar_img, (X_BOTAO_LANCAR, Y_BOTAO_LANCAR))
            screen.blit(imagens_dados[dado1_valor - 1], (X_DADO_1, Y_DADO_1))
            screen.blit(imagens_dados[dado2_valor - 1], (X_DADO_2, Y_DADO_2))
        
        elif estado_jogo == "OPCAO_COMPRA":
            casa_obj = jogo_backend.tabuleiro.get_casa(posicao_para_decisao)
            nome_da_casa = casa_obj.nome
            img_texto_casa = FONTE_PEQUENA.render(nome_da_casa, True, COR_TEXTO_BRANCO)
            screen.blit(img_texto_casa, (X_TEXTO_CARTA, Y_TEXTO_CARTA))
            
            screen.blit(botao_comprar_img, (X_BOTAO_COMPRAR, Y_BOTAO_COMPRAR))
            screen.blit(botao_passar_img, (X_BOTAO_PASSAR, Y_BOTAO_PASSAR))
            screen.blit(imagens_dados[dado1_valor - 1], (X_BOTAO_PROPOSTA, Y_BOTAO_PROPOSTA))
            screen.blit(imagens_dados[dado2_valor - 1], (X_BOTAO_PROPOSTA + 60, Y_BOTAO_PROPOSTA))
            
            if isinstance(casa_obj, Propriedade):
                preco_texto = f"Preço: R$ {casa_obj.preco_compra}"
                img_preco = FONTE_PEQUENA.render(preco_texto, True, COR_TEXTO_BRANCO)
                screen.blit(img_preco, (X_TEXTO_CARTA - 15, Y_TEXTO_CARTA + 20))
        
        # Desenha peões de todos os jogadores
        for i in range(len(nomes_dos_jogadores)):
            jogador_obj = jogo_backend.jogadores[i]
            pos_logica = jogador_obj.posicao
            coords_base = POSICOES_CASAS_XY[pos_logica]
            offset = OFFSETS_PEOES[i]
            coords_final = (coords_base[0] + offset[0], coords_base[1] + offset[1])
            imagem_peao = IMAGENS_PEOES[i]
            screen.blit(imagem_peao, coords_final)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()