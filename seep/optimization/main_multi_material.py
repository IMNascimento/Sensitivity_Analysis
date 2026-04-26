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
        [56.50, 59.12, 59.00],
        [63.70, 57.18, 59.39],
        [78.00, 55.98, 57.73],
        [89.00, 54.30, 57.01],
        [102.50, 53.25, 54.77],
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
    lines.append(f"- Projeto: `{project_path}`")
    lines.append(f"- Análise: `{analysis_name}`")
    lines.append(f"- Gerado em: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append("")

    best = result.get("melhor_global") or {}
    lines.append("## Melhor solução global")
    lines.append("")
    lines.append(f"- RMSE: `{best.get('rmse')}`")
    lines.append(f"- Iteração: `{best.get('iteration')}`")
    lines.append("")

    materials = best.get("materials", {})
    lines.append("| Material | Melhor k | Melhor anisotropia |")
    lines.append("|---|---:|---:|")
    for mat_name, params in materials.items():
        lines.append(f"| {mat_name} | {params['k']} | {params['anisotropia']} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    project_path = r"C:\Users\bruna\Desktop\EESC-USP\26-1\Dissertação\teste.gsz"
    analysis_name = "Barragem Curuá-Una"

    observed_data = build_example_observed_data()

    output_dir = Path("outputs_multi")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "resultado_calibracao_conjunta.csv"
    md_path = output_dir / "resultado_calibracao_conjunta.md"

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
        mode="exact",
        tolerance=1e-2,
        debug=False,
    )

    aco = MultiMaterialACO(
        material_configs=materials,
        n_ants=4,
        zeta=2.0,
        rho=0.3,
        max_iter=20,
        tolerancia=0.01,
        penalty_rmse=1e12,
        debug=True,
    )

    resultado = aco.otimizar(modelo, funcao_objetivo)

    best = resultado.get("melhor_global") or {}
    row = {
        "melhor_rmse": best.get("rmse"),
        "iteracao_melhor": best.get("iteration"),
        "melhores_parametros": str(best.get("materials")),
    }

    save_results_csv(csv_path, row)
    save_results_markdown(md_path, resultado, project_path, analysis_name)

    print("\n" + "=" * 100)
    print("PROCESSAMENTO CONJUNTO FINALIZADO")
    print("=" * 100)
    print(f"CSV salvo em: {csv_path}")
    print(f"Markdown salvo em: {md_path}")


if __name__ == "__main__":
    main()