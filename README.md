# Monopoly - GPMS

Repositório para armazenar o projeto da disciplina de Gerência, Projeto e Manutenção de Software

## 📋 Descrição do Projeto

Este projeto implementa o jogo clássico Monopoly (Banco Imobiliário) em Python, com:
- **Backend completo** com lógica de jogo (movimentação, transações, propriedades)
- **Frontend visual** com PyGame mostrando o tabuleiro completo do jogo

## 🎮 Frontend - Tabuleiro Visual com PyGame

O arquivo `monopoly_board.py` implementa uma visualização completa do tabuleiro do Monopoly usando PyGame.

### Características do Tabuleiro

- **40 casas completas** distribuídas nos 4 lados do tabuleiro
- **Janela de 1200x1200 pixels** para melhor visualização
- **4 cantos especiais**: GRÁTIS, VÁ PARA A CADEIA, PONTO DE PARTIDA, NA CADEIA/VISITANTE
- **22 propriedades** com cores e valores
- **Casas especiais**: Sorte, Cofre, Estações de Metrô, Companhias, Imposto
- **Logo "MONOPOLY"** em diagonal vermelho no centro
- **Ícones desenhados** com formas geométricas do pygame

### Estrutura das Classes

```python
Square          # Classe base para todas as casas
├── Property    # Propriedades com cor e valor
├── SpecialSquare  # Casas especiais (Sorte, Cofre, Estação, etc)
└── CornerSquare   # Casas dos 4 cantos

Board           # Gerencia o tabuleiro completo
```

## 🚀 Requisitos

- Python 3.x
- PyGame

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/zrodrix/Monopoly---GPMS-rd-.git
cd Monopoly---GPMS-rd-
```

2. Instale a dependência PyGame:
```bash
pip install pygame
```

## ▶️ Como Executar

### Visualizar o Tabuleiro (Frontend)

Execute o arquivo do tabuleiro visual:
```bash
python monopoly_board.py
```

Controles:
- **ESC** ou **X** na janela: Fechar o programa

### Backend (Lógica do Jogo)

Para testar a lógica do jogo (versão console):
```bash
cd src
python jogo.py
```

## 📁 Estrutura do Código

```
Monopoly---GPMS-rd-/
├── monopoly_board.py          # Frontend visual do tabuleiro (PyGame)
├── test_board_screenshot.py   # Script para gerar screenshot do tabuleiro
├── monopoly_board_preview.png # Prévia visual do tabuleiro
├── README.md                   # Este arquivo
└── src/                        # Backend do jogo
    ├── main.py
    ├── jogo.py                 # Lógica principal do jogo
    ├── tabuleiro.py            # Classes do tabuleiro e casas
    ├── jogador.py              # Classe Jogador
    ├── banco.py                # Sistema de transações
    ├── propriedades.py
    ├── casas.py
    └── constantes.py
```

## 🎨 Detalhes das 40 Casas

### Lado Superior (0-10):
0. **GRÁTIS** (canto)
1. IPANEMA - $220m (vermelho)
2. SORTE
3. LEBLON - $220m (vermelho)
4. COPACABANA - $120m (vermelho)
5. ESTAÇÃO DE METRÔ CONSOLAÇÃO - $200m
6. AVENIDA COPACABANA - $240m (verde claro)
7. PACAEMBU - $260m (verde claro)
8. COMPANHIA DE DISTRIBUIÇÃO DE ENERGIA - $150m
9. IBIRAPUERA - $280m (verde escuro)
10. **VÁ PARA A CADEIA** (canto)

### Lado Direito (11-19):
11. FÉRIAS NA TAILÂNDIA - $300m (verde escuro)
12. COMPRAR DE CHEFE - $300m (verde escuro)
13. COFRE
14. JOGO ARCADE TETRIS - $320m (verde escuro)
15. ESTAÇÃO DE METRO RIO DE JANEIRO - $400m
16. SORTE
17. FAQUEI A PROVA I - $350m (azul escuro)
18. FAQUEI A PROVA II - $400m (azul escuro)
19. SORTE

### Lado Inferior (20-30):
20. **PONTO DE PARTIDA** (canto)
21. AVENIDA SUMARÉ - $60m (marrom)
22. COFRE
23. PRAÇA DA SÉ - $60m
24. IMPOSTO DE RENDA - PAGUE $200m
25. ESTAÇÃO MARACANÃ - $200m
26. SORTE
27. RUA 25 DE MARÇO - $100m (azul claro)
28. AVENIDA SÃO JOÃO - $100m (azul claro)
29. AVENIDA PAULISTA - $120m (laranja)
30. **NA CADEIA/VISITANTE** (canto)

### Lado Esquerdo (31-39):
31. AVENIDA DO OUVIDOR - $140m (laranja)
32. FLAMINGO - $140m (rosa)
33. COFRE
34. BOTAFOGO - $160m (magenta)
35. SORTE
36. AVENIDA ATLÂNTICA - $180m (magenta)
37. ESTAÇÃO DE METRÔ - $200m
38. AVENIDA VIEIRA SOUTO - $200m (laranja)
39. SORTE

## 🔧 Funcionalidades Implementadas

### Frontend (PyGame):
- ✅ Renderização completa das 40 casas
- ✅ Cores e layout fiel ao design
- ✅ Ícones para casas especiais
- ✅ Logo MONOPOLY no centro
- ✅ Layout responsivo e proporcional

### Backend (Lógica):
- ✅ Sistema de jogadores
- ✅ Movimentação no tabuleiro
- ✅ Transações bancárias
- ✅ Compra e venda de propriedades
- ✅ Cobrança de aluguéis
- ✅ Passagem pela saída com bônus

## 🎯 Próximos Passos

- [ ] Integração do frontend PyGame com o backend
- [ ] Animação de peões dos jogadores
- [ ] Animação de rolagem de dados
- [ ] Sistema de turnos visual
- [ ] Menu de jogo
- [ ] Multiplayer

## 👥 Contribuidores

Projeto desenvolvido para a disciplina de Gerência, Projeto e Manutenção de Software

## 📄 Licença

Este projeto é de uso educacional.
