import pandas as pd

def calcular_indicadores(df):
    df = df.copy()
    df["MM20"] = df["Close"].rolling(20).mean()
    df["MM50"] = df["Close"].rolling(50).mean()
    delta = df["Close"].diff()
    ganhos = delta.clip(lower=0).rolling(14).mean()
    perdas = (-delta.clip(upper=0)).rolling(14).mean()
    rs = ganhos / perdas.replace(0, pd.NA)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["VolumeMedia20"] = df["Volume"].rolling(20).mean()

    # MACD: momentum de curto prazo versus longo prazo.
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["MACD_Sinal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Sinal"]

    # Suporte/resistência simples usando máximas e mínimas recentes.
    df["Suporte20"] = df["Low"].rolling(20).min()
    df["Resistencia20"] = df["High"].rolling(20).max()

    # ATR14: medida simples da volatilidade recente, usada apenas para
    # dimensionar a folga do stop e o alvo técnico.
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - df["Close"].shift()).abs()
    tr3 = (df["Low"] - df["Close"].shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = true_range.rolling(14).mean()
    return df
