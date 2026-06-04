"""
Auditoria / log de DEBUG de uma execução do ACO multi-material.

Foco: registrar PARÂMETROS usados + RESULTADOS, para depurar depois.

Gera dois arquivos:
  1. <caminho>.md  — relatório legível com:
        - hiperparâmetros usados (lidos do próprio objeto ACO);
        - métrica de erro;
        - resumo da execução (convergiu, falhas, nº de avaliações);
        - melhor solução completa (parâmetros de cada material + erro);
        - tabela de convergência por iteração (melhor / média / pior);
        - as melhores N combinações testadas (ranking por erro).
  2. <caminho>_avaliacoes.csv — TODAS as combinações avaliadas (do cache),
        uma linha por combinação: k e anisotropia de cada material + erro.
        Abra no Excel/LibreOffice para filtrar e ordenar à vontade.

Uso:
    from audit import gerar_auditoria
    gerar_auditoria(aco, resultado, funcao_objetivo, "outputs/auditoria.md")
"""

import csv
import os
from datetime import datetime

# Hiperparâmetros que tentamos ler do objeto ACO (nem todos existem em toda versão).
_HIPERPARAMS = [
    "n_ants", "alpha", "zeta", "rho",
    "tau_min", "tau_max", "ratio_cap", "elitist",
    "max_iter", "tolerancia", "penalty_rmse",
]


def _linhas_avaliacoes(resultado):
    """
    Transforma o cache {chave: erro} em linhas tabulares.

    A chave do cache é uma tupla de triplas (nome_material, k, anisotropia),
    ordenada por nome. Devolve (colunas, linhas) prontas para CSV/Markdown,
    ordenadas do menor para o maior erro.
    """
    cache = resultado.get("cache", {})
    linhas = []
    nomes = []
    for chave, erro in cache.items():
        linha = {}
        for (nome, k, a) in chave:
            if nome not in nomes:
                nomes.append(nome)
            linha[f"{nome} / k"] = k
            linha[f"{nome} / anis"] = a
        linha["erro"] = erro
        linhas.append(linha)

    nomes = sorted(nomes)
    colunas = []
    for nome in nomes:
        colunas.append(f"{nome} / k")
        colunas.append(f"{nome} / anis")
    colunas.append("erro")

    linhas.sort(key=lambda r: r.get("erro", float("inf")))
    return colunas, linhas


def gerar_auditoria(aco, resultado, funcao_objetivo=None, caminho=None,
                    titulo="Auditoria da calibração ACO", top_n=30):
    """
    Args:
        aco:             objeto ACO já executado (para ler hiperparâmetros).
        resultado:       dict devolvido por aco.otimizar(...).
        funcao_objetivo: objeto da função objetivo (para ler a métrica). Opcional.
        caminho:         caminho do arquivo .md. O CSV é salvo ao lado, com
                         sufixo "_avaliacoes.csv". Se None, só retorna o texto.
        titulo:          título do relatório.
        top_n:           quantas combinações (melhores) listar no .md.

    Returns:
        str: o relatório em Markdown.
    """
    metric = getattr(funcao_objetivo, "metric", None)
    rotulo_erro = metric.upper() if metric else "erro"

    L = []
    L.append(f"# {titulo}")
    L.append("")
    L.append(f"- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L.append(f"- Classe ACO: `{type(aco).__name__}`")
    if metric:
        L.append(f"- Métrica de erro: **{metric.upper()}**")
    L.append("")

    # ── 1) Hiperparâmetros ───────────────────────────────────────────────────
    L.append("## 1. Hiperparâmetros usados")
    L.append("")
    L.append("| Parâmetro | Valor |")
    L.append("|---|---|")
    for nome in _HIPERPARAMS:
        if hasattr(aco, nome):
            L.append(f"| `{nome}` | {getattr(aco, nome)} |")
    L.append("")

    # ── 2) Resumo da execução ────────────────────────────────────────────────
    best = resultado.get("melhor_global") or {}
    n_iter = len(resultado.get("historico_iteracoes", []))
    L.append("## 2. Resumo da execução")
    L.append("")
    L.append(f"- Iterações executadas: **{n_iter}**")
    L.append(f"- Convergiu (flag): **{resultado.get('convergiu', 'n/a')}**")
    L.append(f"- Falhas de simulação: **{resultado.get('n_falhas', 'n/a')}**")
    L.append(f"- Avaliações únicas (cache): **{len(resultado.get('cache', {}))}**")
    L.append(f"- Melhor {rotulo_erro}: **{best.get('rmse')}** "
             f"(encontrado na iteração **{best.get('iteration')}** de {n_iter})")
    L.append("")

    # ── 3) Melhor solução completa ───────────────────────────────────────────
    L.append("## 3. Melhor solução (parâmetros por material)")
    L.append("")
    mats = best.get("materials", {})
    if mats:
        L.append("| Material | k | anisotropia |")
        L.append("|---|---|---|")
        for nome, p in mats.items():
            L.append(f"| {nome} | {p.get('k')} | {p.get('anisotropia')} |")
    else:
        L.append("> (sem melhor solução registrada)")
    L.append("")

    # ── 4) Tabela de convergência por iteração ───────────────────────────────
    hist = resultado.get("historico_iteracoes", [])
    if hist:
        L.append("## 4. Convergência por iteração")
        L.append("")
        L.append(f"| Iter | Melhor ({rotulo_erro}) | Média | Pior | Falhas |")
        L.append("|---:|---:|---:|---:|---:|")
        for h in hist:
            it = h.get("iteracao", "")
            me = h.get("rmse_melhor", h.get("melhor_rmse_iteracao", ""))
            md = h.get("rmse_media", "")
            pi = h.get("rmse_pior", "")
            fa = h.get("n_falhas_iteracao", "")

            def fmt(x):
                return f"{x:.6g}" if isinstance(x, (int, float)) else x
            L.append(f"| {it} | {fmt(me)} | {fmt(md)} | {fmt(pi)} | {fa} |")
        L.append("")

    # ── 5) Combinações testadas (ranking por erro) ───────────────────────────
    colunas, linhas = _linhas_avaliacoes(resultado)
    if linhas:
        L.append(f"## 5. Melhores {min(top_n, len(linhas))} combinações testadas "
                 f"(de {len(linhas)} no total)")
        L.append("")
        L.append("| # | " + " | ".join(colunas) + " |")
        L.append("|---:|" + "|".join(["---"] * len(colunas)) + "|")
        for rank, r in enumerate(linhas[:top_n], start=1):
            celulas = []
            for c in colunas:
                v = r.get(c, "")
                celulas.append(f"{v:.6g}" if isinstance(v, (int, float)) else str(v))
            L.append(f"| {rank} | " + " | ".join(celulas) + " |")
        L.append("")
        L.append("> Lista COMPLETA das avaliações no CSV ao lado "
                 "(`*_avaliacoes.csv`), para filtrar/ordenar à vontade.")
        L.append("")

    texto = "\n".join(L)

    # ── Salvamento (.md + _avaliacoes.csv) ───────────────────────────────────
    if caminho:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"[auditoria] relatório salvo em: {caminho}")

        if linhas:
            base, _ = os.path.splitext(caminho)
            csv_path = base + "_avaliacoes.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=colunas)
                writer.writeheader()
                writer.writerows(linhas)
            print(f"[auditoria] todas as avaliações salvas em: {csv_path}")

    return texto
