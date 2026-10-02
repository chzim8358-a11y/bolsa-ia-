# BolsaIA V52

## Grande mudança: Jarvis, o assistente da BolsaIA

A V52 adiciona o **Jarvis**, um assistente por voz, gestos e texto que fica na barra lateral
e continua ativo em todas as telas (a aba precisa ficar aberta):

- **Voz:** ative em 🎙️ e diga "Jarvis, como está PETR4?". Só "Jarvis" abre uma janela de 7 s para o comando.
- **Gestos:** ative em ✋ e segure o gesto por ~1 s (👍 resumo, ✌️ Scanner, ☝️ maiores scores, 👎 Início, ✋ ouvir, ✊ silenciar).
- **Texto:** campo na barra lateral, com as mesmas capacidades.
- Responde com a última leitura do painel: resumo do mercado, leitura por ativo, maiores/menores scores, watchlist, alertas e horário do mercado; abre telas por comando.
- Motor 100% local (`assistente.py`): sem IA generativa externa, sem envio de ordens e sem recomendação de compra ou venda.
- Voz e câmera exigem https ou localhost. Os gestos são processados no navegador; a voz usa o reconhecimento do próprio navegador (Chrome, Edge ou Safari).

Arquivos novos: `assistente.py` e a pasta `assistente_component/`. Nenhuma dependência nova no `requirements.txt`.

## V51: Central de Inteligência

A V51 adicionou uma camada explicável sobre os dados técnicos já calculados pelo app:

- leitura individual por ativo;
- Score, RSI e ADX em destaque;
- pontos observados e pontos de atenção;
- resumo descritivo com fonte e status do dado;
- sem IA generativa externa e sem envio de ordens;
- mantém Radar 360°, Comparador Multiativo, Mapa por setor, Realtime Hub, Scanner, Análise, Alertas, Backtest e Paper Trading.

A Central de Inteligência é informativa e educacional; não determina compra, venda ou retorno futuro.
