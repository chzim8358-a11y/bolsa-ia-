# BolsaIA v3 — Scanner automático

Protótipo Streamlit que monitora vários ativos da B3, calcula MM20, MM50, RSI e volume e gera um score/sinal técnico.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Observação

Os dados vêm do Yahoo Finance via yfinance e não devem ser tratados como feed profissional em tempo real. Para uso financeiro real, substitua por um provedor licenciado e implemente autenticação/gestão de risco antes de qualquer integração com ordens.
