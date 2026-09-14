import streamlit as st
import pandas as pd

from dados import (
    dados_yahoo, dados_btg_realtime, cotacoes_btg, btg_disponivel,
    ATIVOS_B3,
)
from indicadores import calcular_indicadores
from analisador import analisar
from dividendos import obter_dividendos_yahoo

st.set_page_config(page_title="BolsaIA v6", page_icon="📡", layout="wide")
st.title("📡 BolsaIA v6 — análise B3 em tempo real")
st.caption("Motor educacional de análise técnica. Não é recomendação de investimento.")

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


def carregar_ativo(ticker, intervalo):
    if usar_btg:
        return dados_btg_realtime(ticker, intervalo=intervalo, secrets=secrets)
    return dados_yahoo(ticker, periodo="1d", intervalo=intervalo)


def analisar_ativo(ticker):
    df = calcular_indicadores(carregar_ativo(ticker, intervalo))
    valid = df.dropna(subset=["MM20", "MM50", "RSI", "VolumeMedia20"])
    if valid.empty:
        raise ValueError("Candles insuficientes para MM20/MM50/RSI.")
    ultima = valid.iloc[-1]
    pontos, sinal, motivos = analisar(ultima)
    return df, ultima, pontos, sinal, motivos


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
            out[selecionados[0]] = float(df.iloc[0][price_col])
        except Exception:
            pass
    return out


@st.cache_data(ttl=60, show_spinner=False)
def dividendos_atualizados(ticker):
    return obter_dividendos_yahoo(ticker)


def painel():
    if not selecionados:
        st.info("Escolha pelo menos um ativo.")
        return

    resultados = []
    detalhes = {}
    realtime_prices = {}
    if usar_btg:
        try:
            realtime_prices = normalizar_cotacao_df(cotacoes_btg(selecionados, secrets=secrets))
        except Exception as e:
            st.warning(f"Cotações realtime indisponíveis nesta atualização: {e}")

    for ticker in selecionados:
        try:
            df, ultima, pontos, sinal, motivos = analisar_ativo(ticker)
            preco = realtime_prices.get(ticker, float(ultima["Close"]))
            resultados.append({
                "Ativo": ticker,
                "Preço": preco,
                "RSI": float(ultima["RSI"]),
                "MM20": float(ultima["MM20"]),
                "MM50": float(ultima["MM50"]),
                "Volume": float(ultima["Volume"]),
                "Score": pontos,
                "Sinal": sinal,
            })
            detalhes[ticker] = (df, ultima, pontos, sinal, motivos, preco)
        except Exception as e:
            resultados.append({
                "Ativo": ticker, "Preço": None, "RSI": None, "MM20": None,
                "MM50": None, "Volume": None, "Score": None, "Sinal": f"ERRO: {e}",
            })

    tabela = pd.DataFrame(resultados)
    st.subheader("🔎 Scanner de oportunidades")
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
            "Volume": st.column_config.NumberColumn(format="%.0f"),
            "Score": st.column_config.NumberColumn(format="%d/100"),
        },
    )

    disponiveis = [x for x in selecionados if x in detalhes]
    if disponiveis:
        ativo = st.selectbox("Ver análise detalhada", disponiveis)
        df, ultima, pontos, sinal, motivos, preco = detalhes[ativo]
        try:
            div = dividendos_atualizados(ativo)
        except Exception as e:
            div = {'dividendo_cota': None, 'dividendos_12m': None, 'ultimo_dividendo': None, 'ultima_data': None, 'yield_12m': None}
            st.warning(f"Dividendos temporariamente indisponíveis: {e}")

        st.markdown("## 💰 Dividendos")
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

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço realtime", f"R$ {preco:.2f}")
        c2.metric("RSI", f"{ultima.RSI:.1f}")
        c3.metric("Score", f"{pontos}/100")
        c4.metric("Sinal", sinal)
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
