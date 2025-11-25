# Instruções para Testar o Backend do Monopoly

## Como Executar os Testes

### Método 1: Executar arquivo de teste completo
\`\`\`bash
python test_tabuleiro.py
\`\`\`

Este comando executará todos os 7 testes automaticamente e mostrará:
- ✓ Testes que passaram
- ❌ Testes que falharam
- Detalhes de cada validação

## O Que Será Testado

### Teste 1: Criação do Tabuleiro
Valida que o tabuleiro foi criado com exatamente 40 casas e que as casas especiais estão nas posições corretas:
- Posição 0: Ponto de Partida
- Posição 10: Cadeia/Prisão
- Posição 20: Estacionamento Grátis
- Posição 30: Vá para a Prisão

### Teste 2: Tipos de Casas
Verifica se todos os tipos de casas foram implementados:
- Propriedades regulares
- Estações de metrô/ferrovias
- Companhias de serviço
- Casas de imposto
- Casas de sorte/revés
- Casas especiais

### Teste 3: Propriedades por Grupo
Valida a organização das propriedades em grupos de cor:
- Marrom, Azul Claro, Rosa, Laranja, Vermelho, Amarelo, Verde, Azul Escuro
- Mostra quantas propriedades existem em cada grupo
- Lista todas as propriedades com seus preços

### Teste 4: Movimentação do Jogador
Testa a lógica de movimentação:
- Movimento simples (ex: posição 0 → 7)
- Movimento que passa pela saída (ex: posição 35 → 5)
- Bônus por passar pela saída (R$200)
- Movimento direto para uma posição específica

### Teste 5: Casas Especiais
Valida o comportamento das casas especiais:
- Casa de Imposto: cobra o valor correto do jogador
- Vá para Prisão: envia o jogador para a posição 10
- Sistema de prisão: entrada e saída funcionando
- Cobranças sendo debitadas do saldo

### Teste 6: Compra de Propriedades
Testa o sistema de compra:
- Verificação de propriedade disponível
- Débito do valor correto do saldo
- Adição da propriedade ao jogador
- Definição do proprietário

### Teste 7: Detecção de Monopólio
Valida o sistema de monopólio:
- Contagem de propriedades por grupo
- Detecção quando jogador tem todas do grupo
- Funcionalidade para habilitar construção de casas/hotéis

## Resultado Esperado

Se tudo estiver funcionando corretamente, você verá:

\`\`\`
==================================================================
✅ TODOS OS TESTES PASSARAM COM SUCESSO!
==================================================================

📋 Resumo da Validação:
  ✓ Tabuleiro com 40 casas criado corretamente
  ✓ Todas as casas especiais funcionando
  ✓ Propriedades organizadas por grupo
  ✓ Movimentação de jogadores implementada
  ✓ Sistema de prisão funcionando
  ✓ Compra de propriedades validada
  ✓ Detecção de monopólio implementada

🎉 Backend do Tabuleiro está pronto para integração!
\`\`\`

## Testes Individuais

Você também pode executar testes específicos editando o arquivo `test_tabuleiro.py` e chamando apenas a função desejada:

\`\`\`python
if __name__ == "__main__":
    tabuleiro = teste_1_criacao_tabuleiro()
    teste_4_movimentacao_jogador(tabuleiro)
\`\`\`

## Integração com Frontend

Após validar o backend, você pode integrar com o frontend usando os seguintes métodos:

\`\`\`python
# Criar tabuleiro
tabuleiro = Tabuleiro()

# Obter informações de uma casa
casa = tabuleiro.get_casa(posicao)
print(casa.nome, casa.tipo)

# Mover jogador
jogador.mover(dados_rolados)

# Executar ação da casa
casa.acao_ao_cair(jogador, banco)

# Verificar monopólio
tem_monopolio = jogador.tem_monopolio(grupo, total_grupo)
\`\`\`

## Troubleshooting

Se algum teste falhar:
1. Verifique se todos os arquivos Python estão no mesmo diretório
2. Confirme que não há erros de importação
3. Leia a mensagem de erro detalhada que será exibida
4. Verifique se as constantes em `constantes.py` estão definidas

## Próximos Passos

Após validar o backend:
1. ✅ Tabuleiro e casas implementados
2. ✅ Sistema de movimentação funcionando
3. 🔄 Integrar com interface Pygame
4. 🔄 Implementar sistema de cartas (Sorte/Revés)
5. 🔄 Adicionar lógica de construção de casas/hotéis
