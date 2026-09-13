import streamlit as st
from dados import dados_demo
from indicadores import calcular_indicadores
from analisador import analisar

st.set_page_config(page_title="BolsaIA", layout="wide")
st.title("📈 BolsaIA — analisador de mercado")

ticker = st.selectbox("Ativo", ["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4"])
df = calcular_indicadores(dados_demo())
ultima = df.dropna().iloc[-1]

pontos, tendencia, motivos = analisar(ultima)

c1, c2, c3 = st.columns(3)
c1.metric("Preço", f"R$ {ultima.Close:.2f}")
c2.metric("RSI", f"{ultima.RSI:.1f}")
c3.metric("Pontuação IA", f"{pontos}/100")

st.subheader(f"{ticker} — {tendencia}")
st.line_chart(df[["Close", "MM20", "MM50"]].dropna())

st.write("**Fatores considerados:**")
for motivo in motivos:
    st.write("•", motivo)

st.caption("Modo DEMO: os dados são simulados. Não use esta versão para decisões financeiras.")
