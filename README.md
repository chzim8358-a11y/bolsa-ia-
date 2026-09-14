# BolsaIA V38

V38 mantém a base funcional da V37 e adiciona uma Central de confiança dos dados, deixando mais claro para o usuário:

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
