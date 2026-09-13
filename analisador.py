def analisar(ultima):
    pontos = 50
    motivos = []
    if ultima["Close"] > ultima["MM20"]:
        pontos += 10; motivos.append("preço acima da MM20")
    else:
        pontos -= 10; motivos.append("preço abaixo da MM20")
    if ultima["MM20"] > ultima["MM50"]:
        pontos += 15; motivos.append("MM20 acima da MM50")
    else:
        pontos -= 15; motivos.append("MM20 abaixo da MM50")
    rsi = float(ultima["RSI"])
    if rsi < 30:
        pontos += 10; motivos.append("RSI em sobrevenda")
    elif rsi > 70:
        pontos -= 10; motivos.append("RSI em sobrecompra")
    else:
        motivos.append("RSI em faixa intermediária")
    if ultima["Volume"] > ultima["VolumeMedia20"]:
        pontos += 10; motivos.append("volume acima da média")
    pontos = max(0, min(100, int(round(pontos))))
    if pontos >= 75: sinal = "COMPRA — forte"
    elif pontos >= 60: sinal = "COMPRA — moderado"
    elif pontos <= 25: sinal = "VENDA — forte"
    elif pontos < 40: sinal = "VENDA — moderado"
    else: sinal = "AGUARDAR"
    return pontos, sinal, motivos
