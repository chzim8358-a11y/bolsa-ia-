import pandas as pd
import numpy as np

def dados_demo(dias=120, preco_inicial=35):
    rng = np.random.default_rng(42)
    retornos = rng.normal(0.001, 0.018, dias)
    precos = preco_inicial * np.cumprod(1 + retornos)

    datas = pd.date_range(end=pd.Timestamp.today(), periods=dias)
    close = pd.Series(precos, index=datas)
    open_ = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, .005, dias))
    high = pd.concat([open_, close], axis=1).max(axis=1) * (1 + rng.random(dias)*.01)
    low = pd.concat([open_, close], axis=1).min(axis=1) * (1 - rng.random(dias)*.01)
    volume = rng.integers(500_000, 2_000_000, dias)

    return pd.DataFrame({
        "Open": open_, "High": high, "Low": low,
        "Close": close, "Volume": volume
    })
