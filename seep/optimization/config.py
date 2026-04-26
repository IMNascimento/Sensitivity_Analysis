from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SeepProjectConfig:
    """
    Armazena a configuração necessária para execução de um modelo SEEP no GeoStudio.

    Esta classe centraliza os parâmetros de integração entre o código Python
    e a análise configurada no projeto GeoStudio. Ela define:

    - qual projeto será aberto;
    - qual análise será resolvida;
    - qual material/objeto será alterado;
    - quais campos representam `k` e anisotropia;
    - quais parâmetros de resultado serão consultados;
    - quais opções extras da análise devem ser consideradas.

    Essa configuração é usada principalmente pela classe `SeepModel`, que
    interpreta esses atributos para abrir o projeto, alterar parâmetros,
    resolver a análise e consultar resultados.

    Attributes:
        project_path (str):
            Caminho absoluto ou relativo do arquivo do projeto GeoStudio
            (`.gsz`) que será aberto.

        analysis_name (str):
            Nome exato da análise dentro do projeto GeoStudio que será usada
            nas operações de `Get`, `Set`, `SolveAnalyses`, `LoadResults`
            e `QueryResults`.

        material_object (str):
            Caminho completo do objeto do material na árvore do GeoStudio
            que será usado como alvo da calibração.
            Exemplo:
            `Materials["Tapete Permeável (Areia)"]`

        k_field_name (str):
            Nome do campo hidráulico do material que representa a condutividade
            a ser calibrada.
            Exemplo típico:
            `KSat`

        anisotropy_field_name (str):
            Nome do campo hidráulico do material que representa a anisotropia.
            Exemplo típico:
            `KYXRatio`

        use_anisotropy (bool):
            Indica se a anisotropia deve ou não ser alterada durante as
            execuções do modelo.

            - Se `False`, apenas o parâmetro `k` será atualizado.
            - Se `True`, o modelo tentará atualizar também o campo de anisotropia.

        result_table (str):
            Nome textual da tabela de resultados do GeoStudio que será
            consultada via `QueryResults`.
            Exemplo típico:
            `Nodes`

        x_param (str):
            Nome textual do parâmetro de resultado correspondente à coordenada X.
            Exemplo:
            `eXCoord`

        y_param (str):
            Nome textual do parâmetro de resultado correspondente à coordenada Y.
            Exemplo:
            `eYCoord`

        value_param (str):
            Nome textual do parâmetro de resultado que representa a variável
            de interesse para comparação com os dados observados.
            Exemplo:
            `eWaterTotalHead`

        step (int):
            Número do passo (step) da análise cujos resultados serão consultados.

        run (Optional[int]):
            Número da execução (`run`) a ser usado na consulta de resultados,
            quando aplicável. Se `None`, esse campo não é enviado explicitamente
            na requisição.

        instance (Optional[int]):
            Número da instância a ser usado na consulta de resultados,
            quando aplicável. Se `None`, esse campo não é enviado explicitamente
            na requisição.

        solve_dependencies (bool):
            Indica se as dependências da análise também devem ser resolvidas
            ao chamar `SolveAnalyses`.
    """

    project_path: str
    analysis_name: str

    material_object: str = 'Materials["Tapete Permeável (Areia)"]'

    k_field_name: str = "KSat"
    anisotropy_field_name: str = "KYXRatio"

    use_anisotropy: bool = False

    result_table: str = "Nodes"
    x_param: str = "eXCoord"
    y_param: str = "eYCoord"
    value_param: str = "eWaterTotalHead"

    step: int = 1
    run: Optional[int] = None
    instance: Optional[int] = None
    solve_dependencies: bool = True


@dataclass
class ACOConfig:
    """
    Armazena os hiperparâmetros e o espaço de busca do algoritmo ACO.

    Esta classe define todos os parâmetros necessários para executar a
    otimização por Colônia de Formigas (Ant Colony Optimization - ACO)
    aplicada à calibração do modelo.

    Ela inclui:
    - o espaço discreto de valores possíveis para `k`;
    - o espaço discreto de valores possíveis para anisotropia;
    - parâmetros de controle do algoritmo;
    - critério de convergência;
    - penalidade para falhas de execução.

    Attributes:
        k_values (List[float]):
            Lista de valores discretos possíveis para o parâmetro `k`
            que o ACO poderá testar.

        anisotropia_values (List[float]):
            Lista de valores discretos possíveis para anisotropia que o
            ACO poderá testar.

            Observação:
            Se o modelo estiver com `use_anisotropy=False`, esses valores
            podem ser ignorados na prática, mas ainda podem existir para
            manter compatibilidade estrutural.

        n_ants (int):
            Número de formigas por iteração do ACO.

        zeta (float):
            Intensidade do reforço de feromônio dado à melhor solução
            de cada iteração.

        rho (float):
            Taxa de evaporação do feromônio.
            Controla o quanto o algoritmo “esquece” soluções antigas.

        max_iter (int):
            Número máximo de iterações do ACO.

        tolerancia (float):
            Critério de convergência baseado no erro.
            Se o melhor RMSE da iteração ficar abaixo desse valor,
            o algoritmo pode encerrar antecipadamente.

        penalty_rmse (float):
            Valor de penalidade aplicado quando ocorre erro na execução
            do modelo ou no cálculo da função objetivo.
            Isso evita interromper a otimização inteira por falha em uma
            única combinação de parâmetros.
    """

    k_values: List[float] = field(default_factory=lambda: [1e-7, 5e-7, 1e-6, 5e-6, 1e-5])
    anisotropia_values: List[float] = field(default_factory=lambda: [0.5, 1.0, 2.0, 5.0, 10.0])
    n_ants: int = 4
    zeta: float = 2.0
    rho: float = 0.3
    max_iter: int = 50
    tolerancia: float = 0.01
    penalty_rmse: float = 1e12

@dataclass
class MaterialCalibrationConfig:
    """
    Configuração de calibração de um material individual.

    Attributes:
        material_name:
            Nome do material no GeoStudio.

        material_object:
            Caminho completo do objeto do material.

        k_field_name:
            Nome do campo de condutividade.

        anisotropy_field_name:
            Nome do campo de anisotropia.

        k_values:
            Lista discreta de valores de k a testar.

        anisotropia_values:
            Lista discreta de valores de anisotropia a testar.
        """
    material_name: str
    material_object: str
    k_field_name: str = "KSat"
    anisotropy_field_name: str = "KYXRatio"
    k_values: List[float] = field(default_factory=list)
    anisotropia_values: List[float] = field(default_factory=list)


@dataclass
class MultiMaterialSeepConfig:
    """
    Configuração do projeto SEEP para calibração conjunta de múltiplos materiais.

    Attributes:
        project_path:
            Caminho do arquivo .gsz.

        analysis_name:
            Nome da análise.

        materials:
            Lista de materiais que participarão da calibração conjunta.

        use_anisotropy:
            Se True, a anisotropia de cada material também será calibrada.

        result_table:
            Tabela de resultados a consultar.

        x_param:
            Parâmetro de coordenada X.

        y_param:
            Parâmetro de coordenada Y.

        value_param:
            Variável de interesse.

        step:
            Step da análise.

        run:
            Run opcional da análise.

        instance:
            Instance opcional da análise.

        solve_dependencies:
            Se True, resolve dependências da análise.
    """
    project_path: str
    analysis_name: str
    materials: List[MaterialCalibrationConfig]

    use_anisotropy: bool = True

    result_table: str = "Nodes"
    x_param: str = "eXCoord"
    y_param: str = "eYCoord"
    value_param: str = "eWaterTotalHead"

    step: int = 1
    run: Optional[int] = None
    instance: Optional[int] = None
    solve_dependencies: bool = True