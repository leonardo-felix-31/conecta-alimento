"""Regressões de renderização dos componentes do dashboard."""

from interface.paginas import dashboard


class _Slot:
    def __init__(self, app):
        self.app = app

    def __enter__(self):
        return self.app

    def __exit__(self, *_args):
        return False


class _StreamlitFalso:
    def __init__(self):
        self.markdowns = []
        self.session_state = {}
        self.vega_specs = []

    def columns(self, especificacao, **_kwargs):
        quantidade = len(especificacao) if isinstance(especificacao, (list, tuple)) else especificacao
        return [_Slot(self) for _ in range(quantidade)]

    def container(self, **_kwargs):
        return _Slot(self)

    def expander(self, *_args, **_kwargs):
        return _Slot(self)

    def markdown(self, conteudo, **_kwargs):
        self.markdowns.append(conteudo)

    def bar_chart(self, *_args, **_kwargs):
        pass

    def vega_lite_chart(self, _data, *, spec, **_kwargs):
        self.vega_specs.append(spec)

    def dataframe(self, *_args, **_kwargs):
        pass

    def caption(self, *_args, **_kwargs):
        pass


def test_dashboard_renderiza_contagem_de_alimentos_sem_erro(monkeypatch):
    dados = {
        "data_referencia": "2026-11-02",
        "doacoes_recebidas": 1,
        "lotes_registrados": 1,
        "lotes_disponiveis": 1,
        "alimentos_disponiveis": 1,
        "estoque_por_alimento": [{
            "id_alimento": 1,
            "alimento": "Arroz",
            "unidade_medida": "KG",
            "saldo": 1000,
        }],
        "saldos_por_lote": [{
            "id_alimento": 1,
            "estado": "disponível",
            "data_validade": "2026-11-09",
        }],
        "lotes_proximos_vencimento": [{
            "alimento": "Arroz",
            "data_validade": "2026-11-09",
        }],
        "lotes_vencidos": [],
        "movimentacoes_recentes": [{
            "data_movimentacao": "2026-11-02T12:30:45-03:00",
            "tipo": "ENTRADA_DOACAO",
            "alimento": "Arroz",
            "unidade_medida": "KG",
            "quantidade": 1000,
            "codigo_lote": "CA-2026-00000001",
            "responsavel": "Operador",
        }],
        "dias_alerta_vencimento": 7,
    }
    monkeypatch.setattr(dashboard, "obter_indicadores", lambda: dados)
    st = _StreamlitFalso()

    dashboard.renderizar(st, {"nome": "Operador", "perfil": "OPERADOR"})

    assert any("em 1 alimento" in conteudo for conteudo in st.markdowns)
    assert any("<table" in conteudo and "Arroz" in conteudo for conteudo in st.markdowns)


def test_grafico_alto_contraste_define_fundo_e_eixos_legiveis():
    st = _StreamlitFalso()
    st.session_state[dashboard.CHAVE_ALTO_CONTRASTE] = True

    dashboard._grafico_movimentacoes(st, [{"data_movimentacao": "2026-11-02T12:30:45-03:00"}])

    spec = st.vega_specs[0]
    assert spec["config"]["background"] == "#000000"
    assert spec["config"]["view"]["fill"] == "#000000"
    assert spec["config"]["axis"]["labelColor"] == "#FFFFFF"
    assert spec["mark"]["color"] == "#FFFF00"
