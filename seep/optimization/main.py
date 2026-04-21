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
        [0.0, 0.0, 12.4],
        [1.0, 0.0, 12.1],
        [2.0, 0.0, 11.8],
        [3.0, 0.0, 11.5],
    ], dtype=float)


def main():
    # Ajustes estes valores Bruna de arcodo com seu projeto.
    seep_cfg = SeepProjectConfig(
        project_path=r"C:\Projetos\modelo_seep.gsz",
        analysis_name="SEEP/W Analysis",
        material_object="CurrentAnalysis.Materials.Material1",

        # ESTES NOMES PRECISAM BATER COM O RETORNO REAL DO Get(...) não se esqueça bruna
        k_field_name="K",
        anisotropy_field_name="AnisotropyRatio",

        # AJUSTE conforme a tabela e o resultado que você quer comparar
        result_table="Nodes",
        x_param="eXCoord",
        y_param="eYCoord",
        value_param="eWaterTotalHead", 
        step=1,
        solve_dependencies=True,
    )

    aco_cfg = ACOConfig(
        k_values=[1e-8, 5e-8, 1e-7, 5e-7, 1e-6],
        anisotropia_values=[0.5, 1.0, 2.0, 5.0, 10.0],
        n_ants=4,
        zeta=2.0,
        rho=0.3,
        max_iter=20,
        tolerancia=0.01,
        penalty_rmse=1e12,
    )

    modelo = SeepModel(seep_cfg)

    print("=" * 80)
    print("1) INSPECIONANDO MATERIAL")
    print("=" * 80)
    try:
        material_info = modelo.inspect_material()
        print(material_info)
    except Exception as e:
        print(f"Falha ao inspecionar material: {e}")

    print("\n" + "=" * 80)
    print("2) LISTANDO PARÂMETROS DE RESULTADO DISPONÍVEIS")
    print("=" * 80)
    try:
        params = modelo.list_available_result_params()
        for item in params[:20]:
            print(item)
        if len(params) > 20:
            print(f"... total de parâmetros encontrados: {len(params)}")
    except Exception as e:
        print(f"Falha ao listar parâmetros: {e}")

    print("\n" + "=" * 80)
    print("3) PREPARANDO FUNÇÃO OBJETIVO")
    print("=" * 80)
    observed_data = build_example_observed_data()
    funcao_objetivo = RMSEObjectiveFunction(observed_data)

    print("\n" + "=" * 80)
    print("4) EXECUTANDO ACO")
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

    print("\n" + "=" * 80)
    print("5) RESULTADO FINAL")
    print("=" * 80)
    print("Melhor solução global:")
    print(resultado["melhor_global"])

    print("\nHistórico RMSE:")
    print(resultado["historico_rmse"])

    print("\nFeromônio final:")
    print(resultado["feromonio_final"])


if __name__ == "__main__":
    main()