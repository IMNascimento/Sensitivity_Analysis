import numpy as np


class MultiMaterialACORobust:
    """
    ACO robusto para calibração conjunta de múltiplos materiais.

    Base teórica: Rao (2009), Seção 13.5 (grafo multilayer da Fig. 13.3),
    com duas correções que fazem o algoritmo CONVERGIR de forma confiável,
    sem travar prematuramente num ótimo local:

    ───────────────────────────────────────────────────────────────────────
    POR QUE O `aco_multi.py` ORIGINAL NÃO CONVERGE
    ───────────────────────────────────────────────────────────────────────
    1. Feromônio numa matriz 2D conjunta (n_k × n_a) por material. O espaço
       a concentrar é grande (n_k·n_a células) e só UMA célula é reforçada
       por iteração → o feromônio nunca se concentra (fica difuso).
    2. Depósito `bonus = ζ / rmse`: a magnitude não tem relação com a
       evaporação (ρ=0.3, baixa). Com reforço fraco e evaporação lenta, a
       distribuição quase não muda → "passeio aleatório", não converge.
    3. Sem limites de feromônio: ou fica difuso (não converge), ou — quando
       o reforço é forte — explode na 1ª solução boa e trava (ótimo local).

    ───────────────────────────────────────────────────────────────────────
    CORREÇÕES DESTA VERSÃO
    ───────────────────────────────────────────────────────────────────────
    A. Estrutura multilayer FIEL ao livro: feromônio 1D independente por
       variável (τ_k e τ_a por material). Espaço a concentrar: n_k + n_a,
       não n_k·n_a. (Eq. 13.38 para a probabilidade.)

    B. Max-Min Ant System (MMAS): feromônio fica preso em [τ_min, τ_max].
       Isso garante probabilidade > 0 em TODO caminho (continua explorando)
       e impede travar num ótimo local — a cura da convergência prematura.

    C. Expoente α na probabilidade: p_ij ∝ τ_ij^α. α controla
       exploração×explotação (α menor = mais exploração).

    D. Sistema de erro robusto: formigas cuja simulação falhou recebem
       `penalty_rmse` mas são EXCLUÍDAS do cálculo de f_worst e NUNCA
       guiam o depósito. O número de falhas é reportado em `n_falhas`,
       então nenhuma informação de erro é perdida.

    E. Reforço elitista opcional: o melhor caminho GLOBAL também é reforçado
       a cada iteração, acelerando a convergência sem perder o melhor.

    Depósito (Eq. 13.37 adaptada para RMSE > 0, com limite):
        razão  = clip(f_worst_valido / f_best, 1.0, ratio_cap)
        Δτ     = ζ · razão
    A razão recompensa quando o melhor é muito superior ao pior, mas é
    limitada por `ratio_cap` (e por τ_max) para nunca explodir, inclusive
    quando há penalidades.
    """

    def __init__(
        self,
        material_configs,
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
        debug=True,
    ):
        """
        Args:
            material_configs: lista de objetos de configuração de material com
                .material_name, .material_object, .k_field_name,
                .anisotropy_field_name, .k_values, .anisotropia_values.
            n_ants:    número de formigas N (mais formigas = mais exploração).
            alpha:     expoente do feromônio na probabilidade (Eq. 13.38).
            zeta:      escala base do depósito ζ (Eq. 13.37).
            rho:       taxa de evaporação ρ ∈ (0, 1).
            tau_min:   limite inferior do feromônio (MMAS).
            tau_max:   limite superior do feromônio (MMAS); τ inicia aqui.
            ratio_cap: teto da razão f_worst/f_best no depósito (anti-explosão).
            elitist:   se True, reforça também o melhor caminho global.
            max_iter:  número máximo de iterações.
            tolerancia: parar se RMSE < tolerancia.
            penalty_rmse: RMSE atribuído quando a simulação falha.
            debug:     imprimir log detalhado.
        """
        self.material_configs = material_configs
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
        self.debug = debug

        # Feromônio multilayer 1D por variável por material.
        # MMAS: inicia em τ_max para máxima exploração inicial.
        self.tau_k = {}
        self.tau_a = {}
        for mat in self.material_configs:
            name = mat.material_name
            self.tau_k[name] = np.full(len(mat.k_values), tau_max, dtype=float)
            self.tau_a[name] = np.full(len(mat.anisotropia_values), tau_max, dtype=float)

        self.cache = {}

    # ------------------------------------------------------------------
    # Seleção roulette-wheel com p_ij ∝ τ_ij^α (Eq. 13.38)
    # ------------------------------------------------------------------
    def _select(self, tau):
        w = tau ** self.alpha
        probs = w / w.sum()
        cumprobs = np.cumsum(probs)
        r = np.random.uniform(0.0, 1.0)
        for j, cp in enumerate(cumprobs):
            if r <= cp:
                return j
        return len(tau) - 1

    def _clip_all(self):
        for name in self.tau_k:
            np.clip(self.tau_k[name], self.tau_min, self.tau_max, out=self.tau_k[name])
            np.clip(self.tau_a[name], self.tau_min, self.tau_max, out=self.tau_a[name])

    def _depositar(self, choices, delta):
        for mat in self.material_configs:
            name = mat.material_name
            i, j = choices[name]
            self.tau_k[name][i] += delta
            self.tau_a[name][j] += delta

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
    # Otimização
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

            # ── Step 3: cada formiga constrói caminhos p/ todos os materiais ──
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

            # ── Melhor da iteração (sempre entre TODAS as formigas) ───────────
            best_ant_idx = int(np.argmin(ant_rmse))
            f_best = float(ant_rmse[best_ant_idx])
            best_choices = ant_choices[best_ant_idx]

            # f_worst e média calculados só sobre formigas VÁLIDAS (sem penalidade).
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

            # ── Step 4: evaporação (Eq. 13.34/13.43) ──────────────────────────
            for name in self.tau_k:
                self.tau_k[name] *= (1.0 - self.rho)
                self.tau_a[name] *= (1.0 - self.rho)

            # ── Depósito limitado (Eq. 13.37 adaptada, anti-explosão) ─────────
            # Só deposita se o melhor da iteração for uma solução válida.
            if not ant_falhou[best_ant_idx]:
                if f_best > 1e-14 and f_worst > f_best:
                    razao = min(f_worst / f_best, self.ratio_cap)
                else:
                    razao = 1.0
                delta = self.zeta * razao

                # Reforça o melhor da iteração.
                self._depositar(best_choices, delta)

                # Elitismo: reforça também o melhor global.
                if self.elitist and best_global_choices is not None:
                    self._depositar(best_global_choices, delta)
            else:
                delta = 0.0  # todas as formigas falharam nesta iteração

            # MMAS: prende o feromônio em [τ_min, τ_max].
            self._clip_all()

            if self.debug:
                print(
                    f"  f_best={f_best:.6g}, f_worst={f_worst:.6g}, "
                    f"Δτ={delta:.4g}, falhas={n_falhas_iter}/{self.n_ants}"
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

            # ── Convergência: todas as formigas no mesmo conjunto de caminhos ─
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
