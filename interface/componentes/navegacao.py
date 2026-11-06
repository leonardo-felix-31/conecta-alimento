"""Navegação lateral somente para os fluxos operacionais disponíveis."""

from __future__ import annotations


def _selecionar(st, pagina: str, aba: str | None = None) -> None:
    st.session_state["pagina_atual"] = pagina
    if aba is not None:
        st.session_state["aba_cadastros"] = aba
    st.rerun()


def renderizar_menu_lateral(st, pagina: str) -> None:
    st.markdown('<div class="ca-sidebar-section">Menu principal</div>', unsafe_allow_html=True)
    with st.container(key="ca-sidebar-main-nav"):
        if st.button(
            "▦　Visão geral", key="nav_visao_geral",
            type="primary" if pagina in {"Menu principal", "Visão geral"} else "secondary",
            width="stretch",
        ):
            _selecionar(st, "Visão geral")
        if st.button(
            "♡　Doações", key="nav_doacoes",
            type="primary" if pagina == "Receber doação" else "secondary", width="stretch",
        ):
            _selecionar(st, "Receber doação")
        if st.button("◇　Estoque", key="nav_estoque", type="secondary", width="stretch"):
            _selecionar(st, "Visão geral")

    st.markdown('<div class="st-key-ca-sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ca-sidebar-section">Cadastros</div>', unsafe_allow_html=True)
    with st.container(key="ca-sidebar-register-nav"):
        if st.button(
            "♙　Doadores", key="nav_doadores",
            type="primary" if pagina == "Cadastros" and st.session_state.get("aba_cadastros") != "Alimentos" else "secondary",
            width="stretch",
        ):
            _selecionar(st, "Cadastros", "Doadores")
        if st.button(
            "▣　Alimentos", key="nav_alimentos",
            type="primary" if pagina == "Cadastros" and st.session_state.get("aba_cadastros") == "Alimentos" else "secondary",
            width="stretch",
        ):
            _selecionar(st, "Cadastros", "Alimentos")
