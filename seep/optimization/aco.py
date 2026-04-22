import numpy as np


class ACO:
    """
    Implementa um algoritmo de Otimização por Colônia de Formigas (ACO)
    para calibração de parâmetros de um modelo numérico.

    Esta implementação foi desenhada para testar combinações discretas de:
    - `k` (por exemplo, condutividade hidráulica)
    - `anisotropia` (por exemplo, razão de anisotropia)

    O algoritmo percorre o espaço de busca usando probabilidades baseadas
    em feromônio. A cada iteração:
    1. Cada formiga escolhe uma combinação `(k, anisotropia)`.
    2. O modelo é executado com esses parâmetros.
    3. A função objetivo calcula o erro (por exemplo, RMSE).
    4. O melhor resultado da iteração reforça o feromônio.
    5. O processo continua até atingir o número máximo de iterações
       ou até convergir por tolerância.

    Observação importante:
    Esta implementação trabalha com um espaço de busca discreto, isto é,
    os valores possíveis de `k` e `anisotropia` devem ser fornecidos
    previamente em listas.

    Attributes:
        k_values (list[float]):
            Lista de valores possíveis para o parâmetro `k`.

        anisotropia_values (list[float]):
            Lista de valores possíveis para anisotropia.

        n_k (int):
            Quantidade de valores possíveis para `k`.

        n_a (int):
            Quantidade de valores possíveis para anisotropia.

        n_ants (int):
            Número de formigas simuladas por iteração.

        zeta (float):
            Fator de reforço do feromônio.
            Quanto maior, maior o prêmio dado à melhor solução da iteração.

        rho (float):
            Taxa de evaporação do feromônio.
            Valores maiores fazem o algoritmo “esquecer” mais rápido
            as soluções anteriores.

        max_iter (int):
            Número máximo de iterações do algoritmo.

        tolerancia (float):
            Critério de convergência baseado no RMSE.
            Se o melhor RMSE da iteração for menor que esse valor,
            o algoritmo encerra antes do limite de iterações.

        penalty_rmse (float):
            Valor de penalidade usado quando ocorre erro na execução
            do modelo ou no cálculo da função objetivo.

        debug (bool):
            Se True, imprime logs detalhados do processo.

        feromonio (np.ndarray):
            Matriz 2D de feromônio com shape `(n_k, n_a)`.
            Cada posição representa a intensidade de preferência
            por uma combinação `(k, anisotropia)`.

        cache (dict[tuple[float, float], float]):
            Cache de resultados já avaliados.
            Evita executar novamente o modelo para combinações
            já testadas anteriormente.
    """

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
        debug=True,
    ):
        """
        Inicializa o algoritmo ACO.

        Args:
            k_values (Sequence[float]):
                Lista ou sequência com os valores discretos possíveis
                do parâmetro `k`.

            anisotropia_values (Sequence[float]):
                Lista ou sequência com os valores discretos possíveis
                do parâmetro de anisotropia.

            n_ants (int, optional):
                Número de formigas por iteração.
                Defaults to 4.

            zeta (float, optional):
                Intensidade do reforço de feromônio aplicado à melhor
                solução da iteração.
                Defaults to 2.0.

            rho (float, optional):
                Taxa de evaporação do feromônio.
                Deve estar normalmente no intervalo `(0, 1)`.
                Defaults to 0.3.

            max_iter (int, optional):
                Número máximo de iterações.
                Defaults to 400.

            tolerancia (float, optional):
                Critério de convergência baseado no RMSE.
                Defaults to 0.01.

            penalty_rmse (float, optional):
                Penalidade atribuída quando ocorre exceção ao executar
                o modelo ou calcular a função objetivo.
                Defaults to 1e12.

            debug (bool, optional):
                Se True, exibe logs detalhados da execução.
                Defaults to True.
        """
        self.k_values = list(k_values)
        self.anisotropia_values = list(anisotropia_values)

        self.n_k = len(self.k_values)
        self.n_a = len(self.anisotropia_values)

        self.n_ants = n_ants
        self.zeta = zeta
        self.rho = rho
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.penalty_rmse = penalty_rmse
        self.debug = debug

        # Matriz inicial de feromônio.
        # Começa com 1 em todas as combinações, sem preferência inicial.
        self.feromonio = np.ones((self.n_k, self.n_a), dtype=float)

        # Cache para evitar rodar o mesmo par (k, anisotropia) mais de uma vez.
        self.cache = {}

    def otimizar(self, modelo, funcao_objetivo):
        """
        Executa o processo de otimização ACO.

        Fluxo do método:
        1. Constrói as probabilidades com base no feromônio atual.
        2. Cada formiga escolhe uma combinação `(k, anisotropia)`.
        3. Executa o modelo com esses parâmetros.
        4. Calcula o RMSE usando a função objetivo.
        5. Seleciona a melhor formiga da iteração.
        6. Aplica evaporação do feromônio.
        7. Reforça o feromônio da melhor solução da iteração.
        8. Atualiza o melhor resultado global.
        9. Repete até convergir ou atingir `max_iter`.

        Requisitos do objeto `modelo`:
        - Deve ter um atributo `config`.
        - Idealmente `modelo.config.use_anisotropy` deve existir
          para informar se anisotropia está ativa ou não.
        - Deve implementar um método:
              modelo.run(k, anisotropia) -> np.ndarray
          que execute a simulação e retorne os resultados modelados.

        Requisitos do objeto `funcao_objetivo`:
        - Deve implementar:
              funcao_objetivo.calcular_rmse(h_modelo) -> float

        Args:
            modelo (object):
                Objeto que representa o modelo a ser calibrado.
                Espera-se que tenha:
                - `config.use_anisotropy` (opcional)
                - método `run(k, anisotropia)`

            funcao_objetivo (object):
                Objeto responsável por calcular o erro entre
                o resultado do modelo e os dados observados.
                Deve ter o método `calcular_rmse`.

        Returns:
            dict:
                Dicionário com os resultados da otimização contendo:

                - `historico_rmse` (list[float]):
                    Melhor RMSE encontrado em cada iteração.

                - `historico_iteracoes` (list[dict]):
                    Lista com resumo de cada iteração:
                    - `iteracao`
                    - `melhor_rmse_iteracao`
                    - `melhor_k_iteracao`
                    - `melhor_anisotropia_iteracao`

                - `melhor_global` (dict | None):
                    Melhor solução encontrada em toda a execução.
                    Estrutura:
                    {
                        "k": float,
                        "anisotropia": float,
                        "rmse": float,
                        "iteration": int,
                    }

                - `feromonio_final` (np.ndarray):
                    Matriz final de feromônio após a última iteração.

                - `cache` (dict):
                    Cache contendo pares `(k, anisotropia)` já avaliados
                    e seus respectivos RMSEs.

        Notes:
            - Se `modelo.config.use_anisotropy` for False, a anisotropia
              será fixada em `1.0`, independentemente dos valores presentes
              em `anisotropia_values`.
            - Em caso de erro na execução de um teste, a combinação recebe
              `penalty_rmse`, evitando interromper a otimização inteira.
        """
        historico_rmse = []
        historico_iteracoes = []

        best_global_rmse = float("inf")
        best_global_params = None

        for iteration in range(1, self.max_iter + 1):
            # Converte a matriz de feromônio em probabilidades.
            probabilidades = self.feromonio / self.feromonio.sum()
            prob_flat = probabilidades.flatten()

            ant_results = []
            ant_indices = []

            for ant in range(self.n_ants):
                # Escolha probabilística de uma célula da matriz de feromônio.
                chosen_index = np.random.choice(len(prob_flat), p=prob_flat)
                i, j = np.unravel_index(chosen_index, self.feromonio.shape)

                k = self.k_values[i]
                a = self.anisotropia_values[j]

                # Se anisotropia estiver desabilitada no modelo,
                # força o valor para 1.0.
                if getattr(modelo.config, "use_anisotropy", True) is False:
                    a = 1.0

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

                if self.debug:
                    print(
                        f"Iter. {iteration} | Formiga {ant + 1}: "
                        f"k={k}, anisotropia={a}, RMSE={rmse:.6f}, origem={source}"
                    )

            # Seleciona a melhor formiga da iteração.
            best_idx = int(np.argmin(ant_results))
            best_rmse = float(ant_results[best_idx])
            best_i, best_j = ant_indices[best_idx]

            best_k_iter = self.k_values[best_i]
            best_a_iter = self.anisotropia_values[best_j]

            if getattr(modelo.config, "use_anisotropy", True) is False:
                best_a_iter = 1.0

            historico_rmse.append(best_rmse)
            historico_iteracoes.append(
                {
                    "iteracao": iteration,
                    "melhor_rmse_iteracao": best_rmse,
                    "melhor_k_iteracao": best_k_iter,
                    "melhor_anisotropia_iteracao": best_a_iter,
                }
            )

            # Atualiza melhor solução global.
            if best_rmse < best_global_rmse:
                best_global_rmse = best_rmse
                best_global_params = {
                    "k": best_k_iter,
                    "anisotropia": best_a_iter,
                    "rmse": best_global_rmse,
                    "iteration": iteration,
                }

            # Evaporação do feromônio.
            self.feromonio *= (1 - self.rho)

            # Reforço da melhor solução da iteração.
            bonus = self.zeta / (best_rmse + 1e-8)
            self.feromonio[best_i, best_j] += bonus

            if self.debug:
                print(f"Melhor RMSE da iteração: {best_rmse:.6f}")
                print(f"Melhor global até agora: {best_global_rmse:.6f}")
                print("-" * 80)

            # Critério de parada por convergência.
            if best_rmse < self.tolerancia:
                if self.debug:
                    print(f"Convergiu na iteração {iteration}")
                break

        return {
            "historico_rmse": historico_rmse,
            "historico_iteracoes": historico_iteracoes,
            "melhor_global": best_global_params,
            "feromonio_final": self.feromonio.copy(),
            "cache": dict(self.cache),
        }