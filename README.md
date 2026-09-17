# BolsaIA V44

## 🧭 Grande mudança: Painel da operação

A V44 adiciona um painel centralizado para testar cenários de uma operação de forma educacional. Ele reúne preço observado, alvo técnico, stop técnico, capital da operação, ganho bruto simulado, risco simulado e relação potencial/risco.

### V44 — novos recursos
- Quantidade de unidades configurável para simulação.
- Capital estimado da operação.
- Ganho bruto simulado caso o alvo técnico seja atingido.
- Perda simulada caso o stop técnico seja atingido.
- Relação potencial/risco.
- Percentuais de distância até alvo e stop.
- Cenários matemáticos rápidos de +1%, +3% e +5%.
- Integração com Score, Real-Time, Paper Trading e Central de Alertas.
- Avisos claros de que os cenários não são previsão nem recomendação.

## Recursos mantidos
- Scanner por categoria: Ações, FIIs / Imobiliário, ETFs e BDRs.
- Análise técnica e Score.
- Motor Real-Time local.
- Paper Trading sem envio de ordens reais.
- Watchlist e alertas de preço/Score.
- Calculadora de risco, lucro e dividendos.
- Navegação e atalhos.

## Execução

```bash
pip install -r requirements.txt
streamlit run app.py
```

> O BolsaIA é um ambiente demonstrativo/educacional. As simulações não movimentam dinheiro real e não enviam ordens para corretoras.
