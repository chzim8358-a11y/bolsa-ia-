from datetime import datetime, timezone
import pandas as pd
import yfinance as yf


def obter_dividendos_yahoo(ticker: str, periodo_dias: int = 370) -> dict:
    """Obtém dividendos reais do histórico do ativo via Yahoo Finance."""
    simbolo = ticker if ticker.endswith('.SA') else f'{ticker}.SA'
    tk = yf.Ticker(simbolo)
    try:
        serie = tk.dividends
    except Exception as exc:
        raise RuntimeError(f'Não foi possível consultar dividendos de {ticker}: {exc}') from exc

    if serie is None or len(serie) == 0:
        return {
            'dividendo_cota': None,
            'dividendos_12m': None,
            'ultimo_dividendo': None,
            'ultima_data': None,
            'yield_12m': None,
        }

    serie = pd.Series(serie).dropna()
    serie.index = pd.to_datetime(serie.index)
    corte = pd.Timestamp.now(tz=serie.index.tz) - pd.Timedelta(days=periodo_dias) if getattr(serie.index, 'tz', None) else pd.Timestamp.now() - pd.Timedelta(days=periodo_dias)
    recente = serie[serie.index >= corte]

    ultimo_valor = float(serie.iloc[-1])
    ultima_data = serie.index[-1]
    total_12m = float(recente.sum())

    # Dividend yield trailing 12 meses será calculado pelo app usando o preço realtime.
    return {
        'dividendo_cota': ultimo_valor,
        'dividendos_12m': total_12m,
        'ultimo_dividendo': ultimo_valor,
        'ultima_data': ultima_data,
        'yield_12m': None,
    }
