def analisar(ultima):
    pontos = 50
    motivos = []

    if ultima["Close"] > ultima["MM20"]:
        pontos += 10
        motivos.append("preço acima da MM20")
    else:
        pontos -= 10

    if ultima["MM20"] > ultima["MM50"]:
        pontos += 15
        motivos.append("MM20 acima da MM50")
    else:
        pontos -= 15

    rsi = ultima["RSI"]
    if rsi < 30:
        pontos += 10
        motivos.append("RSI em região de sobrevenda")
    elif rsi > 70:
        pontos -= 10
        motivos.append("RSI em região de sobrecompra")

    if ultima["Volume"] > ultima["VolumeMedia20"]:
        pontos += 10
        motivos.append("volume acima da média")

    pontos = max(0, min(100, pontos))

    if pontos >= 75:
        tendencia = "ALTA FORTE"
    elif pontos >= 60:
        tendencia = "ALTA"
    elif pontos >= 40:
        tendencia = "NEUTRA"
    elif pontos >= 25:
        tendencia = "BAIXA"
    else:
        tendencia = "BAIXA FORTE"

    return pontos, tendencia, motivos
