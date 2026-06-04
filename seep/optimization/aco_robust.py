import numpy as np


class ACORobust:
    """
    ACO robusto para calibração de UM material (k e anisotropia).

    Mesma teoria do `aco_multi_robust.py` (Rao 2009, Seção 13.5 + MMAS):
      - Feromônio multilayer 1D independente por variável (τ_k, τ_a).
      - Probabilidade p_ij ∝ τ_ij^α (Eq. 13.38).
      - Evaporação em todos os arcos (Eq. 13.34).
      - Depósito limitado no melhor caminho (Eq. 13.37 adaptada para RMSE>0).
      - Max-Min Ant System: τ preso em [τ_min, τ_max] → não trava em ótimo
        local (cura da convergência prematura).
      - Reforço elitista do melhor global.

    Esta classe também serve de implementação de referência validada contra
    o Exemplo 13.5 do livro (ver bloco __main__ ao final).
    """

    def __init__(
        self,
        k_values,
        anisotropia_values,
        n_ants=15,
        alpha=1.0,
        zeta=2.0,
        rho=0.2,
        tau_min=0.05,
        tau_max=5.0,
        ratio_cap=5.0,
        elitist=True,
        max_iter=80,
        tolerancia=0.01,
        penalty_rmse=1e12,
        minimize=True,
        debug=True,
    ):
        self.k_values = list(k_values)
        self.anisotropia_values = list(anisotropia_values)
        self.n_ants = n_ants
        self.alpha = alpha
        self.zeta = zeta
        self.rho = rho
        self.tau_min = tau_min
        self.tau_max = tau_max
        self.ratio_cap = ratio_cap
        self.elitist = elitist
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse
        self.minimize = minimize
        self.debug = debug

        # MMAS: inicia em τ_max.
        self.tau_k = np.full(len(self.k_values), tau_max, dtype=float)
        self.tau_a = np.full(len(self.anisotropia_values), tau_max, dtype=float)

        self.cache = {}

    def _select(self, tau):
        w = tau ** self.alpha
        probs = w / w.sum()
        cumprobs = np.cumsum(probs)
        r = np.random.uniform(0.0, 1.0)
        for j, cp in enumerate(cumprobs):
            if r <= cp:
                return j
        return len(tau) - 1

    def _clip(self):
        np.clip(self.tau_k, self.tau_min, self.tau_max, out=self.tau_k)
        np.clip(self.tau_a, self.tau_min, self.tau_max, out=self.tau_a)

    def otimizar(self, modelo, funcao_objetivo):
        """
        modelo:          objeto com run(k, anisotropia) → array (n,3) e
                         config.use_anisotropy (opcional).
        funcao_objetivo: objeto com calcular_rmse(h_modelo) → float.
        """
        historico_rmse = []
        historico_iteracoes = []
        best_global_rmse = float("inf")
        best_global = None
        best_global_ij = None
        n_falhas_total = 0
        convergiu = False

        for iteration in range(1, self.max_iter + 1):
            ant_rmse = []
            ant_i = []
            ant_j = []
            ant_falhou = []

            for ant in range(self.n_ants):
                i = self._select(self.tau_k)
                j = self._select(self.tau_a)

                k = self.k_values[i]
                a = self.anisotropia_values[j]

                if getattr(modelo.config, "use_anisotropy", True) is False:
                    a = 1.0
                    j = 0

                cache_key = (float(k), float(a))
                falhou = False
                try:
                    if cache_key in self.cache:
                        rmse = self.cache[cache_key]
                        source = "cache"
                    else:
                        h = modelo.run(k, a)
                        rmse = funcao_objetivo.calcular_rmse(h)
                        self.cache[cache_key] = rmse
                        source = "run"
                except Exception as e:
                    rmse = self.penalty_rmse
                    falhou = True
                    n_falhas_total += 1
                    source = f"ERRO: {e}"

                ant_rmse.append(rmse)
                ant_i.append(i)
                ant_j.append(j)
                ant_falhou.append(falhou)

                if self.debug:
                    print(f"Iter {iteration} | Formiga {ant+1}: k={k}, a={a:.4g}, "
                          f"RMSE={rmse:.6g} [{source}]")

            best_ant = int(np.argmin(ant_rmse))
            f_best = float(ant_rmse[best_ant])
            best_i, best_j = ant_i[best_ant], ant_j[best_ant]

            validos = [r for r, fl in zip(ant_rmse, ant_falhou) if not fl]
            f_worst = float(max(validos)) if validos else f_best
            f_media = float(np.mean(validos)) if validos else f_best
            n_falhas_iter = sum(ant_falhou)

            historico_rmse.append(f_best)
            historico_iteracoes.append({
                "iteracao": iteration,
                "melhor_rmse_iteracao": f_best,
                "rmse_melhor": f_best,
                "rmse_media": f_media,
                "rmse_pior": f_worst,
                "melhor_k_iteracao": self.k_values[best_i],
                "melhor_anisotropia_iteracao": self.anisotropia_values[best_j],
                "n_falhas_iteracao": n_falhas_iter,
            })

            if f_best < best_global_rmse:
                best_global_rmse = f_best
                best_global_ij = (best_i, best_j)
                best_global = {
                    "k": self.k_values[best_i],
                    "anisotropia": self.anisotropia_values[best_j],
                    "rmse": best_global_rmse,
                    "iteration": iteration,
                }

            # Evaporação.
            self.tau_k *= (1.0 - self.rho)
            self.tau_a *= (1.0 - self.rho)

            # Depósito limitado (só se o melhor da iteração for válido).
            if not ant_falhou[best_ant]:
                if f_best > 1e-14 and f_worst > f_best:
                    razao = min(f_worst / f_best, self.ratio_cap)
                else:
                    razao = 1.0
                delta = self.zeta * razao

                self.tau_k[best_i] += delta
                self.tau_a[best_j] += delta

                if self.elitist and best_global_ij is not None:
                    gi, gj = best_global_ij
                    self.tau_k[gi] += delta
                    self.tau_a[gj] += delta
            else:
                delta = 0.0

            self._clip()

            if self.debug:
                print(f"  f_best={f_best:.6g}, f_worst={f_worst:.6g}, Δτ={delta:.4g}, "
                      f"falhas={n_falhas_iter}/{self.n_ants}")
                print(f"  τ_k={np.round(self.tau_k, 3)}")
                print(f"  τ_a={np.round(self.tau_a, 3)}")
                print(f"  Melhor global: {best_global_rmse:.6g}")
                print("-" * 80)

            if f_best < self.tolerancia:
                if self.debug:
                    print(f"Convergiu por tolerância na iteração {iteration}")
                convergiu = True
                break

            if all(ant_i[k] == best_i and ant_j[k] == best_j for k in range(self.n_ants)):
                if self.debug:
                    print(f"Convergiu (todas as formigas no mesmo caminho) na iter {iteration}")
                convergiu = True
                break

        return {
            "historico_rmse": historico_rmse,
            "historico_iteracoes": historico_iteracoes,
            "melhor_global": best_global,
            "tau_k_final": self.tau_k.copy(),
            "tau_a_final": self.tau_a.copy(),
            "cache": dict(self.cache),
            "n_falhas": n_falhas_total,
            "convergiu": convergiu,
        }


# ---------------------------------------------------------------------------
# Validação contra o Exemplo 13.5 do livro: min f(x)=x²−2x−11, x∈{0,0.5,...,3}
# Resposta esperada: x*=1.0, f*=−12.0.
#
# Aqui usamos um "modelo" e uma "função objetivo" sintéticos: tratamos x como
# k (anisotropia fixa) e o RMSE = f(x) − min(f) ≥ 0 (deslocado para positivo,
# como ocorre com RMSE real). O ótimo continua em x=1.0.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    x_vals = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    f_real = lambda x: x ** 2 - 2 * x - 11
    f_min = min(f_real(x) for x in x_vals)  # = -12.0

    class _MockConfig:
        use_anisotropy = False

    class _MockModel:
        config = _MockConfig()
        def run(self, k, a):
            # devolve [x, y, valor] num único nó; aqui "valor" = f(k) deslocado
            return np.array([[0.0, 0.0, f_real(k) - f_min]], dtype=float)

    class _MockObjective:
        def calcular_rmse(self, h):
            return float(h[0, 2])  # já é o erro positivo

    acertos = 0
    N = 200
    for seed in range(N):
        np.random.seed(seed)
        aco = ACORobust(
            k_values=x_vals,
            anisotropia_values=[1.0],
            n_ants=8,
            alpha=1.0,
            rho=0.3,
            tau_min=0.05,
            tau_max=5.0,
            max_iter=40,
            tolerancia=-1.0,   # desliga parada por tolerância p/ medir convergência
            debug=False,
        )
        r = aco.otimizar(_MockModel(), _MockObjective())
        if abs(r["melhor_global"]["k"] - 1.0) < 1e-9:
            acertos += 1

    print(f"ACORobust no Exemplo 13.5: acerto do ótimo global x=1.0 em "
          f"{acertos}/{N} = {100*acertos/N:.1f}% das seeds")
    print("(comparar com ~63% do algoritmo puro do livro em aco_book.py)")
