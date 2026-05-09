import csv
from pathlib import Path
from datetime import datetime

import numpy as np

from config import MultiMaterialSeepConfig, MaterialCalibrationConfig
from seep_model import SeepModel
from objective_function import RMSEObjectiveFunction
from aco_multi import MultiMaterialACO


def build_example_observed_data():
    return np.array([
        [56.499999, 59.119999, 61.47],
        [63.70, 57.18, 58.71],
        [78.00, 55.98, 57.15],
        [89.00, 54.30, 56.29],
        [102.50, 53.25, 54.31],
    ], dtype=float)


def build_material_object(material_name: str) -> str:
    return f'Materials["{material_name}"]'


def save_results_csv(output_path: Path, result_row: dict) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result_row.keys()))
        writer.writeheader()
        writer.writerow(result_row)


def save_results_markdown(output_path: Path, result: dict, project_path: str, analysis_name: str) -> None:
    lines = []
    lines.append("# Resultado da calibração conjunta")
    lines.append("")
    lines.append(f"- Projeto: {project_path}")
    lines.append(f"- Análise: {analysis_name}")
    lines.append(f"- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    best = result.get("melhor_global") or {}
    lines.append("## Melhor solução global")
    lines.append("")
    lines.append(f"- RMSE: {best.get('rmse')}")
    lines.append(f"- Iteração: {best.get('iteration')}")
    lines.append("")

    materials = best.get("materials", {})
    lines.append("| Material | Melhor k | Melhor anisotropia |")
    lines.append("|---|---:|---:|")
    for mat_name, params in materials.items():
        lines.append(f"| {mat_name} | {params['k']} | {params['anisotropia']} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def save_full_model_output_csv(output_path: Path, model_output: np.ndarray) -> None:
    """
    Salva a saída bruta do modelo no formato:
    x, y, eWaterTotalHead
    """
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "eWaterTotalHead"])
        writer.writerows(model_output.tolist())


def save_sampled_points_csv(
    output_path: Path,
    observed_data: np.ndarray,
    sampled_points: np.ndarray,
) -> None:
    """
    Salva os pontos observados e os pontos amostrados do modelo usados no RMSE.

    Columns:
    - x_obs
    - y_obs
    - valor_observado
    - x_amostrado
    - y_amostrado
    - eWaterTotalHead_amostrado
    """
    rows = []

    for i in range(len(observed_data)):
        x_obs, y_obs, valor_obs = observed_data[i]
        x_s, y_s, valor_modelado = sampled_points[i]

        rows.append([
            x_obs,
            y_obs,
            valor_obs,
            x_s,
            y_s,
            valor_modelado,
        ])

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "x_obs",
            "y_obs",
            "valor_observado",
            "x_amostrado",
            "y_amostrado",
            "eWaterTotalHead_amostrado",
        ])
        writer.writerows(rows)


def build_best_material_params(best_materials: dict, materials: list[MaterialCalibrationConfig]) -> dict:
    """
    Constrói o dicionário de parâmetros no formato esperado pelo run_multi().
    """
    material_map = {m.material_name: m for m in materials}
    result = {}

    for material_name, best_params in best_materials.items():
        mat_cfg = material_map[material_name]
        result[material_name] = {
            "material_object": mat_cfg.material_object,
            "k_field_name": mat_cfg.k_field_name,
            "anisotropy_field_name": mat_cfg.anisotropy_field_name,
            "k": float(best_params["k"]),
            "anisotropia": float(best_params["anisotropia"]),
        }

    return result


def main():
    project_path = r"C:\Users\bruna\Desktop\EESC-USP\26-1\Dissertacao\teste.gsz"
    analysis_name = "Barragem Curuá-Una"

    observed_data = build_example_observed_data()

    output_dir = Path("outputs_multi")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "resultado_calibracao_conjunta.csv"
    md_path = output_dir / "resultado_calibracao_conjunta.md"
    full_output_csv_path = output_dir / "resultado_bruto_eWaterTotalHead.csv"
    sampled_points_csv_path = output_dir / "resultado_pontos_amostrados.csv"

    materials = [
        MaterialCalibrationConfig(
            material_name="Tapete Permeável (Areia)",
            material_object=build_material_object("Tapete Permeável (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[2.5e-4, 3.0e-4, 3.2808398950131233e-4, 3.5e-4, 4.0e-4],
            anisotropia_values=[0.5, 1.0, 2.0, 5.0],
        ),
        MaterialCalibrationConfig(
            material_name="Dreno Vertical (Areia)",
            material_object=build_material_object("Dreno Vertical (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[2.0e-4, 2.5e-4, 3.0e-4, 3.5e-4, 4.5e-4],
            anisotropia_values=[0.5, 1.0, 2.0, 5.0],
        ),
        MaterialCalibrationConfig(
            material_name="Dreno Horizontal (Areia)",
            material_object=build_material_object("Dreno Horizontal (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[1.5e-4, 2.0e-4, 2.5e-4, 3.0e-4, 3.5e-4],
            anisotropia_values=[0.5, 1.0, 2.0, 5.0],
        ),
        MaterialCalibrationConfig(
            material_name="Fundação Permeável (Areia)",
            material_object=build_material_object("Fundação Permeável (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[8.0e-5, 1.0e-4, 1.2e-4, 1.3123359580052493e-4, 1.5e-4],
            anisotropia_values=[0.5, 1.0, 2.0, 5.0],
        ),
    ]

    seep_cfg = MultiMaterialSeepConfig(
        project_path=project_path,
        analysis_name=analysis_name,
        materials=materials,
        use_anisotropy=True,
        result_table="Nodes",
        x_param="eXCoord",
        y_param="eYCoord",
        value_param="eWaterTotalHead",
        step=1,
        solve_dependencies=True,
    )

    modelo = SeepModel(seep_cfg)
    modelo.open_project()

    funcao_objetivo = RMSEObjectiveFunction(
        observed_data,
        mode="exact",   # troque para "nearest" se quiser
        tolerance=1e-2,
        debug=False,
    )

    aco = MultiMaterialACO(
        material_configs=materials,
        n_ants=4,
        zeta=2.0,
        rho=0.3,
        max_iter=3,
        tolerancia=0.01,
        penalty_rmse=1e12,
        debug=True,
    )

    resultado = aco.otimizar(modelo, funcao_objetivo)

    # ============================================================
    # SALVA RESUMO DA CALIBRAÇÃO
    # ============================================================
    best = resultado.get("melhor_global") or {}
    row = {
        "melhor_rmse": best.get("rmse"),
        "iteracao_melhor": best.get("iteration"),
        "melhores_parametros": str(best.get("materials")),
    }

    save_results_csv(csv_path, row)
    save_results_markdown(md_path, resultado, project_path, analysis_name)

    # ============================================================
    # RODA NOVAMENTE COM A MELHOR SOLUÇÃO E SALVA eWaterTotalHead
    # ============================================================
    best_materials = best.get("materials", {})
    if best_materials:
        best_material_params = build_best_material_params(best_materials, materials)

        best_model_output = modelo.run_multi(best_material_params)
        sampled_points = funcao_objetivo.debug_compare_points(best_model_output)

        save_full_model_output_csv(full_output_csv_path, best_model_output)
        save_sampled_points_csv(sampled_points_csv_path, observed_data, sampled_points)

        print("\n" + "-" * 100)
        print("AMOSTRA DO RESULTADO BRUTO")
        print("-" * 100)
        print(best_model_output[:10])

        print("\n" + "-" * 100)
        print("PONTOS AMOSTRADOS USADOS NO RMSE")
        print("-" * 100)
        print(sampled_points)

    print("\n" + "=" * 100)
    print("PROCESSAMENTO CONJUNTO FINALIZADO")
    print("=" * 100)
    print(f"CSV resumo salvo em: {csv_path}")
    print(f"Markdown resumo salvo em: {md_path}")
    print(f"CSV bruto com eWaterTotalHead salvo em: {full_output_csv_path}")
    print(f"CSV com pontos amostrados salvo em: {sampled_points_csv_path}")


if __name__ == "__main__":
    main()