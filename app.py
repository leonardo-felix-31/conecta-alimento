"""Aplicação Streamlit do Conecta Alimento."""

from __future__ import annotations

import logging
import streamlit as st

from banco import ErroBanco, inicializar
from interface.paginas import cadastros, dashboard, doacao, menu
from servicos import ErroServico
from servicos.autenticacao import (
    autenticar_usuario, contar_usuarios, criar_primeiro_administrador, obter_usuario_ativo,
    verificar_segredo_bootstrap,
)
from servicos import limite_autenticacao
from interface.componentes.visual import (
    CAMINHO_LOGO,
    CHAVE_ALTO_CONTRASTE,
    aplicar_estilos,
    renderizar_controle_acessibilidade,
)
from interface.componentes.navegacao import renderizar_menu_lateral
from servicos.configuracao import ambiente_hospedado, modo_demo, obter_valor

logger = logging.getLogger(__name__)


def _segredo_bootstrap() -> str:
    return obter_valor("CONECTA_BOOTSTRAP_SECRET")


st.set_page_config(page_title="Conecta Alimento", page_icon=str(CAMINHO_LOGO), layout="wide", initial_sidebar_state="expanded")
st.session_state.setdefault(CHAVE_ALTO_CONTRASTE, False)
aplicar_estilos(st, alto_contraste=bool(st.session_state[CHAVE_ALTO_CONTRASTE]))

try:
    inicializar()
except ErroBanco:
    logger.exception("Falha interna ao inicializar o banco de dados")
    st.error("Não foi possível preparar o banco de dados. Consulte o log local para obter detalhes.")
    st.stop()
except Exception:
    logger.exception("Erro inesperado ao inicializar o banco de dados")
    st.error("Ocorreu uma falha ao preparar o aplicativo. Consulte o log local para obter detalhes.")
    st.stop()


def tela_primeiro_administrador() -> None:
    with st.sidebar:
        renderizar_controle_acessibilidade(st)
    st.title("Conecta Alimento")
    st.subheader("Configuração inicial")
    st.info("Crie o primeiro usuário administrador. A senha não será armazenada em texto puro.")
    hospedado = ambiente_hospedado()
    segredo_configurado = _segredo_bootstrap() if hospedado else ""
    if hospedado and not segredo_configurado:
        st.error("A configuração inicial está bloqueada: configure o segredo de bootstrap do ambiente.")
        return
    with st.form("primeiro_administrador"):
        segredo_informado = st.text_input("Chave de autorização inicial", type="password") if hospedado else ""
        nome = st.text_input("Seu nome")
        login = st.text_input("Login", help="Use pelo menos 3 caracteres.")
        senha = st.text_input("Senha", type="password", help="Use pelo menos 12 caracteres.")
        confirmar = st.text_input("Confirme a senha", type="password")
        enviado = st.form_submit_button("Criar administrador", type="primary")
    if enviado:
        if hospedado and not verificar_segredo_bootstrap(segredo_configurado, segredo_informado):
            st.error("Não foi possível autorizar a configuração inicial.")
            return
        if senha != confirmar:
            st.error("As senhas não coincidem.")
            return
        try:
            id_usuario = criar_primeiro_administrador(nome, login, senha)
            st.session_state["usuario_id"] = id_usuario
            st.rerun()
        except ErroServico as exc:
            st.error(str(exc))
        except Exception:
            logger.exception("Falha interna ao criar o primeiro administrador")
            st.error("Não foi possível concluir a configuração inicial. Consulte o log local para obter detalhes.")


def tela_login() -> None:
    with st.sidebar:
        renderizar_controle_acessibilidade(st)
    st.title("Conecta Alimento")
    st.caption("Gestão de doações, lotes e estoque")
    with st.form("login"):
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar", type="primary")
    if enviado:
        if limite_autenticacao.bloqueado(login):
            st.error("Muitas tentativas. Aguarde 15 minutos antes de tentar novamente.")
            return
        try:
            usuario = autenticar_usuario(login, senha)
            if usuario is None:
                limite_autenticacao.registrar_falha(login)
                st.error("Login ou senha inválidos.")
            else:
                limite_autenticacao.limpar(login)
                st.session_state["usuario_id"] = usuario["id_usuario"]
                st.rerun()
        except ErroBanco:
            logger.exception("Falha interna durante autenticação")
            st.error("Não foi possível autenticar no momento. Consulte o log local para obter detalhes.")
        except Exception:
            logger.exception("Erro inesperado durante autenticação")
            st.error("Não foi possível autenticar no momento. Consulte o log local para obter detalhes.")


try:
    total_usuarios = contar_usuarios()
except ErroBanco:
    logger.exception("Falha interna ao consultar usuários")
    st.error("Não foi possível consultar os usuários. Consulte o log local para obter detalhes.")
    st.stop()
except Exception:
    logger.exception("Erro inesperado ao consultar usuários")
    st.error("Ocorreu uma falha ao consultar os usuários. Consulte o log local para obter detalhes.")
    st.stop()

if total_usuarios == 0:
    tela_primeiro_administrador()
    st.stop()

id_usuario = st.session_state.get("usuario_id")
try:
    usuario = obter_usuario_ativo(int(id_usuario)) if id_usuario is not None else None
except ErroBanco:
    logger.exception("Falha interna ao validar a sessão do usuário")
    st.error("Não foi possível validar a sessão. Consulte o log local para obter detalhes.")
    st.stop()
except Exception:
    logger.exception("Erro inesperado ao validar a sessão do usuário")
    st.error("Ocorreu uma falha ao validar a sessão. Consulte o log local para obter detalhes.")
    st.stop()
if usuario is None:
    st.session_state.pop("usuario_id", None)
    tela_login()
    st.stop()

pagina = st.session_state.setdefault("pagina_atual", "Menu principal")

with st.sidebar:
    with st.container(key="ca-sidebar-brand"):
        if st.button("Conecta Alimento", key="nav_menu_principal", width="stretch"):
            st.session_state["pagina_atual"] = "Menu principal"
            st.rerun()
    st.caption("Gestão comunitária")

    renderizar_controle_acessibilidade(st)
    renderizar_menu_lateral(st, pagina)

    with st.container(key="ca-sidebar-footer"):
        if ambiente_hospedado():
            ambiente = "Ambiente de demonstração · Dados fictícios" if modo_demo() else "Ambiente hospedado · Uso de demonstração"
        elif modo_demo():
            ambiente = "Aplicação local · Dados fictícios de demonstração"
        else:
            ambiente = "Aplicação local · Dados armazenados neste computador"
        st.markdown(f'<span class="ca-sidebar-foot-status">●　{ambiente}</span><br><div class="ca-sidebar-foot-note">Conecta Alimento · Gestão comunitária</div>', unsafe_allow_html=True)
        if st.button("Sair", key="logout", width="stretch"):
            st.session_state.pop("usuario_id", None)
            st.session_state.pop("itens_doacao", None)
            st.rerun()

try:
    if pagina == "Menu principal":
        menu.renderizar(st, usuario)
    elif pagina == "Visão geral":
        dashboard.renderizar(st, usuario)
    elif pagina == "Receber doação":
        doacao.renderizar(st, usuario)
    else:
        cadastros.renderizar(st, usuario)
except ErroServico as exc:
    st.error(str(exc))
except ErroBanco:
    logger.exception("Falha interna ao acessar o banco durante a operação da interface")
    st.error("Não foi possível concluir a operação. Consulte o log local para obter detalhes.")
except Exception:
    logger.exception("Erro inesperado durante a operação da interface")
    st.error("Ocorreu uma falha ao concluir a operação. Consulte o log local para obter detalhes.")
