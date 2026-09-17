# BolsaIA V41

## Grande mudança: BolsaIA Real-Time Engine 📡⚡

A V41 introduz um motor local de cotações em memória. Ele recebe preços reais de um provedor configurado (BTG quando disponível, Yahoo como fallback), registra o horário da atualização e entrega um snapshot reutilizável ao app. Isso prepara a arquitetura para atualizações incrementais e futuras conexões WebSocket.

### Novos recursos
- Cache de cotações com TTL e status `fresh/stale`
- Registro de fonte e horário da última atualização
- Health check do motor
- Atualização incremental sem depender de recarregar toda a interface
- Mantidos Scanner, análise, ações, FIIs, ETFs, BDRs, risco, carteira, dividendos e navegação existentes

> O motor não cria preços. Ele apenas organiza e distribui dados recebidos de uma fonte real.
# BolsaIA V39

V39 mantém a base funcional da V37 e adiciona uma Central de confiança dos dados, deixando mais claro para o usuário:

- qual fonte está sendo usada;
- se o feed BTG realtime está configurado;
- quando o ciclo do painel foi executado;
- que o Yahoo Finance é fallback e pode ter atraso;
- que nenhum dado ou sinal representa garantia de retorno.

## Execução

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Realtime B3

Para usar o feed BTG, configure `BTG_API_KEY` nos Secrets do Streamlit Cloud. Sem a chave, o app utiliza Yahoo Finance como fallback.


## V39 — expansão do universo
- Scanner por categoria: Ações, FIIs / Imobiliário, ETFs e BDRs.
- Novo universo de ETFs e BDRs para análise sob demanda.
- Filtros por categoria mantidos junto aos setores.
- Análise e cotação seguem a arquitetura existente; BTG permanece voltado às ações B3 quando configurado.
- Interface preparada para evolução das categorias sem perder a navegação da V37/V38.


## V43 — Paper Trading
- Ambiente de compra e venda **simulada** com R$ 100.000 de caixa inicial.
- Posições, preço médio, patrimônio, P/L e histórico de ordens.
- Nenhuma ordem é enviada a corretoras e nenhum dinheiro real é movimentado.
- Mantém o motor Real-Time local da V41 e o universo de ações, FIIs, ETFs e BDRs.


## V43 — Central de Alertas
- Grande mudança: Watchlist e alertas locais por preço ou Score.
- Alertas são educacionais, locais à sessão e não enviam ordens reais.
- Mantém Paper Trading V42 e Motor Real-Time V41.
