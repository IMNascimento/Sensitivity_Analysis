import numpy as np


class ACO:
    def __init__(
        self,
        k_values,
        anisotropia_values,
        n_ants=4,
        zeta=2.0,
        rho=0.3,
        max_iter=400,
        tolerancia=0.01,
        penalty_rmse=1e12,
    ):
        self.k_values = k_values
        self.anisotropia_values = anisotropia_values

        self.n_k = len(k_values)
        self.n_a = len(anisotropia_values)

        self.n_ants = n_ants
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse

        self.feromonio = np.ones((self.n_k, self.n_a), dtype=float)
        self.cache = {}

    def otimizar(self, modelo, funcao_objetivo):
        historico_rmse = []

        best_global_rmse = float("inf")
        best_global_params = None

        for iteration in range(1, self.max_iter + 1):
            probabilidades = self.feromonio / self.feromonio.sum()
            prob_flat = probabilidades.flatten()

            ant_results = []
            ant_indices = []

            for ant in range(self.n_ants):
                chosen_index = np.random.choice(len(prob_flat), p=prob_flat)
                i, j = np.unravel_index(chosen_index, self.feromonio.shape)

                k = self.k_values[i]
                a = self.anisotropia_values[j]

                cache_key = (float(k), float(a))

                try:
                    if cache_key in self.cache:
                        rmse = self.cache[cache_key]
                        source = "cache"
                    else:
                        h_modelo = modelo.run(k, a)
                        rmse = funcao_objetivo.calcular_rmse(h_modelo)
                        self.cache[cache_key] = rmse
                        source = "run"

                except Exception as e:
                    rmse = self.penalty_rmse
                    source = f"erro: {e}"

                ant_results.append(rmse)
                ant_indices.append((i, j))

                print(
                    f"Iter. {iteration} | Formiga {ant + 1}: "
                    f"k={k}, anisotropia={a}, RMSE={rmse:.6f}, origem={source}"
                )

            best_idx = int(np.argmin(ant_results))
            best_rmse = float(ant_results[best_idx])
            best_i, best_j = ant_indices[best_idx]

            best_k_iter = self.k_values[best_i]
            best_a_iter = self.anisotropia_values[best_j]

            historico_rmse.append(best_rmse)

            if best_rmse < best_global_rmse:
                best_global_rmse = best_rmse
                best_global_params = {
                    "k": best_k_iter,
                    "anisotropia": best_a_iter,
                    "rmse": best_global_rmse,
                    "iteration": iteration,
                }

            # evaporação
            self.feromonio *= (1 - self.rho)

            # reforço no melhor da iteração
            bonus = self.zeta / (best_rmse + 1e-8)
            self.feromonio[best_i, best_j] += bonus

            print(f"Melhor RMSE da iteração: {best_rmse:.6f}")
            print(f"Melhor global até agora: {best_global_rmse:.6f}")
            print("-" * 80)

            if best_rmse < self.tolerancia:
                print(f"Convergiu na iteração {iteration}")
                break

        return {
            "historico_rmse": historico_rmse,
            "melhor_global": best_global_params,
            "feromonio_final": self.feromonio.copy(),
            "cache": dict(self.cache),
        }