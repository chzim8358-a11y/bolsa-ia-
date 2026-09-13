import pandas as pd
import yfinance as yf

ATIVOS_B3 = {
    "PETR4": "PETR4.SA", "VALE3": "VALE3.SA", "ITUB4": "ITUB4.SA",
    "BBAS3": "BBAS3.SA", "BBDC4": "BBDC4.SA", "WEGE3": "WEGE3.SA",
    "ABEV3": "ABEV3.SA", "MGLU3": "MGLU3.SA", "B3SA3": "B3SA3.SA",
    "RENT3": "RENT3.SA", "SUZB3": "SUZB3.SA", "PRIO3": "PRIO3.SA",
}


def dados_reais(ticker: str, periodo: str = "1d", intervalo: str = "5m") -> pd.DataFrame:
    simbolo = ATIVOS_B3.get(ticker, ticker if ticker.endswith(".SA") else f"{ticker}.SA")
    df = yf.download(simbolo, period=periodo, interval=intervalo,
                     auto_adjust=False, progress=False, threads=False)
    if df is None or df.empty:
        raise ValueError(f"Sem dados disponíveis para {ticker} agora.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    df = df[cols].copy().dropna(subset=["Close"])
    if len(df) < 60:
        raise ValueError(f"Poucos candles recebidos para {ticker} ({len(df)}).")
    return df
