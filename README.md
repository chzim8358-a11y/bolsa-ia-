# BolsaIA v14 — Radar + Gestão de Risco

Aplicativo educacional em Streamlit para análise técnica, acompanhamento de carteira simulada e dimensionamento hipotético de posição por risco.

## Novidades da V14
- Scanner com atualização automática a cada 5 segundos quando suportado pelo Streamlit.
- Botão **Atualizar agora** para forçar nova coleta.
- Cache curto de 4 segundos para reduzir chamadas repetidas ao feed.
- Período do Yahoo ajustado automaticamente conforme o intervalo, evitando falta de candles para MM20/MM50 em 1h.
- RSI com suavização de Wilder.
- MM200 opcional para contexto de tendência em históricos longos.
- ADX14 + DI+/DI- para identificar força/direção da tendência.
- Histórico em sessão das mudanças de sinal (ex.: AGUARDAR → COMPRA).
- Horário da última atualização exibido no scanner.
- Gestão de risco, stop, alvo, R/R, ATR, candles, dividendos e carteira simulada mantidos.

## Importante
- O BTG continua sendo o feed principal quando `BTG_API_KEY` está configurada.
- Yahoo Finance continua como fallback.
- O aplicativo não envia ordens reais.
- Score, stop, alvo, quantidade e indicadores são cálculos educacionais/hipotéticos e não garantem resultados.
- Dados de mercado podem sofrer atraso, indisponibilidade, diferenças de ajuste ou falhas de conexão.
