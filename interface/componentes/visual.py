"""Identidade visual compartilhada do Conecta Alimento."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

RAIZ_INTERFACE = Path(__file__).resolve().parent.parent
CAMINHO_LOGO = RAIZ_INTERFACE / "assets" / "logo.svg"
CHAVE_ALTO_CONTRASTE = "modo_alto_contraste"

ALTO_CONTRASTE_CSS = """
  :root {
    color-scheme: dark;
    --ca-sidebar:#000000; --ca-bg:#000000; --ca-white:#000000;
    --ca-active:#FFFF00; --ca-green:#FFFF00; --ca-ink:#FFFFFF;
    --ca-muted:#F2F2F2; --ca-border:#FFFFFF; --ca-soft:#111111;
    --ca-warn:#FFFF00; --ca-warn-bg:#3D2B00; --ca-blue:#80DFFF;
    --ca-purple:#E0D6FF;
  }
  html,body,.stApp,[data-testid="stAppViewContainer"],
  [data-testid="stMain"],[data-testid="stMainBlockContainer"] {
    background:#000000!important;color:#FFFFFF!important;color-scheme:dark!important;
  }
  [data-testid="stHeader"],section[data-testid="stSidebar"],
  section[data-testid="stSidebar"]>div,
  section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background:#000000!important;color:#FFFFFF!important;
  }
  section[data-testid="stSidebar"] {border-right:2px solid #FFFFFF!important;}
  .stApp :is(h1,h2,h3,h4,p,span,small,label,li,summary,td,th,
    [data-testid="stWidgetLabel"],[data-testid="stCaptionContainer"],
    .stMarkdown,.stCaption) {color:#FFFFFF!important;}
  .stApp a,.stApp a:visited {color:#80DFFF!important;text-decoration:underline!important;}
  .stApp :is(input,textarea,[data-baseweb="select"]>div,[role="combobox"]) {
    background:#000000!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;
  }
  .stApp :is(input,textarea)::placeholder {color:#F2F2F2!important;opacity:1!important;}
  .stApp :is([role="option"],[role="listbox"]) {background:#000000!important;color:#FFFFFF!important;}
  .stApp input:disabled,.stApp textarea:disabled {
    background:#111111!important;color:#F2F2F2!important;border-color:#FFFFFF!important;
  }
  .stApp button {
    background:#000000!important;color:#FFFFFF!important;
    border:2px solid #FFFFFF!important;opacity:1!important;
  }
  .stApp button:hover:not(:disabled),.stApp button:disabled {
    background:#111111!important;color:#FFFFFF!important;border-color:#FFFFFF!important;
  }
  .stApp button[kind="primary"],.stApp .stFormSubmitButton>button[kind="primary"],
  .stApp .st-key-ca-primary-cta button,
  section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background:#FFFF00!important;color:#000000!important;border:2px solid #FFFF00!important;
    font-weight:800!important;opacity:1!important;
  }
  .stApp button[kind="primary"] *,
  .stApp .stFormSubmitButton>button[kind="primary"] *,
  .stApp .st-key-ca-primary-cta button *,
  section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] * {
    color:#000000!important;
  }
  .stApp button[kind="primary"]:hover:not(:disabled),
  .stApp .st-key-ca-primary-cta button:hover:not(:disabled) {
    background:#FFFFFF!important;color:#000000!important;border-color:#FFFFFF!important;
  }
  .stApp [role="switch"],.stApp [data-baseweb="switch"],
  .st-key-ca-high-contrast-control [role="switch"],
  .st-key-ca-high-contrast-control [data-baseweb="switch"] {
    background:#FFFF00!important;border:2px solid #FFFFFF!important;
  }
  .stApp [role="switch"] *, .stApp [data-baseweb="switch"] * {background:#000000!important;}
  .stApp [role="tab"] {color:#FFFFFF!important;border-color:#FFFFFF!important;}
  .stApp [role="tab"][aria-selected="true"] {color:#FFFF00!important;border-bottom:3px solid #FFFF00!important;}
  .stApp :is([data-testid="stTabs"],[data-testid="stExpander"],
    [data-testid="stForm"],[data-testid="stAlert"],
    [data-testid="stDataFrame"],[data-testid="stTable"],
    [data-testid="stVegaLiteChart"],[data-testid="stArrowVegaLiteChart"]) {
    background:#000000!important;color:#FFFFFF!important;border-color:#FFFFFF!important;
  }
  .stApp [data-testid="stAlert"] {border:2px solid #FFFFFF!important;}
  .stApp [data-testid="stVegaLiteChart"] svg text,
  .stApp [data-testid="stArrowVegaLiteChart"] svg text {fill:#FFFFFF!important;}
  .stApp [data-testid="stVegaLiteChart"] svg line,
  .stApp [data-testid="stArrowVegaLiteChart"] svg line {stroke:#FFFFFF!important;}
  .st-key-ca-sidebar-brand,.st-key-ca-quick-dashboard,.st-key-ca-quick-donation,
  .st-key-ca-quick-cadastros,.st-key-ca-information-band,
  .st-key-ca-metric-received,.st-key-ca-metric-distributed,
  .st-key-ca-metric-stock,.st-key-ca-metric-expiry,
  .st-key-ca-dashboard-chart,.st-key-ca-dashboard-alerts,
  .st-key-ca-dashboard-stock,.st-key-ca-dashboard-history,
  .st-key-ca-donation-form,.st-key-ca-donation-summary,
  .st-key-ca-cadastros-form,[class*="st-key-ca-donation-item-"] {
    background:#000000!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;
    box-shadow:none!important;
  }
  .st-key-ca-menu-hero {background:#000000!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;}
  .ca-page-title,.ca-section-heading,.ca-panel-heading,.ca-metric-top,
  .ca-quick-card-title,
  .ca-quick-title,.ca-metric-value,.ca-summary-title,.ca-summary-total-value,
  .ca-form-section-label,.ca-info-title,.ca-account-name,.ca-breadcrumb strong,
  .ca-alert-title,.ca-table {color:#FFFFFF!important;}
  .ca-org,.ca-breadcrumb,.ca-page-subtitle,.ca-account-meta,.ca-quick-hint,
  .ca-quick-description,.ca-panel-meta,.ca-metric-note,.ca-summary-subtitle,
  .ca-summary-row,.ca-summary-row strong,.ca-summary-item-name,
  .ca-summary-item-detail,.ca-summary-total-label,.ca-required-note,
  .ca-donation-step,.ca-alert-copy,.ca-alert-empty,.ca-footer,
  .ca-info-copy,.ca-quick-type,.ca-chart-legend,.ca-summary-callout-icon,
  .ca-table th,.ca-table td {color:#F2F2F2!important;}
  .ca-date-filter {background:#000000!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;}
  .ca-legend-dot {background:#FFFF00!important;}
  .ca-status-pill,.ca-quick-icon,.ca-metric-icon,.ca-alert-icon,
  .ca-summary-total,.ca-table-status,.ca-table-status.warn,.ca-table-status.expired {
    background:#FFFF00!important;color:#000000!important;border:1px solid #FFFF00!important;
  }
  .ca-summary-total * {color:#000000!important;}
  .ca-status-pill *,.ca-quick-icon *,.ca-metric-icon *,.ca-alert-icon *,
  .ca-table-status * {color:#000000!important;}
  .ca-alert-header {background:#3D2B00!important;color:#FFFFFF!important;border-bottom:2px solid #FFFFFF!important;}
  .ca-alert-icon.info {background:#00234D!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;}
  .ca-alert-icon.ok {background:#003B22!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;}
  .ca-summary-callout {background:#3D2B00!important;color:#FFFFFF!important;border:2px solid #FFFFFF!important;}
  .ca-summary-callout * {color:#FFFFFF!important;}
  table.ca-table,table.ca-table thead,table.ca-table tbody,table.ca-table tr,
  table.ca-table th,table.ca-table td {background:#000000!important;border-color:#FFFFFF!important;}
  table.ca-table thead {background:#111111!important;}
  .stApp :focus-visible {outline:3px solid #FFFF00!important;outline-offset:3px!important;box-shadow:0 0 0 2px #000000!important;}
  ::selection {background:#FFFF00!important;color:#000000!important;}
  .st-key-ca-high-contrast-control {background:#000000!important;border:2px solid #FFFFFF!important;border-radius:8px;padding:8px 10px;margin:8px 0 12px;}
"""


def uri_logo() -> str:
    """Retorna o símbolo vetorial local como data URI independente do cwd."""
    conteudo = base64.b64encode(CAMINHO_LOGO.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{conteudo}"


def aplicar_estilos(st, *, alto_contraste: bool = False) -> None:
    """Aplica os tokens visuais e componentes próprios do produto."""
    marca = uri_logo()
    st.markdown(f"""
    <style>
      :root {{
        color-scheme: only light;
        --ca-sidebar:#153B32; --ca-bg:#F6F8F5; --ca-white:#FFFFFF;
        --ca-active:#E7F1EB; --ca-green:#257347; --ca-ink:#183326;
        --ca-muted:#687A70; --ca-border:#DCE7DF; --ca-soft:#EEF5EF;
        --ca-warn:#8B5A12; --ca-warn-bg:#FFF8E9; --ca-blue:#376DA8;
        --ca-purple:#7563A4;
      }}
      html,body,.stApp,[data-testid="stAppViewContainer"] {{
        background:var(--ca-bg)!important; color:var(--ca-ink)!important;
        font-family:Inter,"Segoe UI",Arial,sans-serif;
      }}
      [data-testid="stHeader"] {{background:transparent;}}
      .block-container {{box-sizing:border-box;width:100%;max-width:none;padding:28px 48px 24px;}}
      section[data-testid="stSidebar"] {{width:259px!important;min-width:259px!important;background:var(--ca-sidebar)!important;border:0;}}
      section[data-testid="stSidebar"]>div {{height:100%;background:var(--ca-sidebar)!important;padding:20px 18px 18px;}}
      section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{background:var(--ca-sidebar)!important;}}
      section[data-testid="stSidebar"] * {{color:#E5EEE8;}}
      .st-key-ca-sidebar-brand {{padding:0 0 20px;margin-bottom:15px;border-bottom:1px solid rgba(231,241,235,.20);}}
      .st-key-ca-sidebar-brand button {{
        min-height:48px;padding:0 5px 0 64px!important;text-align:left;justify-content:flex-start;
        background-color:transparent!important;background-image:url("{marca}")!important;
        background-repeat:no-repeat!important;background-position:10px center!important;background-size:42px 42px!important;
        border:0!important;box-shadow:none!important;color:#F2F6F3!important;font-size:17px!important;font-weight:700!important;
      }}
      .st-key-ca-sidebar-brand button:hover {{background-color:#214B40!important;}}
      .st-key-ca-sidebar-brand [data-testid="stCaptionContainer"] {{padding-left:64px;margin-top:-12px;color:#AFC8BA!important;font-size:11px;}}
      .ca-sidebar-section {{color:#A7C1B4;font-size:10px;font-weight:700;letter-spacing:.08em;margin:2px 12px 10px;text-transform:uppercase;}}
      .st-key-ca-sidebar-main-nav,.st-key-ca-sidebar-register-nav {{display:flex;flex-direction:column;gap:4px;}}
      section[data-testid="stSidebar"] button {{
        width:100%;min-height:43px;justify-content:flex-start;text-align:left;padding:0 12px;
        border:0!important;border-radius:10px!important;background-color:transparent!important;box-shadow:none!important;
        color:#D3E0D8!important;font-size:13px;font-weight:450;
      }}
      section[data-testid="stSidebar"] button:hover:not(:disabled) {{background-color:#214B40!important;color:#fff!important;}}
      section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {{background:var(--ca-active)!important;color:var(--ca-sidebar)!important;font-weight:700;}}
      section[data-testid="stSidebar"] button:disabled {{opacity:.60;}}
      section[data-testid="stSidebar"] .st-key-ca-sidebar-brand button {{background-color:transparent!important;background-image:url("{marca}")!important;background-repeat:no-repeat!important;background-position:10px center!important;background-size:42px 42px!important;color:#F2F6F3!important;}}
      section[data-testid="stSidebar"] .st-key-ca-sidebar-brand button:hover {{background-color:#214B40!important;}}
      .st-key-ca-sidebar-divider {{border-top:1px solid rgba(231,241,235,.20);margin:16px 0 17px;}}
      .st-key-ca-sidebar-footer {{margin-top:22px;border-top:1px solid rgba(231,241,235,.20);padding:16px 7px 0;color:#C3D5CB;font-size:10px;line-height:1.5;}}
      .ca-sidebar-foot-status {{color:#8AC7A6;font-size:11px;}}
      .ca-sidebar-foot-note {{color:#8FAE9F;font-size:9px;margin-top:15px;}}

      .ca-topline {{display:flex;justify-content:space-between;align-items:center;min-height:40px;}}
      .ca-breadcrumb {{color:#73847B;font-size:12px;}}
      .ca-breadcrumb strong {{color:#304A3E;font-weight:650;}}
      .ca-account {{display:flex;justify-content:flex-end;align-items:center;gap:11px;min-height:40px;}}
      .ca-avatar {{width:38px;height:38px;border-radius:50%;background:#DDECE3;color:#176246;display:grid;place-items:center;font-size:11px;font-weight:750;flex:0 0 38px;}}
      .ca-account-name {{color:#22382E;font-size:13px;font-weight:700;line-height:1.2;}}
      .ca-account-meta {{color:#708178;font-size:10px;margin-top:3px;}}
      .ca-page-heading {{margin-top:25px;}}
      .ca-org {{color:#257347;font-size:10px;font-weight:750;letter-spacing:.11em;line-height:1.5;text-transform:uppercase;margin:0 0 4px;}}
      .ca-page-title {{color:var(--ca-ink);font-size:30px;font-weight:720;letter-spacing:-.035em;line-height:1.12;margin:0;}}
      .ca-page-subtitle {{color:#708178;font-size:14px;line-height:1.45;margin:6px 0 0;}}
      .ca-status-pill {{display:inline-flex;align-items:center;gap:8px;background:#EEF4ED;border-radius:24px;color:#476B55;font-size:10px;line-height:1.3;padding:10px 20px;}}
      .ca-status-dot {{display:inline-block;width:6px;height:6px;border-radius:50%;background:#8BC9A4;}}
      .ca-section-heading {{color:#273F34;font-size:16px;font-weight:700;margin:0;}}
      .ca-quick-hint-right,.ca-panel-meta-right,.ca-required-note-right {{text-align:right;}}

      .st-key-ca-menu-hero {{position:relative;overflow:hidden;background:#EAF3EA!important;border:1px solid #D5E6D7!important;border-radius:17px!important;min-height:204px;margin-top:29px;padding:29px 30px!important;}}
      .st-key-ca-menu-hero:after {{content:"";position:absolute;width:360px;height:360px;right:56px;top:-155px;border:1px solid rgba(46,117,82,.055);border-radius:50%;box-shadow:0 0 0 28px rgba(46,117,82,.025),0 0 0 58px rgba(46,117,82,.02),0 0 0 88px rgba(46,117,82,.015);pointer-events:none;}}
      .st-key-ca-menu-hero .ca-status-pill {{background:#D6E9DC;color:#235C46;font-weight:700;}}
      .st-key-ca-menu-hero h3 {{color:#1E4434;font-size:23px;line-height:1.2;margin:12px 0 7px;}}
      .st-key-ca-menu-hero p {{color:#5D7367;font-size:14px;line-height:1.5;max-width:630px;margin:0;}}
      .st-key-ca-menu-hero .stButton {{position:relative;z-index:1;}}
      .st-key-ca-primary-cta button {{min-height:55px;background:#225B4B!important;border:3px solid #E9A323!important;border-radius:13px!important;color:#fff!important;font-size:13px;}}
      .st-key-ca-quick-access {{margin-top:24px;}}
      .ca-quick-head {{display:flex;justify-content:space-between;align-items:center;margin-bottom:13px;}}
      .ca-quick-title {{color:#263F34;font-size:16px;font-weight:700;}}
      .ca-quick-hint {{color:#7A8981;font-size:11px;}}
      .st-key-ca-quick-dashboard,.st-key-ca-quick-donation,.st-key-ca-quick-cadastros {{min-height:190px;background:#fff!important;border:1px solid var(--ca-border)!important;border-radius:15px!important;padding:19px 19px 14px!important;}}
      .ca-quick-top {{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}}
      .ca-quick-icon {{width:40px;height:40px;display:grid;place-items:center;border-radius:12px;background:#EEF4EF;color:#286B55;font-size:19px;}}
      .ca-quick-type {{color:#78867E;font-size:9px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;}}
      .ca-quick-card-title {{color:#273F34;font-size:14px;font-weight:700;margin-bottom:5px;}}
      .ca-quick-description {{color:#75857C;font-size:11px;line-height:1.45;min-height:35px;}}
      .st-key-ca-information-band {{margin-top:22px;background:#fff!important;border:1px solid var(--ca-border)!important;border-radius:13px!important;padding:13px 16px!important;}}
      .ca-info-title {{color:#334F40;font-size:11px;font-weight:700;}}
      .ca-info-copy {{color:#7A8981;font-size:10px;margin-top:5px;}}
      .ca-footer {{display:flex;justify-content:space-between;align-items:center;color:#8A9991;font-size:10px;margin-top:19px;}}

      .st-key-ca-dashboard-top-tools {{display:flex;justify-content:flex-end;align-items:center;min-height:32px;margin:14px 0 8px;}}
      .ca-date-filter {{display:inline-flex;align-items:center;min-height:40px;padding:0 14px;border:1px solid var(--ca-border);border-radius:10px;background:#fff;color:#43594C;font-size:11px;font-weight:650;}}
      .st-key-ca-metric-received,.st-key-ca-metric-distributed,.st-key-ca-metric-stock,.st-key-ca-metric-expiry {{min-height:113px;background:#fff!important;border:1px solid var(--ca-border)!important;border-radius:13px!important;padding:14px 15px 12px!important;}}
      .st-key-ca-metric-received {{border-left:6px solid #225B4B!important;}}
      .st-key-ca-metric-distributed {{border-left:6px solid #376DA8!important;}}
      .st-key-ca-metric-stock {{border-left:6px solid #7563A4!important;}}
      .st-key-ca-metric-expiry {{border-left:6px solid #8B5A12!important;}}
      .ca-metric-top {{display:flex;align-items:center;gap:9px;color:#63766B;font-size:9px;font-weight:700;letter-spacing:.025em;text-transform:uppercase;}}
      .ca-metric-icon {{width:29px;height:29px;display:grid;place-items:center;background:#EAF2EC;border-radius:9px;color:#276B54;font-size:14px;}}
      .ca-metric-value {{color:#1D3F31;font-size:28px;font-weight:750;line-height:1.05;margin-top:9px;}}
      .ca-metric-note {{color:#7B8982;font-size:9px;margin-top:5px;}}
      .st-key-ca-dashboard-chart,.st-key-ca-dashboard-alerts {{min-height:292px;background:#fff!important;border:1px solid var(--ca-border)!important;border-radius:15px!important;padding:17px 17px 14px!important;}}
      .ca-panel-heading {{color:#293F34;font-size:16px;font-weight:700;}}
      .ca-panel-meta {{color:#76867D;font-size:10px;}}
      .ca-chart-legend {{display:flex;justify-content:flex-end;gap:18px;color:#6F8077;font-size:10px;margin:11px 7px 3px;}}
      .ca-legend-dot {{display:inline-block;width:8px;height:8px;border-radius:50%;background:#2A735C;margin-right:6px;}}
      .ca-alert-header {{background:#FFF8E9;color:#795318;margin:-17px -17px 8px;padding:15px 18px;border-radius:14px 14px 0 0;font-size:16px;font-weight:700;}}
      .ca-alert-row {{display:grid;grid-template-columns:30px 1fr auto;align-items:center;gap:10px;min-height:75px;border-bottom:1px solid #E8EEE9;padding:7px 3px;}}
      .ca-alert-icon {{width:29px;height:29px;display:grid;place-items:center;border-radius:50%;background:#FFF2D7;color:#8B5A12;font-weight:800;font-size:13px;}}
      .ca-alert-icon.info {{background:#EAF1F8;color:#376DA8;}}
      .ca-alert-icon.ok {{background:#E8F2EC;color:#35795D;}}
      .ca-alert-title {{color:#273A30;font-size:11px;font-weight:700;}}
      .ca-alert-copy {{color:#7B8981;font-size:9px;line-height:1.45;margin-top:4px;}}
      .ca-alert-empty {{color:#718178;font-size:11px;padding:17px 4px;}}
      .st-key-ca-dashboard-stock,.st-key-ca-dashboard-history {{margin-top:17px;background:#fff!important;border:1px solid var(--ca-border)!important;border-radius:15px!important;padding:16px 16px 18px!important;}}
      .ca-stock-header {{display:flex;justify-content:space-between;align-items:center;margin:0 0 12px;}}
      table.ca-table {{width:100%;border-collapse:collapse;font-size:10px;color:#354D41;}}
      table.ca-table thead {{background:#F3F6F3;color:#5E7166;}}
      table.ca-table th {{text-align:left;font-weight:700;padding:10px 13px;}}
      table.ca-table td {{border-bottom:1px solid #E6ECE7;padding:10px 13px;}}
      .ca-table-status {{display:inline-block;min-width:65px;text-align:center;border-radius:20px;background:#E7F1EB;color:#287252;font-size:9px;font-weight:700;padding:5px 10px;}}
      .ca-table-status.warn {{background:#FFF2D7;color:#94600F;}}
      .ca-table-status.expired {{background:#FBE9E7;color:#A34436;}}

      .st-key-ca-donation-form,.st-key-ca-donation-summary {{background:#fff!important;border:1px solid var(--ca-border)!important;border-radius:15px!important;padding:19px 21px!important;}}
      .st-key-ca-donation-form,.st-key-ca-donation-summary {{min-height:626px;}}
      .ca-donation-toolbar {{display:flex;justify-content:space-between;align-items:center;margin-top:19px;margin-bottom:14px;}}
      .ca-donation-step {{color:#7B8981;font-size:10px;}}
      .ca-form-panel-heading {{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #E3EAE4;padding:0 0 12px;margin-bottom:9px;}}
      .ca-form-section-label {{color:#597466;font-size:11px;font-weight:750;text-transform:uppercase;letter-spacing:.035em;}}
      .ca-required-note {{color:#849189;font-size:10px;}}
      .ca-summary-title {{color:#2B4437;font-size:14px;font-weight:700;margin:0;}}
      .ca-summary-subtitle {{color:#829087;font-size:10px;line-height:1.5;margin:6px 0 15px;}}
      .ca-summary-row {{display:flex;justify-content:space-between;gap:14px;align-items:center;border-bottom:1px solid #E8EEE9;min-height:38px;color:#7A8981;font-size:10px;}}
      .ca-summary-row strong {{color:#344C3F;font-size:10px;font-weight:700;text-align:right;}}
      .ca-summary-item {{padding:10px 0;border-bottom:1px solid #E8EEE9;}}
      .ca-summary-item-name {{color:#324A3D;font-size:11px;font-weight:700;}}
      .ca-summary-item-detail {{color:#7A8981;font-size:9px;line-height:1.55;margin-top:4px;}}
      .ca-summary-total {{background:#EDF4EE;border:1px solid #D8E8DA;border-radius:11px;padding:14px 15px;margin:15px 0 10px;}}
      .ca-summary-total-label {{color:#6B8074;font-size:10px;}}
      .ca-summary-total-value {{color:#225B48;font-size:25px;font-weight:750;margin-top:3px;}}
      .ca-summary-callout {{display:flex;gap:9px;background:var(--ca-warn-bg);border:1px solid #EEDBAA;border-radius:9px;padding:11px 12px;color:#80612A;font-size:9px;line-height:1.55;margin-top:11px;}}
      .ca-summary-callout-icon {{color:#A57522;font-size:14px;}}
      [class*="st-key-ca-donation-item-"] {{background:#FAFCFA!important;border:1px solid #DCE7DF!important;border-radius:9px!important;padding:7px 10px!important;margin-top:6px;}}
      .st-key-ca-donation-actions {{border-top:1px solid #E5EBE6;margin-top:15px;padding-top:10px;}}
      .st-key-ca-cadastros-form {{background:#fff;border:1px solid var(--ca-border);border-radius:13px;padding:18px 20px;}}

      h1,h2,h3,h4,p {{color:var(--ca-ink);}}
      .stMarkdown p {{line-height:1.45;}}
      input,textarea,[data-baseweb="select"]>div {{background:#fff!important;color:#183326!important;border-color:#C9D8CE!important;border-radius:8px!important;}}
      input:disabled {{background:#F6F8F5!important;color:#687A70!important;}}
      label,[data-testid="stWidgetLabel"] {{color:#334C40!important;font-size:11px!important;}}
      .stButton>button,.stFormSubmitButton>button {{min-height:42px;border-radius:9px;font-size:11px;font-weight:650;border:1px solid #C9D8CE;}}
      .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {{background:#225B4B;color:#fff;border-color:#225B4B;}}
      .stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover {{background:#1B4E40;color:#fff;border-color:#1B4E40;}}
      [data-testid="stAlert"] {{background:#fff;border:1px solid var(--ca-border);color:var(--ca-ink);}}
      div[data-testid="stDataFrame"] {{border:1px solid var(--ca-border);border-radius:10px;overflow:hidden;}}
      @media(max-width:1000px) {{.block-container{{padding:24px;}}.st-key-ca-dashboard-chart,.st-key-ca-dashboard-alerts,.st-key-ca-donation-form,.st-key-ca-donation-summary{{min-height:unset;}}}}
      @media(max-width:700px) {{.block-container{{padding:18px 14px;}}.ca-page-title{{font-size:25px;}}.ca-footer{{align-items:flex-start;flex-direction:column;gap:5px;}}table.ca-table th,table.ca-table td{{padding:8px 7px;}}}}
    </style>
    """, unsafe_allow_html=True)
    if alto_contraste:
        st.markdown(f"<style>{ALTO_CONTRASTE_CSS}</style>", unsafe_allow_html=True)


def renderizar_controle_acessibilidade(st) -> bool:
    """Renderiza o toggle nativo, com rótulo e suporte a teclado.

    O estado é mantido pela chave de sessão CHAVE_ALTO_CONTRASTE.
    """
    with st.container(key="ca-high-contrast-control"):
        return st.toggle(
            "Modo de alto contraste",
            key=CHAVE_ALTO_CONTRASTE,
            help="Alterna para uma paleta de alto contraste. Use Espaço ou Enter para ativar.",
        )


def tabela_html(
    cabecalhos: list[str],
    linhas: list[list[str]],
    *,
    classes: str = "",
    colunas_status: tuple[int, ...] = (),
) -> str:
    """Gera tabela acessível, escapando dados externos e estilizando status conhecidos."""
    header_html = "".join(f"<th scope='col'>{escape(str(item))}</th>" for item in cabecalhos)
    status_classes = {"normal": "", "atenção": " warn", "vencido": " expired"}
    rows = []
    for linha in linhas:
        celulas = []
        for indice, valor in enumerate(linha):
            texto = escape(str(valor))
            if indice in colunas_status:
                classe = status_classes.get(str(valor).strip().casefold(), "")
                texto = f"<span class='ca-table-status{classe}'>{texto}</span>"
            celulas.append(f"<td>{texto}</td>")
        rows.append("<tr>" + "".join(celulas) + "</tr>")
    return (
        f"<table class='ca-table {escape(classes)}'><thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
