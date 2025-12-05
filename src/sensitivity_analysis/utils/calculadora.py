from __future__ import annotations
import numpy as np


class CalculadoraBasica:
    def soma(self, a: float, b: float) -> float:
        return a + b

    def subtrai(self, a: float, b: float) -> float:
        return a - b


class GeradorSinal:
    def seno(self, tamanho: int = 500) -> tuple[np.ndarray, np.ndarray]:
        x = np.linspace(0, 2 * np.pi, tamanho)
        y = np.sin(x)
        return x, y
