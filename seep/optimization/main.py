import numpy as np

from config import SeepProjectConfig, ACOConfig
from seep_model import SeepModel
from objective_function import RMSEObjectiveFunction
from aco import ACO


def build_example_observed_data():
    """
    Substitua pelos seus dados observados reais.
    Formato: [x, y, valor_observado]
    """
    return np.array([
        [56.50, 59.12, 59.00],
        [63.70, 57.18, 59.39],
        [78.00, 55.98, 57.73],
        [89.00, 54.30, 57.01],
        [102.50, 53.25, 54.77],
    ], dtype=float)


def main():
    # =========================
    # CONFIGURAÇÃO DO PROJETO
    # =========================
    seep_cfg = SeepProjectConfig(
        project_path=r"C:\Users\bruna\Desktop\EESC-USP\26-1\Dissertação\teste.gsz",
        analysis_name="Barragem Curuá-Una",
        material_object='Materials["Tapete Permeável (Areia)"]',
        k_field_name="KSat",
        anisotropy_field_name="KYXRatio",
        use_anisotropy=False,   # anisotropia desabilitada por enquanto
        result_table="Nodes",
        x_param="eXCoord",
        y_param="eYCoord",
        value_param="eWaterTotalHead",
        step=1,
        solve_dependencies=True,
    )

    # =========================
    # CONFIGURAÇÃO DO ACO
    # =========================
    aco_cfg = ACOConfig(
        # Sugestão: começar perto do valor real atual do material
        k_values=[2.5e-4, 3.0e-4, 3.2808398950131233e-4, 3.5e-4, 4.0e-4],
        anisotropia_values=[1.0],  # ignorado enquanto use_anisotropy=False
        n_ants=4,
        zeta=2.0,
        rho=0.3,
        max_iter=20,
        tolerancia=0.01,
        penalty_rmse=1e12,
    )

    modelo = SeepModel(seep_cfg)
    modelo.open_project()

    # =========================
    # TESTE 1 - LEITURA DO CAMPO
    # =========================
    print("\n" + "=" * 80)
    print("TESTE 1 - GET DO KSat")
    print("=" * 80)
    modelo.inspect_object(seep_cfg.material_object + ".Hydraulic.KSat")

    # =========================
    # TESTE 2 - ESCRITA DO CAMPO
    # =========================
    print("\n" + "=" * 80)
    print("TESTE 2 - SET APENAS DO KSat")
    print("=" * 80)
    modelo.debug_test_set_individual_fields(
        k=3.2808398950131233e-4,
        anisotropia=1.0,
    )

    # =========================
    # TESTE 3 - EXECUÇÃO ÚNICA
    # =========================
    print("\n" + "=" * 80)
    print("TESTE 3 - EXECUÇÃO ÚNICA")
    print("=" * 80)
    resultado_teste = modelo.debug_single_run(
        k=3.2808398950131233e-4,
        anisotropia=1.0,
    )
    print("[DEBUG] Primeiras 10 linhas do modelo:")
    print(resultado_teste[:10])

    # =========================
    # FUNÇÃO OBJETIVO
    # =========================
    print("\n" + "=" * 80)
    print("TESTE 4 - FUNÇÃO OBJETIVO")
    print("=" * 80)
    observed_data = build_example_observed_data()

    funcao_objetivo = RMSEObjectiveFunction(
        observed_data,
        mode="exact",
        tolerance=1e-2,   # ajuste se precisar
        debug=True,
    )

    rmse_teste = funcao_objetivo.calcular_rmse(resultado_teste)
    print(f"[DEBUG] RMSE exact: {rmse_teste:.6f}")

    # =========================
    # ACO
    # =========================
    print("\n" + "=" * 80)
    print("TESTE 5 - EXECUTANDO ACO")
    print("=" * 80)

    aco = ACO(
        k_values=aco_cfg.k_values,
        anisotropia_values=aco_cfg.anisotropia_values,
        n_ants=aco_cfg.n_ants,
        zeta=aco_cfg.zeta,
        rho=aco_cfg.rho,
        max_iter=aco_cfg.max_iter,
        tolerancia=aco_cfg.tolerancia,
        penalty_rmse=aco_cfg.penalty_rmse,
    )

    resultado = aco.otimizar(modelo, funcao_objetivo)

    # =========================
    # RESULTADO FINAL
    # =========================
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print("Melhor solução global:")
    print(resultado["melhor_global"])

    print("\nHistórico RMSE:")
    print(resultado["historico_rmse"])

    print("\nFeromônio final:")
    print(resultado["feromonio_final"])


if __name__ == "__main__":
    main()