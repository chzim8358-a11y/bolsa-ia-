import pandas as pd

def calcular_indicadores(df):
    df = df.copy().sort_index()
    close = pd.to_numeric(df["Close"], errors="coerce")
    high = pd.to_numeric(df["High"], errors="coerce")
    low = pd.to_numeric(df["Low"], errors="coerce")
    volume = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)

    df["MM20"] = close.rolling(20, min_periods=20).mean()
    df["MM50"] = close.rolling(50, min_periods=50).mean()
    df["MM200"] = close.rolling(200, min_periods=200).mean()

    # RSI de Wilder (mais estável do que médias simples em séries curtas).
    delta = close.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)
    media_ganho = ganho.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    media_perda = perda.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = media_ganho / media_perda.replace(0, pd.NA)
    df["RSI"] = (100 - (100 / (1 + rs))).astype(float)
    # Quando não há perdas no período, RSI deve ser 100; sem ganhos nem perdas, 50.
    df.loc[(media_perda == 0) & (media_ganho > 0), "RSI"] = 100.0
    df.loc[(media_perda == 0) & (media_ganho == 0), "RSI"] = 50.0

    df["VolumeMedia20"] = volume.rolling(20, min_periods=20).mean()

    df["EMA12"] = close.ewm(span=12, adjust=False).mean()
    df["EMA26"] = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["MACD_Sinal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Sinal"]

    df["Suporte20"] = low.rolling(20, min_periods=20).min()
    df["Resistencia20"] = high.rolling(20, min_periods=20).max()

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = true_range.ewm(alpha=1/14, adjust=False, min_periods=14).mean()

    # ADX simplificado: ajuda a separar tendência de lateralização.
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    atr = df["ATR14"].replace(0, pd.NA)
    plus_di = 100 * plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA))
    df["ADX14"] = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean().astype(float)
    df["DI_Plus"] = plus_di.astype(float)
    df["DI_Minus"] = minus_di.astype(float)

    df["Volume"] = volume
    return df
