import streamlit as st
import pandas as pd

from dados import (
    dados_yahoo, dados_btg_realtime, cotacoes_btg, btg_disponivel,
    ATIVOS_B3,
)
from indicadores import calcular_indicadores
from analisador import analisar, analisar_candles, calcular_plano
from dividendos import obter_dividendos_yahoo

st.set_page_config(
    page_title="BolsaIA V20 | Inteligência de Mercado",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# V20 — interface premium, contraste consistente e apresentação para demonstrações/clientes.
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(circle at 15% 0%, #16213a 0%, #0b1020 38%, #070b14 100%); }
.block-container { max-width: 1450px; padding-top: 1.1rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #0d1424; border-right: 1px solid rgba(255,255,255,.09); }
.hero { padding: 1.45rem 1.55rem; border: 1px solid rgba(255,255,255,.10); border-radius: 20px; background: linear-gradient(135deg, rgba(25,38,66,.96), rgba(12,18,32,.96)); box-shadow: 0 14px 40px rgba(0,0,0,.25); margin-bottom: 1rem; }
.hero h1 { margin: 0; font-size: 2.25rem; letter-spacing: -.045em; color:#f8fafc; }
.hero p { margin: .4rem 0 0; color: #aab7cc; }
.section { font-size: 1.08rem; font-weight: 800; margin-top: 1.2rem; padding: .45rem 0; border-bottom: 1px solid rgba(255,255,255,.10); color:#f8fafc; }
.badge { display:inline-block; padding:.3rem .7rem; border-radius:999px; font-size:.78rem; font-weight:750; background:#102a1d; color:#7ee2a8; border:1px solid #24583a; margin-top:.8rem; }
.muted { color:#94a3b8; font-size:.84rem; }
.exec-card { border: 1px solid rgba(255,255,255,.10); border-radius: 16px; padding: 1rem 1.05rem; background: rgba(17,25,43,.86); box-shadow: 0 8px 24px rgba(0,0,0,.18); min-height: 112px; }
.exec-label { color:#8fa0b8; font-size:.76rem; font-weight:750; text-transform:uppercase; letter-spacing:.05em; }
.exec-value { color:#f8fafc; font-size:1.6rem; font-weight:850; margin-top:.2rem; }
.signal-pill { display:inline-block; padding:.3rem .72rem; border-radius:999px; font-weight:800; font-size:.8rem; background:#152744; color:#bcd3ff; border:1px solid #294a80; }
.reason { padding:.45rem .65rem; margin:.25rem 0; border-radius:9px; background:#111a2b; border:1px solid rgba(255,255,255,.06); color:#d9e2f0; }
.stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"] { color:#dbe4f0; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color:#f8fafc; }
.stApp [data-testid="stMetricLabel"] { color:#9fb0c7 !important; }
.stApp [data-testid="stMetricValue"] { color:#f8fafc !important; }
.stApp [data-testid="stMetricDelta"] { color:#b9c7da !important; }
.stApp input, .stApp textarea { color:#f8fafc !important; background:#111827 !important; }
.stApp [data-baseweb="select"] * { color:#f8fafc !important; }
.stApp [data-baseweb="select"] > div { background:#111827 !important; border-color:rgba(255,255,255,.10) !important; }
.stApp [data-baseweb="slider"] { color:#dbe4f0; }
.stApp .stAlert p { color:inherit !important; }
.stApp [data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,.08); border-radius:12px; overflow:hidden; }
.stButton > button, .stDownloadButton > button { border-radius: 11px; font-weight: 750; border:1px solid rgba(255,255,255,.14); }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:rgba(255,255,255,.28); }
div[data-testid="stMetric"] { background: rgba(17,25,43,.78); border: 1px solid rgba(255,255,255,.09); border-radius: 14px; padding: .7rem .8rem; }
[data-testid="stExpander"] { background:rgba(17,25,43,.68); border:1px solid rgba(255,255,255,.09); border-radius:14px; }
@media (max-width: 700px) { .block-container { padding:.7rem .65rem 2rem; } .hero { padding:1.05rem; border-radius:15px; } .hero h1 { font-size:1.7rem; } .section { font-size:1rem; } }
</style>
<div class="hero">
    <h1>📈 BolsaIA <span style="font-size:.55em;">V20</span></h1>
    <p>Inteligência de mercado para análise técnica, radar de oportunidades e gestão de risco.</p>
    <span class="badge">● Modo demonstração · Sem envio de ordens</span>
</div>
""", unsafe_allow_html=True)
st.caption("Ferramenta educacional. Indicadores, scores e cenários são hipotéticos e não constituem recomendação de investimento.")
st.caption("🧭 V20 · Painel de demonstração · Dados dependem da fonte configurada · Nenhuma ordem real é enviada")

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
col1, col2, col3, col4 = st.columns(4)
with col1:
    selecionados = st.multiselect(
        "Ativos monitorados", ativos,
        default=["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4"],
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
    if usar_btg:
        try:
            realtime_prices = normalizar_cotacao_df(cotacoes_btg(selecionados, secrets=secrets))
            if "__single__" in realtime_prices and len(selecionados) == 1:
                realtime_prices[selecionados[0]] = realtime_prices.pop("__single__")
        except Exception as e:
            st.warning(f"Cotações realtime indisponíveis nesta atualização: {e}")

    for ticker in selecionados:
        try:
            df, ultima, pontos, sinal, motivos, candle_leitura, candle_padroes = analisar_ativo(ticker)
            preco = realtime_prices.get(ticker, float(ultima["Close"]))
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

    st.markdown('<div class="section">🔎 Scanner de oportunidades</div>', unsafe_allow_html=True)
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
            "RSI": st.column_config.NumberColumn(format="%.1f"),
            "MM20": st.column_config.NumberColumn(format="R$ %.2f"),
            "MM50": st.column_config.NumberColumn(format="R$ %.2f"),
            "MM200": st.column_config.NumberColumn(format="R$ %.2f"),
            "ADX": st.column_config.NumberColumn(format="%.1f"),
            "Volume": st.column_config.NumberColumn(format="%.0f"),
            "Score": st.column_config.NumberColumn(format="%d/100"),
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
    st.download_button("⬇️ Exportar scanner CSV", csv_scanner, file_name="bolsaia_scanner_v20.csv", mime="text/csv", key="export_scanner_v20")

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
    st.download_button("⬇️ Exportar snapshot completo CSV", csv_snapshot, file_name="bolsaia_snapshot_v19.csv", mime="text/csv", key="export_snapshot_v19")

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
            st.download_button("⬇️ Exportar carteira CSV", csv_carteira, file_name="bolsaia_carteira_v20.csv", mime="text/csv")
    else:
        st.info("Nenhuma posição simulada cadastrada.")

    disponiveis = [x for x in selecionados if x in detalhes]
    if disponiveis:
        ativo = st.selectbox("Ver análise detalhada", disponiveis)
        df, ultima, pontos, sinal, motivos, preco, candle_leitura, candle_padroes = detalhes[ativo]
        plano = calcular_plano(ultima, preco)
        try:
            div = dividendos_atualizados(ativo)
        except Exception as e:
            div = {'dividendo_cota': None, 'dividendos_12m': None, 'ultimo_dividendo': None, 'ultima_data': None, 'yield_12m': None}
            st.warning(f"Dividendos temporariamente indisponíveis: {e}")

        st.markdown('<div class="section">💰 Dividendos</div>', unsafe_allow_html=True)
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

        st.markdown("### 🕯️ Gráfico de Candles")
        try:
            import plotly.graph_objects as go
            grafico_df = df.dropna(subset=["Open", "High", "Low", "Close"]).tail(120)
            fig = go.Figure(data=[go.Candlestick(
                x=grafico_df.index,
                open=grafico_df["Open"], high=grafico_df["High"],
                low=grafico_df["Low"], close=grafico_df["Close"],
                name=ativo
            )])
            fig.add_trace(go.Scatter(x=grafico_df.index, y=grafico_df["MM20"], name="MM20", mode="lines"))
            fig.add_trace(go.Scatter(x=grafico_df.index, y=grafico_df["MM50"], name="MM50", mode="lines"))
            fig.update_layout(height=520, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10),
                              xaxis_title="Tempo", yaxis_title="Preço (R$)")
            st.plotly_chart(fig, use_container_width=True, key=f"candles_{ativo}")
            st.markdown("### 🤖 Leitura das Candles")
            cc1, cc2 = st.columns(2)
            cc1.metric("Última vela", candle_padroes[0] if candle_padroes else "Sem padrão")
            cc2.metric("Viés do padrão", candle_leitura)
            for p in candle_padroes:
                st.write("•", p)
            st.caption("A leitura de candles é baseada em padrões técnicos simples e não constitui recomendação de investimento.")
        except ImportError:
            st.warning("Gráfico de candles requer Plotly. Adicione a dependência 'plotly' ao requirements.txt.")
        st.line_chart(df[["Close", "MM20", "MM50"]].dropna())
        st.write("**Motivos do sinal:**")
        for m in motivos:
            st.write("•", m)
        st.caption(f"Último candle recebido: {df.index[-1]}")

    if usar_btg:
        st.caption("Fonte principal: BTG Solutions Data Services / Market Data B3 em modo realtime. O acesso depende do plano/licença da sua chave.")
    else:
        st.caption("Fallback: Yahoo Finance. Ele não deve ser tratado como feed profissional em tempo real.")


if hasattr(st, "fragment"):
    @st.fragment(run_every="5s")
    def atualizacao():
        painel()
    atualizacao()
else:
    painel()
