# BolsaIA V28 🚀

Inteligência de mercado para análise técnica, scanner de oportunidades e gestão de risco em ambiente educacional.

## O que mudou na V28

- 🧭 **Atalhos rápidos:** Início, Scanner, Análise, Configurações e Login.
- 👤 **Área de login demonstrativa:** estrutura de acesso por sessão, pronta para futura autenticação real.
- 📱 **Interface mais amigável para iniciantes:** textos explicativos, navegação simples e apresentação visual mais clara.
- 📈 **Universo ampliado:** mais ações B3, incluindo PETR3, ITUB3, ITSA4, BBDC3, EGIE3, TOTS3, RADL3, HYPE3, VIVT3, SBSP3, GGBR4, GOAU4, KLBN11, BRFS3 e outras.
- 🏢 **FIIs / imobiliário:** XPML11, MXRF11, HGLG11, BTLG11, KNCR11, XPLG11, TRXF11, XPIN11, VISC11, HSML11 e MALL11.
- ⚡ **Cemig:** CMIG3 e CMIG4 mantidos no universo do scanner.
- ⏱️ **Preços com origem identificada:** BTG para ações quando configurado; Yahoo Finance como fallback. O app não promete tick-by-tick quando a fonte não fornecer isso.
- 🎨 **Identidade BolsaIA:** logo integrada ao cabeçalho e à experiência visual.
- 🛡️ **Modo educacional:** nenhuma ordem real é enviada.

## Realtime

Para usar o feed BTG em ações B3, configure `BTG_API_KEY` em **Streamlit Cloud → Settings → Secrets**.

Sem a chave, o app usa Yahoo Finance como fallback. A latência e a disponibilidade dependem da fonte.

## Execução

```bash
pip install -r requirements.txt
streamlit run app.py
```

> Ferramenta educacional. Indicadores, scores, cenários, stop, alvo e carteira simulada não constituem recomendação de investimento.
