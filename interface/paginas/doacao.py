"""Recebimento de doações com formulário e resumo em duas colunas."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from html import escape

from interface.componentes.formatacao import (
    cabecalho_pagina, formatar_data, formatar_quantidade, rodape_pagina,
)
from servicos import ErroServico
from servicos.cadastros import listar_alimentos, listar_doadores
from servicos.doacoes import receber_doacao
from servicos.relogio import obter_referencia_temporal
from servicos.validacoes import quantidade_para_unidade_base, texto_opcional, validar_data


def _estado_inicial(st) -> None:
    st.session_state.setdefault("itens_doacao", [])


def _resumo(st, doador: dict[str, object] | None, itens: list[dict[str, object]]) -> None:
    totais: dict[str, int] = defaultdict(int)
    for item in itens:
        totais[str(item["unidade_medida"])] += int(item["quantidade_base"])

    with st.container(key="ca-donation-summary"):
        st.markdown('<div class="ca-summary-title">Resumo da doação</div>', unsafe_allow_html=True)
        st.markdown('<div class="ca-summary-subtitle">Confira as informações antes de confirmar o recebimento.</div>', unsafe_allow_html=True)
        nome_doador = escape(str(doador["nome"])) if doador else "Selecione um doador"
        st.markdown(
            f'<div class="ca-summary-row"><span>Doador</span><strong>{nome_doador}</strong></div>'
            f'<div class="ca-summary-row"><span>Itens cadastrados</span><strong>{len(itens)} {"alimento" if len(itens) == 1 else "alimentos"}</strong></div>',
            unsafe_allow_html=True,
        )
        for indice, item in enumerate(itens, start=1):
            nome = escape(str(item["nome_alimento"]))
            quantidade = escape(formatar_quantidade(int(item["quantidade_base"]), str(item["unidade_medida"])))
            validade = escape(formatar_data(item["data_validade"]))
            origem = escape(str(item.get("codigo_origem") or "não informada"))
            st.markdown(
                f'<div class="ca-summary-item"><div class="ca-summary-item-name">{indice}. {nome}</div>'
                f'<div class="ca-summary-item-detail">{quantidade} · Validade {validade}<br>Código de origem: {origem}</div></div>',
                unsafe_allow_html=True,
            )
        if not itens:
            st.markdown('<div class="ca-alert-empty">Adicione alimentos para visualizar o resumo.</div>', unsafe_allow_html=True)
        for unidade, total in sorted(totais.items()):
            unidade_rotulo = {"KG": "kg", "L": "L", "UN": "un"}[unidade]
            st.markdown(
                f'<div class="ca-summary-total"><div class="ca-summary-total-label">Total informado · {unidade_rotulo}</div>'
                f'<div class="ca-summary-total-value">{escape(formatar_quantidade(total, unidade))}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div class="ca-summary-callout"><span class="ca-summary-callout-icon">ⓘ</span>'
            '<span>O estoque será atualizado somente após a confirmação. O código interno de cada lote será gerado automaticamente.</span></div>',
            unsafe_allow_html=True,
        )


def renderizar(st, usuario: dict[str, object]) -> None:
    _estado_inicial(st)
    cabecalho_pagina(
        st, usuario, "Doações / Registrar doação", "Registrar doação",
        "Informe os alimentos recebidos para criar os lotes e atualizar o estoque.",
    )
    doadores = listar_doadores()
    alimentos = listar_alimentos()
    if not doadores or not alimentos:
        st.info("Para receber doações, cadastre ao menos um doador e um alimento na tela Cadastros.")
        rodape_pagina(st)
        return

    st.markdown(
        '<div class="ca-donation-toolbar"><span class="ca-status-pill"><span class="ca-status-dot"></span>NOVO RECEBIMENTO</span>'
        '<span class="ca-donation-step">Etapa 1 de 1 · Dados da doação</span></div>',
        unsafe_allow_html=True,
    )
    coluna_formulario, coluna_resumo = st.columns([2.15, .98], gap="medium")
    data_padrao = obter_referencia_temporal().data_referencia
    confirmar = False
    doador: dict[str, object] | None = None
    data_recebimento = data_padrao
    observacao = ""

    with coluna_formulario:
        with st.container(key="ca-donation-form"):
            titulo, nota = st.columns([2, 1], vertical_alignment="center")
            with titulo:
                st.markdown('<div class="ca-form-panel-heading"><strong>Dados do recebimento</strong></div>', unsafe_allow_html=True)
            with nota:
                st.markdown('<div class="ca-required-note ca-required-note-right">* Campos obrigatórios</div>', unsafe_allow_html=True)

            doador = st.selectbox("Doador *", doadores, format_func=lambda row: row["nome"], key="doacao_doador")
            st.caption("Selecione a pessoa ou organização responsável pela doação.")
            col_data, col_codigo = st.columns(2)
            with col_data:
                data_recebimento = st.date_input("Data de recebimento *", value=data_padrao, format="DD/MM/YYYY", key="doacao_data")
            with col_codigo:
                codigo_origem = st.text_input("Código do lote de origem", key="doacao_codigo_origem", help="Opcional. O código interno do lote é gerado pelo sistema.")

            st.markdown('<div class="ca-form-section-label">Alimento recebido</div>', unsafe_allow_html=True)
            alimento_col, categoria_col = st.columns(2)
            with alimento_col:
                alimento = st.selectbox("Alimento *", alimentos, format_func=lambda row: row["nome"], key="doacao_alimento")
            unidade = str(alimento["unidade_medida"])
            rotulos_unidade = {"KG": "Quilograma (kg)", "L": "Litro (L)", "UN": "Unidade (un)"}
            rotulo_curto = {"KG": "kg", "L": "L", "UN": "un"}[unidade]
            with categoria_col:
                st.text_input("Categoria", value=str(alimento.get("categoria") or "—"), disabled=True, key=f"categoria_alimento_{alimento['id_alimento']}")
            col_quantidade, col_unidade = st.columns(2)
            with col_quantidade:
                quantidade = st.text_input(f"Quantidade recebida ({rotulo_curto}) *", placeholder="Ex.: 2,5", key="doacao_quantidade")
            with col_unidade:
                st.text_input("Unidade de medida *", value=rotulos_unidade[unidade], disabled=True, key=f"unidade_alimento_{alimento['id_alimento']}")
            col_validade, col_observacao = st.columns(2)
            validade_padrao = data_padrao + timedelta(days=30)
            with col_validade:
                validade = st.date_input("Data de validade *", value=validade_padrao, format="DD/MM/YYYY", key="validade_novo_item")
            with col_observacao:
                observacao = st.text_input("Observações", key="doacao_observacao")
            st.caption("A validade deve ser posterior à data de recebimento. O código interno é automático.")

            if st.button("＋　Adicionar outro alimento", key="adicionar_lote", width="content"):
                try:
                    quantidade_base = quantidade_para_unidade_base(quantidade, unidade)
                    validar_data(validade, "a validade")
                    st.session_state["itens_doacao"].append({
                        "id_alimento": alimento["id_alimento"],
                        "nome_alimento": alimento["nome"],
                        "unidade_medida": unidade,
                        "quantidade": quantidade.strip(),
                        "quantidade_base": quantidade_base,
                        "data_validade": validade,
                        "codigo_origem": texto_opcional(codigo_origem),
                    })
                    st.rerun()
                except ErroServico as exc:
                    st.error(str(exc))

            itens = st.session_state["itens_doacao"]
            for indice, item in enumerate(itens):
                with st.container(key=f"ca-donation-item-{indice}"):
                    detalhe, acao = st.columns([5, 1], vertical_alignment="center")
                    with detalhe:
                        st.markdown(f"**{escape(str(item['nome_alimento']))}**", unsafe_allow_html=True)
                        st.caption(
                            f"{formatar_quantidade(int(item['quantidade_base']), item['unidade_medida'])} · "
                            f"Validade {formatar_data(item['data_validade'])} · "
                            f"Origem {item['codigo_origem'] or 'não informada'}"
                        )
                    with acao:
                        if st.button("Remover", key=f"remover_lote_{indice}", width="content"):
                            itens.pop(indice)
                            st.rerun()

            with st.container(key="ca-donation-actions"):
                cancelar, confirmar_col = st.columns(2)
                with cancelar:
                    if st.button("Cancelar", key="cancelar_doacao", width="stretch"):
                        st.session_state["itens_doacao"] = []
                        st.session_state["mensagem_doacao"] = "Itens da doação removidos."
                        st.rerun()
                with confirmar_col:
                    confirmar = st.button(
                        "✓　Confirmar recebimento", key="confirmar_doacao", type="primary",
                        width="stretch", disabled=not itens,
                    )

    with coluna_resumo:
        _resumo(st, doador, st.session_state["itens_doacao"])

    mensagem = st.session_state.pop("mensagem_doacao", None)
    if mensagem:
        st.success(mensagem)
    if confirmar:
        try:
            itens_servico = [{
                "id_alimento": item["id_alimento"],
                "quantidade": item["quantidade"],
                "data_validade": item["data_validade"],
                "codigo_origem": item["codigo_origem"],
            } for item in st.session_state["itens_doacao"]]
            resultado = receber_doacao(
                doador["id_doador"], int(usuario["id_usuario"]), itens_servico,
                data_recebimento=data_recebimento, observacao=observacao,
            )
            st.session_state["itens_doacao"] = []
            st.success(f"Recebimento confirmado. Doação nº {resultado['id_doacao']}.")
            st.write("Lotes internos gerados: " + ", ".join(resultado["codigos_lote"]))
        except ErroServico as exc:
            st.error(str(exc))

    rodape_pagina(st)
