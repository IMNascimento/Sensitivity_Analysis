import numpy as np


class MultiMaterialACOv2:
    """
    ACO para calibração conjunta de múltiplos materiais — versão corrigida (v2).

    Baseado em Rao (2009), Seção 13.5 (Fig. 13.3 — grafo multilayer).

    Estrutura:
        Cada material possui duas camadas independentes:
            τ_k[mat]  : feromônio 1D para os valores de k do material.
            τ_a[mat]  : feromônio 1D para os valores de anisotropia do material.

        Uma formiga escolhe (k_i, a_j) independentemente para cada material.
        Todos os materiais são simulados juntos (run_multi) → um único RMSE global.

    Correções em relação ao aco_multi.py original:
    ────────────────────────────────────────────────
    1. Estrutura multilayer: feromônio separado por variável/material
       (antes: matriz 2D conjunta por material).

    2. Fórmula de depósito corrigida (Eq. 13.37 adaptada para RMSE > 0):
           Δτ = ζ * f_worst / f_best
       — normalizada pela razão pior/melhor da iteração (sem explosão).

    3. Todas as formigas no melhor conjunto de caminhos contribuem
       com o depósito (Eq. 13.42).

    4. Taxa de evaporação ρ ∈ [0.5, 0.8] recomendada pelo livro.
    """

    def __init__(
        self,
        material_configs,
        n_ants=4,
        zeta=2.0,
        rho=0.5,
        max_iter=50,
        tolerancia=0.01,
        penalty_rmse=1e12,
        debug=True,
    ):
        """
        Args:
            material_configs: lista de objetos de configuração de material.
                Cada objeto deve ter:
                    .material_name      (str)
                    .k_values           (list[float])
                    .anisotropia_values (list[float])
                    .material_object    (objeto do material no modelo)
                    .k_field_name       (str)
                    .anisotropy_field_name (str)
            n_ants:       número de formigas.
            zeta:         parâmetro ζ de escala (Eq. 13.37).
            rho:          taxa de evaporação ρ.
            max_iter:     número máximo de iterações.
            tolerancia:   parar se RMSE < tolerancia.
            penalty_rmse: RMSE atribuído quando a simulação falha.
            debug:        imprimir log detalhado.
        """
        self.material_configs = material_configs
        self.n_ants = n_ants
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse
        self.debug = debug

        # Feromônio multilayer: 1D por variável por material
        self.tau_k = {}
        self.tau_a = {}
        for mat in self.material_configs:
            name = mat.material_name
            self.tau_k[name] = np.ones(len(mat.k_values), dtype=float)
            self.tau_a[name] = np.ones(len(mat.anisotropia_values), dtype=float)

        self.cache = {}

    # ------------------------------------------------------------------
    # Seleção por roulette-wheel (Eq. 13.38)
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
    # Δτ normalizado (Eq. 13.37 adaptada para minimização de RMSE > 0)
    # ------------------------------------------------------------------
    def _delta_tau(self, f_best, f_worst):
        if abs(f_best) < 1e-14:
            return self.zeta
        if abs(f_worst - f_best) < 1e-14:
            return self.zeta
        return self.zeta * f_worst / f_best

    # ------------------------------------------------------------------
    # Otimização
    # ------------------------------------------------------------------
    def otimizar(self, modelo, funcao_objetivo):
        """
        Args:
            modelo:
                Objeto com método run_multi(material_params) → array.
                material_params é um dict: {mat_name: {k, anisotropia, ...}}.
            funcao_objetivo:
                Objeto com método calcular_rmse(h_modelo) → float.

        Returns:
            dict com historico_rmse, historico_iteracoes, melhor_global,
            tau_k_final, tau_a_final, cache.
        """
        historico_rmse = []
        historico_iteracoes = []
        best_global_rmse = float("inf")
        best_global_params = None

        for iteration in range(1, self.max_iter + 1):

            ant_rmse = []
            ant_choices = []   # lista de dicts {mat_name: (idx_k, idx_a)}

            # ── Step 3: cada formiga constrói caminhos para todos os materiais ─
            for ant in range(self.n_ants):
                choices = {}
                material_params = {}

                for mat in self.material_configs:
                    name = mat.material_name
                    i = self._select(self.tau_k[name])
                    j = self._select(self.tau_a[name])

                    k = mat.k_values[i]
                    a = mat.anisotropia_values[j]

                    if getattr(modelo.config, "use_anisotropy", True) is False:
                        a = 1.0
                        j = 0

                    choices[name] = (i, j)
                    material_params[name] = {
                        "material_object":     mat.material_object,
                        "k_field_name":        mat.k_field_name,
                        "anisotropy_field_name": mat.anisotropy_field_name,
                        "k":          k,
                        "anisotropia": a,
                        "idx_k":      i,
                        "idx_a":      j,
                    }

                cache_key = tuple(
                    (name, float(p["k"]), float(p["anisotropia"]))
                    for name, p in sorted(material_params.items())
                )

                try:
                    if cache_key in self.cache:
                        rmse = self.cache[cache_key]
                        source = "cache"
                    else:
                        h = modelo.run_multi(material_params)
                        rmse = funcao_objetivo.calcular_rmse(h)
                        self.cache[cache_key] = rmse
                        source = "run"
                except Exception as e:
                    rmse = self.penalty_rmse
                    source = f"erro: {e}"

                ant_rmse.append(rmse)
                ant_choices.append(choices)

                if self.debug:
                    print(f"Iter {iteration} | Formiga {ant+1} | RMSE={rmse:.6f} | [{source}]")
                    for name, p in material_params.items():
                        print(f"   {name}: k={p['k']}, a={p['anisotropia']:.4g}")

            # ── Melhor e pior da iteração ─────────────────────────────────────
            f_best = float(min(ant_rmse))
            f_worst = float(max(ant_rmse))
            best_ant_idx = int(np.argmin(ant_rmse))
            best_choices = ant_choices[best_ant_idx]

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
                "melhor_parametros_iteracao": {
                    name: {
                        "k": self.material_configs[m_idx].k_values[best_choices[name][0]],
                        "anisotropia": self.material_configs[m_idx].anisotropia_values[best_choices[name][1]],
                    }
                    for m_idx, mat in enumerate(self.material_configs)
                    for name in [mat.material_name]
                },
            })

            if f_best < best_global_rmse:
                best_global_rmse = f_best
                best_global_params = {
                    "rmse": best_global_rmse,
                    "iteration": iteration,
                    "materials": {
                        name: {
                            "k": self.material_configs[m_idx].k_values[best_choices[name][0]],
                            "anisotropia": self.material_configs[m_idx].anisotropia_values[best_choices[name][1]],
                        }
                        for m_idx, mat in enumerate(self.material_configs)
                        for name in [mat.material_name]
                    },
                }

            # ── Step 4: atualização do feromônio ─────────────────────────────
            # Evaporação (Eq. 13.43)
            for mat in self.material_configs:
                name = mat.material_name
                self.tau_k[name] *= (1.0 - self.rho)
                self.tau_a[name] *= (1.0 - self.rho)

            # Δτ normalizado (Eq. 13.37 adaptada)
            delta = self._delta_tau(f_best, f_worst)

            # Conta formigas que escolheram exatamente o mesmo conjunto de caminhos
            n_best = sum(
                1 for idx in range(self.n_ants)
                if ant_choices[idx] == best_choices and ant_rmse[idx] == f_best
            )
            total_delta = n_best * delta

            for mat in self.material_configs:
                name = mat.material_name
                i_best, j_best = best_choices[name]
                self.tau_k[name][i_best] += total_delta
                self.tau_a[name][j_best] += total_delta

            if self.debug:
                print(
                    f"  f_best={f_best:.6f}, f_worst={f_worst:.6f}, "
                    f"Δτ={delta:.4g}, n_best={n_best}, total={total_delta:.4g}"
                )
                for mat in self.material_configs:
                    name = mat.material_name
                    print(f"  τ_k[{name}]={np.round(self.tau_k[name], 4)}")
                    print(f"  τ_a[{name}]={np.round(self.tau_a[name], 4)}")
                print(f"  Melhor global até agora: {best_global_rmse:.6f}")
                print("-" * 100)

            # ── Critério de parada ────────────────────────────────────────────
            if f_best < self.tolerancia:
                if self.debug:
                    print(f"Convergiu na iteração {iteration}")
                break

        return {
            "historico_rmse": historico_rmse,
            "historico_iteracoes": historico_iteracoes,
            "melhor_global": best_global_params,
            "tau_k_final": {name: t.copy() for name, t in self.tau_k.items()},
            "tau_a_final": {name: t.copy() for name, t in self.tau_a.items()},
            "cache": dict(self.cache),
        }
