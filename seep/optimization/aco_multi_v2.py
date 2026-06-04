import numpy as np


class MultiMaterialACOv2:
    """
    ACO multi-material FIEL ao algoritmo do livro (Rao, 2009, Seção 13.5).

    Esta é a implementação "de livro": segue passo a passo o procedimento
    13.5.5, apenas adaptada para (a) minimizar RMSE (objetivo positivo) e
    (b) tratar vários materiais / vários parâmetros simultaneamente.

    NÃO usa as melhorias do aco_multi_robust.py (Max-Min Ant System, ratio_cap,
    elitismo). O objetivo aqui é reproduzir o livro tal como está — inclusive
    a sua tendência natural à convergência prematura quando o problema é grande.
    Para produção robusta, use aco_multi_robust.py.

    ───────────────────────────────────────────────────────────────────────────
    MAPEAMENTO LIVRO → NOSSO PROBLEMA
    ───────────────────────────────────────────────────────────────────────────
    Grafo multilayer (Fig. 13.3): cada VARIÁVEL DE PROJETO é uma camada, cada
    VALOR DISCRETO é um nó. No nosso caso cada material tem 2 variáveis de
    projeto: k e anisotropia. Logo, com M materiais há n = 2·M camadas, cada
    uma com o seu vetor de feromônio independente (τ_k[mat], τ_a[mat]).

    Passos (13.5.5):
      Step 1: τ_ij^(1) = 1 em todos os arcos.                  (feromônio igual)
      Step 2: p_ij = τ_ij^α / Σ_m τ_im^α                       (Eq. 13.38)
              seleção por roleta com probabilidade acumulada.
      Step 3: cada formiga monta um caminho completo (um valor por camada);
              avalia f_k = RMSE; acha f_best (13.40) e f_worst (13.41).
      Step 4: convergiu se TODAS as formigas tomam o mesmo caminho. Senão:
              evaporação em TODOS os arcos:  τ ← (1−ρ)·τ        (Eq. 13.34/13.35)
              depósito no caminho da(s) melhor(es) formiga(s):  (Eq. 13.42)
                  τ_ij ← τ_ij + Σ_k Δτ_ij^(k)
              ρ ∈ [0.5, 0.8] recomendado pelo livro.

    DEPÓSITO (Eq. 13.37 adaptada para RMSE > 0):
      No livro f é negativo e Δτ = ζ·f_best/f_worst (> ζ quando o melhor é
      muito melhor que o pior). Para RMSE positivo, o análogo estrutural que
      preserva o objetivo declarado ("mais feromônio às melhores soluções") é

          Δτ = ζ · f_worst / f_best          (≥ ζ; cresce quando f_best << f_worst)

      Formigas cuja simulação falhou (penalidade) são EXCLUÍDAS do cálculo de
      f_worst e nunca guiam o depósito, evitando que a penalidade (1e12)
      exploda o feromônio.
    """

    def __init__(
        self,
        material_configs,
        n_ants=10,
        alpha=1.0,
        zeta=2.0,
        rho=0.5,
        max_iter=80,
        tolerancia=0.01,
        penalty_rmse=1e12,
        debug=True,
    ):
        """
        Args:
            material_configs: lista de objetos com .material_name,
                .material_object, .k_field_name, .anisotropy_field_name,
                .k_values, .anisotropia_values.
            n_ants:    número de formigas N.
            alpha:     expoente α da Eq. 13.38 (1.0 = livro; >1 explora menos).
            zeta:      parâmetro ζ de escala do depósito (Eq. 13.37).
            rho:       taxa de evaporação ρ; livro recomenda [0.5, 0.8].
            max_iter:  número máximo de iterações (l_max).
            tolerancia: parada antecipada se RMSE < tolerancia.
            penalty_rmse: RMSE atribuído quando a simulação falha.
            debug:     imprime log detalhado.
        """
        self.material_configs = material_configs
        self.n_ants = n_ants
        self.alpha = alpha
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse
        self.debug = debug

        # Step 1: feromônio igual a 1 em todos os arcos (multilayer 1D).
        self.tau_k = {}
        self.tau_a = {}
        for mat in self.material_configs:
            name = mat.material_name
            self.tau_k[name] = np.ones(len(mat.k_values), dtype=float)
            self.tau_a[name] = np.ones(len(mat.anisotropia_values), dtype=float)

        self.cache = {}

    # ------------------------------------------------------------------
    # Step 2: seleção por roleta com p_ij ∝ τ_ij^α  (Eq. 13.38)
    # ------------------------------------------------------------------
    def _select(self, tau):
        w = tau ** self.alpha
        probs = w / w.sum()
        cumprobs = np.cumsum(probs)              # faixas de probabilidade acumulada
        r = np.random.uniform(0.0, 1.0)          # número aleatório em (0,1)
        for j, cp in enumerate(cumprobs):
            if r <= cp:
                return j
        return len(tau) - 1

    # ------------------------------------------------------------------
    # Δτ (Eq. 13.37 adaptada para minimização de RMSE > 0)
    # ------------------------------------------------------------------
    def _delta_tau(self, f_best, f_worst):
        if f_best <= 1e-14:          # solução praticamente perfeita
            return self.zeta
        if f_worst <= f_best:        # todas as (válidas) iguais
            return self.zeta
        return self.zeta * (f_worst / f_best)

    def _params_de(self, choices):
        out = {}
        for mat in self.material_configs:
            name = mat.material_name
            i, j = choices[name]
            out[name] = {
                "k": mat.k_values[i],
                "anisotropia": mat.anisotropia_values[j],
            }
        return out

    # ------------------------------------------------------------------
    # Otimização (Steps 2–4 em laço)
    # ------------------------------------------------------------------
    def otimizar(self, modelo, funcao_objetivo):
        """
        Args:
            modelo:          objeto com run_multi(material_params) → array (n,3)
                             e config.use_anisotropy (opcional).
            funcao_objetivo: objeto com calcular_rmse(h_modelo) → float.

        Returns:
            dict com historico_rmse, historico_iteracoes, melhor_global,
            tau_k_final, tau_a_final, cache, n_falhas, convergiu.
        """
        historico_rmse = []
        historico_iteracoes = []
        best_global_rmse = float("inf")
        best_global_choices = None
        best_global_params = None
        n_falhas_total = 0
        convergiu = False

        for iteration in range(1, self.max_iter + 1):

            ant_rmse = []
            ant_choices = []
            ant_falhou = []

            # ── Step 3: cada formiga monta um caminho completo ────────────────
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
                        "material_object": mat.material_object,
                        "k_field_name": mat.k_field_name,
                        "anisotropy_field_name": mat.anisotropy_field_name,
                        "k": k,
                        "anisotropia": a,
                        "idx_k": i,
                        "idx_a": j,
                    }

                cache_key = tuple(
                    (name, float(p["k"]), float(p["anisotropia"]))
                    for name, p in sorted(material_params.items())
                )

                falhou = False
                try:
                    if cache_key in self.cache:
                        rmse = self.cache[cache_key]
                        source = "cache"
                    else:
                        h = modelo.run_multi(material_params)
                        rmse = (funcao_objetivo.calcular(h)
                                if hasattr(funcao_objetivo, "calcular")
                                else funcao_objetivo.calcular_rmse(h))
                        self.cache[cache_key] = rmse
                        source = "run"
                except Exception as e:
                    rmse = self.penalty_rmse
                    falhou = True
                    n_falhas_total += 1
                    source = f"ERRO: {e}"

                ant_rmse.append(rmse)
                ant_choices.append(choices)
                ant_falhou.append(falhou)

                if self.debug:
                    print(f"Iter {iteration} | Formiga {ant+1} | RMSE={rmse:.6g} | [{source}]")
                    for name, p in material_params.items():
                        print(f"   {name}: k={p['k']}, a={p['anisotropia']:.4g}")

            # ── f_best (13.40) e f_worst (13.41) ──────────────────────────────
            best_ant_idx = int(np.argmin(ant_rmse))
            f_best = float(ant_rmse[best_ant_idx])
            best_choices = ant_choices[best_ant_idx]

            # f_worst só sobre formigas VÁLIDAS (penalidades não distorcem Δτ).
            validos = [r for r, fail in zip(ant_rmse, ant_falhou) if not fail]
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
                "n_falhas_iteracao": n_falhas_iter,
                "melhor_parametros_iteracao": self._params_de(best_choices),
            })

            if f_best < best_global_rmse:
                best_global_rmse = f_best
                best_global_choices = best_choices
                best_global_params = {
                    "rmse": best_global_rmse,
                    "iteration": iteration,
                    "materials": self._params_de(best_choices),
                }

            # ── Step 4: evaporação em TODOS os arcos (Eq. 13.34/13.35) ────────
            for name in self.tau_k:
                self.tau_k[name] *= (1.0 - self.rho)
                self.tau_a[name] *= (1.0 - self.rho)

            # ── Depósito (Eq. 13.42 + 13.37 adaptada) ─────────────────────────
            # Soma sobre TODAS as formigas que tomaram o caminho da melhor.
            if not ant_falhou[best_ant_idx]:
                delta = self._delta_tau(f_best, f_worst)
                n_best = sum(
                    1 for idx in range(self.n_ants)
                    if ant_choices[idx] == best_choices and not ant_falhou[idx]
                )
                total_delta = n_best * delta
                for mat in self.material_configs:
                    name = mat.material_name
                    i_best, j_best = best_choices[name]
                    self.tau_k[name][i_best] += total_delta
                    self.tau_a[name][j_best] += total_delta
            else:
                delta = 0.0
                total_delta = 0.0

            if self.debug:
                print(
                    f"  f_best={f_best:.6g}, f_worst={f_worst:.6g}, "
                    f"Δτ={delta:.4g}, total={total_delta:.4g}, "
                    f"falhas={n_falhas_iter}/{self.n_ants}"
                )
                for mat in self.material_configs:
                    name = mat.material_name
                    print(f"  τ_k[{name}]={np.round(self.tau_k[name], 3)}")
                    print(f"  τ_a[{name}]={np.round(self.tau_a[name], 3)}")
                print(f"  Melhor global: {best_global_rmse:.6g}")
                print("-" * 100)

            # ── Parada por tolerância ─────────────────────────────────────────
            if f_best < self.tolerancia:
                if self.debug:
                    print(f"Convergiu por tolerância na iteração {iteration}")
                convergiu = True
                break

            # ── Convergência do livro: todas as formigas no mesmo caminho ─────
            if all(ant_choices[k] == best_choices for k in range(self.n_ants)):
                if self.debug:
                    print(f"Convergiu (todas as formigas no mesmo caminho) na iter {iteration}")
                convergiu = True
                break

        return {
            "historico_rmse": historico_rmse,
            "historico_iteracoes": historico_iteracoes,
            "melhor_global": best_global_params,
            "tau_k_final": {name: t.copy() for name, t in self.tau_k.items()},
            "tau_a_final": {name: t.copy() for name, t in self.tau_a.items()},
            "cache": dict(self.cache),
            "n_falhas": n_falhas_total,
            "convergiu": convergiu,
        }
