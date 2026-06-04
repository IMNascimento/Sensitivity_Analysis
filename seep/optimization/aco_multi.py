import numpy as np


class MultiMaterialACO:
    """
    ACO para calibração conjunta de múltiplos materiais.

    Cada formiga escolhe uma combinação de parâmetros para todos os materiais.
    Depois o modelo executa uma única simulação conjunta e a função objetivo
    calcula um único RMSE global.
    """

    def __init__(
        self,
        material_configs,
        n_ants=10,
        alpha=1.2,
        zeta=2.0,
        rho=0.3,
        max_iter=60,
        tolerancia=0.01,
        penalty_rmse=1e12,
        debug=True,
    ):

        self.material_configs = material_configs   # list de valores de k e anisotropia
        self.n_ants = n_ants
        self.alpha = alpha
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse
        self.debug = debug

        self.feromonios = {}

        for mat in self.material_configs:

            n_k = len(mat.k_values)
            n_a = len(mat.anisotropia_values)
            self.feromonios[mat.material_name] = np.ones(
                (n_k, n_a),
                dtype=float
            )

        self.cache = {} # evita abrir o SEEP pra soluções já testadas

  
    # Escolha probabilística

    def _sample_material_choice(self, material_config):

        fer = self.feromonios[material_config.material_name]

        # Amplificação do feromônio
        fer_alpha = fer ** self.alpha
        probs = fer_alpha / fer_alpha.sum()
        flat_probs = probs.flatten()
        chosen_index = np.random.choice(
            len(flat_probs),
            p=flat_probs
        )

        i, j = np.unravel_index(chosen_index, fer.shape)

        return i, j


    # Otimização

    def otimizar(self, modelo, funcao_objetivo):

        historico_rmse = []
        historico_iteracoes = []

        best_global_rmse = float("inf")
        best_global_params = None

        for iteration in range(1, self.max_iter + 1):

            ant_results = []
            ant_param_sets = []

            # Construção das soluções

            for ant in range(self.n_ants):
                material_params = {}

                for mat in self.material_configs:
                    i, j = self._sample_material_choice(mat)
                    k = mat.k_values[i]
                    a = mat.anisotropia_values[j]

                    if getattr(modelo.config, "use_anisotropy", True) is False:
                        a = 1.0

                    material_params[mat.material_name] = {

                        "material_object": mat.material_object,
                        "k_field_name": mat.k_field_name,
                        "anisotropy_field_name": mat.anisotropy_field_name,
                        "k": k,
                        "anisotropia": a,
                        "idx_k": i,
                        "idx_a": j,
                    }

                cache_key = tuple(
                    (
                        name,
                        float(params["k"]),
                        float(params["anisotropia"]),
                    )
                    for name, params in sorted(material_params.items())
                )

                try:
                    if cache_key in self.cache:
                        rmse = self.cache[cache_key]
                        source = "cache"

                    else:
                        h_modelo = modelo.run_multi(material_params)
                        rmse = funcao_objetivo.calcular_rmse(h_modelo)
                        self.cache[cache_key] = rmse
                        source = "run"

                except Exception as e:
                    rmse = self.penalty_rmse
                    source = f"erro: {e}"

                ant_results.append(rmse)
                ant_param_sets.append(material_params)

                if self.debug:
                    print(
                        f"Iter {iteration} | "
                        f"Formiga {ant+1} | "
                        f"RMSE={rmse:.6f} | "
                        f"{source}"
                    )


            # Melhor da iteração

            best_idx = int(np.argmin(ant_results))
            best_rmse = float(ant_results[best_idx])
            best_params_iter = ant_param_sets[best_idx]
            historico_rmse.append(best_rmse)

            # Atualiza melhor global

            if best_rmse < best_global_rmse:
                best_global_rmse = best_rmse
                best_global_params = best_params_iter

            # Evaporação

            for mat in self.material_configs:
                self.feromonios[mat.material_name] *= (1 - self.rho)

            # Reforço de TODAS as formigas
            worst_rmse = max(ant_results)

            for rmse, params in zip(ant_results, ant_param_sets):
                fitness = worst_rmse / (rmse + 1e-12)
                bonus = self.zeta * fitness

                for mat_name, p in params.items():
                    i = p["idx_k"]
                    j = p["idx_a"]
                    self.feromonios[mat_name][i, j] += bonus

            # Reforço extra do melhor global
            #global_bonus = 2.0 * self.zeta

            #for mat_name, p in best_global_params.items():
                #i = p["idx_k"]
                #j = p["idx_a"]
                #self.feromonios[mat_name][i, j] += global_bonus

            # Limita explosão numérica

            for mat in self.material_configs:
                self.feromonios[mat.material_name] = np.clip(
                    self.feromonios[mat.material_name],
                    1e-6,
                    1e6,
                )

            # Debug

            if self.debug:
                print("=" * 80)
                print(f"Iteração {iteration}")
                print(f"Melhor RMSE da iteração: {best_rmse:.6f}")
                print(f"Melhor RMSE global: {best_global_rmse:.6f}")
                print("=" * 80)
            
            # Critério de parada

            if best_global_rmse < self.tolerancia:
                print(f"Convergência atingida na iteração {iteration}")
                break

        return {

            "historico_rmse": historico_rmse,
            "historico_iteracoes": historico_iteracoes,
            "melhor_global": {

                "rmse": best_global_rmse,
                "materials": {
                    name: {
                        "k": params["k"],
                        "anisotropia": params["anisotropia"],
                    }
                    for name, params in best_global_params.items()
                },
            },

            "feromonios_finais": {
                name: fer.copy()
                for name, fer in self.feromonios.items()
            },

            "cache": dict(self.cache),
        }