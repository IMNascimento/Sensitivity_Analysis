from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import math
import numpy as np
from numpy.typing import NDArray

from sensitivity_analysis.interface.soil import SoilInput
from sensitivity_analysis.interface.soil_result import SoilReliabilityResult

# -------------------------------------------------------------------
# Type aliases
# -------------------------------------------------------------------

DistribuicaoTipo = Literal["Normal", "Lognormal", "Gumbel", "Uniforme"]
MetodoConfiabilidade = Literal["FORM", "FOSM"]
ArrayFloat = NDArray[np.float64]

__all__ = [
    "DistribuicaoTipo",
    "MetodoConfiabilidade",
    "RandomVariableConfig",
    "ReliabilityConfig",
    "SoilReliabilityCalculator",
]


# -------------------------------------------------------------------
# Dataclasses de configuração / entrada
# -------------------------------------------------------------------


@dataclass(slots=True)
class RandomVariableConfig:
    """Configuração de uma variável aleatória usada na análise de confiabilidade."""

    distrib: DistribuicaoTipo
    media: float
    desvio: float
    correlacao: float | None = None




@dataclass(slots=True)
class ReliabilityConfig:
    """Configuração da análise de confiabilidade (método + variáveis aleatórias)."""

    metodo: MetodoConfiabilidade
    random_vars: dict[str, RandomVariableConfig] = field(default_factory=dict)



# -------------------------------------------------------------------
# Calculadora (stub / placeholder)
# -------------------------------------------------------------------


class SoilReliabilityCalculator:
    """Calculadora de confiabilidade de solos (stub/placeholder).

    Atualmente implementa apenas uma lógica fictícia para:
    - gerar uma curva tensão × deformação linear; e
    - calcular um índice β e P_f apenas para testes de interface.

    Substitua o método `analisar` por sua formulação real assim que estiver
    pronta (FORM/FOSM).
    """

    def analisar(
        self,
        soil: SoilInput,
        cfg: ReliabilityConfig,
    ) -> SoilReliabilityResult:
        """Executa uma análise de confiabilidade simplificada.

        Parameters
        ----------
        soil:
            Parâmetros determinísticos do solo e carregamento.
        cfg:
            Configuração de método e variáveis aleatórias.

        Returns
        -------
        SoilReliabilityResult
            Resultado numérico apenas para testes de interface.
        """
        # Deformação máxima: usa epsilon_limite se fornecido e positivo,
        # caso contrário assume 0.02 (2%).
        if soil.epsilon_limite is not None and soil.epsilon_limite > 0.0:
            eps_max: float = soil.epsilon_limite
        else:
            eps_max = 0.02

        npts: int = 100
        epsilon: ArrayFloat = np.linspace(
            0.0,
            eps_max,
            npts,
            dtype=float,
        )

        # Curva tensão × deformação linear simples (placeholder)
        k: float = soil.E50_ref
        sigma: ArrayFloat = k * epsilon

        # Cálculo fictício de índice de confiabilidade (β) apenas para demo
        base: float = soil.sigma_aplicado / (soil.sigma0_eff + 1e-6)
        fator_rv: float = 1.0 + 0.1 * float(len(cfg.random_vars))
        # β maior para casos "mais seguros", apenas ilustrativo
        beta: float = max(0.5, 3.0 / max(base * fator_rv, 1e-6))

        # Probabilidade de falha aproximada usando CDF normal padrão (PLACEHOLDER)
        pf: float = 0.5 * (1.0 - math.erf(beta / math.sqrt(2.0)))

        detalhes_lines = [
            f"Método (placeholder): {cfg.metodo}",
            f"Nº de variáveis aleatórias: {len(cfg.random_vars)}",
            "Obs.: resultados são APENAS PARA TESTES DE INTERFACE.",
            (
                "Substitua o método `analisar` por sua implementação real de "
                "FORM/FOSM."
            ),
        ]
        detalhes: str = "\n".join(detalhes_lines)

        return SoilReliabilityResult(
            indice_confiabilidade=beta,
            prob_falha=pf,
            detalhes=detalhes,
            epsilon=epsilon,
            sigma=sigma,
        )
