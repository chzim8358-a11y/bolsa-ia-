import streamlit as st
import pandas as pd

from dados import (
    dados_yahoo, dados_btg_realtime, cotacoes_btg, btg_disponivel,
    ATIVOS_B3,
)
from indicadores import calcular_indicadores
from analisador import analisar, analisar_candles, calcular_plano
from dividendos import obter_dividendos_yahoo

st.set_page_config(page_title="BolsaIA v10", page_icon="🚀", layout="wide")
st.title("🚀 BolsaIA v10 — Radar + Carteira Simulada")
st.caption("Motor educacional de análise técnica + acompanhamento de carteira simulada. Não é recomendação de investimento.")

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
    valid = df.dropna(subset=["MM20", "MM50", "RSI", "VolumeMedia20", "MACD", "MACD_Sinal"])
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
            out[selecionados[0]] = float(df.iloc[0][price_col])
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
        except Exception as e:
            st.warning(f"Cotações realtime indisponíveis nesta atualização: {e}")

    for ticker in selecionados:
        try:
            df, ultima, pontos, sinal, motivos, candle_leitura, candle_padroes = analisar_ativo(ticker)
            preco = realtime_prices.get(ticker, float(ultima["Close"]))
            plano_scan = calcular_plano(ultima, preco)
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
                "Volume": float(ultima["Volume"]),
                "Score": pontos,
                "Sinal": sinal,
                "Candle": candle_leitura,
                "R/R": plano_scan["risco_retorno"],
                "Yield 12m": dy_scan,
                "Variação": ((preco / float(df["Close"].iloc[-2]) - 1) * 100) if len(df) > 1 and float(df["Close"].iloc[-2]) else None,
                "ATR %": ((float(ultima["ATR14"]) / preco) * 100) if preco and pd.notna(ultima["ATR14"]) else None,
            })
            detalhes[ticker] = (df, ultima, pontos, sinal, motivos, preco, candle_leitura, candle_padroes)
        except Exception as e:
            resultados.append({
                "Ativo": ticker, "Preço": None, "RSI": None, "MM20": None,
                "MM50": None, "Volume": None, "Score": None, "Sinal": f"ERRO: {e}", "Candle": "ERRO", "R/R": None, "Yield 12m": None, "Variação": None, "ATR %": None,
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
            "Candle": st.column_config.TextColumn(),
            "R/R": st.column_config.NumberColumn(format="1:%.2f"),
            "Yield 12m": st.column_config.NumberColumn(format="%.2f%%"),
            "Variação": st.column_config.NumberColumn(format="%.2f%%"),
            "ATR %": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )

    # Radar V9: ranking visual das melhores pontuações entre os ativos monitorados.
    st.markdown("### 🏆 Radar de Oportunidades")
    ranking = tabela.dropna(subset=["Score"]).sort_values(["Score", "R/R"], ascending=[False, False]).reset_index(drop=True)
    if ranking.empty:
        st.info("Ainda não há dados suficientes para montar o radar.")
    else:
        top = ranking.head(3)
        cards = st.columns(len(top))
        for i, (_, row) in enumerate(top.iterrows()):
            with cards[i]:
                medalha = ["🥇", "🥈", "🥉"][i]
                st.metric(f"{medalha} {row['Ativo']}", f"{int(row['Score'])}/100", row["Sinal"])
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

    st.markdown("### 🔔 Histórico de alertas")
    if st.session_state.historico_alertas:
        hist_alertas = pd.DataFrame(st.session_state.historico_alertas)[["hora", "ativo", "score", "sinal", "preco"]].sort_values("hora", ascending=False)
        hist_alertas["hora"] = hist_alertas["hora"].dt.strftime("%d/%m/%Y %H:%M:%S")
        st.dataframe(hist_alertas, use_container_width=True, hide_index=True, column_config={"preco": st.column_config.NumberColumn("Preço", format="R$ %.2f"), "score": st.column_config.NumberColumn("Score", format="%d/100")})
        csv_alertas = hist_alertas.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar alertas CSV", csv_alertas, file_name="bolsaia_alertas_v10.csv", mime="text/csv")
    else:
        st.info("Nenhum alerta registrado nesta sessão ainda. O histórico começa quando um ativo atingir o limiar configurado.")

    # V10: carteira virtual, sem envio de ordens e sem conexão com corretora.
    st.markdown("### 💼 Carteira simulada")
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
            posicoes.append({"Ativo": ticker, "Qtd": qtd, "Preço médio": pm, "Preço atual": atual, "Investido": investido, "Valor atual": valor, "P/L": pl, "P/L %": pl_pct})
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
                "P/L": st.column_config.NumberColumn(format="R$ %.2f"), "P/L %": st.column_config.NumberColumn(format="%.2f%%")})
            csv_carteira = carteira_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar carteira CSV", csv_carteira, file_name="bolsaia_carteira_v10.csv", mime="text/csv")
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
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tendência", "ALTA" if ultima["MM20"] > ultima["MM50"] else "BAIXA")
        m2.metric("MACD", "POSITIVO" if ultima["MACD"] > ultima["MACD_Sinal"] else "NEGATIVO")
        m3.metric("Candle", candle_leitura)
        distancia_suporte = ((float(ultima["Close"]) / float(ultima["Suporte20"])) - 1) * 100 if float(ultima["Suporte20"]) else 0
        m4.metric("Suporte 20", f"R$ {float(ultima['Suporte20']):.2f}", help=f"Preço está {distancia_suporte:.1f}% acima do suporte recente.")
        st.caption("O Score IA combina tendência, RSI, volume, MACD e leitura de candles. É um modelo de análise técnica educacional; não garante movimentos futuros.")

        st.markdown("### 🎯 Plano técnico")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🎯 Alvo técnico", f"R$ {plano['alvo']:.2f}")
        p2.metric("🛑 Stop técnico", f"R$ {plano['stop']:.2f}")
        rr_txt = f"1:{plano['risco_retorno']:.2f}" if plano["risco_retorno"] is not None else "N/D"
        p3.metric("⚖️ Risco/Retorno", rr_txt)
        p4.metric("🧠 Confiança técnica", f"{pontos}/100")
        st.caption("Alvo e stop são níveis técnicos calculados a partir de suporte, resistência e ATR recente. A confiança é o Score técnico do modelo, não uma probabilidade estatística de alta ou queda.")

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
