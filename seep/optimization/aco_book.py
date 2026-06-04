import numpy as np


class ACOBook:
    """
    Implementação fiel ao algoritmo ACO de Rao (2009), Seção 13.5.

    Estrutura multilayer (Fig. 13.3):
      - Uma camada por variável de projeto.
      - Uma array 1D de feromônio por variável (não uma matriz 2D conjunta).
      - Cada formiga escolhe um valor por variável independentemente.

    Fórmulas do livro:
      - Seleção  (Eq. 13.38): p_ij = τ_ij / Σ_m τ_im
      - Depósito (Eq. 13.37): Δτ = ζ * f_best / f_worst   (ants no melhor caminho)
      - Atualiz. (Eq. 13.42): τ^(l) = τ_old + Σ_k Δτ^(k)
      - Evapora. (Eq. 13.43): τ_old = (1 − ρ) * τ^(l−1)

    Para minimização de RMSE (valores positivos), o sinal da razão é invertido:
      Δτ = ζ * f_worst / f_best
    pois no exemplo do livro f_best e f_worst são negativos (f_best/f_worst > 1).

    Convergência (Step 4): todas as formigas escolhem o mesmo caminho.
    """

    def __init__(
        self,
        variable_values,
        n_ants=4,
        zeta=2.0,
        rho=0.5,
        max_iter=50,
        tolerancia=None,
        minimize=True,
        debug=True,
    ):
        """
        Args:
            variable_values: lista de listas.
                Ex.: [[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]] para 1 variável.
                Ex.: [[k1, k2, ...], [a1, a2, ...]] para 2 variáveis.
            n_ants:    número de formigas N.
            zeta:      parâmetro ζ de escala do depósito (Eq. 13.37).
            rho:       taxa de evaporação ρ ∈ (0.5, 0.8) recomendada pelo livro.
            max_iter:  número máximo de iterações.
            tolerancia: critério adicional de parada por valor de f.
            minimize:  True → minimizar f; False → maximizar f.
            debug:     True → imprime detalhes de cada iteração.
        """
        self.variable_values = [list(v) for v in variable_values]
        self.n_vars = len(self.variable_values)
        self.p = [len(v) for v in self.variable_values]
        self.n_ants = n_ants
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.minimize = minimize
        self.debug = debug

        # τ^(1) = 1 para todos os arcos (livro: "equal amounts of pheromone")
        self.tau = [np.ones(p_i, dtype=float) for p_i in self.p]

    # ------------------------------------------------------------------
    # Seleção por roulette-wheel com probabilidade acumulada (Eq. 13.38)
    # ------------------------------------------------------------------
    def _select(self, tau_i):
        probs = tau_i / tau_i.sum()
        cumprobs = np.cumsum(probs)
        r = np.random.uniform(0.0, 1.0)
        for j, cp in enumerate(cumprobs):
            if r <= cp:
                return j
        return len(tau_i) - 1

    # ------------------------------------------------------------------
    # Otimização principal
    # ------------------------------------------------------------------
    def optimize(self, func):
        """
        Args:
            func: callable.
                  Se n_vars == 1: recebe float, retorna float.
                  Se n_vars >  1: recebe lista [x1, x2, ...], retorna float.

        Returns:
            dict com 'best_x', 'best_f', 'history', 'tau_final'.
        """
        best_global_f = float("inf") if self.minimize else float("-inf")
        best_global_x = None
        history = []

        for iteration in range(1, self.max_iter + 1):

            # ── Step 3: cada formiga constrói um caminho completo ─────────────
            ant_indices = []
            ant_x = []
            ant_f = []

            for k in range(self.n_ants):
                idx = [self._select(self.tau[i]) for i in range(self.n_vars)]
                x = [self.variable_values[i][j] for i, j in enumerate(idx)]
                fval = func(x[0] if self.n_vars == 1 else x)
                ant_indices.append(idx)
                ant_x.append(x)
                ant_f.append(fval)

                if self.debug:
                    vals = ", ".join(f"x{i+1}={v:.5g}" for i, v in enumerate(x))
                    print(f"  Formiga {k+1}: {vals} → f={fval:.6g}")

            # ── Melhor e pior desta iteração ──────────────────────────────────
            if self.minimize:
                f_best = min(ant_f)
                f_worst = max(ant_f)
                best_k = int(np.argmin(ant_f))
            else:
                f_best = max(ant_f)
                f_worst = min(ant_f)
                best_k = int(np.argmax(ant_f))

            best_indices = ant_indices[best_k]
            best_x = ant_x[best_k]

            is_better = (f_best < best_global_f) if self.minimize else (f_best > best_global_f)
            if is_better:
                best_global_f = f_best
                best_global_x = best_x[:]

            history.append({
                "iteration": iteration,
                "f_best": f_best,
                "f_worst": f_worst,
                "x_best": best_x[:],
            })

            if self.debug:
                print(
                    f"Iter {iteration}: f_best={f_best:.6g} "
                    f"(x={best_x}), f_worst={f_worst:.6g}"
                )

            # ── Step 4: atualização do feromônio ──────────────────────────────
            # Evaporação (Eq. 13.43)
            for i in range(self.n_vars):
                self.tau[i] *= (1.0 - self.rho)

            # Depósito (Eq. 13.37)
            # Caso todos os valores iguais: evita divisão por zero
            if abs(f_worst - f_best) < 1e-14:
                delta_tau = self.zeta
            elif self.minimize and f_best > 0.0 and f_worst > 0.0:
                # Minimização de RMSE (positivo): razão invertida para que
                # Δτ > ζ quando f_best << f_worst (boa solução muito melhor)
                delta_tau = self.zeta * f_worst / f_best
            else:
                # Fórmula original do livro (válida para f negativos)
                delta_tau = self.zeta * f_best / f_worst

            # Soma contribuições de TODAS as formigas que escolheram o melhor caminho
            n_best_ants = sum(
                1 for k_ant in range(self.n_ants)
                if ant_indices[k_ant] == best_indices and ant_f[k_ant] == f_best
            )
            total_delta = n_best_ants * delta_tau

            for i in range(self.n_vars):
                self.tau[i][best_indices[i]] += total_delta

            if self.debug:
                print(
                    f"  n_formigas_melhor={n_best_ants}, "
                    f"Δτ={delta_tau:.4g}, total={total_delta:.4g}"
                )
                for i in range(self.n_vars):
                    print(f"  τ[var{i+1}]={np.round(self.tau[i], 4)}")
                print("-" * 70)

            # ── Critério de parada por tolerância ────────────────────────────
            if self.tolerancia is not None:
                if self.minimize and f_best <= self.tolerancia:
                    if self.debug:
                        print(f"Convergiu por tolerância na iteração {iteration}")
                    break

            # ── Convergência: todas formigas no mesmo caminho ─────────────────
            all_same = all(ant_indices[k] == best_indices for k in range(self.n_ants))
            if all_same:
                if self.debug:
                    print(f"Convergiu (todas formigas no mesmo caminho) na iter {iteration}")
                break

        return {
            "best_x": best_global_x,
            "best_f": best_global_f,
            "history": history,
            "tau_final": [t.copy() for t in self.tau],
        }


# ---------------------------------------------------------------------------
# Teste rápido: Exemplo 13.5 do livro — minimizar f(x) = x² − 2x − 11
# Resposta esperada: x* = 1.0, f* = −12.0
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(0)

    x_vals = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    def f(x):
        return x ** 2 - 2 * x - 11

    aco = ACOBook(
        variable_values=[x_vals],
        n_ants=4,
        zeta=2.0,
        rho=0.5,
        max_iter=20,
        minimize=True,
        debug=True,
    )

    result = aco.optimize(f)
    print("=" * 70)
    print(f"Melhor x encontrado : {result['best_x']}")
    print(f"Melhor f encontrado : {result['best_f']:.4f}  (esperado: -12.0)")
    print(f"τ final             : {np.round(result['tau_final'][0], 4)}")
