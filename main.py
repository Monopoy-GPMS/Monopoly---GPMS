import pygame
import sys
import os
import random
from jogo import Jogo
from propriedades import Propriedade

# --- 1. Inicialização e Configurações ---
pygame.init()

# ... (logo após pygame.init()) ...
pygame.font.init() # Inicializa o módulo de fontes

# Tenta carregar uma fonte bonita. Se não encontrar, usa a padrão.
# (Você pode usar um arquivo .ttf se tiver um do seu Figma)
try:
    FONTE_PADRAO = pygame.font.SysFont('Arial', 15)
    FONTE_PEQUENA = pygame.font.SysFont('Arial', 10)
except Exception as e:
    print(f"Erro ao carregar fonte: {e}. Usando fonte padrão.")
    FONTE_PADRAO = pygame.font.Font(None, 15) # Fonte padrão do Pygame
    FONTE_PEQUENA = pygame.font.Font(None, 10)
# ===============================================
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
        return imagem.convert_alpha() # Para imagens com transparência (PNGs)
    else:
        return imagem.convert()       # Para imagens opacas (performance)

# --- Carregando as imagens ---
# (Certifique-se que estes arquivos estão na pasta 'assets')

# 1. O Tabuleiro
tabuleiro_img = carregar_imagem('tabuleiro.png')

# 2. O Botão 'Lançar Dados'
botao_lancar_img = carregar_imagem('botao_lancar.png', alpha=True)

# 3. O Painel de UI (NOVO!)
#    (Exporte APENAS o retângulo cinza arredondado do Figma)
painel_ui_img = carregar_imagem('painel_ui.png', alpha=True) # <-- NOVO

fazar_proposta_img = carregar_imagem('fazer_proposta.png', alpha=True)

fundo_interativo_img = carregar_imagem('fundo_interativos.png', alpha=True)

# --- Carregando Peões (NOVO!) ---
peao_jogador_1_img = carregar_imagem('peao_1.png', alpha=True)
peao_jogador_2_img = carregar_imagem('peao_2.png', alpha=True)
peao_jogador_3_img = carregar_imagem('peao_3.png', alpha=True)
peao_jogador_4_img = carregar_imagem('peao_4.png', alpha=True)



# --- Carregando os Dados (NOVO!) ---
# Carrega todas as 6 faces dos dados em uma lista
imagens_dados = []
for i in range(1, 7):
    nome_arquivo = f'dado_{i}.png'
    imagens_dados.append(carregar_imagem(nome_arquivo, alpha=True))
# Agora, imagens_dados[0] é 'dado_1.png', imagens_dados[1] é 'dado_2.png', etc.

# --- Variáveis de Estado dos Dados (NOVO!) ---
# Começa mostrando 6 e 6 (ou qualquer valor que você quiser)

##jogador_atual = 0 # Começa com o Jogador 1 (índice 0)
###num_jogadores = 4 # Exemplo
# Guarda a POSIÇÃO (índice de 0 a 39) de cada jogador

###posicoes_jogadores = [0,0,0,0]

nomes_dos_jogadores = ["Vinicius", "Guilherme"] ##integração com o backend
jogo_backend = Jogo(nomes_dos_jogadores) 
###jogador_atual = jogo_backend.indice_turno_atual
# Define o estado atual do jogo para controlar a UI
# "INICIO_TURNO" = Mostra "Lançar Dados"
# "OPCAO_COMPRA" = Mostra "Comprar / Passar"
estado_jogo = "INICIO_TURNO"

posicao_para_decisao = 0

OFFSETS_PEOES = [
    (10, 10),   # Jogador 1
    (45, 10),  # Jogador 2 (15 pixels à direita)
    (10, 45),  # Jogador 3 (15 pixels abaixo)
    (45, 45)  # Jogador 4 (15 abaixo e 15 à direita)
]# Todos começam no "Ponto de Partida" (posição 0)


IMAGENS_PEOES = [
    peao_jogador_1_img,
    peao_jogador_2_img,
    peao_jogador_3_img,
    peao_jogador_4_img
]

dado1_valor = 6
dado2_valor = 6

botao_comprar_img = carregar_imagem('comprar.png', alpha=True) # <-- NOVO
botao_passar_img = carregar_imagem('passar_vez.png', alpha=True)  # <-- NOVO


POSICOES_TEXTO_JOGADOR = [
    (33, 85),   # Posição do texto do Jogador 1 
    (1211, 85), # Posição do texto do Jogador 2 
    (30, 677),  # Posição do texto do Jogador 3 
    (1210, 677) # Posição do texto do Jogador 4 
]


POSICOES_CASAS_XY = [
(1048,837.37),
(972,837.37),
(899,837.37),
(823,837.37),
(748,837.37),
(672,837.37),
(599,837.37),
(523,837.37),
(449,837.37),
(374,837.37),
(262,837.37),
(262,762.37),
(262,687.37),
(262,613.37),
(262,538.37),
(262,464.37),
(262,388.37),
(262,313.37),
(262,240.37),
(262,164.37),
(262,49.37),
(374,49.37),
(449,49.37),
(523,49.37),
(598,49.37),
(671,49.37),
(747,49.37),
(822,49.37),
(898,49.37),
(973,49.37),
(1048,49.37),
(1048,165.37),
(1048,241.37),
(1048,319.37),
(1048,389.37),
(1048,464.37),
(1048,539.37),
(1048,613.37),
(1048,688.37),
(1048,762.37),
]


# Lista com o nome de cada casa, na ordem de 0 a 39
"""
NOMES_CASAS = [
    "Ponto de Partida",     # 0
    "Avenida Sumaré",    # 1
    "Cofre",               # 2
    "Praça da Sé",    # 3
    "Imposto de Renda",    # 4
    "Estação Maracanã",    # 5
    "Rua 25 de Março",     # 6
    "Sorte",               # 7
    "Avenida São João",      # 8
    "Avenida Paulista",  # 9
    "Cadeia (Visitante)",  # 10
    "Avenida Vieira Souto",   # 11
    "Companhia Elétrica",  # 12
    "Niterói",     # 13
    "Avenida Atlântica",   # 14
    "Estação de Metrô Carioca",   # 15
    "Avenida Presidente Juscelino Kubitschek",  # 16
    "Cofre",               # 17
    "Avenida Engenheiro Luiz Carlos Berrini",    # 18
    "Avenida Brigadeiro Faria Lima",    # 19
    "Parada Livre",        # 20
    "Ipanema",  # 21
    "Sorte",               # 22
    "Leblon",   # 23
    "Copacabana", # 24
    "Estação de Metrô Consolação",  # 25
    "Avenida Cidade Jardim",          # 26
    "Pacaembu",              # 27
    "Companhia de Distribuição de Água",             # 28
    "Ibirapuera",              # 29
    "Vá para a Cadeia",    # 30
    "Barra da Tijuca",     # 31
    "Jardim Botânico",     # 32
    "Cofre",               # 33
    "Lagoa Rodrigo de Freitas",  # 34
    "Estação de Metrô da Republica",  # 35
    "Sorte",               # 36
    "Avenida Morumbi",       # 37
    "Taxa de Riqueza",     # 38
    "Rua Oscar Freire"     # 39
    ]
    """
# ====================================================================
# --- 3. POSIÇÕES E RECTS (COM VALORES DO FIGMA) ---
# ====================================================================

# --- Posição do Tabuleiro ---
X_TABULEIRO = 260
Y_TABULEIRO = 49
TAMANHO_TABULEIRO = 924 
tabuleiro_img = pygame.transform.scale(tabuleiro_img, (TAMANHO_TABULEIRO, TAMANHO_TABULEIRO))


# --- Posição do Painel de UI (SEUS VALORES!) ---
X_PAINEL_UI = 397       # <-- SEU VALOR X
Y_PAINEL_UI = 670       # <-- SEU VALOR Y
LARGURA_PAINEL_UI = 394 # <-- SEU VALOR L
ALTURA_PAINEL_UI = 146  # <-- SEU VALOR A
# (Não precisamos de um 'rect' para ele, pois ele (provavelmente) não é clicável)


X_FUNDO_INTERA = 561       # <-- SEU VALOR X
Y_FUNDO_INTERA = 690       # <-- SEU VALOR Y
LARGURA_FUNDO_INTERA = 207 # <-- SEU VALOR L
ALTURA_FUNDO_INTERA = 109  # <-- SEU VALOR A
# (Não precisamos de um 'rect' para ele, pois ele (provavelmente) não é clicável)


# --- Posição do Botão 'Lançar Dados' ---
X_BOTAO_PROPOSTA = 408
Y_BOTAO_PROPOSTA = 743
LARGURA_BOTAO_PROPOSTA = 128
ALTURA_BOTAO_PROPOSTA = 29
# Retângulo clicável
botao_proposta_rect = pygame.Rect(X_BOTAO_PROPOSTA, Y_BOTAO_PROPOSTA, LARGURA_BOTAO_PROPOSTA, ALTURA_BOTAO_PROPOSTA)


# --- Posição do Botão 'Lançar Dados' ---
X_BOTAO_LANCAR = 408
Y_BOTAO_LANCAR = 777
LARGURA_BOTAO_LANCAR = 128
ALTURA_BOTAO_LANCAR = 29
# Retângulo clicável
botao_lancar_rect = pygame.Rect(X_BOTAO_LANCAR, Y_BOTAO_LANCAR, LARGURA_BOTAO_LANCAR, ALTURA_BOTAO_LANCAR)


X_BOTAO_COMPRAR = 640       
Y_BOTAO_COMPRAR = 714       
LARGURA_BOTAO_COMPRAR = 125 
ALTURA_BOTAO_COMPRAR = 29   
botao_comprar_rect = pygame.Rect(X_BOTAO_COMPRAR, Y_BOTAO_COMPRAR, LARGURA_BOTAO_COMPRAR, ALTURA_BOTAO_COMPRAR)


# --- Botão 'PASSAR A VEZ' (NOVO!) ---
# (!!! VALORES DO FIGMA !!!)
X_BOTAO_PASSAR = 640        
Y_BOTAO_PASSAR = 748        
LARGURA_BOTAO_PASSAR = 125  
ALTURA_BOTAO_PASSAR = 29    
botao_passar_rect = pygame.Rect(X_BOTAO_PASSAR, Y_BOTAO_PASSAR, LARGURA_BOTAO_PASSAR, ALTURA_BOTAO_PASSAR)

X_DADO_1, Y_DADO_1 = 593, 718 
X_DADO_2, Y_DADO_2 = 685, 718 

# --- Posição do Texto "Vez de:" (NOVO!) ---
# (VALOR DO FIGMA !!!)
X_TEXTO_TURNO, Y_TEXTO_TURNO = 410, 691 
COR_TEXTO_BRANCO = (255, 255, 255)

X_TEXTO_CARTA, Y_TEXTO_CARTA = 576, 689

# ====================================================================

# --- 4. O Game Loop Principal ---
running = True
while running:
    
# --- 5. Processamento de Eventos (Inputs) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Verifica por clique do mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                
                print(f"Clique do mouse em: {event.pos}") # Ótimo para depurar

                # --- LÓGICA DO ESTADO "INICIO_TURNO" ---
                if estado_jogo == "INICIO_TURNO":
                    
                    # Se clicar em 'Lançar Dados'
                    if botao_lancar_rect.collidepoint(event.pos):
                        
                        # (!!! LÓGICA ANTIGA DELETADA !!!)
                        
                        # (!!! NOVA LÓGICA DO BACKEND !!!)
                        # 1. Chama o backend para rolar e mover
                        #    O backend já atualiza a posição do jogador internamente
                        casa_onde_parei = jogo_backend.rolar_dados_e_mover()
                        print(f"Backend moveu jogador para: {casa_onde_parei.nome}")

                        # 2. Atualiza os dados do frontend (para mostrar o resultado visual)
                        dado1_valor = jogo_backend.ultimo_d1
                        dado2_valor = jogo_backend.ultimo_d2
                        
                        # 3. Pergunta ao backend o que fazer agora
                        acao_necessaria = jogo_backend.obter_acao_para_casa(casa_onde_parei)
                        
                        # 4. Processa a resposta do backend
                        if acao_necessaria["tipo"] == "DECISAO_COMPRA":
                            print("Backend: 'DECISAO_COMPRA'. Mudando estado da UI.")
                            # Salva a POSIÇÃO (índice 0-39) para o loop de desenho
                            jogador_que_moveu = jogo_backend.jogadores[jogo_backend.indice_turno_atual]
                            posicao_para_decisao = jogador_que_moveu.posicao
                            estado_jogo = "OPCAO_COMPRA"
                        
                        elif acao_necessaria["tipo"] in ["ACAO_AUTOMATICA", "PAGAR_ALUGUEL"]:
                            print(f"Backend: '{acao_necessaria['tipo']}'. Executando e finalizando turno.")
                            # Ações como "Vá para a Prisão" ou "Pagar Aluguel"
                            jogo_backend.executar_acao_automatica(casa_onde_parei)
                            jogo_backend.finalizar_turno()
                            # O estado da UI continua "INICIO_TURNO" para o próximo jogador
                        
                        else: # "NENHUMA_ACAO" (ex: Parada Livre, Prisão)
                            print("Backend: 'NENHUMA_ACAO'. Finalizando turno.")
                            jogo_backend.finalizar_turno()
                            # O estado da UI continua "INICIO_TURNO"

                    # Se clicar em 'Fazer proposta'
                    if botao_proposta_rect.collidepoint(event.pos):
                        print("AÇÃO: Fazer uma proposta!") # (Lógica futura)

                # --- LÓGICA DO ESTADO "OPCAO_COMPRA" ---
                elif estado_jogo == "OPCAO_COMPRA":
                    
                    # Se clicar em 'Comprar'
                    if botao_comprar_rect.collidepoint(event.pos):
                        print("UI: Clicou 'Comprar'. Chamando backend...")
                        # 1. Backend executa a compra (dinheiro, dono, etc.)
                        jogo_backend.executar_compra() 
                        # 2. Backend passa a vez
                        jogo_backend.finalizar_turno() 
                        # 3. UI reseta o estado
                        estado_jogo = "INICIO_TURNO" 

                    # Se clicar em 'Passar'
                    if botao_passar_rect.collidepoint(event.pos):
                        print("UI: Clicou 'Passar'. Chamando backend...")
                        # 1. (Lógica de leilão viria aqui, por enquanto só finaliza)
                        # 2. Backend passa a vez
                        jogo_backend.finalizar_turno() 
                        # 3. UI reseta o estado
                        estado_jogo = "INICIO_TURNO"
        
    # --- 6. Lógica de Desenho (Renderização) ---
    #    A ORDEM AQUI É IMPORTANTE (CAMADAS)

    # Camada 0: Limpa a tela com a cor de fundo preta
    screen.fill(COR_FUNDO)
    
    # Camada 1: Desenha o tabuleiro
    screen.blit(tabuleiro_img, (X_TABULEIRO, Y_TABULEIRO))
    
    # Camada 2: Desenha o painel cinza (NOVO!)
    #    (Note que desenhamos este ANTES dos botões)
    screen.blit(painel_ui_img, (X_PAINEL_UI, Y_PAINEL_UI)) # <-- NOVO

    screen.blit(fundo_interativo_img, (X_FUNDO_INTERA, Y_FUNDO_INTERA))

    # Este loop desenha o status de TODOS os jogadores, O TEMPO TODO.
    ALTURA_LINHA_TEXTO = 20 

    for i in range(len(jogo_backend.jogadores)):
            # 1. Pega o jogador e a posição base (X,Y) para desenhar
            jogador_obj = jogo_backend.jogadores[i]
            posicao_base = POSICOES_TEXTO_JOGADOR[i]
            
            # --- Linha 1: Nome e Saldo ---
            saldo = jogo_backend.banco.consultar_saldo(jogador_obj.nome)
            texto_status = f"{jogador_obj.nome}: R$ {saldo}"
            
            # Renderiza com a fonte padrão
            img_status = FONTE_PADRAO.render(texto_status, True, COR_TEXTO_BRANCO)
            
            # Desenha a primeira linha na posição base
            screen.blit(img_status, posicao_base)
            
            # --- Linhas seguintes: Propriedades ---
            
            # Define um contador de linha, começando da "linha 2"
            linha_atual = 1 
            
            # Itera sobre a lista de propriedades do backend (!!!)
            for prop in jogador_obj.propriedades:
                
                # Pega o nome da propriedade do objeto
                nome_prop = prop.nome
                
                # Formata o texto (com um recuo)
                texto_prop = f"  - {nome_prop}"
                
                # Renderiza com a fonte PEQUENA (para caber mais)
                img_prop = FONTE_PEQUENA.render(texto_prop, True, COR_TEXTO_BRANCO)
                
                # Calcula a posição Y para esta nova linha
                # (Y_base + (qual_linha_estamos * altura_da_linha))
                posicao_y = posicao_base[1] + (linha_atual * ALTURA_LINHA_TEXTO)
                posicao_prop = (posicao_base[0], posicao_y) # (O X é o mesmo)
                
                # Desenha o nome da propriedade na tela
                screen.blit(img_prop, posicao_prop)
                
                # Incrementa o contador de linha
                linha_atual += 1
            
    # --- FIM DA CAMADA DE STATUS ---

    # --- CAMADA DE TEXTO (NOVO!) ---
    # 1. Crie o texto dinâmico
    #    (Lembre-se que jogador_atual é 0-3, então somamos 1)


    # 1. Pega o índice do jogador atual DO BACKEND
    indice_jogador = jogo_backend.indice_turno_atual

    # 2. Pega o objeto Jogador real da lista DO BACKEND
    jogador_obj_atual = jogo_backend.jogadores[indice_jogador]
    texto_do_turno = f"Vez de: {jogador_obj_atual.nome}"

    # 2. Renderize o texto em uma imagem (Surface)
    #    (True = Anti-aliasing, para deixar as letras suaves)
    img_texto_turno = FONTE_PADRAO.render(texto_do_turno, True, COR_TEXTO_BRANCO)

    # 3. Desenhe (blit) a imagem do texto na tela
    screen.blit(img_texto_turno, (X_TEXTO_TURNO, Y_TEXTO_TURNO))

        # Camada 3: Desenha o botão por cima do painel
    if estado_jogo == "INICIO_TURNO":
    # Desenha os botões "Lançar" e "Proposta"
        screen.blit(fazar_proposta_img, (X_BOTAO_PROPOSTA, Y_BOTAO_PROPOSTA))
        screen.blit(botao_lancar_img, (X_BOTAO_LANCAR, Y_BOTAO_LANCAR))
        
        # Desenha os dados (mostra o último resultado)
        screen.blit(imagens_dados[dado1_valor - 1], (X_DADO_1, Y_DADO_1))
        screen.blit(imagens_dados[dado2_valor - 1], (X_DADO_2, Y_DADO_2))

    elif estado_jogo == "OPCAO_COMPRA":
        # Desenha os botões "Comprar" e "Passar"
# 1. Pega o objeto 'Casa' DO BACKEND usando a posição que salvamos
        casa_obj = jogo_backend.tabuleiro.get_casa(posicao_para_decisao)
        
        # 2. Pega o nome direto do objeto
        nome_da_casa = casa_obj.nome
        img_texto_casa = FONTE_PEQUENA.render(nome_da_casa, True, COR_TEXTO_BRANCO)
        screen.blit(img_texto_casa, (X_TEXTO_CARTA, Y_TEXTO_CARTA))

        screen.blit(botao_comprar_img, (X_BOTAO_COMPRAR, Y_BOTAO_COMPRAR))
        screen.blit(botao_passar_img, (X_BOTAO_PASSAR, Y_BOTAO_PASSAR))

        screen.blit(imagens_dados[dado1_valor - 1], (X_BOTAO_PROPOSTA, Y_BOTAO_PROPOSTA))
        screen.blit(imagens_dados[dado2_valor - 1], (X_BOTAO_PROPOSTA + 60, Y_BOTAO_PROPOSTA))

        # (BÔNUS: Mostrar o preço, se for uma propriedade)
        
        if isinstance(casa_obj, Propriedade):
            preco_texto = f"Preço: R$ {casa_obj.preco_compra}"
            img_preco = FONTE_PEQUENA.render(preco_texto, True, COR_TEXTO_BRANCO)
            screen.blit(img_preco, (X_TEXTO_CARTA - 15, Y_TEXTO_CARTA + 20)) # 20 pixels abaixo
    
    # (Opcional: desenhe a imagem da carta da propriedade aqui)

    # 1. Pega o nome da casa da nossa "base de dados"
        ##nome_da_casa = NOMES_CASAS[posicao_para_decisao]

        img_texto_casa = FONTE_PEQUENA.render(nome_da_casa, True, COR_TEXTO_BRANCO)


        screen.blit(img_texto_casa, (X_TEXTO_CARTA, Y_TEXTO_CARTA))

# --- CAMADA DE PEÕES (NOVO!) ---
    # Desenha cada peão na sua posição correta

    for i in range(len(nomes_dos_jogadores)):
        # 1. Pega a posição lógica (o número da casa, 0-39)
        jogador_obj = jogo_backend.jogadores[i]

        pos_logica = jogador_obj.posicao
        
        # 2. Pega a coordenada (X, Y) base para aquela casa
        coords_base = POSICOES_CASAS_XY[pos_logica]
        
        # 3. Pega o offset (deslocamento) para este jogador (i)
        offset = OFFSETS_PEOES[i]
        
        # 4. Calcula a coordenada final de desenho
        coords_final = (coords_base[0] + offset[0], coords_base[1] + offset[1])
        
        # 5. Pega a imagem correta do peão
        imagem_peao = IMAGENS_PEOES[i]
        
        # 6. Desenha o peão na tela
        screen.blit(imagem_peao, coords_final)
        # --- 7. Atualiza a Tela ---
    pygame.display.flip()

# --- Fim do Jogo ---
pygame.quit()
sys.exit()