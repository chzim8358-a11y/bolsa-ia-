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
    return df
