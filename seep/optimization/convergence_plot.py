"""
Plotagem de convergência do ACO — mostra se o erro está "afunilando".

Funciona com o dicionário de resultado de QUALQUER versão do ACO deste projeto
(aco.py, aco_v2.py, aco_robust.py, aco_multi*.py, aco_book.py). O gráfico tem:

  - Linha do MELHOR RMSE por iteração (o que melhora/desce).
  - Linha do melhor GLOBAL acumulado (monótona, nunca sobe).
  - Banda min–máx das formigas + média por iteração (a dispersão).
    Quando a banda ESTREITA, o algoritmo está afunilando (convergindo).

Uso:
    from convergence_plot import plot_convergencia
    res = aco.otimizar(modelo, objetivo)
    plot_convergencia(res, titulo="ACO robusto", salvar="conv.png")
"""

import numpy as np

# Backend não-interativo como fallback (ambientes sem display).
import matplotlib
try:
    import matplotlib.pyplot as plt
    _HAS_DISPLAY = True
except Exception:                       # pragma: no cover
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _HAS_DISPLAY = False


# Chaves possíveis em cada entrada do histórico (tolerante às várias versões).
_KEYS_MELHOR = ("rmse_melhor", "melhor_rmse_iteracao", "f_best", "melhor_rmse")
_KEYS_MEDIA = ("rmse_media", "media_rmse_iteracao", "f_mean")
_KEYS_PIOR = ("rmse_pior", "pior_rmse_iteracao", "f_worst")


def _primeiro(d, chaves):
    for k in chaves:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _extrair(resultado):
    """Devolve (iters, melhor, media, pior) a partir do dict de resultado."""
    hist = resultado.get("historico_iteracoes") or resultado.get("history") or []
    iters, melhor, media, pior = [], [], [], []
    for n, h in enumerate(hist, start=1):
        iters.append(h.get("iteracao", h.get("iteration", n)))
        melhor.append(_primeiro(h, _KEYS_MELHOR))
        media.append(_primeiro(h, _KEYS_MEDIA))
        pior.append(_primeiro(h, _KEYS_PIOR))
    return (np.array(iters, dtype=float),
            np.array(melhor, dtype=float),
            media, pior)


def _mascarar_penalidade(arr, limiar=1e11):
    """Penalidades (ex.: 1e12) viram NaN para não estragar a escala do gráfico."""
    a = np.array(arr, dtype=float)
    a[a >= limiar] = np.nan
    return a


def plot_convergencia(resultado, titulo="Convergência do ACO",
                      salvar=None, mostrar=True, log_y=False, ax=None):
    """
    Args:
        resultado: dict retornado por otimizar()/optimize().
        titulo:    título do gráfico.
        salvar:    caminho .png para salvar (ou None).
        mostrar:   se True e houver display, chama plt.show().
        log_y:     escala logarítmica no eixo do erro (útil p/ RMSE pequeno).
        ax:        eixo matplotlib existente (para subplots); senão cria um.

    Returns:
        o eixo (ax) usado.
    """
    iters, melhor, media, pior = _extrair(resultado)
    melhor = _mascarar_penalidade(melhor)

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 5.5))

    # Banda de dispersão das formigas (afunilamento), se disponível.
    if all(v is not None for v in pior) and len(pior) == len(iters):
        pior_m = _mascarar_penalidade(pior)
        base = melhor
        if all(v is not None for v in media) and len(media) == len(iters):
            base = _mascarar_penalidade(media)
        ax.fill_between(iters, melhor, pior_m, alpha=0.15, color="tab:blue",
                        label="dispersão formigas (melhor–pior)")
        if base is not melhor:
            ax.plot(iters, base, color="tab:gray", lw=1.0, ls=":",
                    label="média das formigas")

    # Melhor global acumulado (monótono).
    glob = np.fmin.accumulate(np.where(np.isnan(melhor), np.inf, melhor))
    glob[np.isinf(glob)] = np.nan
    ax.plot(iters, glob, color="tab:green", lw=2.2, label="melhor global (acumulado)")

    # Melhor por iteração.
    ax.plot(iters, melhor, color="tab:blue", lw=1.6, marker="o", ms=3,
            label="melhor da iteração")

    if log_y:
        ax.set_yscale("log")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("RMSE")
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)

    if salvar:
        ax.figure.savefig(salvar, dpi=120, bbox_inches="tight")
        print(f"[plot] gráfico salvo em: {salvar}")
    if mostrar and _HAS_DISPLAY:
        plt.show()

    return ax


def plot_comparacao(resultados, titulo="Comparação de convergência (melhor global)",
                    salvar=None, mostrar=True, log_y=False):
    """
    Sobrepõe o melhor global de várias execuções num único gráfico.

    Args:
        resultados: dict {nome: resultado_dict}.
    """
    _, ax = plt.subplots(figsize=(9, 5.5))
    for nome, res in resultados.items():
        iters, melhor, _, _ = _extrair(res)
        melhor = _mascarar_penalidade(melhor)
        glob = np.fmin.accumulate(np.where(np.isnan(melhor), np.inf, melhor))
        glob[np.isinf(glob)] = np.nan
        ax.plot(iters, glob, lw=2.0, marker="o", ms=3, label=nome)

    if log_y:
        ax.set_yscale("log")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("RMSE (melhor global acumulado)")
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)

    if salvar:
        ax.figure.savefig(salvar, dpi=120, bbox_inches="tight")
        print(f"[plot] gráfico salvo em: {salvar}")
    if mostrar and _HAS_DISPLAY:
        plt.show()
    return ax
