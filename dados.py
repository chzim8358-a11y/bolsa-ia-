import pandas as pd
import yfinance as yf


ATIVOS_B3 = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "BBAS3": "BBAS3.SA",
    "BBDC4": "BBDC4.SA",
}


def dados_reais(ticker: str, periodo: str = "5d", intervalo: str = "5m") -> pd.DataFrame:
    """Baixa candles recentes de uma ação da B3 via Yahoo Finance.

    Observação: é uma fonte prática para protótipo e pode ter atraso/limitações.
    Para uso profissional, substitua por um provedor de market data autorizado.
    """
    simbolo = ATIVOS_B3.get(ticker, ticker if ticker.endswith(".SA") else f"{ticker}.SA")

    df = yf.download(
        simbolo,
        period=periodo,
        interval=intervalo,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if df is None or df.empty:
        raise ValueError(f"Não foi possível obter dados para {ticker} agora.")

    # Algumas versões do yfinance retornam colunas MultiIndex mesmo para um ativo.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    colunas = ["Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in colunas if c in df.columns]].copy()
    df = df.dropna(subset=["Close"])

    if len(df) < 60:
        raise ValueError("Foram recebidos poucos candles para calcular MM50/RSI com segurança.")

    return df


def dados_demo(dias=120, preco_inicial=35):
    # Mantido para testes/offline.
    import numpy as np

    rng = np.random.default_rng(42)
    retornos = rng.normal(0.001, 0.018, dias)
    precos = preco_inicial * np.cumprod(1 + retornos)
    datas = pd.date_range(end=pd.Timestamp.today(), periods=dias)
    close = pd.Series(precos, index=datas)
    open_ = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, .005, dias))
    high = pd.concat([open_, close], axis=1).max(axis=1) * (1 + rng.random(dias)*.01)
    low = pd.concat([open_, close], axis=1).min(axis=1) * (1 - rng.random(dias)*.01)
    volume = rng.integers(500_000, 2_000_000, dias)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume})
