# BolsaIA v2 — dados de mercado

Painel experimental em Streamlit para acompanhar ações da B3 com dados recentes, indicadores técnicos e atualização automática.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## O que mudou

- Conexão com dados recentes via `yfinance`.
- Suporte a PETR4, VALE3, ITUB4, BBAS3 e BBDC4.
- Candles de 1m, 5m, 15m, 30m e 1h.
- Atualização automática aproximadamente a cada 25 segundos.
- Cache curto para evitar consultas excessivas.
- MM20, MM50, RSI 14 e média de volume continuam sendo usados pelo analisador.
- `dados_demo()` foi mantido para testes offline.

## Importante sobre "tempo real"

Esta versão é um protótipo de monitoramento e **não garante cotação em tempo real nem execução de ordens**. O Yahoo Finance pode fornecer dados atrasados, ter limitações e indisponibilidade.

Para transformar o projeto em uma plataforma profissional, o próximo passo é conectar um provedor de market data autorizado/licenciado e, separadamente, implementar autenticação e integração com uma corretora caso sejam necessárias ordens.
