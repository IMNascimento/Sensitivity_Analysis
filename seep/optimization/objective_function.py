import numpy as np


class RMSEObjectiveFunction:
    def __init__(self, observed_data: np.ndarray):
        if observed_data.ndim != 2 or observed_data.shape[1] != 3:
            raise ValueError(
                "observed_data deve ter shape (n, 3) no formato [x, y, valor_observado]."
            )

        self.observed_data = np.array(observed_data, dtype=float)

    def calcular_rmse(self, model_output: np.ndarray) -> float:
        if model_output.ndim != 2 or model_output.shape[1] != 3:
            raise ValueError(
                "model_output deve ter shape (n, 3) no formato [x, y, valor_modelado]."
            )

        model_output = np.array(model_output, dtype=float)

        if len(model_output) != len(self.observed_data):
            raise ValueError(
                f"Quantidade de resultados diferente: observado={len(self.observed_data)} "
                f"modelado={len(model_output)}."
            )

        if not np.allclose(model_output[:, :2], self.observed_data[:, :2], atol=1e-8):
            raise ValueError(
                "As coordenadas (x, y) de model_output e observed_data não correspondem."
            )

        observed = self.observed_data[:, 2]
        simulated = model_output[:, 2]

        rmse = float(np.sqrt(np.mean((observed - simulated) ** 2)))
        return rmse