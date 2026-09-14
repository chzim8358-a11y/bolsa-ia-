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

    rsi = float(ultima["RSI"])
    if rsi < 30:
        pontos += 8; motivos.append("RSI em sobrevenda")
    elif rsi > 70:
        pontos -= 8; motivos.append("RSI em sobrecompra")
    else:
        motivos.append("RSI em faixa intermediária")

    if float(ultima["Volume"]) > float(ultima["VolumeMedia20"]):
        pontos += 8; motivos.append("volume acima da média")

    macd = float(ultima["MACD"])
    macd_sinal = float(ultima["MACD_Sinal"])
    if macd > macd_sinal:
        pontos += 8; motivos.append("MACD acima da linha de sinal")
    else:
        pontos -= 8; motivos.append("MACD abaixo da linha de sinal")

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
    """Identifica padrões simples nas últimas velas. É análise técnica, não previsão."""
    if df is None or len(df) < 2:
        return "Sem dados suficientes", "NEUTRO", []

    atual = df.iloc[-1]
    anterior = df.iloc[-2]
    o, h, l, c = map(float, [atual["Open"], atual["High"], atual["Low"], atual["Close"]])
    po, pc = float(anterior["Open"]), float(anterior["Close"])
    corpo = abs(c - o)
    amplitude = max(h - l, 1e-9)
    superior = h - max(o, c)
    inferior = min(o, c) - l
    sinais = []
    viés = 0

    if corpo / amplitude <= 0.10:
        sinais.append("Doji: indecisão")

    if inferior >= corpo * 2 and superior <= max(corpo * 0.75, amplitude * 0.08) and c >= o:
        sinais.append("Martelo: possível reação compradora")
        viés += 1

    if superior >= corpo * 2 and inferior <= max(corpo * 0.75, amplitude * 0.08) and c <= o:
        sinais.append("Estrela cadente: possível pressão vendedora")
        viés -= 1

    if pc < po and c > o and o <= pc and c >= po:
        sinais.append("Engolfo de alta")
        viés += 2
    elif pc > po and c < o and o >= pc and c <= po:
        sinais.append("Engolfo de baixa")
        viés -= 2

    if not sinais:
        sinais.append("Nenhum padrão forte detectado na última vela")

    if viés > 0:
        leitura = "ALTA"
    elif viés < 0:
        leitura = "BAIXA"
    else:
        leitura = "NEUTRO"
    return sinais[0], leitura, sinais


def calcular_plano(ultima, preco=None):
    """Calcula níveis técnicos de referência; não é previsão nem recomendação."""
    preco = float(preco if preco is not None else ultima["Close"])
    suporte = float(ultima["Suporte20"])
    resistencia = float(ultima["Resistencia20"])
    atr = float(ultima.get("ATR14", 0) or 0)

    if atr <= 0:
        atr = max(preco * 0.01, 0.01)

    # Stop abaixo do suporte recente, com pequena folga de volatilidade.
    stop = suporte - 0.25 * atr
    if stop >= preco:
        stop = preco - atr

    # Alvo prioriza resistência recente; se já estiver acima dela, usa uma extensão de 1,5 ATR.
    alvo = resistencia if resistencia > preco else preco + 1.5 * atr
    risco = preco - stop
    retorno = alvo - preco
    rr = (retorno / risco) if risco > 0 else None

    # "Confiança" é apenas uma tradução visual do score técnico; não é probabilidade estatística.
    return {
        "preco": preco,
        "stop": stop,
        "alvo": alvo,
        "risco_por_acao": max(risco, 0),
        "retorno_por_acao": max(retorno, 0),
        "risco_retorno": rr,
        "atr": atr,
    }
