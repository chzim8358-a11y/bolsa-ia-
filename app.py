import streamlit as st
import pandas as pd
import base64
import math
from pathlib import Path

from dados import (
    dados_yahoo, dados_btg_realtime, cotacoes_btg, cotacoes_yahoo_realtime, btg_disponivel,
    ATIVOS_B3,
)
from indicadores import calcular_indicadores
from analisador import analisar, analisar_candles, calcular_plano
from dividendos import obter_dividendos_yahoo

st.set_page_config(
    page_title="BolsaIA V33 | Inteligência de Mercado",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# V29 — identidade visual premium baseada na nova marca BolsaIA; foco em apresentação comercial.
_logo_path = Path(__file__).with_name("logo.png")
_logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode("ascii") if _logo_path.exists() else ""
_hero_html = """
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(circle at 12% -5%, #112a52 0%, #09111f 34%, #050811 78%); }
.block-container { max-width: 1480px; padding-top: .7rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#08111f,#0b1424); border-right: 1px solid rgba(90,170,255,.12); }
.hero { position:relative; overflow:hidden; padding:1.25rem 1.35rem; border:1px solid rgba(91,190,255,.18); border-radius:22px; background:linear-gradient(135deg,rgba(13,31,58,.97),rgba(7,13,26,.98)); box-shadow:0 18px 55px rgba(0,0,0,.28); margin-bottom:.9rem; }
.hero:after { content:""; position:absolute; width:280px; height:280px; right:-120px; top:-160px; border-radius:50%; background:rgba(0,210,255,.10); filter:blur(8px); }
.brand-row { display:flex; align-items:center; gap:1rem; position:relative; z-index:1; }
.brand-logo { width:92px; height:92px; object-fit:cover; border-radius:18px; border:1px solid rgba(255,255,255,.12); box-shadow:0 10px 30px rgba(0,0,0,.28); }
.hero h1 { margin:0; font-size:2.25rem; letter-spacing:-.045em; color:#f8fafc; }
.hero .tagline { margin:.28rem 0 0; color:#a9bbd3; font-size:1rem; }
.hero .mini { margin-top:.65rem; display:flex; gap:.45rem; flex-wrap:wrap; }
.chip { display:inline-block; padding:.32rem .62rem; border-radius:999px; font-size:.74rem; font-weight:800; background:#0c2038; color:#8edcff; border:1px solid #164a72; }
.chip.green { color:#7ee2a8; background:#0d281d; border-color:#20573a; }
.section { font-size:1.08rem; font-weight:850; margin-top:1.2rem; padding:.52rem 0; border-bottom:1px solid rgba(255,255,255,.10); color:#f8fafc; }
.badge { display:inline-block; padding:.3rem .7rem; border-radius:999px; font-size:.78rem; font-weight:750; background:#102a1d; color:#7ee2a8; border:1px solid #24583a; margin-top:.8rem; }
.muted { color:#94a3b8; font-size:.84rem; }
.exec-card { border:1px solid rgba(96,170,255,.13); border-radius:17px; padding:1rem 1.05rem; background:linear-gradient(145deg,rgba(16,31,54,.9),rgba(10,17,30,.9)); box-shadow:0 9px 28px rgba(0,0,0,.2); min-height:112px; }
.exec-label { color:#8fa6c5; font-size:.76rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
.exec-value { color:#f8fafc; font-size:1.6rem; font-weight:900; margin-top:.2rem; }
.v22-hero { margin:.7rem 0 1.1rem; padding:1rem 1.15rem; border-radius:18px; border:1px solid rgba(70,207,255,.16); background:linear-gradient(135deg,rgba(10,27,50,.88),rgba(8,15,28,.88)); }
.v22-kicker { color:#62d8ff; font-size:.72rem; font-weight:900; text-transform:uppercase; letter-spacing:.09em; }
.v22-title { color:#f8fafc; font-size:1.45rem; font-weight:900; margin:.15rem 0 .2rem; }
.v22-sub { color:#9fb2ca; font-size:.86rem; }
.v22-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.7rem; margin-top:.8rem; }
.v22-tile { padding:.75rem .8rem; border-radius:13px; background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.07); }
.v22-tile strong { display:block; color:#f8fafc; font-size:.92rem; }
.v22-tile span { color:#91a6c1; font-size:.76rem; }
@media (max-width:700px) { .v22-grid { grid-template-columns:1fr; } .v22-title { font-size:1.2rem; } } 
.v27-market { display:grid; grid-template-columns:1.4fr .8fr .8fr .8fr; gap:.7rem; margin:.8rem 0 1rem; }
.v27-panel { border:1px solid rgba(96,170,255,.14); border-radius:16px; padding:.85rem .95rem; background:rgba(12,23,40,.78); }
.v27-kicker { color:#7ddcff; font-size:.68rem; font-weight:900; text-transform:uppercase; letter-spacing:.08em; }
.v27-big { color:#f8fafc; font-size:1.35rem; font-weight:900; margin-top:.15rem; }
.v27-small { color:#8fa6c5; font-size:.76rem; margin-top:.18rem; }
.v27-dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:.4rem; background:#5ee6a1; box-shadow:0 0 12px rgba(94,230,161,.45); }
.v27-dot.warn { background:#ffd166; box-shadow:0 0 12px rgba(255,209,102,.35); }
.v27-dot.bad { background:#ff6b7a; box-shadow:0 0 12px rgba(255,107,122,.35); }
.v27-rank { padding:.65rem .75rem; border-radius:12px; background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.06); margin:.4rem 0; }
.v27-rank-row { display:flex; align-items:center; justify-content:space-between; gap:.6rem; }
.v27-score { font-weight:900; color:#f8fafc; }
.v27-bar { height:7px; border-radius:99px; background:#17253a; overflow:hidden; margin-top:.45rem; }
.v27-fill { height:100%; border-radius:99px; background:#46cfff; }
@media (max-width:900px) { .v27-market { grid-template-columns:1fr 1fr; } }
@media (max-width:600px) { .v27-market { grid-template-columns:1fr; } }
.signal-pill { display:inline-block; padding:.3rem .72rem; border-radius:999px; font-weight:800; font-size:.8rem; background:#152744; color:#bcd3ff; border:1px solid #294a80; }
.reason { padding:.45rem .65rem; margin:.25rem 0; border-radius:9px; background:#0d1728; border:1px solid rgba(255,255,255,.06); color:#d9e2f0; }
.stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"] { color:#dbe4f0; }
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6 { color:#f8fafc; }
.stApp [data-testid="stMetricLabel"] { color:#9fb0c7 !important; }
.stApp [data-testid="stMetricValue"] { color:#f8fafc !important; }
.stApp [data-testid="stMetricDelta"] { color:#b9c7da !important; }
.stApp input,.stApp textarea { color:#f8fafc !important; background:#0e1828 !important; }
.stApp [data-baseweb="select"] * { color:#f8fafc !important; }
.stApp [data-baseweb="select"] > div { background:#0e1828 !important; border-color:rgba(255,255,255,.10) !important; }
.stApp [data-baseweb="slider"] { color:#dbe4f0; }
.stApp .stAlert p { color:inherit !important; }
.stApp [data-testid="stDataFrame"] { border:1px solid rgba(96,170,255,.12); border-radius:13px; overflow:hidden; }
.stButton > button,.stDownloadButton > button { border-radius:11px; font-weight:800; border:1px solid rgba(105,180,255,.20); }
.stButton > button:hover,.stDownloadButton > button:hover { border-color:rgba(105,210,255,.48); transform:translateY(-1px); }
div[data-testid="stMetric"] { background:rgba(13,24,42,.82); border:1px solid rgba(96,170,255,.11); border-radius:14px; padding:.7rem .8rem; }
[data-testid="stExpander"] { background:rgba(13,24,42,.68); border:1px solid rgba(96,170,255,.10); border-radius:14px; }
@media (max-width:700px) { .block-container { padding:.45rem .65rem 2rem; } .hero { padding:1rem; border-radius:17px; } .brand-logo { width:68px; height:68px; border-radius:14px; } .hero h1 { font-size:1.65rem; } .hero .tagline { font-size:.88rem; } .section { font-size:1rem; } }

.client-strip { display:flex; justify-content:space-between; gap:.7rem; align-items:center; flex-wrap:wrap; margin:.75rem 0 1rem; padding:.7rem .9rem; border-radius:14px; background:rgba(13,24,42,.72); border:1px solid rgba(96,170,255,.11); color:#a9bbd3; font-size:.82rem; }
.client-strip strong { color:#f8fafc; }
.trust-row { display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin:.8rem 0 1.1rem; }
.trust-item { padding:.7rem .8rem; border-radius:12px; background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07); }
.trust-item b { display:block; color:#eaf3ff; font-size:.82rem; }
.trust-item span { color:#8fa6c5; font-size:.72rem; }
.quick-nav { display:grid; grid-template-columns:repeat(5,1fr); gap:.55rem; margin:.7rem 0 1rem; }
.quick-link { display:flex; align-items:center; justify-content:center; min-height:46px; padding:.55rem .7rem; border-radius:11px; font-weight:800; text-decoration:none !important; color:#dbeafe !important; background:rgba(18,27,43,.92); border:1px solid rgba(105,180,255,.20); transition:transform .15s ease,border-color .15s ease,background .15s ease; }
.quick-link:hover { transform:translateY(-1px); border-color:rgba(105,210,255,.55); background:rgba(24,39,62,.98); }
.quick-link.primary { color:#8edcff !important; border-color:#164a72; background:#0c2038; }
.quick-link.green { color:#7ee2a8 !important; border-color:#20573a; background:#0d281d; }
.quick-nav-note { color:#8fa6c5; font-size:.75rem; margin:-.45rem 0 .7rem; }
@media (max-width:700px) { .quick-nav { grid-template-columns:repeat(2,1fr); } }
.footer { margin-top:1.8rem; padding:1rem 0 .2rem; border-top:1px solid rgba(255,255,255,.08); color:#71839b; font-size:.74rem; text-align:center; }
@media (max-width:700px) { .trust-row { grid-template-columns:1fr; } }
</style>

<div id="home-top" class="hero">
  <div class="brand-row">
    <img class="brand-logo" src="data:image/png;base64,LOGO_B64" />
    <div>
      <h1>BolsaIA <span style="font-size:.52em;color:#46cfff;">V33</span></h1>
      <div class="tagline">Inteligência de mercado para análise técnica, radar e gestão de risco.</div>
      <div class="mini"><span class="chip">⚡ Scanner inteligente</span><span class="chip">📊 Análise técnica</span><span class="chip green">🛡️ Carteira simulada</span></div>
    </div>
  </div>
</div>
"""
_hero_html = _hero_html.replace("LOGO_B64", _logo_b64)
st.markdown(_hero_html, unsafe_allow_html=True)

# V28: atalhos de navegação simples e visíveis para iniciantes.
if "pagina" not in st.session_state:
    st.session_state.pagina = "🏠 Início"
if "logado" not in st.session_state:
    st.session_state.logado = False

st.markdown("<div class='section'>🚀 Atalhos</div>", unsafe_allow_html=True)
st.markdown("""
<div class="quick-nav">
  <a class="quick-link" href="#home-top">🏠 Início</a>
  <a class="quick-link primary" href="#scanner-section">⚡ Scanner</a>
  <a class="quick-link" href="#analysis-section">📊 Análise</a>
</div>
""", unsafe_allow_html=True)
nav_cols = st.columns(2)
for col, label, value in [
    (nav_cols[0], "⚙️ Config", "⚙️ Config"),
    (nav_cols[1], "👤 Login", "👤 Login"),
]:
    with col:
        if st.button(label, use_container_width=True, key=f"nav_{value}"):
            st.session_state.pagina = value
            st.rerun()

if st.session_state.pagina == "👤 Login":
    st.markdown("<div class='section'>👤 Área do usuário</div>", unsafe_allow_html=True)
    st.info("🔐 Login demonstrativo da V28. O acesso é local à sessão nesta versão; ainda não há autenticação externa nem banco de usuários.")
    if not st.session_state.logado:
        with st.form("login_v28"):
            email = st.text_input("E-mail", placeholder="voce@exemplo.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            entrar = st.form_submit_button("🚀 Entrar", use_container_width=True)
        if entrar:
            if email.strip() and senha:
                st.session_state.logado = True
                st.session_state.usuario = email.strip()
                st.success(f"🟢 Sessão demonstrativa iniciada para {email.strip()}.")
            else:
                st.error("Preencha e-mail e senha para continuar.")
    else:
        st.success(f"🟢 Sessão ativa: {st.session_state.get('usuario', 'usuário')}")
        if st.button("Sair", key="logout_v28"):
            st.session_state.logado = False
            st.session_state.pop("usuario", None)
            st.rerun()
    st.stop()

if st.session_state.pagina == "⚙️ Config":
    st.markdown("<div class='section'>⚙️ Configurações rápidas</div>", unsafe_allow_html=True)
    st.write("**Feed principal:**", "BTG realtime" if btg_disponivel(st.secrets if hasattr(st, "secrets") else None) else "Yahoo Finance fallback")
    st.write("**Ciclo do scanner:** 5 segundos")
    st.write("**Universo:** ações B3 + FIIs / imobiliário")
    st.info("💡 Para cotações de ações B3 mais próximas do tempo real, configure BTG_API_KEY nos Secrets do Streamlit Cloud. O Yahoo Finance permanece como fallback e pode ter atraso.")
    st.stop()

st.markdown("""
<div class="client-strip"><span><strong>BolsaIA</strong> · painel inteligente para leitura de mercado</span><span>🔒 Ambiente demonstrativo · sem envio de ordens reais</span></div>
<div class="trust-row">
  <div class="trust-item"><b>⚡ Scanner</b><span>Encontra ativos que merecem atenção.</span></div>
  <div class="trust-item"><b>📊 Análise</b><span>Organiza indicadores técnicos em uma visão simples.</span></div>
  <div class="trust-item"><b>🛡️ Risco</b><span>Simula stop, alvo e exposição por operação.</span></div>
</div>
""", unsafe_allow_html=True)
st.caption("Ferramenta educacional. Indicadores, scores e cenários são hipotéticos e não constituem recomendação de investimento.")
st.caption("🧭 V33 · Painel de demonstração · Preços dependem da fonte configurada · Nenhuma ordem real é enviada")

# V15: status operacional, qualidade do dado e horário da última atualização.
def _status_mercado():
    agora = pd.Timestamp.now(tz="America/Sao_Paulo")
    abre = agora.replace(hour=10, minute=0, second=0, microsecond=0)
    fecha = agora.replace(hour=17, minute=55, second=0, microsecond=0)
    if agora.weekday() < 5 and abre <= agora <= fecha:
        return "🟢 Mercado B3 aberto", agora
    return "⚪ Mercado B3 fechado", agora

status_mercado, agora_status = _status_mercado()
st.caption(f"{status_mercado} · Horário de Brasília: {agora_status.strftime('%d/%m/%Y %H:%M:%S')}")

# V30: Home inteligente para leitura rápida por iniciantes.
def _texto_tendencia(media_score):
    if media_score >= 65:
        return "🟢 Mercado com viés técnico positivo", "Há mais sinais favoráveis no universo monitorado neste momento."
    if media_score >= 50:
        return "🟡 Mercado misto / seletivo", "Existem oportunidades pontuais, mas os sinais estão divididos."
    return "🔴 Mercado mais defensivo", "Os sinais técnicos estão menos favoráveis; vale acompanhar o risco com atenção."

if st.session_state.pagina == "🏠 Início":
    st.markdown('<div class="section">🧠 Seu painel em linguagem simples</div>', unsafe_allow_html=True)
    st.info("👋 **Bem-vindo à BolsaIA.** Você não precisa entender todos os indicadores para começar. O painel abaixo resume o que os dados técnicos estão mostrando e deixa os detalhes disponíveis quando você quiser aprofundar.")
    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown('<div class="exec-card"><div class="exec-label">O que procurar</div><div class="exec-value">🏆 Score</div><div class="muted">Quanto maior, mais sinais técnicos favoráveis.</div></div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="exec-card"><div class="exec-label">Como entender</div><div class="exec-value">🟢🟡🔴</div><div class="muted">Verde = favorável · amarelo = atenção · vermelho = defensivo.</div></div>', unsafe_allow_html=True)
    with h3:
        st.markdown('<div class="exec-card"><div class="exec-label">Dados</div><div class="exec-value">📡 Atualizados</div><div class="muted">A fonte e a qualidade do preço aparecem no scanner.</div></div>', unsafe_allow_html=True)
    st.markdown("### 🚦 Como usar a BolsaIA")
    st.write("**1.** Abra o **Scanner** para encontrar ativos que merecem atenção.")
    st.write("**2.** Escolha um ativo e abra a **Análise** para entender o motivo do sinal.")
    st.write("**3.** Consulte **Risco** e o plano técnico antes de interpretar qualquer cenário.")
    st.caption("💡 Os sinais são educacionais e baseados em indicadores técnicos. Eles não garantem retorno e não substituem análise profissional.")


if st.session_state.pagina == "⚡ Scanner":
    st.markdown("<div class='section'>⚡ Scanner de oportunidades</div>", unsafe_allow_html=True)
    st.caption("Escolha os ativos abaixo. O score é técnico e educacional; ele não é uma promessa de retorno.")
elif st.session_state.pagina == "📊 Análise":
    st.markdown("<div class='section'>📊 Análise técnica</div>", unsafe_allow_html=True)
    st.caption("Escolha qualquer ação ou FII cadastrado para abrir uma análise completa. O carregamento é feito sob demanda para evitar baixar o universo inteiro de uma vez.")

try:
    secrets = st.secrets
except Exception:
    secrets = None

usar_btg = btg_disponivel(secrets)
if usar_btg:
    st.success("🟢 Feed BTG configurado: cotações/candles B3 em modo realtime.")
else:
    st.warning("🟡 Feed realtime ainda não configurado. O app está usando Yahoo Finance como fallback.")
    st.info("Para ativar o realtime, configure BTG_API_KEY em Manage app → Settings → Secrets no Streamlit Cloud.")

ativos = list(ATIVOS_B3.keys())
SETOR_ATIVO = {
    "PETR3":"Petróleo", "PETR4":"Petróleo", "PRIO3":"Petróleo",
    "VALE3":"Mineração", "CSNA3":"Mineração", "CMIN3":"Mineração", "GGBR4":"Siderurgia", "GOAU4":"Siderurgia",
    "ITUB3":"Bancos", "ITUB4":"Bancos", "ITSA4":"Bancos/Participações", "BBAS3":"Bancos", "BBDC3":"Bancos", "BBDC4":"Bancos",
    "BBSE3":"Seguros", "B3SA3":"Serviços financeiros",
    "CMIG3":"Energia", "CMIG4":"Energia", "ELET3":"Energia", "ELET6":"Energia", "CPLE6":"Energia", "CPFE3":"Energia", "TAEE11":"Energia", "EGIE3":"Energia",
    "SBSP3":"Saneamento", "WEGE3":"Indústria", "EMBR3":"Indústria", "TOTS3":"Tecnologia",
    "RADL3":"Saúde", "HYPE3":"Saúde", "VIVT3":"Telecom", "ABEV3":"Consumo", "MGLU3":"Varejo", "LREN3":"Varejo",
    "RENT3":"Transportes", "AZUL4":"Transportes", "BRFS3":"Alimentos", "SUZB3":"Papel e celulose", "KLBN11":"Papel e celulose",
    "XPML11":"FIIs / Imobiliário", "MXRF11":"FIIs / Imobiliário", "HGLG11":"FIIs / Imobiliário", "BTLG11":"FIIs / Imobiliário",
    "KNCR11":"FIIs / Imobiliário", "XPLG11":"FIIs / Imobiliário", "TRXF11":"FIIs / Imobiliário", "XPIN11":"FIIs / Imobiliário",
    "VISC11":"FIIs / Imobiliário", "HSML11":"FIIs / Imobiliário", "MALL11":"FIIs / Imobiliário"
}
with st.expander("🧭 Filtro por setor", expanded=False):
    setores = sorted(set(SETOR_ATIVO.values()))
    setores_sel = st.multiselect("Setores", setores, default=setores)
    categorias = st.multiselect("Categoria", ["Ações", "FIIs / Imobiliário"], default=["Ações", "FIIs / Imobiliário"])
    def _categoria(t):
        return "FIIs / Imobiliário" if SETOR_ATIVO.get(t) == "FIIs / Imobiliário" else "Ações"
    ativos = [a for a in ativos if SETOR_ATIVO.get(a, "Outros") in setores_sel and _categoria(a) in categorias]

col1, col2, col3, col4 = st.columns(4)
with col1:
    selecionados = st.multiselect(
        "Ativos monitorados", ativos,
        default=["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "CMIG4", "XPML11"],
    )
with col2:
    intervalo = st.selectbox("Candles", ["1m", "5m", "15m", "30m", "1h"], index=1)
with col3:
    st.metric("Atualização", "5 s")
with col4:
    limiar = st.slider("Alerta a partir de", 50, 95, 75)

if st.button("🔄 Atualizar agora", use_container_width=False):
    st.cache_data.clear()
    st.rerun()

# V14: parâmetros de gestão de risco + monitoramento de mudanças de sinal.
with st.sidebar:
    st.markdown("### 🛡️ Gestão de risco")
    risco_reais = st.number_input("Risco máximo por operação (R$)", min_value=1.0, value=100.0, step=10.0)
    capital_risco = st.number_input("Capital disponível (R$)", min_value=100.0, value=10000.0, step=500.0)
    risco_total_max = st.number_input("Risco máximo total simulado (R$)", min_value=1.0, value=300.0, step=25.0)
    cooldown_alerta = st.number_input("Intervalo mínimo do mesmo alerta (s)", min_value=10, value=60, step=10)


@st.cache_data(ttl=4, show_spinner=False)
def _carregar_ativo_cache(ticker, intervalo, usar_btg_flag, api_key_marker):
    if usar_btg_flag:
        # A chave é usada apenas como marcador de cache; não é exibida nem retornada.
        return dados_btg_realtime(ticker, intervalo=intervalo, secrets=st.secrets)
    return dados_yahoo(ticker, intervalo=intervalo)

def carregar_ativo(ticker, intervalo):
    marker = "btg" if usar_btg else "yahoo"
    return _carregar_ativo_cache(ticker, intervalo, usar_btg, marker)


def _idade_dado_minutos(index):
    try:
        if index is None or len(index) == 0:
            return None
        ultimo = pd.Timestamp(index[-1])
        if ultimo.tzinfo is None:
            ultimo = ultimo.tz_localize("America/Sao_Paulo")
        else:
            ultimo = ultimo.tz_convert("America/Sao_Paulo")
        agora = pd.Timestamp.now(tz="America/Sao_Paulo")
        return max(0.0, (agora - ultimo).total_seconds() / 60.0)
    except Exception:
        return None

def _status_dado(idade_min):
    if idade_min is None:
        return "N/D"
    if idade_min <= 2:
        return "🟢 fresco"
    if idade_min <= 10:
        return "🟡 recente"
    return "🔴 atrasado"

def analisar_ativo(ticker):
    df = calcular_indicadores(carregar_ativo(ticker, intervalo))
    valid = df.dropna(subset=["MM20", "MM50", "RSI", "VolumeMedia20", "MACD", "MACD_Sinal", "ATR14"])
    if valid.empty:
        raise ValueError("Candles insuficientes para os indicadores.")
    ultima = valid.iloc[-1]
    grafico_df = df.dropna(subset=["Open", "High", "Low", "Close"]).tail(120)
    _, candle_leitura, candle_padroes = analisar_candles(grafico_df)
    pontos, sinal, motivos = analisar(ultima, candle_leitura=candle_leitura)
    return df, ultima, pontos, sinal, motivos, candle_leitura, candle_padroes


def normalizar_cotacao_df(df):
    if df is None or df.empty:
        return {}
    # Tenta identificar o ticker e o último preço independentemente do formato retornado.
    out = {}
    lower = {str(c).lower(): c for c in df.columns}
    ticker_col = next((lower[k] for k in ["symbol", "ticker", "asset"] if k in lower), None)
    price_col = next((lower[k] for k in ["last", "price", "lastprice", "close"] if k in lower), None)
    if ticker_col and price_col:
        for _, row in df.iterrows():
            try:
                out[str(row[ticker_col]).upper()] = float(row[price_col])
            except Exception:
                pass
    elif len(df) == 1 and price_col:
        try:
            # Algumas respostas de quote omitem o ticker; o chamador faz o fallback
            # pelo ativo solicitado, sem depender de variável global.
            out["__single__"] = float(df.iloc[0][price_col])
        except Exception:
            pass
    return out


@st.cache_data(ttl=60, show_spinner=False)
def dividendos_atualizados(ticker):
    return obter_dividendos_yahoo(ticker)


def painel():
    if "historico_alertas" not in st.session_state:
        st.session_state.historico_alertas = []
    if not selecionados:
        st.info("Escolha pelo menos um ativo.")
        return

    resultados = []
    detalhes = {}
    realtime_prices = {}
    realtime_source = {}
    # V28: preço mais atual disponível por fonte. BTG é usado para ações B3 quando configurado;
    # FIIs e fallback usam Yahoo Finance. A interface informa a origem para não confundir
    # cotação de mercado com dado tick-by-tick.
    acoes_sel = [t for t in selecionados if SETOR_ATIVO.get(t) != "FIIs / Imobiliário"]
    fiis_sel = [t for t in selecionados if SETOR_ATIVO.get(t) == "FIIs / Imobiliário"]
    if usar_btg and acoes_sel:
        try:
            realtime_prices.update(normalizar_cotacao_df(cotacoes_btg(acoes_sel, secrets=secrets)))
            if "__single__" in realtime_prices and len(acoes_sel) == 1:
                realtime_prices[acoes_sel[0]] = realtime_prices.pop("__single__")
            for t in acoes_sel:
                if t in realtime_prices:
                    realtime_source[t] = "BTG · realtime"
        except Exception as e:
            st.warning(f"Cotações BTG indisponíveis nesta atualização: {e}")
    yahoo_sel = [t for t in selecionados if t not in realtime_prices]
    if yahoo_sel:
        try:
            yp = cotacoes_yahoo_realtime(yahoo_sel)
            realtime_prices.update(yp)
            for t in yp:
                realtime_source[t] = "Yahoo · último preço disponível"
        except Exception:
            pass

    for ticker in selecionados:
        try:
            df, ultima, pontos, sinal, motivos, candle_leitura, candle_padroes = analisar_ativo(ticker)
            preco = realtime_prices.get(ticker, float(ultima["Close"]))
            fonte_preco = realtime_source.get(ticker, "Candle · fallback")
            plano_scan = calcular_plano(ultima, preco)
            risco_pct = (plano_scan["risco_por_acao"] / preco * 100) if preco else None
            qtd_risco = int(risco_reais / plano_scan["risco_por_acao"]) if plano_scan["risco_por_acao"] > 0 else 0
            qtd_capital = int(capital_risco / preco) if preco else 0
            qtd_sugerida = max(0, min(qtd_risco, qtd_capital))
            try:
                div_scan = dividendos_atualizados(ticker)
                dy_scan = ((div_scan.get("dividendos_12m") / preco) * 100) if preco and div_scan.get("dividendos_12m") is not None else None
            except Exception:
                dy_scan = None
            resultados.append({
                "Ativo": ticker,
                "Preço": preco,
                "Categoria": "FII" if SETOR_ATIVO.get(ticker) == "FIIs / Imobiliário" else "Ação",
                "Fonte preço": fonte_preco,
                "RSI": float(ultima["RSI"]),
                "MM20": float(ultima["MM20"]),
                "MM50": float(ultima["MM50"]),
                "MM200": float(ultima["MM200"]) if pd.notna(ultima.get("MM200")) else None,
                "ADX": float(ultima["ADX14"]) if pd.notna(ultima.get("ADX14")) else None,
                "Volume": float(ultima["Volume"]),
                "Score": pontos,
                "Sinal": sinal,
                "Δ Score": None,

                "Candle": candle_leitura,
                "R/R": plano_scan["risco_retorno"],
                "Yield 12m": dy_scan,
                "Variação": ((preco / float(df["Close"].iloc[-2]) - 1) * 100) if len(df) > 1 and float(df["Close"].iloc[-2]) else None,
                "ATR %": ((float(ultima["ATR14"]) / preco) * 100) if preco and pd.notna(ultima["ATR14"]) else None,
                "Stop": plano_scan["stop"],
                "Alvo": plano_scan["alvo"],
                "Risco/ação": plano_scan["risco_por_acao"],
                "Dist. stop %": risco_pct,
                "Qtd. risco": qtd_sugerida,
                "Idade dado (min)": _idade_dado_minutos(df.index),
                "Status dado": _status_dado(_idade_dado_minutos(df.index)),
            })
            detalhes[ticker] = (df, ultima, pontos, sinal, motivos, preco, candle_leitura, candle_padroes)
        except Exception as e:
            resultados.append({
                "Ativo": ticker, "Preço": None, "RSI": None, "MM20": None,
                "MM50": None, "MM200": None, "ADX": None, "Volume": None, "Score": None, "Sinal": f"ERRO: {e}", "Δ Score": None, "Candle": "ERRO", "R/R": None, "Yield 12m": None, "Variação": None, "ATR %": None, "Stop": None, "Alvo": None, "Risco/ação": None, "Dist. stop %": None, "Qtd. risco": None, "Idade dado (min)": None, "Status dado": "N/D",
            })

    tabela = pd.DataFrame(resultados)

    # V31: ranking inteligente + semáforo + explicação simples do score.
    def _semaforo_score(score):
        if pd.isna(score): return ("⚪", "Sem dados")
        score = float(score)
        if score >= 75: return ("🟢", "Forte")
        if score >= 50: return ("🟡", "Atenção")
        return ("🔴", "Defensivo")

    def _explicar_sinal(row):
        score = row.get("Score")
        partes = []
        if pd.notna(score):
            if float(score) >= 75: partes.append("vários sinais técnicos estão favoráveis")
            elif float(score) >= 50: partes.append("os sinais técnicos estão mistos")
            else: partes.append("os sinais técnicos estão mais defensivos")
        rsi = row.get("RSI")
        if pd.notna(rsi):
            if float(rsi) < 30: partes.append("RSI em região de sobrevenda")
            elif float(rsi) > 70: partes.append("RSI em região de sobrecompra")
            else: partes.append("RSI em faixa intermediária")
        mm20, mm50 = row.get("MM20"), row.get("MM50")
        if pd.notna(mm20) and pd.notna(mm50):
            partes.append("MM20 acima da MM50" if float(mm20) > float(mm50) else "MM20 abaixo da MM50")
        return " · ".join(partes) if partes else "Dados insuficientes para explicar o cenário."

    if not tabela.empty:
        tabela[["Semáforo", "Leitura"]] = tabela.apply(
            lambda r: pd.Series(_semaforo_score(r.get("Score"))), axis=1
        )
        tabela["Por que? "] = tabela.apply(_explicar_sinal, axis=1)
        tabela.rename(columns={"Por que? ": "Por que?"}, inplace=True)
        tabela["Posição"] = None
        valid_rank = tabela.dropna(subset=["Score"]).sort_values(["Score", "R/R"], ascending=[False, False])
        for pos, idx in enumerate(valid_rank.index, 1):
            tabela.loc[idx, "Posição"] = pos

    # V17: variação do Score entre ciclos para detectar aceleração ou perda de força.
    scores_anteriores = st.session_state.get("ultimos_scores", {})
    if not tabela.empty:
        tabela["Δ Score"] = tabela.apply(
            lambda r: (float(r["Score"]) - scores_anteriores.get(str(r["Ativo"])))
            if pd.notna(r.get("Score")) and str(r["Ativo"]) in scores_anteriores else None, axis=1
        )
        st.session_state.ultimos_scores = {
            str(r["Ativo"]): float(r["Score"]) for _, r in tabela.iterrows() if pd.notna(r.get("Score"))
        }

    # V14: histórico de mudanças de sinal para não depender apenas do alerta atual.
    atual_sinais = {str(r["Ativo"]): r["Sinal"] for _, r in tabela.iterrows() if pd.notna(r.get("Sinal"))}
    anteriores = st.session_state.get("ultimos_sinais", {})
    mudancas = []
    for ativo_sinal, sinal_atual in atual_sinais.items():
        if ativo_sinal in anteriores and anteriores[ativo_sinal] != sinal_atual:
            mudancas.append(f"{ativo_sinal}: {anteriores[ativo_sinal]} → {sinal_atual}")
    st.session_state.ultimos_sinais = atual_sinais
    st.session_state.ultima_atualizacao_painel = pd.Timestamp.now(tz="America/Sao_Paulo")
    if mudancas:
        st.warning("🔔 Mudança de sinal: " + " · ".join(mudancas))

    # V18: visão executiva para apresentação a clientes.
    valid_scores = tabela.dropna(subset=["Score"]).copy()
    total_monitorados = len(tabela)
    melhor_score = int(valid_scores["Score"].max()) if not valid_scores.empty else None
    melhor_ativo = str(valid_scores.loc[valid_scores["Score"].idxmax(), "Ativo"]) if not valid_scores.empty else "N/D"
    compras = int(valid_scores["Sinal"].astype(str).str.startswith("COMPRA").sum()) if not valid_scores.empty else 0
    dados_frescos = int((tabela["Status dado"] == "🟢 fresco").sum())
    st.markdown('<div class="section">📊 Visão executiva</div>', unsafe_allow_html=True)
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.markdown(f'<div class="exec-card"><div class="exec-label">Ativos monitorados</div><div class="exec-value">{total_monitorados}</div><div class="muted">universo atual</div></div>', unsafe_allow_html=True)
    with e2:
        st.markdown(f'<div class="exec-card"><div class="exec-label">Maior Score</div><div class="exec-value">{melhor_score if melhor_score is not None else "N/D"}/100</div><div class="muted">{melhor_ativo}</div></div>', unsafe_allow_html=True)
    with e3:
        st.markdown(f'<div class="exec-card"><div class="exec-label">Sinais de compra</div><div class="exec-value">{compras}</div><div class="muted">no monitoramento atual</div></div>', unsafe_allow_html=True)
    with e4:
        st.markdown(f'<div class="exec-card"><div class="exec-label">Dados frescos</div><div class="exec-value">{dados_frescos}/{total_monitorados}</div><div class="muted">idade ≤ 2 min</div></div>', unsafe_allow_html=True)
    st.caption("Visão executiva resumida para leitura rápida. Os indicadores são técnicos e educacionais; não representam probabilidade de retorno.")
    # V28: camada comercial de leitura rápida, sem alterar os cálculos do scanner.
    if not valid_scores.empty:
        top_row = valid_scores.sort_values(["Score", "R/R"], ascending=[False, False]).iloc[0]
        top_ativo = str(top_row["Ativo"])
        top_score = int(top_row["Score"])
        top_sinal = str(top_row["Sinal"])
        top_preco = float(top_row["Preço"]) if pd.notna(top_row["Preço"]) else None
        top_var = float(top_row["Variação"]) if pd.notna(top_row["Variação"]) else None
        risco_pct_top = float(top_row["Dist. stop %"]) if pd.notna(top_row["Dist. stop %"]) else None
        status_top = str(top_row["Status dado"])
        html = f"""
<div class="v22-hero">
  <div class="v22-kicker">🎯 Destaque da sessão · V28</div>
  <div class="v22-title">{top_ativo} · Score {top_score}/100 · {top_sinal}</div>
  <div class="v22-sub">Leitura executiva baseada nos mesmos indicadores técnicos do scanner. Use os detalhes abaixo para entender o cenário.</div>
  <div class="v22-grid">
    <div class="v22-tile"><strong>{("R$ %.2f" % top_preco) if top_preco is not None else "N/D"}</strong><span>Preço observado</span></div>
    <div class="v22-tile"><strong>{(("%.2f%%" % top_var) if top_var is not None else "N/D")}</strong><span>Variação</span></div>
    <div class="v22-tile"><strong>{(("%.2f%%" % risco_pct_top) if risco_pct_top is not None else "N/D")}</strong><span>Distância técnica ao stop</span></div>
  </div>
  <div class="v22-sub" style="margin-top:.65rem;">Fonte/qualidade do dado: {status_top} · O Score é técnico e educacional, não uma probabilidade de retorno.</div>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)

    # V27: resumo comercial do mercado e ranking compacto, sem alterar os cálculos.
    if not valid_scores.empty:
        media_score = float(valid_scores["Score"].mean())
        fortes = int((valid_scores["Score"] >= 75).sum())
        neutros = int(((valid_scores["Score"] >= 40) & (valid_scores["Score"] < 60)).sum())
        quedas = int((valid_scores["Score"] < 40).sum())
        if media_score >= 65:
            clima, dot_cls = "Viés técnico positivo", ""
        elif media_score >= 50:
            clima, dot_cls = "Mercado misto / seletivo", "warn"
        else:
            clima, dot_cls = "Viés técnico defensivo", "bad"
        st.markdown(f"""
<div class="v27-market">
  <div class="v27-panel"><div class="v27-kicker">🧭 Leitura do universo</div><div class="v27-big"><span class="v27-dot {dot_cls}"></span>{clima}</div><div class="v27-small">Score médio dos ativos monitorados: {media_score:.0f}/100</div></div>
  <div class="v27-panel"><div class="v27-kicker">🔥 Fortes</div><div class="v27-big">{fortes}</div><div class="v27-small">Score ≥ 75</div></div>
  <div class="v27-panel"><div class="v27-kicker">⏳ Seletivos</div><div class="v27-big">{neutros}</div><div class="v27-small">Score entre 40 e 59</div></div>
  <div class="v27-panel"><div class="v27-kicker">⚠️ Defensivos</div><div class="v27-big">{quedas}</div><div class="v27-small">Score &lt; 40</div></div>
</div>
""", unsafe_allow_html=True)
        ranking25 = valid_scores.sort_values(["Score", "R/R"], ascending=[False, False]).head(5)
        with st.expander("🏆 Top 5 inteligente", expanded=True):
            for pos, (_, rr) in enumerate(ranking25.iterrows(), 1):
                score25 = int(rr["Score"])
                sinal25 = str(rr["Sinal"])
                sem25 = str(rr.get("Semáforo", "⚪"))
                leitura25 = str(rr.get("Leitura", "Sem dados"))
                motivo25 = str(rr.get("Por que?", ""))
                st.markdown(f"""
<div class="v27-rank">
  <div class="v27-rank-row"><strong>#{pos} · {rr["Ativo"]}</strong><span class="v27-score">{sem25} {score25}/100 · {sinal25}</span></div>
  <div class="v27-bar"><div class="v27-fill" style="width:{score25}%"></div></div>
  <div class="muted" style="margin-top:.35rem;">{leitura25} · {motivo25}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div id="scanner-section"></div><div class="section">🔎 Scanner de oportunidades</div>', unsafe_allow_html=True)
    stamp = st.session_state.get("ultima_atualizacao_painel")
    if stamp is not None:
        st.caption(f"🕒 Última atualização dos dados do scanner: {stamp.strftime('%d/%m/%Y %H:%M:%S')} (Brasília) · ciclo automático de 5 s")
    alertas = tabela[tabela["Score"].fillna(-1) >= limiar].sort_values("Score", ascending=False)
    if not alertas.empty:
        st.success("🚨 Oportunidade detectada: " + ", ".join(
            f"{r.Ativo} ({int(r.Score)}/100)" for _, r in alertas.iterrows()
        ))
    else:
        st.info(f"Nenhum ativo atingiu o nível de alerta de {limiar}/100.")

    st.dataframe(
        tabela, use_container_width=True, hide_index=True,
        column_config={
            "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
            "Categoria": st.column_config.TextColumn(),
            "Fonte preço": st.column_config.TextColumn(),
            "RSI": st.column_config.NumberColumn(format="%.1f"),
            "MM20": st.column_config.NumberColumn(format="R$ %.2f"),
            "MM50": st.column_config.NumberColumn(format="R$ %.2f"),
            "MM200": st.column_config.NumberColumn(format="R$ %.2f"),
            "ADX": st.column_config.NumberColumn(format="%.1f"),
            "Volume": st.column_config.NumberColumn(format="%.0f"),
            "Score": st.column_config.NumberColumn(format="%d/100"),
            "Semáforo": st.column_config.TextColumn(),
            "Leitura": st.column_config.TextColumn(),
            "Por que?": st.column_config.TextColumn(),
            "Posição": st.column_config.NumberColumn(format="%d"),
            "Δ Score": st.column_config.NumberColumn(format="%+.0f"),
            "Candle": st.column_config.TextColumn(),
            "R/R": st.column_config.NumberColumn(format="1:%.2f"),
            "Yield 12m": st.column_config.NumberColumn(format="%.2f%%"),
            "Variação": st.column_config.NumberColumn(format="%.2f%%"),
            "ATR %": st.column_config.NumberColumn(format="%.2f%%"),
            "Stop": st.column_config.NumberColumn(format="R$ %.2f"),
            "Alvo": st.column_config.NumberColumn(format="R$ %.2f"),
            "Risco/ação": st.column_config.NumberColumn(format="R$ %.2f"),
            "Dist. stop %": st.column_config.NumberColumn(format="%.2f%%"),
            "Qtd. risco": st.column_config.NumberColumn(format="%d"),
            "Idade dado (min)": st.column_config.NumberColumn(format="%.1f"),
            "Status dado": st.column_config.TextColumn(),
        },
    )

    csv_scanner = tabela.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar scanner CSV", csv_scanner, file_name="bolsaia_scanner_v33.csv", mime="text/csv", key="export_scanner_v27")

    # V13: resumo de risco do scanner.
    st.markdown('<div class="section">🛡️ Gestão de risco por ativo</div>', unsafe_allow_html=True)
    risco_view = tabela[["Ativo", "Preço", "Stop", "Alvo", "Risco/ação", "Dist. stop %", "Qtd. risco"]].dropna(subset=["Preço", "Stop", "Alvo"]).copy()
    if not risco_view.empty:
        st.dataframe(risco_view, use_container_width=True, hide_index=True, column_config={
            "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
            "Stop": st.column_config.NumberColumn(format="R$ %.2f"),
            "Alvo": st.column_config.NumberColumn(format="R$ %.2f"),
            "Risco/ação": st.column_config.NumberColumn(format="R$ %.2f"),
            "Dist. stop %": st.column_config.NumberColumn(format="%.2f%%"),
            "Qtd. risco": st.column_config.NumberColumn(format="%d"),
        })
        st.caption(f"Cálculo educacional: a quantidade é limitada por R$ {risco_reais:,.2f} de risco por operação e por {capital_risco:,.2f} de capital disponível. Não é recomendação de tamanho de posição.".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.info("Sem dados suficientes para calcular o risco.")

    # V17: risco agregado das quantidades simuladas sugeridas pelo scanner.
    try:
        risco_agregado = float((tabela["Qtd. risco"].fillna(0) * tabela["Risco/ação"].fillna(0)).sum())
    except Exception:
        risco_agregado = 0.0
    if risco_agregado > risco_total_max:
        st.warning(f"⚠️ Risco agregado potencial do scanner: R$ {risco_agregado:,.2f} — acima do limite simulado de R$ {risco_total_max:,.2f}.".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.info(f"🛡️ Risco agregado potencial do scanner: R$ {risco_agregado:,.2f} / R$ {risco_total_max:,.2f}.".replace(",", "X").replace(".", ",").replace("X", "."))

    # V17: snapshot completo para auditoria da sessão.
    csv_snapshot = tabela.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar snapshot completo CSV", csv_snapshot, file_name="bolsaia_snapshot_v33.csv", mime="text/csv", key="export_snapshot_v27")

    # Radar V9: ranking visual das melhores pontuações entre os ativos monitorados.
    st.markdown('<div class="section">🏆 Radar de Oportunidades</div>', unsafe_allow_html=True)
    ranking = tabela.dropna(subset=["Score"]).sort_values(["Score", "R/R"], ascending=[False, False]).reset_index(drop=True)
    if ranking.empty:
        st.info("Ainda não há dados suficientes para montar o radar.")
    else:
        top = ranking.head(3)
        cards = st.columns(len(top))
        for i, (_, row) in enumerate(top.iterrows()):
            with cards[i]:
                medalha = ["🥇", "🥈", "🥉"][i]
                st.markdown(f"### {medalha} {row['Ativo']}")
                st.metric("Score técnico", f"{int(row['Score'])}/100")
                st.progress(min(max(int(row['Score']), 0), 100), text=f"Força do sinal: {int(row['Score'])}%")
                st.markdown(f"<span class='signal-pill'>{row['Sinal']}</span>", unsafe_allow_html=True)
                rr = row["R/R"]
                dy = row["Yield 12m"]
                st.caption(f"R/R: {('1:' + format(rr, '.2f')) if pd.notna(rr) else 'N/D'} · Yield 12m: {(format(dy, '.2f') + '%') if pd.notna(dy) else 'N/D'}")

    # Colunas extras ficam formatadas no painel completo.
    # O ranking usa o mesmo Score técnico; não representa probabilidade de lucro.

    st.caption("🏆 O radar ordena os ativos pelo Score técnico e usa o R/R como desempate. O ranking é educacional e não constitui recomendação de investimento.")

    # V10: histórico de alertas para não perder uma oportunidade enquanto o painel atualiza.
    agora = pd.Timestamp.now(tz="America/Sao_Paulo")
    for _, r in alertas.iterrows():
        chave = (r["Ativo"], int(r["Score"]))
        ultimo = next((x for x in reversed(st.session_state.historico_alertas) if x["chave"] == chave), None)
        if ultimo is None or (agora - ultimo["hora"]).total_seconds() >= 60:
            st.session_state.historico_alertas.append({"hora": agora, "ativo": r["Ativo"], "score": int(r["Score"]), "sinal": r["Sinal"], "preco": r["Preço"], "chave": chave})
    st.session_state.historico_alertas = st.session_state.historico_alertas[-50:]

    st.markdown('<div class="section">🔔 Histórico de alertas</div>', unsafe_allow_html=True)
    if st.session_state.historico_alertas:
        hist_alertas = pd.DataFrame(st.session_state.historico_alertas)[["hora", "ativo", "score", "sinal", "preco"]].sort_values("hora", ascending=False)
        hist_alertas["hora"] = hist_alertas["hora"].dt.strftime("%d/%m/%Y %H:%M:%S")
        st.dataframe(hist_alertas, use_container_width=True, hide_index=True, column_config={"preco": st.column_config.NumberColumn("Preço", format="R$ %.2f"), "score": st.column_config.NumberColumn("Score", format="%d/100")})
        csv_alertas = hist_alertas.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar alertas CSV", csv_alertas, file_name="bolsaia_alertas_v18.csv", mime="text/csv")
    else:
        st.info("Nenhum alerta registrado nesta sessão ainda. O histórico começa quando um ativo atingir o limiar configurado.")

    # V10: carteira virtual, sem envio de ordens e sem conexão com corretora.
    st.markdown('<div class="section">💼 Carteira simulada</div>', unsafe_allow_html=True)
    st.caption("A carteira é apenas uma simulação local desta sessão. Nenhuma ordem real é enviada.")
    if "carteira" not in st.session_state:
        st.session_state.carteira = {}
    with st.expander("Adicionar/atualizar posição", expanded=False):
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            ativo_pos = st.selectbox("Ativo", ativos, key="carteira_ativo")
        with pc2:
            qtd_pos = st.number_input("Quantidade", min_value=1, value=100, step=1, key="carteira_qtd")
        preco_atual_pos = float(realtime_prices.get(ativo_pos, tabela.loc[tabela["Ativo"] == ativo_pos, "Preço"].iloc[0])) if not tabela.loc[tabela["Ativo"] == ativo_pos, "Preço"].dropna().empty else 0.0
        with pc3:
            preco_medio = st.number_input("Preço médio (R$)", min_value=0.01, value=max(round(preco_atual_pos, 2), 0.01), step=0.01, key="carteira_preco")
        if st.button("💾 Salvar posição simulada", key="salvar_posicao"):
            st.session_state.carteira[ativo_pos] = {"quantidade": int(qtd_pos), "preco_medio": float(preco_medio)}
            st.success(f"Posição simulada de {ativo_pos} salva.")

    if st.session_state.carteira:
        posicoes = []
        for ticker, pos in st.session_state.carteira.items():
            linha = tabela[tabela["Ativo"] == ticker]
            if linha.empty or pd.isna(linha.iloc[0]["Preço"]):
                continue
            atual = float(linha.iloc[0]["Preço"])
            qtd = int(pos["quantidade"])
            pm = float(pos["preco_medio"])
            investido = qtd * pm
            valor = qtd * atual
            pl = valor - investido
            pl_pct = (pl / investido * 100) if investido else 0
            linha0 = linha.iloc[0]
            stop_pos = float(linha0["Stop"]) if pd.notna(linha0.get("Stop")) else None
            alvo_pos = float(linha0["Alvo"]) if pd.notna(linha0.get("Alvo")) else None
            if stop_pos is not None and atual <= stop_pos:
                status_pos = "🛑 stop atingido"
            elif alvo_pos is not None and atual >= alvo_pos:
                status_pos = "🎯 alvo atingido"
            else:
                status_pos = "🟢 em acompanhamento"
            dist_alvo = ((alvo_pos / atual) - 1) * 100 if alvo_pos and atual else None
            dist_stop = ((atual / stop_pos) - 1) * 100 if stop_pos and atual else None
            posicoes.append({"Ativo": ticker, "Qtd": qtd, "Preço médio": pm, "Preço atual": atual, "Investido": investido, "Valor atual": valor, "P/L": pl, "P/L %": pl_pct, "Stop": stop_pos, "Alvo": alvo_pos, "Status": status_pos, "Dist. alvo %": dist_alvo, "Dist. stop %": dist_stop})
        if posicoes:
            carteira_df = pd.DataFrame(posicoes)
            total_inv = carteira_df["Investido"].sum()
            total_val = carteira_df["Valor atual"].sum()
            total_pl = total_val - total_inv
            k1, k2, k3 = st.columns(3)
            k1.metric("Capital simulado", f"R$ {total_inv:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            k2.metric("Valor atual", f"R$ {total_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            k3.metric("P/L simulado", f"R$ {total_pl:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), f"{(total_pl / total_inv * 100) if total_inv else 0:.2f}%")
            st.dataframe(carteira_df, use_container_width=True, hide_index=True, column_config={
                "Preço médio": st.column_config.NumberColumn(format="R$ %.2f"), "Preço atual": st.column_config.NumberColumn(format="R$ %.2f"),
                "Investido": st.column_config.NumberColumn(format="R$ %.2f"), "Valor atual": st.column_config.NumberColumn(format="R$ %.2f"),
                "P/L": st.column_config.NumberColumn(format="R$ %.2f"), "P/L %": st.column_config.NumberColumn(format="%.2f%%"),
                "Stop": st.column_config.NumberColumn(format="R$ %.2f"), "Alvo": st.column_config.NumberColumn(format="R$ %.2f"),
                "Dist. alvo %": st.column_config.NumberColumn(format="%.2f%%"), "Dist. stop %": st.column_config.NumberColumn(format="%.2f%%"),
                "Status": st.column_config.TextColumn()})

            # V12: visão consolidada do patrimônio e evolução da carteira simulada.
            total_pl_pct = (total_pl / total_inv * 100) if total_inv else 0.0
            total_div = 0.0
            for ticker, pos in st.session_state.carteira.items():
                try:
                    div_pos = dividendos_atualizados(ticker)
                    qtd = int(pos["quantidade"])
                    total_div += float(div_pos.get("dividendos_12m") or 0) * qtd
                except Exception:
                    pass
            patrimonio_com_div = total_val + total_div
            resultado_total = patrimonio_com_div - total_inv
            k4, k5 = st.columns(2)
            k4.metric("💰 Dividendos 12m estimados", f"R$ {total_div:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            k5.metric("📊 Resultado + dividendos", f"R$ {resultado_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), f"{(resultado_total / total_inv * 100) if total_inv else 0:.2f}%")

            # Histórico simples da sessão: guarda o valor da carteira para desenhar a evolução.
            agora_hist = pd.Timestamp.now(tz="America/Sao_Paulo")
            if "historico_carteira" not in st.session_state:
                st.session_state.historico_carteira = []
            if not st.session_state.historico_carteira or (agora_hist - st.session_state.historico_carteira[-1]["hora"]).total_seconds() >= 5:
                st.session_state.historico_carteira.append({"hora": agora_hist, "valor": total_val, "investido": total_inv})
            st.session_state.historico_carteira = st.session_state.historico_carteira[-300:]
            hist_df = pd.DataFrame(st.session_state.historico_carteira).set_index("hora")
            st.markdown("### 📈 Evolução da carteira (sessão atual)")
            st.line_chart(hist_df[["valor", "investido"]])
            st.caption("A evolução é registrada somente durante esta sessão do app; ela não representa histórico de rentabilidade real.")

            csv_carteira = carteira_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar carteira CSV", csv_carteira, file_name="bolsaia_carteira_v33.csv", mime="text/csv")
    else:
        st.info("Nenhuma posição simulada cadastrada.")

    # V33: análise detalhada sob demanda de TODO o universo cadastrado.
    # O app não precisa baixar todos os ativos ao mesmo tempo: o usuário escolhe um
    # ativo/FII e os dados são carregados somente para aquele ativo.
    universo_analise = list(dict.fromkeys(ativos))
    if universo_analise:
        ativo = st.selectbox("🔎 Escolha qualquer ação ou FII para análise completa", universo_analise, key="analise_ativo_v33")
        if ativo in detalhes:
            df, ultima, pontos, sinal, motivos, preco, candle_leitura, candle_padroes = detalhes[ativo]
        else:
            try:
                df, ultima, pontos, sinal, motivos, candle_leitura, candle_padroes = analisar_ativo(ativo)
                preco = float(ultima["Close"])
                detalhes[ativo] = (df, ultima, pontos, sinal, motivos, preco, candle_leitura, candle_padroes)
            except Exception as e:
                st.error(f"Não foi possível carregar a análise de {ativo}: {e}")
                st.stop()
        plano = calcular_plano(ultima, preco)
        try:
            div = dividendos_atualizados(ativo)
        except Exception as e:
            div = {'dividendo_cota': None, 'dividendos_12m': None, 'ultimo_dividendo': None, 'ultima_data': None, 'yield_12m': None}
            st.warning(f"Dividendos temporariamente indisponíveis: {e}")

        st.markdown('<div id="analysis-section"></div><div class="section">💰 Dividendos</div>', unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        if div.get("dividendo_cota") is not None:
            d1.metric("Dividendo/cota", f"R$ {div['dividendo_cota']:.4f}")
        else:
            d1.metric("Dividendo/cota", "N/D")
        if div.get("dividendos_12m") is not None:
            d2.metric("Dividendos 12 meses", f"R$ {div['dividendos_12m']:.4f}")
        else:
            d2.metric("Dividendos 12 meses", "N/D")
        if preco and div.get("dividendos_12m") is not None:
            dy = (div["dividendos_12m"] / preco) * 100
            d3.metric("Dividend Yield", f"{dy:.2f}%")
        else:
            d3.metric("Dividend Yield", "N/D")
        if div.get("ultima_data") is not None:
            data_ult = pd.Timestamp(div["ultima_data"]).strftime("%d/%m/%Y")
            d4.metric("Último dividendo", f"R$ {div['ultimo_dividendo']:.4f}", help=f"Data registrada: {data_ult}")
        else:
            d4.metric("Último dividendo", "N/D")
        st.caption("🔄 Dividendos: fonte Yahoo Finance, atualização automática a cada 60 s. Preço/cotação continua no ciclo realtime de 5 s.")

        # Simulador simples de renda com dividendos. Usa valores históricos
        # efetivamente registrados; não é uma previsão de pagamento futuro.
        st.markdown("### 🧮 Quanto você receberia em dividendos?")
        qtd_custom = st.number_input("Quantidade de ações", min_value=1, value=100, step=1, key=f"qtd_div_{ativo}")
        ultimo_por_acao = div.get("ultimo_dividendo")
        total_12m_por_acao = div.get("dividendos_12m")
        if ultimo_por_acao is not None:
            r10 = ultimo_por_acao * 10
            r100 = ultimo_por_acao * 100
            r1000 = ultimo_por_acao * 1000
            rc = ultimo_por_acao * qtd_custom
            a10 = total_12m_por_acao * 10 if total_12m_por_acao is not None else None
            a100 = total_12m_por_acao * 100 if total_12m_por_acao is not None else None
            a1000 = total_12m_por_acao * 1000 if total_12m_por_acao is not None else None
            ac = total_12m_por_acao * qtd_custom if total_12m_por_acao is not None else None
            s1, s2, s3 = st.columns(3)
            s1.metric("10 ações", f"R$ {r10:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                      help="Valor aproximado usando o último dividendo registrado por ação.")
            s2.metric("100 ações", f"R$ {r100:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                      help="Valor aproximado usando o último dividendo registrado por ação.")
            s3.metric("1.000 ações", f"R$ {r1000:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                      help="Valor aproximado usando o último dividendo registrado por ação.")
            st.success(f"💰 Com **{qtd_custom:,} ações**, o último dividendo registrado corresponderia a aproximadamente **R$ {rc:,.2f}**.".replace(",", "X").replace(".", ",").replace("X", "."))
            if ac is not None:
                st.info(f"📊 Se o ritmo dos últimos 12 meses se repetisse, **{qtd_custom:,} ações** representariam cerca de **R$ {ac:,.2f}** em dividendos no período.".replace(",", "X").replace(".", ",").replace("X", "."))

        if div.get("ultima_data") is not None:
            data_ult = pd.Timestamp(div["ultima_data"]).strftime("%d/%m/%Y")
            st.caption(f"📅 Último registro de dividendo: {data_ult}. O histórico do Yahoo não garante a existência ou o valor de um próximo pagamento.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço realtime", f"R$ {preco:.2f}")
        c2.metric("RSI", f"{ultima.RSI:.1f}")
        c3.metric("Score IA", f"{pontos}/100")
        c4.metric("Sinal", sinal)

        st.markdown("### 🧠 Confluência da IA")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Tendência", "ALTA" if ultima["MM20"] > ultima["MM50"] else "BAIXA")
        m2.metric("MACD", "POSITIVO" if ultima["MACD"] > ultima["MACD_Sinal"] else "NEGATIVO")
        m3.metric("Candle", candle_leitura)
        adx_txt = f"{float(ultima['ADX14']):.1f}" if pd.notna(ultima.get("ADX14")) else "N/D"
        m4.metric("ADX 14", adx_txt, help="Acima de ~25 sugere tendência mais forte; abaixo disso pode indicar lateralização.")
        distancia_suporte = ((float(ultima["Close"]) / float(ultima["Suporte20"])) - 1) * 100 if float(ultima["Suporte20"]) else 0
        m5.metric("Suporte 20", f"R$ {float(ultima['Suporte20']):.2f}", help=f"Preço está {distancia_suporte:.1f}% acima do suporte recente.")
        st.caption("O Score IA combina tendência, RSI, volume, MACD e leitura de candles. É um modelo de análise técnica educacional; não garante movimentos futuros.")
        st.markdown("### 💡 Por que este sinal?")
        for motivo in motivos[:6]:
            st.markdown(f"<div class='reason'>• {motivo}</div>", unsafe_allow_html=True)

        st.markdown("### 🎯 Plano técnico")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🎯 Alvo técnico", f"R$ {plano['alvo']:.2f}")
        p2.metric("🛑 Stop técnico", f"R$ {plano['stop']:.2f}")
        rr_txt = f"1:{plano['risco_retorno']:.2f}" if plano["risco_retorno"] is not None else "N/D"
        p3.metric("⚖️ Risco/Retorno", rr_txt)
        p4.metric("🧠 Confiança técnica", f"{pontos}/100")
        st.caption("Alvo e stop são níveis técnicos calculados a partir de suporte, resistência e ATR recente. A confiança é o Score técnico do modelo, não uma probabilidade estatística de alta ou queda.")

        st.markdown("### 🛡️ Calculadora de risco")
        rr1, rr2, rr3, rr4 = st.columns(4)
        perda_unit = plano["risco_por_acao"]
        qtd_risco_det = int(risco_reais / perda_unit) if perda_unit > 0 else 0
        qtd_cap_det = int(capital_risco / preco) if preco else 0
        qtd_final_det = max(0, min(qtd_risco_det, qtd_cap_det))
        rr1.metric("Risco/ação", f"R$ {perda_unit:.2f}")
        rr2.metric("Distância ao stop", f"{(perda_unit / preco * 100):.2f}%" if preco else "N/D")
        rr3.metric("Qtd. pelo risco", f"{qtd_risco_det}")
        rr4.metric("Qtd. final", f"{qtd_final_det}")
        perda_max = qtd_final_det * perda_unit
        st.caption(f"Se o stop técnico fosse atingido, a perda simulada nessa quantidade seria de aproximadamente R$ {perda_max:,.2f}. O cálculo é hipotético e não considera custos, impostos, slippage ou gaps.".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("### 💰 Calculadora de objetivo de lucro")
        st.caption("Descubra, em uma simulação, quantas ações/cotas seriam necessárias para atingir um valor de lucro informado. O cálculo usa o preço observado e um preço-alvo técnico; não representa promessa de retorno.")
        calc1, calc2, calc3 = st.columns(3)
        with calc1:
            objetivo_lucro = st.number_input("🎯 Quero buscar um lucro de (R$)", min_value=1.0, value=500.0, step=50.0, key=f"objetivo_lucro_v33_{ativo}")
        with calc2:
            preco_alvo_sim = st.number_input("Preço-alvo simulado (R$)", min_value=0.01, value=max(float(plano["alvo"]), float(preco)+0.01), step=0.10, key=f"alvo_calc_v33_{ativo}")
        with calc3:
            unidades_orcamento = int(capital_risco / preco) if preco else 0
            st.metric("Unidades pelo capital definido", f"{unidades_orcamento}")

        ganho_unit = max(float(preco_alvo_sim) - float(preco), 0.0)
        if ganho_unit <= 0:
            st.warning("⚠️ O preço-alvo precisa ser maior que o preço observado para calcular um lucro positivo por unidade.")
        else:
            qtd_objetivo = int(math.ceil(float(objetivo_lucro) / ganho_unit))
            capital_objetivo = qtd_objetivo * float(preco)
            lucro_simulado = qtd_objetivo * ganho_unit
            cc1, cc2, cc3, cc4 = st.columns(4)
            cc1.metric("Preço observado", f"R$ {float(preco):.2f}")
            cc2.metric("Ganho por unidade", f"R$ {ganho_unit:.2f}")
            cc3.metric("Quantidade necessária", f"{qtd_objetivo:,}".replace(",", "."))
            cc4.metric("Capital estimado", f"R$ {capital_objetivo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.success(f"💡 Para buscar **R$ {objetivo_lucro:,.2f}** de lucro, nesse cenário seriam necessárias aproximadamente **{qtd_objetivo:,} unidades**, compradas a R$ {float(preco):,.2f}, com lucro bruto simulado de **R$ {lucro_simulado:,.2f}** se o preço chegasse a R$ {float(preco_alvo_sim):,.2f}.".replace(",", "X").replace(".", ",").replace("X", "."))
            if qtd_objetivo > unidades_orcamento and unidades_orcamento > 0:
                st.info(f"📌 Com o capital de R$ {capital_risco:,.2f}, caberiam aproximadamente {unidades_orcamento:,} unidades nesse preço. Isso é apenas uma comparação de orçamento, não uma sugestão de investimento.".replace(",", "X").replace(".", ",").replace("X", "."))

        # V33: meta de renda por dividendos, usando somente o histórico efetivamente registrado.
        div_obj = div.get("dividendos_12m")
        if div_obj is not None and float(div_obj) > 0:
            st.markdown("### 🪙 Quantas unidades para uma meta de dividendos?")
            meta_div = st.number_input("Meta de dividendos no período de 12 meses (R$)", min_value=1.0, value=500.0, step=50.0, key=f"meta_div_v33_{ativo}")
            qtd_div_meta = int(math.ceil(meta_div / float(div_obj)))
            capital_div_meta = qtd_div_meta * float(preco)
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("Dividendos 12m por unidade", f"R$ {float(div_obj):.4f}")
            dc2.metric("Quantidade estimada", f"{qtd_div_meta:,}".replace(",", "."))
            dc3.metric("Capital ao preço observado", f"R$ {capital_div_meta:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.caption("⚠️ Essa conta repete o valor histórico de dividendos dos últimos 12 meses apenas como simulação. Pagamentos futuros, valores e datas não são garantidos.")

        st.markdown("### 📈 Gráfico profissional V33")
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            grafico_df = df.dropna(subset=["Open", "High", "Low", "Close"]).tail(160).copy()
            grafico_df["Volume"] = grafico_df["Volume"].fillna(0)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07, row_heights=[0.74, 0.26])
            fig.add_trace(go.Candlestick(
                x=grafico_df.index, open=grafico_df["Open"], high=grafico_df["High"],
                low=grafico_df["Low"], close=grafico_df["Close"], name=ativo
            ), row=1, col=1)
            if "MM20" in grafico_df:
                fig.add_trace(go.Scatter(x=grafico_df.index, y=grafico_df["MM20"], name="MM20", mode="lines"), row=1, col=1)
            if "MM50" in grafico_df:
                fig.add_trace(go.Scatter(x=grafico_df.index, y=grafico_df["MM50"], name="MM50", mode="lines"), row=1, col=1)
            if "MM200" in grafico_df:
                fig.add_trace(go.Scatter(x=grafico_df.index, y=grafico_df["MM200"], name="MM200", mode="lines"), row=1, col=1)
            fig.add_trace(go.Bar(x=grafico_df.index, y=grafico_df["Volume"], name="Volume", opacity=0.55), row=2, col=1)
            fig.update_layout(height=650, xaxis_rangeslider_visible=False, hovermode="x unified",
                              margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h"))
            fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_xaxes(title_text="Tempo", row=2, col=1)
            st.plotly_chart(fig, use_container_width=True, key=f"candles_v33_{ativo}")

            st.markdown("### 🎛️ Leitura rápida do gráfico")
            g1, g2, g3, g4 = st.columns(4)
            close_now = float(grafico_df["Close"].iloc[-1])
            close_prev = float(grafico_df["Close"].iloc[-2]) if len(grafico_df) > 1 else close_now
            g1.metric("Último preço", f"R$ {close_now:.2f}", f"{((close_now/close_prev)-1)*100:+.2f}%" if close_prev else None)
            g2.metric("MM20", f"R$ {float(grafico_df['MM20'].iloc[-1]):.2f}" if pd.notna(grafico_df['MM20'].iloc[-1]) else "N/D")
            g3.metric("MM50", f"R$ {float(grafico_df['MM50'].iloc[-1]):.2f}" if pd.notna(grafico_df['MM50'].iloc[-1]) else "N/D")
            g4.metric("Volume", f"{float(grafico_df['Volume'].iloc[-1]):,.0f}".replace(",", "."))

            st.markdown("### 🤖 Leitura das candles")
            cc1, cc2 = st.columns(2)
            cc1.metric("Última vela", candle_padroes[0] if candle_padroes else "Sem padrão")
            cc2.metric("Viés do padrão", candle_leitura)
            for p in candle_padroes:
                st.write("•", p)
            st.caption("O gráfico é uma ferramenta educacional. Médias, volume e candles ajudam a interpretar o histórico, mas não garantem movimentos futuros.")
        except ImportError:
            st.warning("Gráfico profissional requer Plotly. Adicione 'plotly' ao requirements.txt.")
        st.line_chart(df[["Close", "MM20", "MM50"]].dropna())
        st.write("**Motivos do sinal:**")
        for m in motivos:
            st.write("•", m)
        st.caption(f"Último candle recebido: {df.index[-1]}")

    if usar_btg:
        st.caption("Fonte principal: BTG Solutions Data Services / Market Data B3 em modo realtime. O acesso depende do plano/licença da sua chave.")
    else:
        st.caption("Fallback: Yahoo Finance. Ele não deve ser tratado como feed profissional em tempo real.")


st.markdown("<div class='footer'>BolsaIA V33 · Inteligência de Mercado · Demonstração educacional · Dados dependem da fonte configurada</div>", unsafe_allow_html=True)

if hasattr(st, "fragment"):
    @st.fragment(run_every="5s")
    def atualizacao():
        painel()
    atualizacao()
else:
    painel()
