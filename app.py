import streamlit as st
import pandas as pd
from dados import dados_reais, ATIVOS_B3
from indicadores import calcular_indicadores
from analisador import analisar

st.set_page_config(page_title="BolsaIA v3", page_icon="📈", layout="wide")
st.title("📈 BolsaIA — monitor automático")
st.caption("Protótipo educacional: o motor combina indicadores técnicos. Não é recomendação de investimento.")

ativos = list(ATIVOS_B3.keys())
col1, col2, col3 = st.columns(3)
with col1:
    selecionados = st.multiselect("Ativos monitorados", ativos, default=["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4"])
with col2:
    intervalo = st.selectbox("Candles", ["1m", "5m", "15m", "30m", "1h"], index=1)
with col3:
    st.metric("Atualização", "25 s")

@st.cache_data(ttl=20, show_spinner=False)
def carregar(ticker, intervalo):
    return dados_reais(ticker, periodo="1d", intervalo=intervalo)

def analisar_ativo(ticker):
    df = calcular_indicadores(carregar(ticker, intervalo))
    valid = df.dropna(subset=["MM20", "MM50", "RSI", "VolumeMedia20"])
    if valid.empty:
        raise ValueError("Candles insuficientes")
    ultima = valid.iloc[-1]
    pontos, sinal, motivos = analisar(ultima)
    return df, ultima, pontos, sinal, motivos

def painel():
    if not selecionados:
        st.info("Escolha pelo menos um ativo.")
        return
    resultados = []
    detalhes = {}
    for ticker in selecionados:
        try:
            df, ultima, pontos, sinal, motivos = analisar_ativo(ticker)
            resultados.append({
                "Ativo": ticker,
                "Preço": float(ultima["Close"]),
                "RSI": float(ultima["RSI"]),
                "MM20": float(ultima["MM20"]),
                "MM50": float(ultima["MM50"]),
                "Volume": float(ultima["Volume"]),
                "Score": pontos,
                "Sinal": sinal,
            })
            detalhes[ticker] = (df, ultima, pontos, sinal, motivos)
        except Exception as e:
            resultados.append({"Ativo": ticker, "Preço": None, "RSI": None, "MM20": None, "MM50": None, "Volume": None, "Score": None, "Sinal": f"ERRO: {e}"})

    tabela = pd.DataFrame(resultados)
    st.subheader("🔎 Scanner de oportunidades")
    st.dataframe(tabela, use_container_width=True, hide_index=True,
                 column_config={
                     "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
                     "RSI": st.column_config.NumberColumn(format="%.1f"),
                     "MM20": st.column_config.NumberColumn(format="R$ %.2f"),
                     "MM50": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Volume": st.column_config.NumberColumn(format="%.0f"),
                     "Score": st.column_config.NumberColumn(format="%d/100"),
                 })

    disponiveis = [x for x in selecionados if x in detalhes]
    if disponiveis:
        ativo = st.selectbox("Ver análise detalhada", disponiveis)
        df, ultima, pontos, sinal, motivos = detalhes[ativo]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Preço", f"R$ {ultima.Close:.2f}")
        c2.metric("RSI", f"{ultima.RSI:.1f}")
        c3.metric("Score", f"{pontos}/100")
        c4.metric("Sinal", sinal)
        st.line_chart(df[["Close", "MM20", "MM50"]].dropna())
        st.write("**Motivos do sinal:**")
        for m in motivos: st.write("•", m)
        st.caption(f"Último candle recebido: {df.index[-1]}")

    st.caption("Os dados podem ter atraso, limites ou indisponibilidade. Para trading real, use market data licenciado e uma corretora compatível.")

if hasattr(st, "fragment"):
    @st.fragment(run_every="25s")
    def atualizacao(): painel()
    atualizacao()
else:
    painel()
