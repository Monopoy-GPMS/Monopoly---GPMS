# sistema_eventos.py
# Módulo para gerenciar eventos do jogo (ganhos, perdas, marcos, etc)

from datetime import datetime
from enum import Enum

class TipoEvento(Enum):
    """Tipos de eventos que podem ocorrer no jogo"""
    COMPRA_PROPRIEDADE = "compra_propriedade"
    VENDA_PROPRIEDADE = "venda_propriedade"
    PAGAMENTO_ALUGUEL = "pagamento_aluguel"
    RECEBIMENTO_ALUGUEL = "recebimento_aluguel"
    CONSTRUCAO_CASA = "construcao_casa"
    CONSTRUCAO_HOTEL = "construcao_hotel"
    PAGAR_IMPOSTO = "pagar_imposto"
    PRISAO = "prisao"
    SAIR_PRISAO = "sair_prisao"
    PEGAR_CARTA = "pegar_carta"
    MONOPÓLIO_COMPLETADO = "monopolio_completado"
    JOGADOR_FALIDO = "jogador_falido"
    JOGADOR_VENCEDOR = "jogador_vencedor"
    DUPLA_ROLADA = "dupla_rolada"
    PASSAGEM_SAIDA = "passagem_saida"
    HIPOTECA_PROPRIEDADE = "hipoteca_propriedade"
    DESHIPOTECA_PROPRIEDADE = "deshipoteca_propriedade"
    TRANSFERENCIA_PROPRIEDADE = "transferencia_propriedade"
    SALDO_CRITICO = "saldo_critico"  # Saldo abaixo de 200
    SALDO_ALTO = "saldo_alto"  # Saldo acima de 3000


class Evento:
    """Representa um evento no jogo"""
    
    def __init__(self, tipo, jogador, descricao, dados_adicionais=None):
        """
        Args:
            tipo: TipoEvento
            jogador: Nome do jogador envolvido
            descricao: Descrição textual do evento
            dados_adicionais: Dict com dados específicos do evento
        """
        self.tipo = tipo
        self.jogador = jogador
        self.descricao = descricao
        self.timestamp = datetime.now()
        self.dados_adicionais = dados_adicionais or {}
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.tipo.value.upper()}: {self.descricao}"
    
    def to_dict(self):
        """Converte evento para dicionário"""
        return {
            'tipo': self.tipo.value,
            'jogador': self.jogador,
            'descricao': self.descricao,
            'timestamp': self.timestamp.isoformat(),
            'dados': self.dados_adicionais
        }


class SistemaEventos:
    """
    Gerencia todos os eventos que ocorrem durante o jogo.
    Mantém histórico, dispara callbacks e fornece análises.
    """
    
    def __init__(self):
        self.eventos = []
        self.callbacks = {}  # {TipoEvento: [funções_callback]}
        self.habilitado = True
    
    def registrar_callback(self, tipo_evento, funcao_callback):
        """
        Registra uma função para ser chamada quando um evento ocorre.
        
        Args:
            tipo_evento: TipoEvento para ouvir
            funcao_callback: Função a ser chamada(evento)
        """
        if tipo_evento not in self.callbacks:
            self.callbacks[tipo_evento] = []
        self.callbacks[tipo_evento].append(funcao_callback)
        print(f"  > Callback registrado para {tipo_evento.value}")
    
    def disparar_evento(self, tipo, jogador, descricao, dados_adicionais=None):
        """
        Dispara um novo evento no sistema.
        
        Args:
            tipo: TipoEvento
            jogador: Nome do jogador
            descricao: Descrição do evento
            dados_adicionais: Dados extras
        """
        if not self.habilitado:
            return
        
        evento = Evento(tipo, jogador, descricao, dados_adicionais)
        self.eventos.append(evento)
        
        print(f"  > EVENTO: {evento}")
        
        if tipo in self.callbacks:
            for callback in self.callbacks[tipo]:
                try:
                    callback(evento)
                except Exception as e:
                    print(f"  > ERRO ao executar callback: {e}")
    
    def obter_historico(self, filtro_jogador=None, filtro_tipo=None, limite=None):
        """
        Retorna histórico de eventos com filtros opcionais.
        
        Args:
            filtro_jogador: Filtra por nome do jogador
            filtro_tipo: Filtra por TipoEvento
            limite: Número máximo de eventos a retornar
            
        Returns:
            list: Lista de eventos
        """
        resultado = self.eventos[:]
        
        if filtro_jogador:
            resultado = [e for e in resultado if e.jogador == filtro_jogador]
        
        if filtro_tipo:
            resultado = [e for e in resultado if e.tipo == filtro_tipo]
        
        if limite:
            resultado = resultado[-limite:]
        
        return resultado
    
    def obter_estatisticas_jogador(self, nome_jogador):
        """
        Retorna estatísticas de um jogador com base em eventos.
        
        Args:
            nome_jogador: Nome do jogador
            
        Returns:
            dict: Estatísticas do jogador
        """
        eventos_jogador = self.obter_historico(filtro_jogador=nome_jogador)
        
        stats = {
            'nome': nome_jogador,
            'total_eventos': len(eventos_jogador),
            'propriedades_compradas': len([e for e in eventos_jogador if e.tipo == TipoEvento.COMPRA_PROPRIEDADE]),
            'propriedades_vendidas': len([e for e in eventos_jogador if e.tipo == TipoEvento.VENDA_PROPRIEDADE]),
            'casas_construidas': len([e for e in eventos_jogador if e.tipo == TipoEvento.CONSTRUCAO_CASA]),
            'hoteis_construidos': len([e for e in eventos_jogador if e.tipo == TipoEvento.CONSTRUCAO_HOTEL]),
            'vezes_preso': len([e for e in eventos_jogador if e.tipo == TipoEvento.PRISAO]),
            'vezes_passou_saida': len([e for e in eventos_jogador if e.tipo == TipoEvento.PASSAGEM_SAIDA]),
            'aluguel_pago_total': sum([e.dados_adicionais.get('valor', 0) for e in eventos_jogador if e.tipo == TipoEvento.PAGAMENTO_ALUGUEL]),
            'aluguel_recebido_total': sum([e.dados_adicionais.get('valor', 0) for e in eventos_jogador if e.tipo == TipoEvento.RECEBIMENTO_ALUGUEL]),
            'monopolios_completados': len([e for e in eventos_jogador if e.tipo == TipoEvento.MONOPÓLIO_COMPLETADO]),
        }
        
        return stats
    
    def limpar_historico(self):
        """Limpa o histórico de eventos (use com cautela)"""
        self.eventos = []
        print("  > Histórico de eventos limpo")
    
    def exportar_historico(self, caminho_arquivo):
        """
        Exporta o histórico para um arquivo JSON.
        
        Args:
            caminho_arquivo: Caminho do arquivo para salvar
        """
        import json
        dados = [e.to_dict() for e in self.eventos]
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        print(f"  > Histórico exportado para {caminho_arquivo}")
    
    def __str__(self):
        return f"SistemaEventos: {len(self.eventos)} eventos registrados"
