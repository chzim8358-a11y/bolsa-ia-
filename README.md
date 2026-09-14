# BolsaIA v15 — Radar + Gestão de Risco

Aplicativo educacional em Streamlit para análise técnica, scanner de oportunidades, acompanhamento de carteira simulada e dimensionamento hipotético de posição por risco.

## Novidades da V15
- Indicador de **qualidade/idade dos candles** no scanner (fresco, recente ou atrasado).
- Coluna de idade do dado em minutos para ajudar a identificar feed desatualizado.
- **Exportação completa do scanner em CSV**, além dos alertas e da carteira.
- Carteira simulada agora mostra **stop, alvo, distância até os níveis e status** (acompanhamento, stop ou alvo atingido).
- Mantidos o ciclo automático de 5 s, botão Atualizar agora, BTG realtime quando configurado e Yahoo como fallback.
- Mantidos Score técnico, ADX + DI+/DI-, MM200, RSI Wilder, candles, dividendos, radar, histórico de alertas e gestão de risco.

## Importante
- O BTG continua sendo o feed principal quando `BTG_API_KEY` está configurada.
- Yahoo Finance continua como fallback.
- O aplicativo não envia ordens reais.
- Score, stop, alvo, quantidade e indicadores são cálculos educacionais/hipotéticos e não garantem resultados.
- A carteira e o histórico continuam sendo locais à sessão do Streamlit.
- Dados de mercado podem sofrer atraso, indisponibilidade, diferenças de ajuste ou falhas de conexão.
