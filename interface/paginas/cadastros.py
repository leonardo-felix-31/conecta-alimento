"""Formulários de doadores e alimentos com desativação lógica."""

from __future__ import annotations

from interface.componentes.formatacao import cabecalho_pagina, rodape_pagina
from servicos import ErroServico
from servicos.cadastros import (
    cadastrar_alimento, cadastrar_doador, desativar_alimento, desativar_doador,
    listar_alimentos, listar_doadores,
)

TIPOS_DOADOR = {
    "Pessoa física": "PESSOA_FISICA",
    "Empresa": "EMPRESA",
    "Organização": "ORGANIZACAO",
}


def _pagina_doadores(st) -> None:
    st.markdown("#### Cadastro de doadores")
    with st.container(key="ca-cadastros-form"):
        with st.form("novo_doador", clear_on_submit=True):
            nome = st.text_input("Nome do doador")
            col_tipo, col_telefone = st.columns(2)
            with col_tipo:
                tipo_rotulo = st.selectbox("Tipo", list(TIPOS_DOADOR))
            with col_telefone:
                telefone = st.text_input("Telefone (opcional)")
            email = st.text_input("E-mail (opcional)")
            enviado = st.form_submit_button("Cadastrar doador", type="primary")
    if enviado:
        try:
            cadastrar_doador(nome, TIPOS_DOADOR[tipo_rotulo], telefone=telefone, email=email)
            st.success("Doador cadastrado.")
        except ErroServico as exc:
            st.error(str(exc))
    st.markdown("#### Doadores cadastrados")
    doadores = listar_doadores(incluir_inativos=True)
    if doadores:
        st.dataframe([{
            "Nome": row["nome"], "Tipo": str(row["tipo"]).replace("_", " ").title(),
            "Telefone": row["telefone"] or "—", "E-mail": row["email"] or "—",
            "Situação": "Ativo" if row["ativo"] else "Inativo",
        } for row in doadores], width="stretch", hide_index=True)
        ativos = [row for row in doadores if row["ativo"]]
        if ativos:
            selecionado = st.selectbox("Desativar doador", ativos, format_func=lambda row: row["nome"], key="desativar_doador")
            if st.button("Desativar selecionado", key="btn_desativar_doador"):
                try:
                    desativar_doador(selecionado["id_doador"])
                    st.session_state["mensagem_cadastro"] = "Doador desativado; o histórico foi preservado."
                    st.rerun()
                except ErroServico as exc:
                    st.error(str(exc))
    else:
        st.markdown('<div class="ca-alert-empty">Nenhum doador cadastrado.</div>', unsafe_allow_html=True)


def _pagina_alimentos(st) -> None:
    st.markdown("#### Cadastro de alimentos")
    with st.container(key="ca-cadastros-form"):
        with st.form("novo_alimento", clear_on_submit=True):
            nome_alimento = st.text_input("Nome do alimento")
            col_categoria, col_unidade = st.columns(2)
            with col_categoria:
                categoria = st.text_input("Categoria")
            with col_unidade:
                unidade = st.selectbox(
                    "Unidade de controle", ["KG", "L", "UN"],
                    format_func=lambda item: {"KG": "Quilograma (kg)", "L": "Litro (L)", "UN": "Unidade (un)"}[item],
                )
            enviado = st.form_submit_button("Cadastrar alimento", type="primary")
    if enviado:
        try:
            cadastrar_alimento(nome_alimento, categoria, unidade)
            st.success("Alimento cadastrado.")
        except ErroServico as exc:
            st.error(str(exc))
    st.markdown("#### Alimentos cadastrados")
    alimentos = listar_alimentos(incluir_inativos=True)
    if alimentos:
        st.dataframe([{
            "Nome": row["nome"], "Categoria": row["categoria"],
            "Unidade": row["unidade_medida"], "Situação": "Ativo" if row["ativo"] else "Inativo",
        } for row in alimentos], width="stretch", hide_index=True)
        ativos = [row for row in alimentos if row["ativo"]]
        if ativos:
            selecionado = st.selectbox(
                "Desativar alimento", ativos,
                format_func=lambda row: f"{row['nome']} ({row['unidade_medida']})",
                key="desativar_alimento",
            )
            if st.button("Desativar selecionado", key="btn_desativar_alimento"):
                try:
                    desativar_alimento(selecionado["id_alimento"])
                    st.session_state["mensagem_cadastro"] = "Alimento desativado; o histórico e sua unidade foram preservados."
                    st.rerun()
                except ErroServico as exc:
                    st.error(str(exc))
    else:
        st.markdown('<div class="ca-alert-empty">Nenhum alimento cadastrado.</div>', unsafe_allow_html=True)


def renderizar(st, usuario: dict[str, object] | None = None) -> None:
    cabecalho_pagina(
        st, usuario or {"nome": "Operador"}, "Cadastros", "Cadastros",
        "Consulte doadores e alimentos e mantenha os registros organizados.",
    )
    mensagem = st.session_state.pop("mensagem_cadastro", None)
    if mensagem:
        st.success(mensagem)
    aba = st.radio(
        "Área de cadastro", ["Doadores", "Alimentos"], horizontal=True,
        key="aba_cadastros", label_visibility="collapsed",
    )
    if aba == "Doadores":
        _pagina_doadores(st)
    else:
        _pagina_alimentos(st)
    rodape_pagina(st)
