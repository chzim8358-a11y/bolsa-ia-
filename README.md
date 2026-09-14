# BolsaIA V19 — Dashboard Comercial

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

V16 — melhorias
- Alertas com detecção de entrada no limiar e cooldown para reduzir repetição.
- Delta de Score entre ciclos para mostrar aceleração/desaceleração do sinal.
- Limite de risco agregado da carteira simulada.
- Exportação de snapshot completo do scanner.
- Indicador de qualidade/idade dos dados mais explícito.
- Correção de normalização de cotações para respostas de uma única linha.


## V17 — apresentação profissional
- Identidade visual e cabeçalho de produto.
- Dashboard mais limpo para demonstrações.
- Seções e métricas com hierarquia visual.
- Preparação da interface para futuros clientes.
- Mantidas as funções técnicas, radar, risco, dividendos, carteira simulada e exportações.
- Nenhuma ordem real é enviada.


## V18 — dashboard comercial
- Visão executiva com KPIs para leitura rápida.
- Radar visual com barra de força do Score e sinal destacado.
- Explicação resumida do motivo de cada sinal na análise detalhada.
- Identidade de produto preparada para demonstrações e futuros clientes.
- Exportações atualizadas para a versão V18.
- Mantida a separação entre simulação educacional e ordens reais.


## V19 — correção visual e experiência
- Correção de contraste para evitar textos e métricas praticamente invisíveis em tema claro.
- Tema Streamlit definido explicitamente para manter fundo, texto e componentes consistentes.
- Responsividade melhorada para telas de celular.
- Cabeçalho, exportações e identificação da versão atualizados para V19.
- Mantidas as funções técnicas e educacionais existentes.
