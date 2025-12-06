from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

ArrayFloat = NDArray[np.float64]

@dataclass(slots=True)
class SoilReliabilityResult:
    """
    Resultado simplificado da análise de confiabilidade.

    Por enquanto é apenas um container de dados numéricos para a interface,
    sem pretensão de rigor estatístico (PLACEHOLDER).
    """

    indice_confiabilidade: float
    prob_falha: float
    detalhes: str
    epsilon: ArrayFloat
    sigma: ArrayFloat
