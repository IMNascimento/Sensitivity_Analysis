from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SoilInput:
    """Dados de entrada determinísticos do problema de solo."""

    # Condições do solo
    gama: float
    e0: float
    sigma0_eff: float  # tensão vertical efetiva inicial (kPa)

    # Parâmetros de rigidez
    E50_ref: float
    Eoed_ref: float
    Eur_ref: float
    m: float
    p_ref: float
    nu: float

    # Parâmetros de resistência
    phi: float
    c: float
    psi: float

    # Parâmetros de endurecimento
    h0: float
    alfa_h: float

    # Carregamento atual
    sigma_aplicado: float

    # Função limite / deformação limite
    g_func_text: str | None = None
    epsilon_limite: float | None = None