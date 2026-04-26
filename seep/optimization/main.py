import csv
from pathlib import Path
from datetime import datetime

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


def build_material_object(material_name: str) -> str:
    return f'Materials["{material_name}"]'


def save_results_csv(output_path: Path, rows: list[dict]) -> None:
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_results_markdown(
    output_path: Path,
    rows: list[dict],
    project_path: str,
    analysis_name: str,
) -> None:
    lines = []
    lines.append("# Resultado da calibração por material")
    lines.append("")
    lines.append(f"- Projeto: `{project_path}`")
    lines.append(f"- Análise: `{analysis_name}`")
    lines.append(f"- Gerado em: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append("")

    if rows:
        lines.append("## Resumo")
        lines.append("")
        lines.append("| Material | k testados | anisotropias testadas | Melhor k | Melhor anisotropia | Melhor RMSE | Iteração | Status |")
        lines.append("|---|---|---|---:|---:|---:|---:|---|")

        for row in rows:
            lines.append(
                f"| {row['material']} | {row['k_values']} | {row['anisotropia_values']} | "
                f"{row['melhor_k']} | {row['melhor_anisotropia']} | "
                f"{row['melhor_rmse']} | {row['iteracao_melhor']} | {row['status']} |"
            )

        lines.append("")
        lines.append("## Observações")
        lines.append("")
        lines.append("- Cada material foi calibrado com uma configuração própria de ACO.")
        lines.append("- A sessão do projeto foi mantida aberta durante a execução.")
        lines.append("- A anisotropia foi ativada e agora faz parte do espaço de busca.")
    else:
        lines.append("Nenhum resultado foi gerado.")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    project_path = r"C:\Users\bruna\Desktop\EESC-USP\26-1\Dissertação\teste.gsz"
    analysis_name = "Barragem Curuá-Una"

    observed_data = build_example_observed_data()

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "resultado_calibracao.csv"
    md_path = output_dir / "resultado_calibracao.md"

    # ============================================================
    # UM JOB COMPLETO POR MATERIAL
    # CADA MATERIAL TEM SEU PRÓPRIO ACO
    # AGORA COM ANISOTROPIA ATIVA
    # ============================================================
    material_jobs = [
        {
            "material_name": "Tapete Permeável (Areia)",
            "aco_cfg": ACOConfig(
                k_values=[2.5e-4, 3.0e-4, 3.2808398950131233e-4, 3.5e-4, 4.0e-4],
                anisotropia_values=[0.5, 1.0, 2.0, 5.0],
                n_ants=4,
                zeta=2.0,
                rho=0.3,
                max_iter=20,
                tolerancia=0.01,
                penalty_rmse=1e12,
            ),
        },
        {
            "material_name": "Dreno Vertical (Areia)",
            "aco_cfg": ACOConfig(
                k_values=[2.0e-4, 2.5e-4, 3.0e-4, 3.5e-4, 4.5e-4],
                anisotropia_values=[0.5, 1.0, 2.0, 5.0],
                n_ants=5,
                zeta=2.0,
                rho=0.25,
                max_iter=25,
                tolerancia=0.01,
                penalty_rmse=1e12,
            ),
        },
        {
            "material_name": "Dreno Horizontal (Areia)",
            "aco_cfg": ACOConfig(
                k_values=[1.5e-4, 2.0e-4, 2.5e-4, 3.0e-4, 3.5e-4],
                anisotropia_values=[0.5, 1.0, 2.0, 5.0],
                n_ants=4,
                zeta=2.0,
                rho=0.3,
                max_iter=20,
                tolerancia=0.01,
                penalty_rmse=1e12,
            ),
        },
        {
            "material_name": "Fundação Permeável (Areia)",
            "aco_cfg": ACOConfig(
                k_values=[8.0e-5, 1.0e-4, 1.2e-4, 1.3123359580052493e-4, 1.5e-4],
                anisotropia_values=[0.5, 1.0, 2.0, 5.0],
                n_ants=4,
                zeta=2.0,
                rho=0.3,
                max_iter=20,
                tolerancia=0.01,
                penalty_rmse=1e12,
            ),
        },
    ]

    # ============================================================
    # CONFIG BASE DO PROJETO
    # ============================================================
    seep_cfg = SeepProjectConfig(
        project_path=project_path,
        analysis_name=analysis_name,
        material_object=build_material_object(material_jobs[0]["material_name"]),
        k_field_name="KSat",
        anisotropy_field_name="KYXRatio",
        use_anisotropy=True,   # <- AGORA ATIVADO
        result_table="Nodes",
        x_param="eXCoord",
        y_param="eYCoord",
        value_param="eWaterTotalHead",
        step=1,
        solve_dependencies=True,
    )

    modelo = SeepModel(seep_cfg)
    modelo.open_project()

    results_rows = []

    for job in material_jobs:
        material_name = job["material_name"]
        aco_cfg = job["aco_cfg"]

        print("\n" + "=" * 100)
        print(f"INICIANDO MATERIAL: {material_name}")
        print("=" * 100)

        modelo.config.material_object = build_material_object(material_name)

        funcao_objetivo = RMSEObjectiveFunction(
            observed_data,
            mode="exact",      # troque para "nearest" se quiser
            tolerance=1e-2,
            debug=False,
        )

        status = "ok"
        melhor_k = None
        melhor_anisotropia = None
        melhor_rmse = None
        iteracao_melhor = None
        erro_msg = ""

        try:
            k_inicial = aco_cfg.k_values[min(2, len(aco_cfg.k_values) - 1)]
            anisotropia_inicial = aco_cfg.anisotropia_values[min(1, len(aco_cfg.anisotropia_values) - 1)]

            print("\n" + "-" * 80)
            print("TESTE INICIAL - GET DO KSat")
            print("-" * 80)
            modelo.inspect_object(modelo.config.material_object + ".Hydraulic.KSat")

            print("\n" + "-" * 80)
            print("TESTE INICIAL - GET DO RATIO")
            print("-" * 80)
            modelo.inspect_object(modelo.config.material_object + ".Hydraulic." + modelo.config.anisotropy_field_name)

            print("\n" + "-" * 80)
            print("TESTE INICIAL - SET DO KSat E RATIO")
            print("-" * 80)
            modelo.debug_test_set_individual_fields(
                k=k_inicial,
                anisotropia=anisotropia_inicial,
            )

            print("\n" + "-" * 80)
            print("TESTE INICIAL - EXECUÇÃO ÚNICA")
            print("-" * 80)
            resultado_teste = modelo.debug_single_run(
                k=k_inicial,
                anisotropia=anisotropia_inicial,
            )

            rmse_teste = funcao_objetivo.calcular_rmse(resultado_teste)
            print(f"[DEBUG] RMSE teste inicial: {rmse_teste:.6f}")

            print("\n" + "-" * 80)
            print("EXECUTANDO ACO")
            print("-" * 80)

            aco = ACO(
                k_values=aco_cfg.k_values,
                anisotropia_values=aco_cfg.anisotropia_values,
                n_ants=aco_cfg.n_ants,
                zeta=aco_cfg.zeta,
                rho=aco_cfg.rho,
                max_iter=aco_cfg.max_iter,
                tolerancia=aco_cfg.tolerancia,
                penalty_rmse=aco_cfg.penalty_rmse,
                debug=True,
            )

            resultado = aco.otimizar(modelo, funcao_objetivo)

            melhor_global = resultado["melhor_global"] or {}
            melhor_k = melhor_global.get("k")
            melhor_anisotropia = melhor_global.get("anisotropia")
            melhor_rmse = melhor_global.get("rmse")
            iteracao_melhor = melhor_global.get("iteration")

            print("\n" + "-" * 80)
            print("RESULTADO DO MATERIAL")
            print("-" * 80)
            print(melhor_global)

        except Exception as e:
            status = "erro"
            erro_msg = str(e)
            print(f"[ERRO] Material '{material_name}': {erro_msg}")

        results_rows.append(
            {
                "material": material_name,
                "k_values": str(aco_cfg.k_values),
                "anisotropia_values": str(aco_cfg.anisotropia_values),
                "melhor_k": melhor_k,
                "melhor_anisotropia": melhor_anisotropia,
                "melhor_rmse": melhor_rmse,
                "iteracao_melhor": iteracao_melhor,
                "status": status,
                "erro": erro_msg,
            }
        )

    save_results_csv(csv_path, results_rows)
    save_results_markdown(md_path, results_rows, project_path, analysis_name)

    print("\n" + "=" * 100)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 100)
    print(f"CSV salvo em: {csv_path}")
    print(f"Markdown salvo em: {md_path}")


if __name__ == "__main__":
    main()