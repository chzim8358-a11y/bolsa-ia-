# BolsaIA V39

V39 amplia o universo do BolsaIA para além de ações, mantendo a base funcional da V38.

## Novidades da V39

- **FIIs ampliados**: mais fundos imobiliários no universo monitorado.
- **ETFs**: BOVA11, SMAL11, IVVB11, DIVO11, GOLD11, HASH11, XINA11 e WRLD11.
- **BDRs**: AAPL34, MSFT34, GOOG34, AMZO34, NVDC34 e TSLA34.
- **Filtro por tipo de ativo**: Ação, FII, ETF e BDR.
- **Análise detalhada sob demanda** para qualquer ativo cadastrado.
- **Scanner multiclasse**: o campo Categoria agora diferencia Ação, FII, ETF e BDR.
- **Realtime mais seguro**: BTG continua reservado para ações quando configurado; demais tipos usam Yahoo Finance como fonte de cotação/candles.
- **Dashboard por categoria** para visualizar a composição do universo monitorado.
- Mantida a experiência em **modo Iniciante / Avançado**, gestão de risco, carteira simulada, dividendos e calculadora de objetivo de lucro.

## Execução

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Realtime B3

Para usar o feed BTG, configure `BTG_API_KEY` nos Secrets do Streamlit Cloud. Sem a chave, o app utiliza Yahoo Finance como fallback. A disponibilidade e latência dependem da fonte; o painel é educacional e não constitui recomendação de investimento.
