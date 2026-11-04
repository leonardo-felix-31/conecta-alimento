"""Dashboard real com estoque, movimentações recentes e alertas."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from html import escape

from interface.componentes.formatacao import (
    cabecalho_pagina, formatar_data, formatar_quantidade, rodape_pagina,
)
from interface.componentes.visual import CHAVE_ALTO_CONTRASTE, tabela_html
from servicos.dashboard import obter_indicadores


ROTULOS_MOVIMENTO = {
    "ENTRADA_DOACAO": "Entradas",
    "SAIDA_DISTRIBUICAO": "Distribuições",
    "ESTORNO_DISTRIBUICAO": "Estornos",
    "AJUSTE_ENTRADA": "Ajustes de entrada",
    "AJUSTE_SAIDA": "Ajustes de saída",
    "PERDA": "Perdas",
}


def _cartao_metrica(st, chave: str, icone: str, rotulo: str, valor: str, detalhe: str, *, desenvolvimento: bool = False) -> None:
    with st.container(key=chave):
        classe_valor = "ca-metric-development" if desenvolvimento else "ca-metric-value"
        st.markdown(
            f'<div class="ca-metric-top"><span class="ca-metric-icon">{escape(icone)}</span>{escape(rotulo)}</div>'
            f'<div class="{classe_valor}">{escape(valor)}</div>'
            f'<div class="ca-metric-note">{escape(detalhe)}</div>',
            unsafe_allow_html=True,
        )


def _grafico_movimentacoes(st, movimentacoes: list[dict[str, object]]) -> None:
    if not movimentacoes:
        st.markdown('<div class="ca-alert-empty">As movimentações aparecerão aqui após o primeiro recebimento.</div>', unsafe_allow_html=True)
        return
    contagem: dict[str, int] = defaultdict(int)
    for movimento in movimentacoes:
        dia = str(movimento["data_movimentacao"])[:10]
        contagem[dia] += 1
    dados = [
        {"Data": formatar_data(dia), "Movimentações": total}
        for dia, total in sorted(contagem.items())
    ]
    alto_contraste = bool(st.session_state.get(CHAVE_ALTO_CONTRASTE, False))
    if alto_contraste:
        # O tema automático do st.bar_chart define a área do gráfico como clara,
        # mesmo quando a página está em alto contraste. Um spec explícito mantém
        # fundo, eixos e grade legíveis no mesmo tema da interface.
        spec = {
            "mark": {"type": "bar", "color": "#FFFF00", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
            "encoding": {
                "x": {
                    "field": "Data", "type": "ordinal", "sort": None,
                    "axis": {
                        "title": "Data", "labelColor": "#FFFFFF", "titleColor": "#FFFFFF",
                        "domainColor": "#FFFFFF", "tickColor": "#FFFFFF", "grid": False,
                        "labelAngle": -45,
                    },
                },
                "y": {
                    "field": "Movimentações", "type": "quantitative",
                    "axis": {
                        "title": "Movimentações", "labelColor": "#FFFFFF",
                        "titleColor": "#FFFFFF", "domainColor": "#FFFFFF",
                        "tickColor": "#FFFFFF", "gridColor": "#666666",
                    },
                },
                "tooltip": [
                    {"field": "Data", "type": "ordinal"},
                    {"field": "Movimentações", "type": "quantitative"},
                ],
            },
            "height": 212,
            "config": {
                "background": "#000000",
                "view": {"fill": "#000000", "stroke": "#FFFFFF"},
                "axis": {
                    "labelColor": "#FFFFFF", "titleColor": "#FFFFFF",
                    "domainColor": "#FFFFFF", "tickColor": "#FFFFFF",
                    "gridColor": "#666666",
                },
            },
        }
        st.vega_lite_chart(
            dados, spec=spec, width="stretch", height=212, theme=None,
            alt="Quantidade de movimentações registradas agrupadas por dia.",
        )
    else:
        st.bar_chart(
            dados, x="Data", y="Movimentações", color="#257347", height=212,
            width="stretch", sort=False,
            alt="Quantidade de movimentações registradas agrupadas por dia.",
        )
    st.markdown('<div class="ca-panel-meta">Movimentações reais agrupadas por data · últimos 10 eventos</div>', unsafe_allow_html=True)


def _tabela_estoque(st, dados: dict[str, object]) -> None:
    alimentos = dados["estoque_por_alimento"]
    saldos = dados.get("saldos_por_lote", [])
    referencia = date.fromisoformat(str(dados["data_referencia"]))
    limite = int(dados["dias_alerta_vencimento"])
    if not alimentos:
        st.markdown('<div class="ca-alert-empty">Não há saldo disponível dentro da validade.</div>', unsafe_allow_html=True)
        return

    linhas: list[list[str]] = []
    for alimento in alimentos:
        lotes_validos = [
            lote for lote in saldos
            if int(lote["id_alimento"]) == int(alimento["id_alimento"])
            and lote["estado"] == "disponível"
        ]
        validade = min((str(lote["data_validade"]) for lote in lotes_validos), default="")
        estado = "Normal"
        if validade:
            dias = (date.fromisoformat(validade) - referencia).days
            if dias <= limite:
                estado = "Atenção"
        linhas.append([
            str(alimento["alimento"]),
            formatar_quantidade(int(alimento["saldo"]), str(alimento["unidade_medida"])),
            formatar_data(validade) if validade else "—",
            estado,
        ])
    st.markdown(
        tabela_html(
            ["Alimento", "Quantidade", "Validade mais próxima", "Status"],
            linhas, colunas_status=(3,),
        ),
        unsafe_allow_html=True,
    )


def _painel_alertas(st, dados: dict[str, object]) -> None:
    proximos = dados["lotes_proximos_vencimento"]
    vencidos = dados["lotes_vencidos"]
    if proximos:
        primeiro = proximos[0]
        titulo = f"Atenção: {len(proximos)} lotes próximos do vencimento"
        detalhe = f"Verifique os itens com validade nos próximos {int(dados['dias_alerta_vencimento'])} dias."
        linha = (
            '<div class="ca-alert-row"><span class="ca-alert-icon">!</span><div>'
            f'<div class="ca-alert-title">{escape(titulo)}</div><div class="ca-alert-copy">{escape(detalhe)}</div>'
            f'<div class="ca-alert-copy">Mais próximo: {escape(str(primeiro["alimento"]))} · {escape(formatar_data(primeiro["data_validade"]))}</div>'
            '</div></div>'
        )
    else:
        linha = '<div class="ca-alert-row"><span class="ca-alert-icon ok">✓</span><div><div class="ca-alert-title">Nenhum lote próximo do vencimento</div><div class="ca-alert-copy">Não há lotes na faixa de alerta configurada.</div></div></div>'
    if vencidos:
        titulo_vencidos = f"{len(vencidos)} lotes vencidos com saldo"
        linha_vencidos = (
            '<div class="ca-alert-row"><span class="ca-alert-icon">!</span><div>'
            f'<div class="ca-alert-title">{escape(titulo_vencidos)}</div>'
            '<div class="ca-alert-copy">Esses itens não entram no saldo disponível.</div></div></div>'
        )
    else:
        linha_vencidos = '<div class="ca-alert-row"><span class="ca-alert-icon ok">✓</span><div><div class="ca-alert-title">Sem lotes vencidos com saldo</div><div class="ca-alert-copy">Os lotes vencidos são excluídos do estoque disponível.</div></div></div>'
    em_desenvolvimento = (
        '<div class="ca-alert-row"><span class="ca-alert-icon info">i</span><div>'
        '<div class="ca-alert-title">Solicitações e distribuições</div>'
        '<div class="ca-alert-copy">Em desenvolvimento · ainda não geram indicadores operacionais.</div></div></div>'
    )
    st.markdown(
        '<div class="ca-alert-header">!　Alertas e pendências</div>' + linha + linha_vencidos + em_desenvolvimento,
        unsafe_allow_html=True,
    )


def renderizar(st, usuario: dict[str, object] | None = None) -> None:
    dados = obter_indicadores()
    usuario = usuario or {"nome": "Operador"}
    cabecalho_pagina(
        st, usuario, "Visão geral", "Visão geral",
        "Acompanhe o recebimento, o estoque e os alertas de validade.",
    )
    with st.container(key="ca-dashboard-top-tools"):
        st.markdown(
            f'<span class="ca-date-filter">Posição do estoque · {escape(formatar_data(dados["data_referencia"]))}</span>',
            unsafe_allow_html=True,
        )

    metricas = st.columns(4, gap="small")
    cartoes = [
        ("ca-metric-received", "↓", "Doações recebidas", str(dados["doacoes_recebidas"]), "registros acumulados", False),
        ("ca-metric-distributed", "↗", "Alimentos distribuídos", "Em desenvolvimento", "distribuições ainda indisponíveis", True),
        ("ca-metric-stock", "▦", "Lotes disponíveis", str(dados["lotes_disponiveis"]), f"em {dados['alimentos_disponiveis']} {'alimento' if dados['alimentos_disponiveis'] == 1 else 'alimentos'}", False),
        ("ca-metric-expiry", "!", "Próximos do vencimento", str(len(dados["lotes_proximos_vencimento"])), f"validade em até {dados['dias_alerta_vencimento']} dias", False),
    ]
    for coluna, (chave, icone, rotulo, valor, detalhe, desenvolvimento) in zip(metricas, cartoes):
        with coluna:
            _cartao_metrica(st, chave, icone, rotulo, valor, detalhe, desenvolvimento=desenvolvimento)

    esquerda, direita = st.columns([1.16, 1], gap="medium")
    with esquerda:
        with st.container(key="ca-dashboard-chart"):
            titulo, nota = st.columns([2, 1], vertical_alignment="center")
            with titulo:
                st.markdown('<div class="ca-panel-heading">▮　Movimentação de alimentos</div>', unsafe_allow_html=True)
            with nota:
                st.markdown('<div class="ca-panel-meta ca-panel-meta-right">Últimos registros</div>', unsafe_allow_html=True)
            _grafico_movimentacoes(st, dados["movimentacoes_recentes"])
    with direita:
        with st.container(key="ca-dashboard-alerts"):
            _painel_alertas(st, dados)

    with st.container(key="ca-dashboard-stock"):
        esquerda_titulo, descricao = st.columns([2, 1], vertical_alignment="center")
        with esquerda_titulo:
            st.markdown('<div class="ca-panel-heading">▦　Estoque por alimento</div>', unsafe_allow_html=True)
        with descricao:
            st.markdown('<div class="ca-panel-meta ca-panel-meta-right">Saldo disponível por lote</div>', unsafe_allow_html=True)
        _tabela_estoque(st, dados)

    movimentos = dados["movimentacoes_recentes"]
    with st.expander("Histórico recente de movimentações"):
        if movimentos:
            st.dataframe([{
                "Data e hora": formatar_data(row["data_movimentacao"]),
                "Movimento": ROTULOS_MOVIMENTO.get(str(row["tipo"]), str(row["tipo"]).replace("_", " ").title()),
                "Alimento": row["alimento"],
                "Quantidade": formatar_quantidade(int(row["quantidade"]), str(row["unidade_medida"])),
                "Lote": row["codigo_lote"],
                "Responsável": row["responsavel"],
            } for row in movimentos], width="stretch", hide_index=True)
        else:
            st.caption("Nenhuma movimentação registrada.")

    rodape_pagina(st, f"Conecta Alimento · Indicadores reais · {dados['dias_alerta_vencimento']} dias para alerta de validade")
