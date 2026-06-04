"""
Main de calibração conjunta multi-material usando o ACO ROBUSTO.

Idêntico ao main_multi_material.py, porém:
  - usa MultiMaterialACORobust (multilayer + Max-Min Ant System + α + depósito
    limitado), que converge de forma confiável (ver tests/test_aco_mock.py);
  - gera ao final um gráfico de convergência (afunilamento do RMSE).

Os helpers de salvamento (CSV/Markdown) são reaproveitados de
main_multi_material.py para não duplicar código.
"""

from pathlib import Path

import numpy as np

from config import MultiMaterialSeepConfig, MaterialCalibrationConfig
from seep_model import SeepModel
from objective_function import RMSEObjectiveFunction
from aco_multi_robust import MultiMaterialACORobust
from convergence_plot import plot_convergencia

# Reaproveita os utilitários já existentes do main original.
from main_multi_material import (
    build_example_observed_data,
    build_material_object,
    build_best_material_params,
    save_results_csv,
    save_results_markdown,
    save_full_model_output_csv,
    save_sampled_points_csv,
)


def main():
    project_path = r"C:\Users\bruna\Desktop\EESC-USP\26-1\Dissertacao\teste.gsz"
    analysis_name = "Barragem Curuá-Una"

    observed_data = build_example_observed_data()

    output_dir = Path("outputs_multi_robust")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "resultado_calibracao_conjunta.csv"
    md_path = output_dir / "resultado_calibracao_conjunta.md"
    full_output_csv_path = output_dir / "resultado_bruto_eWaterTotalHead.csv"
    sampled_points_csv_path = output_dir / "resultado_pontos_amostrados.csv"
    plot_path = output_dir / "convergencia.png"

    materials = [
        MaterialCalibrationConfig(
            material_name="Aba Jusante (Areia Silto Argilosa)",
            material_object=build_material_object("Aba Jusante (Areia Silto Argilosa)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[9.0e-8, 3.0e-8, 5.0e-8, 3.0e-9, 5.5e-9, 9.0e-9],
            anisotropia_values=[0.2, 1.0, 0.5, 0.4],
        ),
        MaterialCalibrationConfig(
            material_name="Núcleo (Argila Compactada)",
            material_object=build_material_object("Núcleo (Argila Compactada)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[9.0e-9, 5.5e-9, 3.5e-9, 5.0e-10, 8.5e-10, 9.0e-10],
            anisotropia_values=[0.2, 0.4, 0.8, 0.6],
        ),
        MaterialCalibrationConfig(
            material_name="Dreno Horizontal (Areia)",
            material_object=build_material_object("Dreno Horizontal (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[1.0e-4, 3.5e-4, 4.5e-4, 1.2e-4, 2.2e-4, 5.2e-4],
            anisotropia_values=[0.2, 0.4, 0.5, 1.0],
        ),
        MaterialCalibrationConfig(
            material_name="Fundação Permeável (Areia)",
            material_object=build_material_object("Fundação Permeável (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[4.0e-5, 2.0e-5, 5.0e-5, 1.5e-6, 3.0e-6, 6.0e-6],
            anisotropia_values=[0.2, 1.0, 0.8, 0.6],
        ),
        MaterialCalibrationConfig(
            material_name="Camada Impermeável",
            material_object=build_material_object("Camada Impermeável"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[1.0e-12, 1.2e-12, 1.5e-12, 2.0e-12, 1.8e-12, 0.9e-12],
            anisotropia_values=[0.2, 1.0, 0.9, 0.4],
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

    # ────────────────────────────────────────────────────────────────────────
    # ACO ROBUSTO
    # ────────────────────────────────────────────────────────────────────────
    # Config proven no banco de testes (acerto 100% do ótimo):
    #   n_ants=15, alpha=1.0, rho=0.2, max_iter=80.
    # ATENÇÃO ao custo: cada formiga × iteração é uma simulação do GeoStudio.
    #   15 × 80 = até 1200 solves (o cache reaproveita combinações repetidas).
    # Para um teste rápido, reduza n_ants e max_iter (ex.: n_ants=8, max_iter=20).
    aco = MultiMaterialACORobust(
        material_configs=materials,
        n_ants=15,
        alpha=1.0,
        zeta=2.0,
        rho=0.2,
        tau_min=0.05,
        tau_max=5.0,
        ratio_cap=5.0,
        elitist=True,
        max_iter=80,
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
        "convergiu": resultado.get("convergiu"),
        "n_falhas": resultado.get("n_falhas"),
        "n_avaliacoes": len(resultado.get("cache", {})),
        "melhores_parametros": str(best.get("materials")),
    }

    save_results_csv(csv_path, row)
    save_results_markdown(md_path, resultado, project_path, analysis_name)

    # ============================================================
    # GRÁFICO DE CONVERGÊNCIA (afunilamento do RMSE)
    # ============================================================
    plot_convergencia(
        resultado,
        titulo="Calibração conjunta (ACO robusto) — convergência do RMSE",
        salvar=str(plot_path),
        mostrar=False,  # salva PNG sem bloquear; use True p/ abrir a janela
    )

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
    print("PROCESSAMENTO CONJUNTO (ROBUSTO) FINALIZADO")
    print("=" * 100)
    print(f"Convergiu: {resultado.get('convergiu')} | "
          f"falhas: {resultado.get('n_falhas')} | "
          f"avaliações únicas: {len(resultado.get('cache', {}))}")
    print(f"CSV resumo salvo em: {csv_path}")
    print(f"Markdown resumo salvo em: {md_path}")
    print(f"CSV bruto com eWaterTotalHead salvo em: {full_output_csv_path}")
    print(f"CSV com pontos amostrados salvo em: {sampled_points_csv_path}")
    print(f"Gráfico de convergência salvo em: {plot_path}")


if __name__ == "__main__":
    main()
