def analisar(ultima, candle_leitura="NEUTRO"):
    pontos = 50
    motivos = []

    if ultima["Close"] > ultima["MM20"]:
        pontos += 8; motivos.append("preço acima da MM20")
    else:
        pontos -= 8; motivos.append("preço abaixo da MM20")
    if ultima["MM20"] > ultima["MM50"]:
        pontos += 12; motivos.append("MM20 acima da MM50")
    else:
        pontos -= 12; motivos.append("MM20 abaixo da MM50")

    if ultima.get("MM200") == ultima.get("MM200") and ultima["MM200"]:
        if ultima["Close"] > ultima["MM200"]:
            pontos += 5; motivos.append("preço acima da MM200")
        else:
            pontos -= 5; motivos.append("preço abaixo da MM200")

    rsi = float(ultima["RSI"])
    if rsi < 30:
        pontos += 8; motivos.append("RSI em sobrevenda")
    elif rsi > 70:
        pontos -= 8; motivos.append("RSI em sobrecompra")
    else:
        motivos.append("RSI em faixa intermediária")

    if float(ultima["Volume"]) > float(ultima["VolumeMedia20"]):
        pontos += 8; motivos.append("volume acima da média")
    else:
        motivos.append("volume abaixo da média")

    macd = float(ultima["MACD"]); macd_sinal = float(ultima["MACD_Sinal"])
    if macd > macd_sinal:
        pontos += 8; motivos.append("MACD acima da linha de sinal")
    else:
        pontos -= 8; motivos.append("MACD abaixo da linha de sinal")

    adx = ultima.get("ADX14")
    if adx == adx:
        adx = float(adx)
        if adx >= 25:
            if float(ultima.get("DI_Plus", 0)) > float(ultima.get("DI_Minus", 0)):
                pontos += 7; motivos.append("ADX indica tendência com DI+ dominante")
            else:
                pontos -= 7; motivos.append("ADX indica tendência com DI- dominante")
        else:
            motivos.append("ADX abaixo de 25: tendência fraca/lateralização")

    if candle_leitura == "ALTA":
        pontos += 6; motivos.append("padrão de candle com viés de alta")
    elif candle_leitura == "BAIXA":
        pontos -= 6; motivos.append("padrão de candle com viés de baixa")

    pontos = max(0, min(100, int(round(pontos))))
    if pontos >= 75: sinal = "COMPRA — forte"
    elif pontos >= 60: sinal = "COMPRA — moderado"
    elif pontos <= 25: sinal = "VENDA — forte"
    elif pontos < 40: sinal = "VENDA — moderado"
    else: sinal = "AGUARDAR"
    return pontos, sinal, motivos


def analisar_candles(df):
    if df is None or len(df) < 2:
        return "Sem dados suficientes", "NEUTRO", []
    atual = df.iloc[-1]; anterior = df.iloc[-2]
    o, h, l, c = map(float, [atual["Open"], atual["High"], atual["Low"], atual["Close"]])
    po, pc = float(anterior["Open"]), float(anterior["Close"])
    corpo = abs(c-o); amplitude=max(h-l,1e-9); superior=h-max(o,c); inferior=min(o,c)-l
    sinais=[]; vies=0
    if corpo/amplitude <= 0.10: sinais.append("Doji: indecisão")
    if inferior >= corpo*2 and superior <= max(corpo*.75, amplitude*.08) and c >= o:
        sinais.append("Martelo: possível reação compradora"); vies += 1
    if superior >= corpo*2 and inferior <= max(corpo*.75, amplitude*.08) and c <= o:
        sinais.append("Estrela cadente: possível pressão vendedora"); vies -= 1
    if pc < po and c > o and o <= pc and c >= po:
        sinais.append("Engolfo de alta"); vies += 2
    elif pc > po and c < o and o >= pc and c <= po:
        sinais.append("Engolfo de baixa"); vies -= 2
    if not sinais: sinais.append("Nenhum padrão forte detectado na última vela")
    leitura = "ALTA" if vies > 0 else "BAIXA" if vies < 0 else "NEUTRO"
    return sinais[0], leitura, sinais


def calcular_plano(ultima, preco=None):
    preco=float(preco if preco is not None else ultima["Close"])
    suporte=float(ultima["Suporte20"]); resistencia=float(ultima["Resistencia20"])
    atr=float(ultima.get("ATR14",0) or 0)
    if atr <= 0: atr=max(preco*.01,.01)
    stop=suporte-.25*atr
    if stop >= preco: stop=preco-atr
    alvo=resistencia if resistencia>preco else preco+1.5*atr
    risco=max(preco-stop,0); retorno=max(alvo-preco,0)
    rr=(retorno/risco) if risco>0 else None
    return {"preco":preco,"stop":stop,"alvo":alvo,"risco_por_acao":risco,"retorno_por_acao":retorno,"risco_retorno":rr,"atr":atr}
