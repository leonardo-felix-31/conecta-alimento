"""Formatadores de valores para apresentação brasileira."""

import html
from datetime import date, datetime

from servicos.validacoes import quantidade_para_exibicao


def formatar_data(valor: str | date | datetime) -> str:
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    try:
        if "T" in valor:
            instante = datetime.fromisoformat(valor)
            return instante.strftime("%d/%m/%Y %H:%M")
        return date.fromisoformat(valor).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(valor)


def formatar_quantidade(valor_base: int, unidade: str) -> str:
    rotulos = {"KG": "kg", "L": "L", "UN": "un"}
    return f"{quantidade_para_exibicao(valor_base, unidade)} {rotulos[unidade]}"


def cabecalho_pagina(st, usuario: dict[str, object], pagina: str, titulo: str, descricao: str) -> None:
    """Desenha o cabeçalho comum sem substituir controles Streamlit por HTML."""
    nome_original = str(usuario.get("nome", "Usuário"))
    nome = html.escape(nome_original)
    iniciais = "".join(parte[0] for parte in nome_original.split()[:2]).upper() or "CA"
    iniciais = html.escape(iniciais)
    perfil_original = str(usuario.get("perfil", "OPERADOR"))
    perfil = html.escape(perfil_original.replace("_", " ").title())
    esquerda, direita = st.columns([3, 1.35], vertical_alignment="center")
    with esquerda:
        partes = [html.escape(parte.strip()) for parte in pagina.split("/") if parte.strip()]
        caminho = " / ".join(partes[:-1])
        breadcrumb = f"Início / {caminho + ' / ' if caminho else ''}<strong>{partes[-1] if partes else ''}</strong>"
        st.markdown(f'<div class="ca-breadcrumb">{breadcrumb}</div>', unsafe_allow_html=True)
    with direita:
        st.markdown(
            f'<div class="ca-account"><div class="ca-avatar">{iniciais}</div>'
            f'<div><div class="ca-account-name">{nome}</div>'
            f'<div class="ca-account-meta">Perfil: {perfil} · Sessão ativa</div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="ca-page-heading"><div class="ca-org">Associação Comunitária Mesa Solidária</div>'
        f'<h1 class="ca-page-title">{html.escape(titulo)}</h1>'
        f'<div class="ca-page-subtitle">{html.escape(descricao)}</div></div>',
        unsafe_allow_html=True,
    )


def rodape_pagina(st, nota: str = "Conecta Alimento · Gestão comunitária de alimentos") -> None:
    st.markdown(
        f'<div class="ca-footer"><span>{html.escape(nota)}</span>'
        '<span>Aplicação local · Dados neste computador</span></div>',
        unsafe_allow_html=True,
    )
