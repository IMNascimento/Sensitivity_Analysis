"""
Banco de testes do ACO multi-material com um MODELO SINTÉTICO de ótimo conhecido.

Objetivo
────────
Validar se cada variante do ACO CONVERGE para o ótimo global SEM precisar
rodar o GeoStudio (que é caro e lento). Usamos:

  - MockMaterialConfig : mesma interface dos material_configs reais.
  - MockSeepModel      : run_multi(...) devolve [x, y, valor] como o SeepModel.
  - ErrorObjectiveFunction REAL : exercita o mesmo "sistema de erro" da produção.

O modelo sintético gera o "head" em N nós como uma função LINEAR dos parâmetros
de todos os materiais:

    valor_no_no_n = Σ_m [ A[n, ·] · (log10(k_m), a_m) ]

Os dados observados são gerados com os parâmetros VERDADEIROS (theta*). Como a
matriz de coeficientes A tem posto completo de coluna, o RMSE = 0 ocorre em um
ÚNICO ponto do grid (o ótimo global é único e conhecido). A superfície de erro
é suave (tipo "bacia"), então um ACO que funciona deve encontrá-lo.

Como rodar:
    python3 seep/optimization/tests/test_aco_mock.py
"""

import os
import sys

import numpy as np

# Permite importar os módulos de seep/optimization sem instalar o pacote.
HERE = os.path.dirname(os.path.abspath(__file__))
OPT_DIR = os.path.dirname(HERE)
sys.path.insert(0, OPT_DIR)

from objective_function import ErrorObjectiveFunction  # noqa: E402
from aco_multi import MultiMaterialACO               # noqa: E402
from aco_multi_v2 import MultiMaterialACOv2          # noqa: E402
from aco_multi_robust import MultiMaterialACORobust  # noqa: E402
from convergence_plot import plot_convergencia, plot_comparacao  # noqa: E402
from barragem_materials import build_barragem_materials  # noqa: E402


# ───────────────────────────────────────────────────────────────────────────
# Mock APENAS do modelo (GeoStudio). A configuração de material vem da MESMA
# fonte usada pelo main_multi_material_robust.py (barragem_materials.py).
# ───────────────────────────────────────────────────────────────────────────
class _MockConfig:
    def __init__(self, use_anisotropy=True):
        self.use_anisotropy = use_anisotropy


class MockSeepModel:
    """
    Modelo sintético. O "head" em cada nó é linear nos parâmetros de todos os
    materiais. Coeficientes fixos (seed) com posto completo → ótimo único.

    Pode injetar falhas (exceções) para exercitar o sistema de penalidade:
    `fail_prob` é a probabilidade de uma chamada run_multi lançar exceção.
    """

    def __init__(self, material_configs, n_nodes=12, use_anisotropy=True,
                 fail_prob=0.0, seed=123):
        self.material_configs = material_configs
        self.config = _MockConfig(use_anisotropy)
        self.fail_prob = fail_prob
        self._rng = np.random.RandomState(seed)

        # Vetor de parâmetros theta = [log10(k_m), a_m] concatenado por material.
        self.dim = 2 * len(material_configs)
        # Matriz de coeficientes (n_nodes x dim), posto de coluna completo.
        self.A = self._rng.uniform(-1.0, 1.0, size=(n_nodes, self.dim))
        # Coordenadas fixas dos nós.
        self.coords = np.column_stack([
            np.arange(n_nodes, dtype=float),
            np.zeros(n_nodes, dtype=float),
        ])

    def _theta(self, material_params):
        vals = []
        for mat in self.material_configs:
            p = material_params[mat.material_name]
            vals.append(np.log10(p["k"]))
            vals.append(p["anisotropia"])
        return np.array(vals, dtype=float)

    def _head(self, theta):
        return self.A @ theta  # (n_nodes,)

    def run_multi(self, material_params):
        if self._rng.uniform() < self.fail_prob:
            raise RuntimeError("falha sintética de simulação (teste de penalidade)")
        heads = self._head(self._theta(material_params))
        return np.column_stack([self.coords, heads])

    # observado: head gerado com os parâmetros verdadeiros
    def observed(self, theta_true):
        heads = self._head(theta_true)
        return np.column_stack([self.coords, heads])


def build_true_theta(material_configs, true_idx):
    """theta* a partir dos índices verdadeiros (idx_k, idx_a) por material."""
    vals = []
    for mat in material_configs:
        ik, ia = true_idx[mat.material_name]
        vals.append(np.log10(mat.k_values[ik]))
        vals.append(mat.anisotropia_values[ia])
    return np.array(vals, dtype=float)


# ───────────────────────────────────────────────────────────────────────────
# Cenário de teste
# ───────────────────────────────────────────────────────────────────────────
def make_scenario():
    """
    Usa EXATAMENTE os materiais reais da barragem (barragem_materials.py),
    a mesma fonte do main_multi_material_robust.py. Só o modelo (GeoStudio) é
    substituído pelo MockSeepModel.

    O ótimo verdadeiro é escolhido por índice dentro do espaço de cada material
    (idx_k em [0, n_k-1], idx_a em [0, n_a-1]). Se você mudar os materiais em
    barragem_materials.py, esta escolha é normalizada para continuar válida.
    """
    mats = build_barragem_materials()

    # Ótimo verdadeiro: pega um índice "do meio" dentro de cada espaço, de forma
    # determinística e sempre dentro dos limites (robusto a mudanças no grid).
    true_idx = {}
    for m in mats:
        ik = len(m.k_values) // 2
        ia = len(m.anisotropia_values) // 2
        true_idx[m.material_name] = (ik, ia)
    return mats, true_idx


def avalia(nome, classe, kwargs, mats, true_idx, modelo, objetivo, seed=0):
    np.random.seed(seed)
    aco = classe(material_configs=mats, debug=False, **kwargs)
    res = aco.otimizar(modelo, objetivo)
    melhor = res["melhor_global"]
    achou = all(
        abs(melhor["materials"][mat.material_name]["k"] - mat.k_values[true_idx[mat.material_name][0]]) < 1e-20
        and abs(melhor["materials"][mat.material_name]["anisotropia"]
                - mat.anisotropia_values[true_idx[mat.material_name][1]]) < 1e-9
        for mat in mats
    )
    n_eval = len(res.get("cache", {}))
    convergiu = res.get("convergiu", "n/a")
    n_falhas = res.get("n_falhas", "n/a")
    print(f"  {nome:24s} | RMSE*={melhor['rmse']:.4g} | ótimo={'SIM' if achou else 'não'} "
          f"| convergiu={convergiu} | n_eval={n_eval} | falhas={n_falhas}")
    return res


def taxa_acerto(nome, classe, kwargs, mats, true_idx, theta_true, n_seeds=30, fail_prob=0.0):
    acertos = 0
    for s in range(n_seeds):
        modelo = MockSeepModel(mats, use_anisotropy=True, fail_prob=fail_prob, seed=1000 + s)
        objetivo = ErrorObjectiveFunction(modelo.observed(theta_true), mode="nearest")
        np.random.seed(s)
        aco = classe(material_configs=mats, debug=False, **kwargs)
        res = aco.otimizar(modelo, objetivo)
        melhor = res["melhor_global"]
        if all(
            abs(melhor["materials"][m.material_name]["k"]
                - m.k_values[true_idx[m.material_name][0]]) < 1e-20
            and abs(melhor["materials"][m.material_name]["anisotropia"]
                    - m.anisotropia_values[true_idx[m.material_name][1]]) < 1e-9
            for m in mats
        ):
            acertos += 1
    print(f"  {nome:24s} | acerto do ótimo: {acertos}/{n_seeds} = {100*acertos/n_seeds:.0f}% "
          f"(fail_prob={fail_prob})")


def main():
    mats, true_idx = make_scenario()
    theta_true = build_true_theta(mats, true_idx)

    modelo = MockSeepModel(mats, use_anisotropy=True, seed=123)
    objetivo = ErrorObjectiveFunction(modelo.observed(theta_true), mode="nearest")

    combos = 1
    for m in mats:
        combos *= len(m.k_values) * len(m.anisotropia_values)
    print("=" * 100)
    print(f"CENÁRIO: {len(mats)} materiais REAIS (MaterialCalibrationConfig), "
          f"ótimo conhecido. RMSE=0 no ótimo (superfície suave).")
    print(f"  Materiais: {', '.join(m.material_name for m in mats)}")
    print(f"  Espaço de busca conjunto: {combos:,} combinações")
    print("=" * 100)

    print("\n[1] Execução única (seed=0), parâmetros equivalentes:")
    res_orig = avalia("aco_multi (original)", MultiMaterialACO,
                      dict(n_ants=10, rho=0.3, max_iter=50, tolerancia=-1),
                      mats, true_idx, modelo, objetivo)
    res_v2 = avalia("aco_multi_v2", MultiMaterialACOv2,
                    dict(n_ants=10, rho=0.5, max_iter=50, tolerancia=-1),
                    mats, true_idx, modelo, objetivo)
    res_robust = avalia("aco_multi_robust", MultiMaterialACORobust,
                        dict(n_ants=25, alpha=1.0, rho=0.15, max_iter=150, tolerancia=-1),
                        mats, true_idx, modelo, objetivo)

    # ── Gráficos de convergência ─────────────────────────────────────────────
    # mostrar=False para o teste não bloquear; os PNGs ficam salvos ao lado.
    # Para ver na tela, abra os .png ou use plot_convergencia(res, mostrar=True).
    print("\n[gráficos]")
    plot_convergencia(
        res_robust,
        titulo="aco_multi_robust — afunilamento do erro (banda melhor–pior estreitando)",
        salvar=os.path.join(HERE, "conv_robust.png"), mostrar=False,
    )
    plot_comparacao(
        {"original": res_orig, "v2": res_v2, "robust": res_robust},
        titulo="Comparação: melhor RMSE global por iteração",
        salvar=os.path.join(HERE, "conv_comparacao.png"), mostrar=False,
    )

    print("\n[2] Taxa de acerto do ótimo global (30 seeds, sem falhas):")
    taxa_acerto("aco_multi (original)", MultiMaterialACO,
                dict(n_ants=15, rho=0.3, max_iter=80, tolerancia=-1),
                mats, true_idx, theta_true)
    taxa_acerto("aco_multi_v2", MultiMaterialACOv2,
                dict(n_ants=15, rho=0.5, max_iter=80, tolerancia=-1),
                mats, true_idx, theta_true)
    taxa_acerto("aco_multi_robust", MultiMaterialACORobust,
                dict(n_ants=25, alpha=1.0, rho=0.15, max_iter=150, tolerancia=-1),
                mats, true_idx, theta_true)

    print("\n[3] Sistema de erro: 25% das simulações falham (penalidade):")
    taxa_acerto("aco_multi_v2", MultiMaterialACOv2,
                dict(n_ants=15, rho=0.5, max_iter=80, tolerancia=-1),
                mats, true_idx, theta_true, fail_prob=0.25)
    taxa_acerto("aco_multi_robust", MultiMaterialACORobust,
                dict(n_ants=25, alpha=1.0, rho=0.15, max_iter=150, tolerancia=-1),
                mats, true_idx, theta_true, fail_prob=0.25)
    print()


if __name__ == "__main__":
    main()
