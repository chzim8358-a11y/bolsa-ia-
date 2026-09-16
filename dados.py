import os
from datetime import date, timedelta
import pandas as pd
import yfinance as yf

ATIVOS_B3={"PETR3":"PETR3.SA","PETR4":"PETR4.SA","VALE3":"VALE3.SA","ITUB3":"ITUB3.SA","ITUB4":"ITUB4.SA","ITSA4":"ITSA4.SA","BBAS3":"BBAS3.SA","BBDC3":"BBDC3.SA","BBDC4":"BBDC4.SA","WEGE3":"WEGE3.SA","ABEV3":"ABEV3.SA","MGLU3":"MGLU3.SA","B3SA3":"B3SA3.SA","RENT3":"RENT3.SA","SUZB3":"SUZB3.SA","PRIO3":"PRIO3.SA","BBSE3":"BBSE3.SA","CMIG3":"CMIG3.SA","CMIG4":"CMIG4.SA","ELET3":"ELET3.SA","ELET6":"ELET6.SA","CPLE6":"CPLE6.SA","CPFE3":"CPFE3.SA","TAEE11":"TAEE11.SA","CSNA3":"CSNA3.SA","CMIN3":"CMIN3.SA","LREN3":"LREN3.SA","EMBR3":"EMBR3.SA","TOTS3":"TOTS3.SA","RADL3":"RADL3.SA","HYPE3":"HYPE3.SA","VIVT3":"VIVT3.SA","EGIE3":"EGIE3.SA","SBSP3":"SBSP3.SA","GGBR4":"GGBR4.SA","GOAU4":"GOAU4.SA","KLBN11":"KLBN11.SA","BRFS3":"BRFS3.SA","AZUL4":"AZUL4.SA","XPML11":"XPML11.SA","MXRF11":"MXRF11.SA","HGLG11":"HGLG11.SA","BTLG11":"BTLG11.SA","KNCR11":"KNCR11.SA","XPLG11":"XPLG11.SA","TRXF11":"TRXF11.SA","XPIN11":"XPIN11.SA","VISC11":"VISC11.SA","HSML11":"HSML11.SA","MALL11":"MALL11.SA","BOVA11":"BOVA11.SA","SMAL11":"SMAL11.SA","IVVB11":"IVVB11.SA","DIVO11":"DIVO11.SA","GOLD11":"GOLD11.SA","HASH11":"HASH11.SA","XINA11":"XINA11.SA","WRLD11":"WRLD11.SA","AAPL34":"AAPL34.SA","MSFT34":"MSFT34.SA","GOOG34":"GOOG34.SA","AMZO34":"AMZO34.SA","NVDC34":"NVDC34.SA","TSLA34":"TSLA34.SA"}
INTERVALOS={"1m":"1m","5m":"5m","15m":"15m","30m":"30m","1h":"1h"}
YAHOO_PERIODOS={"1m":"5d","5m":"30d","15m":"60d","30m":"60d","1h":"6mo"}

def _normalizar(df):
    if df is None or df.empty: return pd.DataFrame()
    df=df.copy()
    if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
    lower={str(c).lower():c for c in df.columns}; mapa={}
    for alvo,candidatos in {"Open":["open"],"High":["high"],"Low":["low"],"Close":["close","last","price"],"Volume":["volume"]}.items():
        for c in candidatos:
            if c in lower: mapa[lower[c]]=alvo; break
    df=df.rename(columns=mapa)
    for c in ["Open","High","Low","Close","Volume"]:
        if c not in df.columns:
            if c=="Volume": df[c]=0.0
            else: raise ValueError(f"Coluna {c} não encontrada nos dados.")
    if not isinstance(df.index,pd.DatetimeIndex):
        for candidate in ["datetime","date","time","timestamp"]:
            if candidate in df.columns:
                df.index=pd.to_datetime(df.pop(candidate),errors="coerce"); break
        else: df.index=pd.to_datetime(df.index,errors="coerce")
    df=df[~df.index.isna()].sort_index()
    for c in ["Open","High","Low","Close","Volume"]: df[c]=pd.to_numeric(df[c],errors="coerce")
    return df[["Open","High","Low","Close","Volume"]].dropna(subset=["Close"])

def dados_yahoo(ticker,periodo=None,intervalo="5m"):
    simbolo=ATIVOS_B3.get(ticker,ticker if ticker.endswith(".SA") else f"{ticker}.SA")
    periodo=periodo or YAHOO_PERIODOS.get(intervalo,"1d")
    df=yf.download(simbolo,period=periodo,interval=intervalo,auto_adjust=False,progress=False,threads=False)
    df=_normalizar(df)
    if df.empty: raise ValueError(f"Sem dados disponíveis para {ticker} agora.")
    return df.tail(2000)

def _btg_api_key(secrets=None):
    if secrets is not None:
        try:
            key=secrets.get("BTG_API_KEY")
            if key: return str(key)
        except Exception: pass
    return os.getenv("BTG_API_KEY","").strip()

def btg_disponivel(secrets=None): return bool(_btg_api_key(secrets))

def _btg_client(secrets=None):
    key=_btg_api_key(secrets)
    if not key: raise RuntimeError("BTG_API_KEY não configurada.")
    try: import btgsolutions_dataservices as btg
    except ImportError as exc: raise RuntimeError("Dependência BTG Solutions não instalada.") from exc
    return btg

def _anterior_dia_util(d):
    d=d-timedelta(days=1)
    while d.weekday()>=5: d-=timedelta(days=1)
    return d

def dados_btg_realtime(ticker,intervalo="5m",secrets=None):
    btg=_btg_client(secrets); candles=btg.IntradayCandles(api_key=_btg_api_key(secrets))
    atual=candles.get_intraday_candles(market_type="stocks",tickers=[ticker],delay="realtime",timezone="America/Sao_Paulo",candle_period=INTERVALOS.get(intervalo,intervalo),mode="absolute",raw_data=False)
    atual_df=_normalizar(atual.get(ticker,pd.DataFrame()))
    try:
        hist=btg.HistoricalCandles(api_key=_btg_api_key(secrets)); d=_anterior_dia_util(date.today())
        historico=hist.get_intraday_history_candles(market_type="stocks",ticker=ticker,date=d.isoformat(),candle=INTERVALOS.get(intervalo,intervalo),corporate_events_adj=True,rmv_after_market=True,timezone="America/Sao_Paulo",raw_data=False,round=True)
        hist_df=_normalizar(historico)
    except Exception: hist_df=pd.DataFrame()
    if not hist_df.empty and not atual_df.empty:
        df=pd.concat([hist_df,atual_df]).sort_index(); df=df[~df.index.duplicated(keep="last")]
    else: df=atual_df if not atual_df.empty else hist_df
    if df.empty: raise ValueError(f"BTG não retornou candles para {ticker}.")
    return df.tail(600)

def cotacoes_btg(tickers,secrets=None):
    btg=_btg_client(secrets); quotes=btg.Quotes(api_key=_btg_api_key(secrets))
    df=quotes.get_quote(tickers=list(tickers),market_type="stocks",mode="realtime",raw_data=False)
    return df if isinstance(df,pd.DataFrame) else pd.DataFrame(df)


def cotacoes_yahoo_realtime(tickers):
    """Obtém o último preço disponível no Yahoo Finance.
    Observação: a disponibilidade/latência depende da fonte; não é garantido como tick-by-tick.
    """
    out = {}
    for ticker in tickers:
        simbolo = ATIVOS_B3.get(ticker, ticker if ticker.endswith(".SA") else f"{ticker}.SA")
        try:
            t = yf.Ticker(simbolo)
            info = t.fast_info
            price = info.get("last_price") if hasattr(info, "get") else None
            if price is not None and pd.notna(price):
                out[ticker] = float(price)
        except Exception:
            pass
    return out


def atualizar_cotacoes_engine(tickers, engine, secrets=None):
    """Atualiza o motor com a melhor fonte disponível e devolve seu snapshot."""
    tickers=list(tickers)
    if btg_disponivel(secrets):
        try:
            q=cotacoes_btg(tickers, secrets=secrets)
            out={}
            if isinstance(q,pd.DataFrame):
                # tenta localizar a coluna de último preço de forma tolerante
                lower={str(c).lower():c for c in q.columns}
                pc=next((lower[k] for k in ("last_price","last","price","close") if k in lower),None)
                tc=next((lower[k] for k in ("ticker","symbol","code") if k in lower),None)
                if pc:
                    if tc:
                        for _,r in q.iterrows():
                            if pd.notna(r[pc]): out[str(r[tc]).upper()]=float(r[pc])
                    elif len(q)==len(tickers):
                        for t,v in zip(tickers,q[pc]):
                            if pd.notna(v): out[t]=float(v)
            if out:
                engine.update(out, source="BTG realtime")
                return engine.snapshot(tickers)
        except Exception:
            pass
    out=cotacoes_yahoo_realtime(tickers)
    engine.update(out, source="Yahoo fallback")
    return engine.snapshot(tickers)
