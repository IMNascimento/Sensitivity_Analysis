import numpy as np


class ACOv2:
    """
    ACO para calibração de UM material — versão corrigida (v2).

    Diferenças em relação ao aco.py original:
    1. Estrutura multilayer (livro Fig. 13.3):
       - τ_k[i]  : feromônio 1D para escolha do i-ésimo valor de k.
       - τ_a[j]  : feromônio 1D para escolha do j-ésimo valor de anisotropia.
       - Cada variável tem sua própria distribuição; as escolhas são independentes.

    2. Fórmula de depósito corrigida (Eq. 13.37 adaptada para RMSE > 0):
       Δτ = ζ * f_worst / f_best
       — normalizada pela razão pior/melhor da iteração corrente.
       — quando f_best << f_worst, o depósito é proporcional à superioridade.

    3. Todas as formigas no melhor caminho contribuem (livro Eq. 13.42):
       total_Δτ = n_melhores_formigas × Δτ

    4. Taxa de evaporação recomendada pelo livro: ρ ∈ [0.5, 0.8].
    """

    def __init__(
        self,
        k_values,
        anisotropia_values,
        n_ants=4,
        zeta=2.0,
        rho=0.5,
        max_iter=50,
        tolerancia=0.01,
        penalty_rmse=1e12,
        debug=True,
    ):
        self.k_values = list(k_values)
        self.anisotropia_values = list(anisotropia_values)
        self.n_ants = n_ants
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse
        self.debug = debug

        # Feromônio independente por variável (multilayer)
        self.tau_k = np.ones(len(self.k_values), dtype=float)
        self.tau_a = np.ones(len(self.anisotropia_values), dtype=float)

        self.cache = {}

    # ------------------------------------------------------------------
    # Seleção por roulette-wheel cumulativa (Eq. 13.38)
    # ------------------------------------------------------------------
    def _select(self, tau):
        probs = tau / tau.sum()
        cumprobs = np.cumsum(probs)
        r = np.random.uniform(0.0, 1.0)
        for j, cp in enumerate(cumprobs):
            if r <= cp:
                return j
        return len(tau) - 1

    # ------------------------------------------------------------------
    # Cálculo do Δτ (Eq. 13.37 adaptada para minimização de RMSE > 0)
    # ------------------------------------------------------------------
    def _delta_tau(self, f_best, f_worst):
        if abs(f_best) < 1e-14:
            return self.zeta
        if abs(f_worst - f_best) < 1e-14:
            return self.zeta
        # Para RMSE positivo: ratio invertida pois f_best < f_worst
        return self.zeta * f_worst / f_best

    # ------------------------------------------------------------------
    # Otimização
    # ------------------------------------------------------------------
    def otimizar(self, modelo, funcao_objetivo):
        """
        Args:
            modelo:           objeto com método run(k, anisotropia) → array
                              e atributo config.use_anisotropy (opcional).
            funcao_objetivo:  objeto com método calcular_rmse(h_modelo) → float.

        Returns:
            dict com historico_rmse, historico_iteracoes, melhor_global,
            tau_k_final, tau_a_final, cache.
        """
        historico_rmse = []
        historico_iteracoes = []
        best_global_rmse = float("inf")
        best_global_params = None

        for iteration in range(1, self.max_iter + 1):

            # ── Step 3: cada formiga escolhe (k, anisotropia) ────────────────
            ant_rmse = []
            ant_i = []
            ant_j = []

            for ant in range(self.n_ants):
                i = self._select(self.tau_k)
                j = self._select(self.tau_a)

                k = self.k_values[i]
                a = self.anisotropia_values[j]

                if getattr(modelo.config, "use_anisotropy", True) is False:
                    a = 1.0
                    j = 0  # ignora índice real de anisotropia

                cache_key = (float(k), float(a))

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
                    source = f"erro: {e}"

                ant_rmse.append(rmse)
                ant_i.append(i)
                ant_j.append(j)

                if self.debug:
                    print(
                        f"Iter {iteration} | Formiga {ant+1}: "
                        f"k={k}, a={a:.4g}, RMSE={rmse:.6f}, [{source}]"
                    )

            # ── Melhor e pior da iteração ─────────────────────────────────────
            f_best = float(min(ant_rmse))
            f_worst = float(max(ant_rmse))
            best_ant = int(np.argmin(ant_rmse))
            best_i_iter = ant_i[best_ant]
            best_j_iter = ant_j[best_ant]
            best_k_iter = self.k_values[best_i_iter]
            best_a_iter = self.anisotropia_values[best_j_iter]

            _validos = [r for r in ant_rmse if r < self.penalty_rmse]
            _f_pior = float(max(_validos)) if _validos else f_best
            _f_media = float(np.mean(_validos)) if _validos else f_best

            historico_rmse.append(f_best)
            historico_iteracoes.append({
                "iteracao": iteration,
                "melhor_rmse_iteracao": f_best,
                "rmse_melhor": f_best,
                "rmse_media": _f_media,
                "rmse_pior": _f_pior,
                "melhor_k_iteracao": best_k_iter,
                "melhor_anisotropia_iteracao": best_a_iter,
            })

            if f_best < best_global_rmse:
                best_global_rmse = f_best
                best_global_params = {
                    "k": best_k_iter,
                    "anisotropia": best_a_iter,
                    "rmse": best_global_rmse,
                    "iteration": iteration,
                }

            # ── Step 4: atualização do feromônio ─────────────────────────────
            # Evaporação (Eq. 13.43)
            self.tau_k *= (1.0 - self.rho)
            self.tau_a *= (1.0 - self.rho)

            # Δτ normalizado (Eq. 13.37 adaptada)
            delta = self._delta_tau(f_best, f_worst)

            # Conta todas as formigas no melhor caminho (Eq. 13.42)
            n_best = sum(
                1 for idx in range(self.n_ants)
                if ant_i[idx] == best_i_iter
                and ant_j[idx] == best_j_iter
                and ant_rmse[idx] == f_best
            )
            total_delta = n_best * delta

            self.tau_k[best_i_iter] += total_delta
            self.tau_a[best_j_iter] += total_delta

            if self.debug:
                print(
                    f"  f_best={f_best:.6f}, f_worst={f_worst:.6f}, "
                    f"Δτ={delta:.4g}, n_best={n_best}, total={total_delta:.4g}"
                )
                print(f"  τ_k={np.round(self.tau_k, 4)}")
                print(f"  τ_a={np.round(self.tau_a, 4)}")
                print(f"  Melhor global até agora: {best_global_rmse:.6f}")
                print("-" * 80)

            # ── Critério de parada ────────────────────────────────────────────
            if f_best < self.tolerancia:
                if self.debug:
                    print(f"Convergiu na iteração {iteration}")
                break

        return {
            "historico_rmse": historico_rmse,
            "historico_iteracoes": historico_iteracoes,
            "melhor_global": best_global_params,
            "tau_k_final": self.tau_k.copy(),
            "tau_a_final": self.tau_a.copy(),
            "cache": dict(self.cache),
        }
