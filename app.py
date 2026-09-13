import streamlit as st
from dados import dados_reais
from indicadores import calcular_indicadores
from analisador import analisar

st.set_page_config(page_title="BolsaIA", page_icon="📈", layout="wide")
st.title("📈 BolsaIA — analisador de mercado")
st.caption("Monitoramento automático de mercado para fins educacionais. Não é recomendação de investimento.")

ticker = st.selectbox("Ativo", ["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4"])
intervalo = st.selectbox("Intervalo dos candles", ["1m", "5m", "15m", "30m", "1h"], index=1)

@st.cache_data(ttl=25, show_spinner=False)
def carregar(ticker_selecionado, intervalo_selecionado):
    periodo = "1d" if intervalo_selecionado in ("1m", "5m", "15m", "30m", "1h") else "5d"
    return dados_reais(ticker_selecionado, periodo=periodo, intervalo=intervalo_selecionado)


def painel():
    try:
        df = carregar(ticker, intervalo)
        df = calcular_indicadores(df)
        df_valid = df.dropna(subset=["MM20", "MM50", "RSI", "VolumeMedia20"])

        if df_valid.empty:
            st.warning("Ainda não há candles suficientes para calcular todos os indicadores.")
            return

        ultima = df_valid.iloc[-1]
        anterior = df_valid.iloc[-2] if len(df_valid) > 1 else None
        pontos, tendencia, motivos = analisar(ultima)

        preco_delta = None
        if anterior is not None:
            preco_delta = float(ultima["Close"] - anterior["Close"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço", f"R$ {ultima.Close:.2f}", f"{preco_delta:+.2f}" if preco_delta is not None else None)
        c2.metric("RSI", f"{ultima.RSI:.1f}")
        c3.metric("Volume", f"{ultima.Volume:,.0f}".replace(",", "."))
        c4.metric("Pontuação IA", f"{pontos}/100")

        st.subheader(f"{ticker} — {tendencia}")
        st.line_chart(df[["Close", "MM20", "MM50"]].dropna())

        st.write("**Fatores considerados:**")
        for motivo in motivos:
            st.write("•", motivo)

        ultimo_horario = df.index[-1]
        st.caption(f"Último candle recebido: {ultimo_horario} · Atualização automática a cada ~25 s")

    except Exception as e:
        st.error(f"Não foi possível atualizar os dados: {e}")
        st.info("Verifique sua conexão com a internet e tente novamente. Se o problema persistir, o provedor de dados pode estar temporariamente indisponível.")


# O fragmento faz o painel ser reexecutado periodicamente sem precisar apertar F5.
if hasattr(st, "fragment"):
    @st.fragment(run_every="25s")
    def atualizacao_automatica():
        painel()
    atualizacao_automatica()
else:
    painel()

st.divider()
st.caption("PROTÓTIPO: os dados vêm de um provedor público e podem sofrer atraso, limites ou indisponibilidade. Para operação financeira real, use market data autorizado/licenciado.")
