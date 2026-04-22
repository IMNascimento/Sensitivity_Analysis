import numpy as np


class RMSEObjectiveFunction:
    """
    Calcula o erro RMSE entre valores observados e valores produzidos pelo modelo.

    Esta classe foi criada para trabalhar com saídas de modelos numéricos
    que retornam resultados no formato:

        [x, y, valor_modelado]

    e com dados observados no formato:

        [x, y, valor_observado]

    A classe oferece dois modos de correspondência entre os pontos observados
    e os pontos do modelo:

    - ``nearest``:
        Para cada ponto observado, usa o ponto do modelo mais próximo
        em termos de distância euclidiana no plano ``(x, y)``.

    - ``exact``:
        Para cada ponto observado, procura um ponto do modelo com coordenadas
        iguais dentro de uma tolerância especificada. Se não encontrar,
        lança erro.

    Além do cálculo do RMSE, a classe também pode operar em modo de depuração,
    mostrando quais coordenadas do modelo foram usadas para representar cada
    ponto observado.

    Attributes:
        observed_data (np.ndarray):
            Array de shape ``(n, 3)`` contendo os dados observados no formato
            ``[x, y, valor_observado]``.

        mode (str):
            Estratégia usada para associar pontos observados aos pontos do modelo.
            Pode ser:
            - ``"nearest"``
            - ``"exact"``

        tolerance (float):
            Tolerância usada no modo ``"exact"`` para considerar duas
            coordenadas equivalentes.

        debug (bool):
            Se True, imprime detalhes dos pontos observados e dos pontos
            do modelo utilizados no cálculo.
    """

    def __init__(
        self,
        observed_data: np.ndarray,
        mode: str = "nearest",
        tolerance: float = 1e-3,
        debug: bool = False,
    ):
        """
        Inicializa a função objetivo baseada em RMSE.

        Args:
            observed_data (np.ndarray):
                Array com shape ``(n, 3)`` no formato
                ``[x, y, valor_observado]``.

            mode (str, optional):
                Modo de correspondência entre os pontos observados e os pontos
                do modelo. Valores aceitos:
                - ``"nearest"``: usa o ponto do modelo mais próximo.
                - ``"exact"``: exige correspondência por coordenada dentro da
                  tolerância.
                Defaults to ``"nearest"``.

            tolerance (float, optional):
                Tolerância usada no modo ``"exact"`` para comparar as
                coordenadas ``x`` e ``y``.
                Defaults to ``1e-3``.

            debug (bool, optional):
                Se True, imprime informações detalhadas dos pontos usados
                no cálculo.
                Defaults to ``False``.

        Raises:
            ValueError:
                Se ``observed_data`` não tiver shape ``(n, 3)``.

            ValueError:
                Se ``mode`` não for ``"nearest"`` nem ``"exact"``.
        """
        if observed_data.ndim != 2 or observed_data.shape[1] != 3:
            raise ValueError(
                "observed_data deve ter shape (n, 3) no formato [x, y, valor_observado]."
            )

        if mode not in {"nearest", "exact"}:
            raise ValueError("mode deve ser 'nearest' ou 'exact'.")

        self.observed_data = np.array(observed_data, dtype=float)
        self.mode = mode
        self.tolerance = float(tolerance)
        self.debug = debug

    def calcular_rmse(self, model_output: np.ndarray) -> float:
        """
        Calcula o RMSE entre os valores observados e os valores do modelo.

        O método primeiro associa os pontos observados aos pontos do modelo
        usando a estratégia definida em ``self.mode``. Depois disso, extrai
        apenas os valores escalares observados e modelados e calcula o
        erro quadrático médio da raiz (RMSE).

        Args:
            model_output (np.ndarray):
                Array com shape ``(n, 3)`` no formato
                ``[x, y, valor_modelado]``.

        Returns:
            float:
                Valor do RMSE entre os dados observados e os dados
                amostrados do modelo.

        Raises:
            ValueError:
                Se ``model_output`` não tiver shape ``(n, 3)``.
        """
        if model_output.ndim != 2 or model_output.shape[1] != 3:
            raise ValueError(
                "model_output deve ter shape (n, 3) no formato [x, y, valor_modelado]."
            )

        model_output = np.array(model_output, dtype=float)

        if self.mode == "nearest":
            sampled_model = self._sample_model_nearest(model_output)
        else:
            sampled_model = self._sample_model_exact(model_output)

        observed = self.observed_data[:, 2]
        simulated = sampled_model[:, 2]

        rmse = float(np.sqrt(np.mean((observed - simulated) ** 2)))
        return rmse

    def _sample_model_nearest(self, model_output: np.ndarray) -> np.ndarray:
        """
        Amostra o modelo usando o ponto mais próximo para cada observação.

        Para cada ponto observado ``(x, y)``, o método busca o ponto do modelo
        com menor distância euclidiana e usa seu valor escalar como estimativa
        do valor modelado naquele ponto.

        Args:
            model_output (np.ndarray):
                Array com shape ``(n, 3)`` no formato
                ``[x, y, valor_modelado]``.

        Returns:
            np.ndarray:
                Array com shape ``(m, 3)`` no formato
                ``[x_obs, y_obs, valor_modelado_amostrado]``,
                onde ``m`` é o número de observações.

        Notes:
            - Este modo é útil quando as coordenadas observadas não coincidem
              exatamente com os nós da malha do modelo.
            - Este modo sempre encontra uma correspondência, desde que
              ``model_output`` não esteja vazio.
        """
        model_xy = model_output[:, :2]
        model_values = model_output[:, 2]

        sampled = []

        for obs in self.observed_data:
            x_obs, y_obs, val_obs = obs

            diffs = model_xy - np.array([x_obs, y_obs], dtype=float)
            dists = np.linalg.norm(diffs, axis=1)
            idx = int(np.argmin(dists))

            x_model = model_xy[idx, 0]
            y_model = model_xy[idx, 1]
            v_model = model_values[idx]

            sampled.append([x_obs, y_obs, v_model])

            if self.debug:
                print("[DEBUG][nearest]")
                print(f"  observado: x={x_obs:.6f}, y={y_obs:.6f}, valor={val_obs:.6f}")
                print(f"  modelo   : x={x_model:.6f}, y={y_model:.6f}, valor={v_model:.6f}")
                print(f"  distância: {dists[idx]:.6f}")
                print("-" * 60)

        return np.array(sampled, dtype=float)

    def _sample_model_exact(self, model_output: np.ndarray) -> np.ndarray:
        """
        Amostra o modelo usando correspondência exata de coordenadas.

        Para cada ponto observado ``(x, y)``, o método procura pontos do modelo
        cujas coordenadas estejam dentro da tolerância definida em
        ``self.tolerance``. Se encontrar mais de um ponto, escolhe o mais
        próximo. Se não encontrar nenhum, lança erro.

        Args:
            model_output (np.ndarray):
                Array com shape ``(n, 3)`` no formato
                ``[x, y, valor_modelado]``.

        Returns:
            np.ndarray:
                Array com shape ``(m, 3)`` no formato
                ``[x_obs, y_obs, valor_modelado_amostrado]``,
                onde ``m`` é o número de observações.

        Raises:
            ValueError:
                Se nenhum ponto do modelo for encontrado para uma coordenada
                observada dentro da tolerância especificada.

        Notes:
            - Este modo é indicado quando os pontos observados já coincidem
              com nós conhecidos da malha.
            - Se a malha do modelo não contiver exatamente as coordenadas
              observadas, este método pode falhar.
        """
        model_xy = model_output[:, :2]
        model_values = model_output[:, 2]

        sampled = []

        for obs in self.observed_data:
            x_obs, y_obs, val_obs = obs

            dx = np.abs(model_xy[:, 0] - x_obs)
            dy = np.abs(model_xy[:, 1] - y_obs)

            mask = (dx <= self.tolerance) & (dy <= self.tolerance)
            idxs = np.where(mask)[0]

            if len(idxs) == 0:
                raise ValueError(
                    f"Nenhum nó encontrado para x={x_obs}, y={y_obs} "
                    f"com tolerância={self.tolerance}."
                )

            if len(idxs) > 1:
                local_xy = model_xy[idxs]
                local_diffs = local_xy - np.array([x_obs, y_obs], dtype=float)
                local_dists = np.linalg.norm(local_diffs, axis=1)
                idx = int(idxs[np.argmin(local_dists)])
            else:
                idx = int(idxs[0])

            x_model = model_xy[idx, 0]
            y_model = model_xy[idx, 1]
            v_model = model_values[idx]

            sampled.append([x_obs, y_obs, v_model])

            if self.debug:
                print("[DEBUG][exact]")
                print(f"  observado: x={x_obs:.6f}, y={y_obs:.6f}, valor={val_obs:.6f}")
                print(f"  modelo   : x={x_model:.6f}, y={y_model:.6f}, valor={v_model:.6f}")
                print(f"  dx       : {abs(x_model - x_obs):.6f}")
                print(f"  dy       : {abs(y_model - y_obs):.6f}")
                print("-" * 60)

        return np.array(sampled, dtype=float)

    def debug_compare_points(self, model_output: np.ndarray) -> np.ndarray:
        """
        Retorna os pontos do modelo usados para representar os pontos observados.

        Este método é útil para depuração e validação, pois permite verificar
        exatamente quais pontos do modelo foram associados às observações,
        conforme o modo atual da classe.

        Args:
            model_output (np.ndarray):
                Array com shape ``(n, 3)`` no formato
                ``[x, y, valor_modelado]``.

        Returns:
            np.ndarray:
                Array com shape ``(m, 3)`` no formato
                ``[x_obs, y_obs, valor_modelado_amostrado]``, contendo os
                valores do modelo efetivamente usados na comparação.

        Notes:
            - Se ``mode="nearest"``, usa o ponto mais próximo.
            - Se ``mode="exact"``, usa a correspondência exata com tolerância.
        """
        if self.mode == "nearest":
            return self._sample_model_nearest(model_output)
        return self._sample_model_exact(model_output)