"""Testes do modo de alto contraste sem iniciar app ou banco real."""

from interface.componentes.visual import (
    CHAVE_ALTO_CONTRASTE,
    aplicar_estilos,
    renderizar_controle_acessibilidade,
)


class _Container:
    def __init__(self, st):
        self.st = st

    def __enter__(self):
        return self.st

    def __exit__(self, *_args):
        return False


class _StreamlitFalso:
    def __init__(self):
        self.session_state = {}
        self.markdowns = []
        self.toggles = []

    def markdown(self, conteudo, **_kwargs):
        self.markdowns.append(conteudo)

    def container(self, **_kwargs):
        return _Container(self)

    def toggle(self, label, *, key, help):
        self.toggles.append((label, key, help))
        self.session_state.setdefault(key, False)
        return self.session_state[key]


def _css(st):
    return "\n".join(st.markdowns)


def test_controle_de_acessibilidade_tem_rotulo_e_chave_de_sessao():
    st = _StreamlitFalso()
    st.session_state.setdefault(CHAVE_ALTO_CONTRASTE, False)

    assert renderizar_controle_acessibilidade(st) is False
    assert st.toggles[0][0] == "Modo de alto contraste"
    assert st.toggles[0][1] == CHAVE_ALTO_CONTRASTE
    assert "Espaço ou Enter" in st.toggles[0][2]


def test_alternancia_mantem_estado_nos_reruns_e_restaura_padrao():
    st = _StreamlitFalso()
    st.session_state.setdefault(CHAVE_ALTO_CONTRASTE, False)

    aplicar_estilos(st, alto_contraste=st.session_state[CHAVE_ALTO_CONTRASTE])
    renderizar_controle_acessibilidade(st)
    assert "--ca-bg:#000000" not in _css(st)

    # Simula a alteração que o widget nativo grava na Session State antes do rerun.
    st.session_state[CHAVE_ALTO_CONTRASTE] = True
    st.markdowns.clear()
    aplicar_estilos(st, alto_contraste=st.session_state[CHAVE_ALTO_CONTRASTE])
    assert renderizar_controle_acessibilidade(st) is True
    css_ativo = _css(st)
    assert "--ca-bg:#000000" in css_ativo
    assert "#FFFF00" in css_ativo
    assert ":focus-visible" in css_ativo
    assert ".stApp .st-key-ca-primary-cta button *" in css_ativo
    assert "[data-baseweb=\"switch\"]" in css_ativo

    # Um rerun normal conserva o valor e reaplica a paleta.
    st.markdowns.clear()
    aplicar_estilos(st, alto_contraste=st.session_state[CHAVE_ALTO_CONTRASTE])
    assert renderizar_controle_acessibilidade(st) is True
    assert "--ca-bg:#000000" in _css(st)

    st.session_state[CHAVE_ALTO_CONTRASTE] = False
    st.markdowns.clear()
    aplicar_estilos(st, alto_contraste=st.session_state[CHAVE_ALTO_CONTRASTE])
    assert renderizar_controle_acessibilidade(st) is False
    assert "--ca-bg:#000000" not in _css(st)
