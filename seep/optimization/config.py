from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SeepProjectConfig:
    project_path: str
    analysis_name: str

    material_object: str = 'Materials["Tapete Permeável (Areia)"]'

    k_field_name: str = "KSat"
    anisotropy_field_name: str = "KYXRatio"

    use_anisotropy: bool = False

    result_table: str = "Nodes"
    x_param: str = "eXCoord"
    y_param: str = "eYCoord"
    value_param: str = "eWaterTotalHead"

    step: int = 1
    run: Optional[int] = None
    instance: Optional[int] = None
    solve_dependencies: bool = True


@dataclass
class ACOConfig:
    k_values: List[float] = field(default_factory=lambda: [1e-7, 5e-7, 1e-6, 5e-6, 1e-5])
    anisotropia_values: List[float] = field(default_factory=lambda: [0.5, 1.0, 2.0, 5.0, 10.0])
    n_ants: int = 4
    zeta: float = 2.0
    rho: float = 0.3
    max_iter: int = 50
    tolerancia: float = 0.01
    penalty_rmse: float = 1e12