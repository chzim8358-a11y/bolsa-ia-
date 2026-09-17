"""BolsaIA V44 - Realtime Hub local.
Mantém cache, timestamps, idade do dado e uma interface de ingestão para uma
futura conexão tick-by-tick/WebSocket. O hub não fabrica preços: ele distribui
com baixa latência os dados recebidos de um feed de mercado configurado.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Iterable, Optional

@dataclass
class Quote:
    ticker: str
    price: float
    source: str
    updated_at: float
    status: str = "fresh"

    @property
    def age_seconds(self) -> float:
        return max(0.0, time.time() - self.updated_at)

    @property
    def updated_iso(self) -> str:
        return datetime.fromtimestamp(self.updated_at, tz=timezone.utc).isoformat()

class RealtimeEngine:
    def __init__(self, ttl_seconds: int = 15):
        self.ttl_seconds = ttl_seconds
        self._quotes: Dict[str, Quote] = {}
        self._lock = Lock()

    def update(self, quotes: Dict[str, float], source: str = "provider") -> Dict[str, Quote]:
        now = time.time()
        with self._lock:
            for ticker, price in quotes.items():
                if price is None:
                    continue
                self._quotes[ticker] = Quote(ticker, float(price), source, now)
        return self.snapshot()

    def snapshot(self, tickers: Optional[Iterable[str]] = None) -> Dict[str, Quote]:
        wanted = set(tickers) if tickers is not None else None
        now = time.time()
        with self._lock:
            result = {}
            for ticker, quote in self._quotes.items():
                if wanted is not None and ticker not in wanted:
                    continue
                quote.status = "fresh" if now - quote.updated_at <= self.ttl_seconds else "stale"
                result[ticker] = quote
            return dict(result)

    def clear(self):
        with self._lock:
            self._quotes.clear()

    def ingest(self, ticker: str, price: float, source: str = "feed", updated_at: float | None = None):
        """Ingere uma cotação individual do feed upstream.

        Este é o ponto de entrada para um futuro WebSocket/tick feed próprio.
        """
        ts = time.time() if updated_at is None else float(updated_at)
        with self._lock:
            self._quotes[ticker] = Quote(ticker, float(price), source, ts)
        return self.snapshot([ticker]).get(ticker)

    def health(self) -> dict:
        snap = self.snapshot()
        fresh = sum(q.status == "fresh" for q in snap.values())
        ages = [q.age_seconds for q in snap.values()]
        return {
            "cached": len(snap),
            "fresh": fresh,
            "stale": len(snap) - fresh,
            "ttl_seconds": self.ttl_seconds,
            "max_age_seconds": round(max(ages), 2) if ages else None,
        }
