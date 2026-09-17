# BolsaIA V44

## V44 — Realtime Hub + Painel da Operação

Esta versão reúne as duas frentes planejadas para a V44:

- Motor Realtime Hub local com cache, timestamps e controle de idade dos dados.
- Integração com feed upstream configurado (BTG quando disponível; Yahoo como fallback).
- Painel da operação: capital, alvo, stop, risco/retorno, quantidade e cenários.
- Calculadora de objetivo de lucro e quantidade necessária.
- Paper Trading educacional.
- Central de Alertas e Watchlist.
- Scanner, análise técnica, indicadores, dividendos e filtros de categorias.

### Importante
O Hub local não cria preços. Ele distribui os dados recebidos de uma fonte de mercado.
Google pode ser usado como referência de conferência, mas não deve ser tratado como feed de ingestão.
Para tick-by-tick real, conecte um feed licenciado/WebSocket.

Nenhuma ordem real é enviada.
