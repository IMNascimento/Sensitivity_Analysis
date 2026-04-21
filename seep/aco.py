import numpy as np

class ACO:
    def __init__(self, k_values, anisotropia_values, n_ants=4, zeta=2.0, rho=0.3, max_iter=400, tolerancia=0.01):
        self.k_values= k_values
        self.anisotropia_values = anisotropia_values

        self.n_k = len(k_values)
        self.n_a = len(anisotropia_values)

        self.n_ants = n_ants
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia

        self.feromonio = np.ones((self.n_k, self.n_a))

    def otimizar(self, modelo, funcao_objetivo):
        historico_rmse = []

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

                h_modelo = modelo.run(k, a)

                rmse = funcao_objetivo.calcular_rmse(h_modelo)

                ant_results.append(rmse)
                ant_indices.append((i, j))
                print(f"Iter. {iteration} | Formiga {ant+1}:"f"k={k}, a:{a}, RMSE={rmse:.4f}")
            
            best_idx = np.argmin(ant_results)
            best_rmse = ant_results[best_idx]

            best_i, best_j = ant_indices[best_idx]

            historico_rmse.append(best_rmse)

            self.feromonio *= (1 - self.rho)
            bonus = self.zeta / (best_rmse + 1e-8)
            self.feromonio[best_i, best_j] += bonus
            
            print(f"Melhor RMSE da iteração: {best_rmse:.4f}")
            print("-"*60)

            if best_rmse < self.tolerancia:
                print(f"Convergiu na iteração {iteration}")
                break

        return historico_rmse
