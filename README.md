# BolsaIA v6 — B3 em tempo real

Evolução da v4 para uma arquitetura preparada para **Market Data B3 em tempo real**.

## O que mudou

- Integração opcional com **BTG Solutions Data Services** para cotações e candles B3 em modo `realtime`.
- Fallback para Yahoo Finance quando a chave BTG não estiver configurada.
- Atualização do painel a cada **5 segundos**.
- Cotações em lote para reduzir chamadas.
- Histórico intraday complementar para manter MM20/MM50 utilizáveis.
- RSI, MM20, MM50, volume, score e alertas continuam na aplicação.
- Novo painel de dividendos: dividendos por ação dos últimos 12 meses e último dividendo por cota.
- Dividendos usam Yahoo Finance como referência e não são feed realtime.

A documentação oficial do BTG descreve `Quotes.get_quote(..., mode="realtime")` e `IntradayCandles.get_intraday_candles(..., delay="realtime")` para dados B3. O acesso real depende da chave/plano contratado.

## Configuração no Streamlit Cloud

1. Faça upload/commit dos arquivos desta pasta no GitHub.
2. No Streamlit Cloud, abra **Manage app → Settings → Secrets**.
3. Adicione:

```toml
BTG_API_KEY = "SUA_CHAVE_BTG"
```

> Remova o espaço em `BT G`: o valor correto deve ser a sua chave completa, sem espaços.

4. Salve e reinicie/republique o app.
5. O painel deverá mostrar `Feed BTG configurado`.

## Dependências

`requirements.txt` instala Streamlit, pandas, numpy, yfinance e o cliente oficial Python do BTG Solutions.

## Importante

Dados de mercado em tempo real da B3 são um serviço licenciado. A B3 informa que Market Data pode ser distribuído em tempo real ou com atraso e que o acesso indireto ocorre por distribuidores autorizados. Use uma chave/plano compatível com seu uso.

A BolsaIA é um protótipo educacional e **não executa ordens** nem constitui recomendação de investimento.
