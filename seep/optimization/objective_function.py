import numpy as np


class RMSEObjectiveFunction:
    def __init__(
        self,
        observed_data: np.ndarray,
        mode: str = "nearest",
        tolerance: float = 1e-3,
        debug: bool = False,
    ):
        """
        observed_data shape (n, 3): [x, y, valor_observado]

        mode:
            - "nearest": usa o nó mais próximo
            - "exact": tenta usar a coordenada exata com tolerância

        tolerance:
            tolerância usada no modo "exact"

        debug:
            se True, imprime quais pontos do modelo foram usados
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
        model_output shape (n, 3): [x, y, valor_modelado]
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
        Para cada ponto observado (x, y), encontra o nó do modelo mais próximo.
        Retorna shape (n, 3): [x_obs, y_obs, valor_modelado]
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
        Para cada ponto observado (x, y), tenta encontrar um nó do modelo
        com coordenadas iguais dentro da tolerância.
        Retorna shape (n, 3): [x_obs, y_obs, valor_modelado]

        Se não encontrar, lança erro.
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

            # se houver mais de um, pega o mais próximo
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
        Retorna os pontos amostrados do modelo de acordo com o modo atual.
        Útil para inspecionar qual coordenada foi usada.
        """
        if self.mode == "nearest":
            return self._sample_model_nearest(model_output)
        return self._sample_model_exact(model_output)