"""
Abre as janelas INTERATIVAS do matplotlib com os gráficos de convergência.

Use o botão de salvar (ícone de disquete) da própria janela para salvar a
imagem onde você quiser, no formato que preferir (PNG, PDF, SVG...).

As duas janelas abrem ao mesmo tempo; o script fica vivo até você fechá-las.

Rodar:
    python3 seep/optimization/tests/mostrar_graficos.py
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OPT_DIR = os.path.dirname(HERE)
sys.path.insert(0, OPT_DIR)
sys.path.insert(0, HERE)

from objective_function import ErrorObjectiveFunction          # noqa: E402
from aco_multi import MultiMaterialACO                        # noqa: E402
from aco_multi_v2 import MultiMaterialACOv2                   # noqa: E402
from aco_multi_robust import MultiMaterialACORobust           # noqa: E402
from convergence_plot import plot_convergencia, plot_comparacao  # noqa: E402
import test_aco_mock as T                                     # noqa: E402


def main():
    mats, true_idx = T.make_scenario()
    theta_true = T.build_true_theta(mats, true_idx)

    modelo = T.MockSeepModel(mats, use_anisotropy=True, seed=123)
    objetivo = ErrorObjectiveFunction(modelo.observed(theta_true), mode="nearest")

    # Reexecuta as três versões (seed=0) para reconstruir os históricos.
    np.random.seed(0)
    res_orig = MultiMaterialACO(material_configs=mats, n_ants=10, rho=0.3,
                                max_iter=50, tolerancia=-1, debug=False
                                ).otimizar(modelo, objetivo)
    np.random.seed(0)
    res_v2 = MultiMaterialACOv2(material_configs=mats, n_ants=10, rho=0.5,
                                max_iter=50, tolerancia=-1, debug=False
                                ).otimizar(modelo, objetivo)
    np.random.seed(0)
    res_robust = MultiMaterialACORobust(material_configs=mats, n_ants=15, alpha=1.0,
                                        rho=0.2, max_iter=80, tolerancia=-1,
                                        debug=False).otimizar(modelo, objetivo)

    # Cria as duas figuras SEM bloquear (mostrar=False)...
    plot_convergencia(
        res_robust,
        titulo="aco_multi_robust — afunilamento do erro",
        mostrar=False,
    )
    plot_comparacao(
        {"original": res_orig, "v2": res_v2, "robust": res_robust},
        titulo="Comparação: melhor RMSE global por iteração",
        mostrar=False,
    )

    # ...e abre AS DUAS janelas ao mesmo tempo. Fecha as janelas para encerrar.
    print("Abrindo as janelas interativas. Use o botão de salvar (disquete) "
          "para salvar onde quiser. Feche as janelas para encerrar o script.")
    plt.show()


if __name__ == "__main__":
    main()
