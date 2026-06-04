"""
Fonte ÚNICA de verdade da configuração de materiais da barragem.

Tanto o main de produção (main_multi_material_robust.py) quanto o banco de
testes (tests/test_aco_mock.py) importam daqui. Assim, ao alterar os materiais
ou seus espaços de busca (k_values / anisotropia_values), o teste sintético
passa a refletir EXATAMENTE a mesma configuração da calibração real — sem
precisar duplicar a lista nem deixar os dois fora de sincronia.

Este módulo NÃO importa nada do GeoStudio (grpc/gsi), então pode ser importado
em qualquer ambiente, inclusive na máquina sem o GeoStudio.
"""

from config import MaterialCalibrationConfig


def material_object(material_name: str) -> str:
    """Caminho do objeto do material na árvore do GeoStudio."""
    return f'Materials["{material_name}"]'


def build_barragem_materials():
    """
    Devolve a lista de MaterialCalibrationConfig da barragem.

    Edite AQUI (e somente aqui) os materiais e seus espaços de busca discretos.
    """
    return [
        MaterialCalibrationConfig(
            material_name="Aba Jusante (Areia Silto Argilosa)",
            material_object=material_object("Aba Jusante (Areia Silto Argilosa)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[9.0e-8, 3.0e-8, 5.0e-8, 3.0e-9, 5.5e-9, 9.0e-9],
            anisotropia_values=[0.2, 1.0, 0.5, 0.4],
        ),
        MaterialCalibrationConfig(
            material_name="Núcleo (Argila Compactada)",
            material_object=material_object("Núcleo (Argila Compactada)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[9.0e-9, 5.5e-9, 3.5e-9, 5.0e-10, 8.5e-10, 9.0e-10],
            anisotropia_values=[0.2, 0.4, 0.8, 0.6],
        ),
        MaterialCalibrationConfig(
            material_name="Dreno Horizontal (Areia)",
            material_object=material_object("Dreno Horizontal (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[1.0e-4, 3.5e-4, 4.5e-4, 1.2e-4, 2.2e-4, 5.2e-4],
            anisotropia_values=[0.2, 0.4, 0.5, 1.0],
        ),
        MaterialCalibrationConfig(
            material_name="Fundação Permeável (Areia)",
            material_object=material_object("Fundação Permeável (Areia)"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[4.0e-5, 2.0e-5, 5.0e-5, 1.5e-6, 3.0e-6, 6.0e-6],
            anisotropia_values=[0.2, 1.0, 0.8, 0.6],
        ),
        MaterialCalibrationConfig(
            material_name="Camada Impermeável",
            material_object=material_object("Camada Impermeável"),
            k_field_name="KSat",
            anisotropy_field_name="KYXRatio",
            k_values=[1.0e-12, 1.2e-12, 1.5e-12, 2.0e-12, 1.8e-12, 0.9e-12],
            anisotropia_values=[0.2, 1.0, 0.9, 0.4],
        ),
    ]
