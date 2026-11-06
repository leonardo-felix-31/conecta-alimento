"""Menu principal organizado segundo a identidade visual do protótipo."""

from __future__ import annotations

from interface.componentes.formatacao import cabecalho_pagina, rodape_pagina


def _atalho(st, atalho: tuple[str, str, str, str, str, str, str, str | None]) -> None:
    chave, icone, categoria, titulo, descricao, rotulo, destino, aba = atalho
    with st.container(key=chave):
        st.markdown(
            f'<div class="ca-quick-top"><span class="ca-quick-icon">{icone}</span>'
            f'<span class="ca-quick-type">{categoria}</span></div>'
            f'<div class="ca-quick-card-title">{titulo}</div>'
            f'<div class="ca-quick-description">{descricao}</div>',
            unsafe_allow_html=True,
        )
        if st.button(f"{rotulo}　→", key=f"atalho_{chave}", width="content"):
            st.session_state["pagina_atual"] = destino
            if aba is not None:
                st.session_state["aba_cadastros"] = aba
            st.rerun()


def renderizar(st, usuario: dict[str, object]) -> None:
    cabecalho_pagina(
        st, usuario, "Menu principal", "Menu principal",
        "Organize o recebimento de doações e acompanhe o estoque em um só lugar.",
    )

    with st.container(key="ca-menu-hero"):
        texto, acao = st.columns([2.5, 1], vertical_alignment="center")
        with texto:
            st.markdown(
                '<div class="ca-status-pill"><span class="ca-status-dot"></span>OPERAÇÃO PRIORITÁRIA</div>',
                unsafe_allow_html=True,
            )
            st.markdown("### Registrar uma nova doação")
            st.markdown(
                "Cadastre os alimentos recebidos, informe as quantidades e as datas de validade. "
                "O estoque será atualizado após a confirmação do recebimento."
            )
        with acao:
            with st.container(key="ca-primary-cta"):
                if st.button("＋　Registrar doação", key="menu_registrar_doacao", type="primary", width="stretch"):
                    _navegar(st, "Receber doação")
            st.caption("Ação principal do sistema")

    with st.container(key="ca-quick-access"):
        esquerda, direita = st.columns([2, 1], vertical_alignment="center")
        with esquerda:
            st.markdown('<div class="ca-quick-title">Acesso rápido</div>', unsafe_allow_html=True)
        with direita:
            st.markdown('<div class="ca-quick-hint ca-quick-hint-right">Selecione uma área para continuar</div>', unsafe_allow_html=True)

        linha_superior = st.columns(3, gap="medium")
        atalhos = [
            ("ca-quick-dashboard", "▦", "Operação", "Visão geral", "Confira indicadores, movimentações e alertas de validade.", "Acessar visão geral", "Visão geral", None),
            ("ca-quick-donation", "♡", "Recebimento", "Doações", "Registre doações recebidas e os lotes de alimentos.", "Registrar doação", "Receber doação", None),
            ("ca-quick-stock", "◇", "Operação", "Estoque", "Consulte quantidades disponíveis, lotes e validades.", "Acessar estoque", "Visão geral", None),
            ("ca-quick-donors", "♙", "Cadastros", "Doadores", "Consulte e mantenha o cadastro de doadores.", "Consultar doadores", "Cadastros", "Doadores"),
            ("ca-quick-foods", "▣", "Cadastros", "Alimentos", "Consulte e mantenha o cadastro de alimentos.", "Consultar alimentos", "Cadastros", "Alimentos"),
        ]
        for coluna, atalho in zip(linha_superior, atalhos[:3]):
            with coluna:
                _atalho(st, atalho)
        linha_inferior = st.columns([.5, 1.5, 1.5, .5], gap="medium")
        for coluna, atalho in zip(linha_inferior[1:3], atalhos[3:]):
            with coluna:
                _atalho(st, atalho)

    with st.container(key="ca-information-band"):
        icone, texto = st.columns([.12, 2], vertical_alignment="center")
        with icone:
            st.markdown('<span class="ca-quick-icon">ⓘ</span>', unsafe_allow_html=True)
        with texto:
            st.markdown('<div class="ca-info-title">Informações organizadas, decisões mais claras</div>', unsafe_allow_html=True)
            st.markdown('<div class="ca-info-copy">Registre cada recebimento para manter o estoque e os indicadores atualizados.</div>', unsafe_allow_html=True)

    rodape_pagina(st, "Conecta Alimento · Gestão comunitária de alimentos")
