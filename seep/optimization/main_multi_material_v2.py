"""
Main de calibração conjunta multi-material usando o ACO v2 (FIEL AO LIVRO).

Espelha o main_multi_material_robust.py, mas usa MultiMaterialACOv2 — a
implementação fiel ao algoritmo de Rao (2009, Seção 13.5), adaptada para RMSE
e múltiplos materiais. Serve para COMPARAR o algoritmo "de livro" com o robusto.

ATENÇÃO: o v2 (algoritmo puro do livro) tende a CONVERGÊNCIA PREMATURA em
espaços de busca grandes (trava num ótimo local). Para produção, prefira
main_multi_material_robust.py. Este main existe para fins de estudo/comparação.

Fonte de materiais e helpers de salvamento são compartilhados (barragem_materials
e main_multi_material), garantindo a MESMA configuração do main robusto.
"""

from pathlib import Path

from config import MultiMaterialSeepConfig
from seep_model import SeepModel
from objective_function import RMSEObjectiveFunction
from aco_multi_v2 import MultiMaterialACOv2
from convergence_plot import plot_convergencia
from barragem_materials import build_barragem_materials

from main_multi_material import (
    build_example_observed_data,
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

    output_dir = Path("outputs_multi_v2")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "resultado_calibracao_conjunta.csv"
    md_path = output_dir / "resultado_calibracao_conjunta.md"
    full_output_csv_path = output_dir / "resultado_bruto_eWaterTotalHead.csv"
    sampled_points_csv_path = output_dir / "resultado_pontos_amostrados.csv"
    plot_path = output_dir / "convergencia.png"

    # Fonte única de verdade dos materiais (mesma do main robusto e do teste).
    materials = build_barragem_materials()

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
    # ACO v2 — parâmetros do LIVRO (ρ ∈ [0.5, 0.8], α = 1.0).
    # Sem Max-Min Ant System: propenso a convergência prematura em espaços
    # grandes. Comparar o gráfico de convergência com o do main robusto.
    # ────────────────────────────────────────────────────────────────────────
    aco = MultiMaterialACOv2(
        material_configs=materials,
        n_ants=15,
        alpha=1.0,
        zeta=2.0,
        rho=0.5,
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
        titulo="Calibração conjunta (ACO v2 / livro) — convergência do RMSE",
        salvar=str(plot_path),
        mostrar=False,
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
    print("PROCESSAMENTO CONJUNTO (v2 / LIVRO) FINALIZADO")
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
