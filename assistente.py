"""Jarvis · assistente da BolsaIA (V52).

Motor de comandos 100% local: interpreta o que o usuário digitou, falou ou sinalizou
com um gesto, consulta a última leitura do painel e responde em linguagem simples.

- Não usa IA generativa externa.
- Não envia ordens e não dá recomendação de compra ou venda.
- Para trocar por um LLM no futuro, basta substituir `processar()`: o app só depende
  do objeto `Resposta` que ela devolve.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Como o navegador costuma transcrever "Jarvis" (reconhecimento de voz erra bastante).
PALAVRAS_CHAVE = ["jarvis", "jarves", "jarvi", "jarviz"]

# Tempo que o gesto precisa ficar parado para disparar, e pausa entre disparos.
HOLD_MS = 900
COOLDOWN_MS = 3500

# Gestos reconhecidos pelo MediaPipe -> rótulo e comando.
# Comandos que começam com "@" são tratados no navegador (não vão para o Python).
GESTOS = {
    "Thumb_Up": {"rotulo": "👍 Resumo do mercado", "comando": "resumo do mercado"},
    "Victory": {"rotulo": "✌️ Abrir Scanner", "comando": "abrir scanner"},
    "Pointing_Up": {"rotulo": "☝️ Maiores scores", "comando": "maiores scores"},
    "Thumb_Down": {"rotulo": "👎 Voltar ao Início", "comando": "abrir inicio"},
    "Open_Palm": {"rotulo": "✋ Ouvir comando", "comando": "@ouvir"},
    "Closed_Fist": {"rotulo": "✊ Silenciar voz", "comando": "@silenciar"},
}

# (palavras que o usuário diz, rótulo exato da tela no app)
PAGINAS = [
    (("inicio", "home"), "🏠 Início"),
    (("scanner",), "⚡ Scanner"),
    (("analise",), "📊 Análise"),
    (("alerta", "alertas"), "🔔 Alertas"),
    (("backtest",), "🧪 Backtest"),
    (("historico",), "📈 Histórico"),
    (("config", "configuracao", "configuracoes"), "⚙️ Config"),
    (("login",), "👤 Login"),
]

AVISO = "_Leitura técnica e educacional; não é recomendação de investimento._"

_NUMEROS = {
    "um": "1", "dois": "2", "tres": "3", "quatro": "4", "cinco": "5", "seis": "6",
    "sete": "7", "oito": "8", "nove": "9", "dez": "10", "onze": "11",
}
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200d]")

_componente = None


@dataclass
class Resposta:
    texto: str                  # o que aparece na tela (markdown)
    fala: str                   # o que é lido em voz alta
    navegar: str | None = None  # rótulo da tela para abrir
    ativo: str | None = None    # ativo para pré-selecionar na Análise


# ----------------------------------------------------------------------------
# Componente Streamlit (voz + gestos rodam no navegador)
# ----------------------------------------------------------------------------
def componente():
    """Declara (uma única vez) o componente que cuida de microfone, câmera e fala."""
    global _componente
    if _componente is None:
        import streamlit.components.v1 as components

        pasta = Path(__file__).parent / "assistente_component"
        _componente = components.declare_component("jarvis_bolsaia", path=str(pasta))
    return _componente


# ----------------------------------------------------------------------------
# Texto
# ----------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """minúsculas, sem acento e sem pontuação; remove a palavra de ativação."""
    t = unicodedata.normalize("NFD", str(texto).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for p in PALAVRAS_CHAVE:
        t = re.sub(rf"\b{p}\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _tem(t: str, *palavras: str) -> bool:
    """True se alguma palavra (ou início de palavra) aparece no texto."""
    return any(re.search(rf"\b{re.escape(p)}", t) for p in palavras)


def extrair_ativos(t: str, universo) -> list[str]:
    """Acha tickers no texto normalizado: 'petr4', 'petr 4', 'petr quatro', 'b3 sa 3'."""
    lookup = {a.lower(): a for a in universo}
    tokens = [_NUMEROS.get(x, x) for x in t.split()]
    achados: list[str] = []
    for i in range(len(tokens)):
        for n in (1, 2, 3):
            if i + n > len(tokens):
                break
            cand = "".join(tokens[i:i + n])
            if cand in lookup and lookup[cand] not in achados:
                achados.append(lookup[cand])
                break
    return achados


def para_fala(texto: str) -> str:
    """Converte o texto da tela em algo que soa bem na voz sintética."""
    def reais(m):
        inteiro = m.group(1).replace(".", "")
        cents = m.group(2)
        if cents and cents != "00":
            return f"{inteiro} reais e {cents} centavos"
        return f"{inteiro} reais"

    t = re.sub(r"R\$\s*(\d+(?:\.\d{3})*)(?:,(\d{2}))?", reais, texto)
    t = t.replace("%", " por cento").replace("→", " para ").replace(" vs. ", " versus ")
    t = re.sub(r"[*_`#>]", "", t)
    t = _EMOJI.sub("", t)
    t = re.sub(r"\s*[·—]\s*", ", ", t)
    t = re.sub(r"^\s*(\d+)\.\s", r"\1, ", t, flags=re.M)
    t = re.sub(r":\s*\n+\s*", ": ", t)
    t = re.sub(r"\s*\n+\s*", ". ", t)
    return re.sub(r"\s+", " ", t).strip()


def _brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v: float) -> str:
    return f"{v:+.2f}%".replace(".", ",")


def _num(linha, coluna):
    v = linha.get(coluna)
    return None if v is None or pd.isna(v) else float(v)


def _r(texto: str, aviso: bool = False, **kw) -> Resposta:
    fala = para_fala(texto)
    if aviso:
        texto = f"{texto}\n\n{AVISO}"
    return Resposta(texto=texto, fala=fala, **kw)


# ----------------------------------------------------------------------------
# Dados do painel
# ----------------------------------------------------------------------------
def status_mercado():
    """Mesma regra do cabeçalho do app: dias úteis, 10:00 às 17:55 (Brasília)."""
    agora = pd.Timestamp.now(tz="America/Sao_Paulo")
    abre = agora.replace(hour=10, minute=0, second=0, microsecond=0)
    fecha = agora.replace(hour=17, minute=55, second=0, microsecond=0)
    return agora.weekday() < 5 and abre <= agora <= fecha, agora


def _tabela(ctx):
    snap = ctx.get("snapshot")
    if not snap:
        return None, None
    tab = snap.get("tabela")
    if tab is None or len(tab) == 0:
        return None, None
    return tab, snap.get("quando")


def _nota_tempo(quando) -> str:
    """Avisa quando a leitura está velha (o painel só atualiza nas telas com Scanner/Início)."""
    if quando is None:
        return ""
    try:
        idade = (pd.Timestamp.now(tz=getattr(quando, "tzinfo", None)) - quando).total_seconds()
        if idade > 90:
            return f" (dados das {quando.strftime('%H:%M:%S')}; abra o Início ou o Scanner para atualizar)"
    except Exception:
        pass
    return ""


def _sem_dados() -> Resposta:
    return _r("Ainda não tenho uma leitura de mercado. Abra o Início ou o Scanner e aguarde alguns segundos para o painel carregar.")


# ----------------------------------------------------------------------------
# Respostas
# ----------------------------------------------------------------------------
def _ajuda() -> Resposta:
    return _r(
        "Posso: **resumir o mercado**, **ler um ativo** (\"como está PETR4?\"), "
        "mostrar os **maiores ou menores scores**, falar da sua **watchlist** e dos **alertas**, "
        "dizer se o **mercado está aberto** e **abrir telas** (\"abrir scanner\", \"abrir análise de VALE3\"). "
        "Não faço recomendação de compra ou venda e não envio ordens."
    )


def _resumo(tab, quando) -> Resposta:
    v = tab.dropna(subset=["Score"])
    if v.empty:
        return _r("Os ativos monitorados ainda estão sem score válido.")
    media = float(v["Score"].mean())
    clima = "viés técnico positivo" if media >= 65 else "sinais mistos" if media >= 50 else "viés mais defensivo"
    compras = int(v["Sinal"].astype(str).str.startswith("COMPRA").sum())
    melhor = v.loc[v["Score"].idxmax()]
    aberto, _ = status_mercado()
    mercado = "Mercado B3 aberto." if aberto else "Mercado B3 fechado."
    txt = (
        f"{mercado} Entre {len(tab)} ativos monitorados, o score médio é {media:.0f}: {clima}. "
        f"{compras} com sinal COMPRA no modelo. Maior score: {melhor['Ativo']} ({float(melhor['Score']):.0f})."
        f"{_nota_tempo(quando)}"
    )
    return _r(txt, aviso=True)


def _ranking(tab, quando, maiores: bool, n: int = 3) -> Resposta:
    v = tab.dropna(subset=["Score"]).sort_values("Score", ascending=not maiores).head(n)
    if v.empty:
        return _r("Ainda não há scores válidos para ordenar.")
    titulo = "Maiores scores técnicos agora" if maiores else "Menores scores técnicos agora"
    linhas = []
    for i, (_, r) in enumerate(v.iterrows(), 1):
        rsi = _num(r, "RSI")
        extra = f", RSI {rsi:.0f}" if rsi is not None else ""
        linhas.append(f"{i}. **{r['Ativo']}** — score {float(r['Score']):.0f}{extra}")
    return _r(f"{titulo}{_nota_tempo(quando)}:\n" + "\n".join(linhas), aviso=True)


def _leitura(tab, ativo: str):
    linha = tab[tab["Ativo"] == ativo]
    if linha.empty:
        return None
    r = linha.iloc[0]
    cab = f"**{ativo}**"
    preco, var = _num(r, "Preço"), _num(r, "Variação")
    if preco is not None:
        cab += f" — {_brl(preco)}"
        if var is not None:
            cab += f" ({_pct(var)} vs. candle anterior)"
    partes = []
    score = _num(r, "Score")
    if score is not None:
        sem = f" {r.get('Semáforo', '')} {r.get('Leitura', '')}".rstrip()
        partes.append(f"Score {score:.0f}{sem}")
    for rotulo, col in (("RSI", "RSI"), ("ADX", "ADX")):
        v = _num(r, col)
        if v is not None:
            partes.append(f"{rotulo} {v:.0f}")
    sinal = r.get("Sinal")
    if isinstance(sinal, str) and sinal:
        partes.append(f"sinal do modelo: {sinal}")
    txt = cab + ". " + " · ".join(partes) + "." if partes else cab + "."
    por_que = r.get("Por que?")
    if isinstance(por_que, str) and por_que:
        txt += f" {por_que[0].upper()}{por_que[1:]}."
    fonte = r.get("Fonte preço")
    if isinstance(fonte, str) and fonte:
        txt += f" Fonte: {fonte}."
    return txt


def _watchlist(ctx) -> Resposta:
    lista = ctx.get("watchlist") or []
    if not lista:
        return _r("Sua watchlist está vazia. Você pode montá-la na tela de Alertas.")
    tab, quando = _tabela(ctx)
    partes = []
    for t in lista:
        score = None
        if tab is not None:
            linha = tab[tab["Ativo"] == t]
            if not linha.empty:
                score = _num(linha.iloc[0], "Score")
        partes.append(f"{t} ({score:.0f})" if score is not None else f"{t} (sem leitura agora)")
    return _r(f"Sua watchlist: {', '.join(partes)}.{_nota_tempo(quando)}")


def _alertas(ctx) -> Resposta:
    n = int(ctx.get("alertas") or 0)
    d = int(ctx.get("alertas_disparados") or 0)
    if n == 0:
        return _r("Você ainda não configurou alertas nesta sessão. Diga \"abrir alertas\" para criar um.")
    txt = f"Você tem {n} alerta{'s' if n != 1 else ''} configurado{'s' if n != 1 else ''} nesta sessão"
    txt += f" e {d} disparado{'s' if d != 1 else ''} na última checagem." if d else "; nenhum disparou na última checagem."
    return _r(txt)


# ----------------------------------------------------------------------------
# Roteador de comandos
# ----------------------------------------------------------------------------
def _pagina_pedida(t: str):
    for palavras, rotulo in PAGINAS:
        if any(re.search(rf"\b{p}\b", t) for p in palavras):
            return rotulo
    return None


def processar(entrada: str, ctx: dict) -> Resposta:
    """Interpreta um comando e devolve a resposta. `ctx` traz snapshot, universo, alertas e watchlist."""
    t = normalizar(entrada)
    universo = ctx.get("universo") or []
    ativos = extrair_ativos(t, universo)
    tab, quando = _tabela(ctx)

    if not t or t in {"oi", "ola", "e ai", "bom dia", "boa tarde", "boa noite"}:
        return _r("Pois não? Posso resumir o mercado, ler um ativo ou abrir uma tela. Diga \"ajuda\" para ver os comandos.")
    if _tem(t, "obrigad", "valeu"):
        return _r("Disponha!")
    if _tem(t, "ajuda", "comandos", "o que voce faz", "o que voce pode", "o que posso"):
        return _ajuda()

    abrir = _tem(t, "abr", "ir para", "va para", "vai para", "mostr", "leva", "navega", "analis")

    # Pedido de recomendação: explica o limite e oferece a leitura técnica.
    if _tem(t, "comprar", "vender", "devo", "vale a pena", "recomend"):
        base = "Não faço recomendação de compra ou venda, mas posso mostrar a leitura técnica."
        if ativos and tab is not None:
            leitura = _leitura(tab, ativos[0])
            if leitura:
                return _r(f"{base} {leitura}", aviso=True)
        return _r(f"{base} Diga o ativo, por exemplo \"como está PETR4?\".")

    # Abrir a Análise de um ativo específico.
    if ativos and abrir:
        a = ativos[0]
        leitura = _leitura(tab, a) if tab is not None else None
        txt = f"Abrindo a análise de {a}." + (f" {leitura}" if leitura else "")
        return _r(txt, aviso=bool(leitura), navegar="📊 Análise", ativo=a)

    # Leitura de um ou mais ativos.
    if ativos:
        if tab is None:
            return _sem_dados()
        leituras, fora = [], []
        for a in ativos[:3]:
            texto = _leitura(tab, a)
            (leituras if texto else fora).append(texto or a)
        if leituras:
            txt = "\n\n".join(leituras) + _nota_tempo(quando)
            if fora:
                txt += f"\n\n{', '.join(fora)} não está entre os ativos monitorados agora."
            return _r(txt, aviso=True)
        return _r(f"{', '.join(fora)} não está entre os ativos monitorados no Scanner agora. Abrindo a Análise para carregar sob demanda.",
                  navegar="📊 Análise", ativo=fora[0])

    if _tem(t, "aberto", "fechado", "horario") and _tem(t, "mercado", "bolsa", "b3"):
        aberto, agora = status_mercado()
        estado = "aberto" if aberto else "fechado"
        return _r(f"O mercado B3 está {estado} agora ({agora.strftime('%H:%M')}, horário de Brasília).")

    # Navegação por tela.
    pagina = _pagina_pedida(t)
    if pagina and (abrir or len(t.split()) <= 2):
        if pagina == "🔔 Alertas" and not abrir:
            return _alertas(ctx)
        return _r(f"Abrindo {pagina.split(' ', 1)[1]}.", navegar=pagina)

    if _tem(t, "watchlist", "favorit", "minha lista"):
        return _watchlist(ctx)
    if _tem(t, "alerta"):
        return _alertas(ctx)

    precisa_dados = (
        _tem(t, "resumo", "panorama", "situacao", "como esta o mercado", "mercado hoje", "mercado")
        or _tem(t, "maiores", "melhores", "top", "destaque", "mais fortes", "menores", "piores", "mais fracos", "defensiv")
    )
    if precisa_dados and tab is None:
        return _sem_dados()
    if _tem(t, "menores", "piores", "mais fracos", "defensiv"):
        return _ranking(tab, quando, maiores=False)
    if _tem(t, "maiores", "melhores", "top", "destaque", "mais fortes"):
        return _ranking(tab, quando, maiores=True)
    if _tem(t, "resumo", "panorama", "situacao", "mercado"):
        return _resumo(tab, quando)

    return _r("Não entendi esse comando. Tente \"resumo do mercado\", \"como está PETR4?\", \"maiores scores\" ou \"abrir scanner\". Diga \"ajuda\" para ver tudo.")


def texto_ajuda_markdown() -> str:
    """Conteúdo do painel 'Comandos, gestos e privacidade' da barra lateral."""
    gestos = "\n".join(f"- {g['rotulo']}" for g in GESTOS.values())
    return (
        f"**Voz:** ative em 🎙️ e diga _“{PALAVRAS_CHAVE[0].capitalize()}, como está PETR4?”_. "
        f"Dizer só “{PALAVRAS_CHAVE[0].capitalize()}” abre uma janela de 7 s para o comando.\n\n"
        "**Exemplos:** resumo do mercado · maiores scores · piores scores · como está VALE3 · "
        "abrir scanner · abrir análise de ITUB4 · minha watchlist · alertas · mercado está aberto?\n\n"
        f"**Gestos** (segure ~1 s):\n{gestos}\n\n"
        "**Privacidade:** os gestos são processados no seu navegador; a imagem da câmera não vai para o servidor. "
        "A voz usa o reconhecimento do navegador (no Chrome e no Edge, o áudio é enviado ao serviço de voz do próprio navegador). "
        "Funciona com a aba aberta, em https ou localhost.\n\n"
        "_Informativo e educacional. Não envia ordens nem recomenda compra ou venda._"
    )
