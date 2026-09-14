# BolsaIA v11 — Radar + Carteira Simulada

Aplicativo educacional em Streamlit para análise técnica de ativos B3.

## Novidades da V11
- Tudo da V10, com status do mercado B3 e horário de Brasília visíveis no painel.
- Carteira virtual: quantidade, preço médio, valor atual e P/L simulado.
- Exportação da carteira para CSV.
- Scanner enriquecido com variação do candle e ATR percentual.

## Mantido das versões anteriores
- Radar/ranking dos ativos monitorados pelo Score técnico.
- Top 3 oportunidades com Score, sinal, risco/retorno e Dividend Yield de 12 meses.
- Tabela do scanner com R/R e Yield 12m.
- Mantém candles, RSI, MACD, médias móveis, plano técnico, stop/alvo e dividendos.
- BTG continua como feed realtime opcional; Yahoo Finance permanece como fallback.

## Arquivos
- `app.py`
- `dados.py`
- `indicadores.py`
- `analisador.py`
- `dividendos.py`
- `requirements.txt`
- `README.md`

> O Score/ranking é uma ferramenta educacional de análise técnica e não garante movimentos futuros nem constitui recomendação de investimento.

- Pacote limpo: a versão distribuída não inclui a pasta `__pycache__` nem arquivos `.pyc`.
- Atualização automática do painel a cada 5 segundos quando suportada pela versão do Streamlit.
