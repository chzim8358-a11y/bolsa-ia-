import os
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

ATIVOS_B3 = {
    "PETR4": "PETR4.SA", "VALE3": "VALE3.SA", "ITUB4": "ITUB4.SA",
    "BBAS3": "BBAS3.SA", "BBDC4": "BBDC4.SA", "WEGE3": "WEGE3.SA",
    "ABEV3": "ABEV3.SA", "MGLU3": "MGLU3.SA", "B3SA3": "B3SA3.SA",
    "RENT3": "RENT3.SA", "SUZB3": "SUZB3.SA", "PRIO3": "PRIO3.SA",
}

INTERVALOS = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h"}


def _normalizar(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    rename = {str(c).lower(): c for c in df.columns}
    # BTG normalmente usa nomes em minúsculas; Yahoo usa maiúsculas.
    mapa = {}
    for alvo, candidatos in {
        "Open": ["open", "Open"], "High": ["high", "High"],
        "Low": ["low", "Low"], "Close": ["close", "Close", "last"],
        "Volume": ["volume", "Volume"],
    }.items():
        for c in candidatos:
            if c in df.columns:
                mapa[c] = alvo
                break
            if c.lower() in rename:
                mapa[rename[c.lower()]] = alvo
                break
    df = df.rename(columns=mapa)
    needed = ["Open", "High", "Low", "Close", "Volume"]
    for c in needed:
        if c not in df.columns:
            if c == "Volume":
                df[c] = 0.0
            else:
                raise ValueError(f"Coluna {c} não encontrada nos dados.")
    # Normaliza datetime sem depender do nome exato da coluna.
    if not isinstance(df.index, pd.DatetimeIndex):
        for candidate in ["datetime", "date", "time", "timestamp"]:
            if candidate in df.columns:
                df.index = pd.to_datetime(df.pop(candidate), errors="coerce")
                break
        else:
            df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()].sort_index()
    for c in needed:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[needed].dropna(subset=["Close"])


def dados_yahoo(ticker: str, periodo: str = "1d", intervalo: str = "5m") -> pd.DataFrame:
    simbolo = ATIVOS_B3.get(ticker, ticker if ticker.endswith(".SA") else f"{ticker}.SA")
    df = yf.download(simbolo, period=periodo, interval=intervalo,
                     auto_adjust=False, progress=False, threads=False)
    df = _normalizar(df)
    if df.empty:
        raise ValueError(f"Sem dados disponíveis para {ticker} agora.")
    return df


def _btg_api_key(secrets=None):
    if secrets is not None:
        try:
            key = secrets.get("BTG_API_KEY")
            if key:
                return str(key)
        except Exception:
            pass
    return os.getenv("BTG_API_KEY", "").strip()


def btg_disponivel(secrets=None) -> bool:
    return bool(_btg_api_key(secrets))


def _btg_client(secrets=None):
    key = _btg_api_key(secrets)
    if not key:
        raise RuntimeError("BTG_API_KEY não configurada.")
    try:
        import btgsolutions_dataservices as btg
    except ImportError as exc:
        raise RuntimeError("Dependência BTG Solutions não instalada.") from exc
    return btg


def _anterior_dia_util(d: date) -> date:
    d = d - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def dados_btg_realtime(ticker: str, intervalo: str = "5m", secrets=None) -> pd.DataFrame:
    """Retorna candles intraday B3 via BTG em modo realtime."""
    btg = _btg_client(secrets)
    candles = btg.IntradayCandles(api_key=_btg_api_key(secrets))
    atual = candles.get_intraday_candles(
        market_type="stocks",
        tickers=[ticker],
        delay="realtime",
        timezone="America/Sao_Paulo",
        candle_period=INTERVALOS.get(intervalo, intervalo),
        mode="absolute",
        raw_data=False,
    )
    atual_df = _normalizar(atual.get(ticker, pd.DataFrame()))

    # Mantém histórico recente para que MM20/MM50 funcionem desde a abertura.
    # O histórico é apenas complementar; a última atualização vem do feed realtime.
    try:
        hist = btg.HistoricalCandles(api_key=_btg_api_key(secrets))
        d = _anterior_dia_util(date.today())
        historico = hist.get_intraday_history_candles(
            market_type="stocks",
            ticker=ticker,
            date=d.isoformat(),
            candle=INTERVALOS.get(intervalo, intervalo),
            corporate_events_adj=True,
            rmv_after_market=True,
            timezone="America/Sao_Paulo",
            raw_data=False,
            round=True,
        )
        hist_df = _normalizar(historico)
    except Exception:
        hist_df = pd.DataFrame()

    if not hist_df.empty and not atual_df.empty:
        df = pd.concat([hist_df, atual_df]).sort_index()
        df = df[~df.index.duplicated(keep="last")]
    else:
        df = atual_df if not atual_df.empty else hist_df
    if df.empty:
        raise ValueError(f"BTG não retornou candles para {ticker}.")
    return df.tail(600)


def cotacoes_btg(tickers, secrets=None) -> pd.DataFrame:
    """Busca cotações em lote em modo realtime para reduzir chamadas."""
    btg = _btg_client(secrets)
    quotes = btg.Quotes(api_key=_btg_api_key(secrets))
    df = quotes.get_quote(tickers=list(tickers), market_type="stocks", mode="realtime", raw_data=False)
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    return df


def dividendos_yahoo(ticker: str) -> dict:
    """Referência de dividendos por ação usando o histórico do Yahoo Finance."""
    simbolo = ATIVOS_B3.get(ticker, ticker if ticker.endswith(".SA") else f"{ticker}.SA")
    try:
        hist = yf.Ticker(simbolo).dividends
        if hist is None or hist.empty:
            return {"dividendo_12m": 0.0, "ultimo_dividendo": 0.0, "data_ultimo": None}
        hist = pd.to_numeric(hist, errors="coerce").dropna()
        if hist.empty:
            return {"dividendo_12m": 0.0, "ultimo_dividendo": 0.0, "data_ultimo": None}
        idx = pd.to_datetime(hist.index, errors="coerce")
        hist.index = idx.tz_localize(None) if getattr(idx, "tz", None) is not None else idx
        inicio = pd.Timestamp.now() - pd.Timedelta(days=365)
        return {"dividendo_12m": float(hist[hist.index >= inicio].sum()), "ultimo_dividendo": float(hist.iloc[-1]), "data_ultimo": hist.index[-1].strftime("%d/%m/%Y")}
    except Exception:
        return {"dividendo_12m": 0.0, "ultimo_dividendo": 0.0, "data_ultimo": None}
