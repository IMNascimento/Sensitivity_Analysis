import grpc
import numpy as np
import gsi
from google.protobuf import json_format

from config import SeepProjectConfig


class SeepModel:
    """
    Encapsula a comunicação com um projeto GeoStudio/SEEP por meio da API gRPC.

    Esta classe centraliza as responsabilidades de:
    - abrir e manter a sessão do projeto;
    - inspecionar objetos do modelo via `Get`;
    - escrever parâmetros escalares via `Set`;
    - atualizar parâmetros hidráulicos do material alvo;
    - resolver a análise;
    - carregar e consultar resultados;
    - devolver os resultados do modelo em formato NumPy.

    A classe foi desenhada para um fluxo de calibração, em que um otimizador
    externo (por exemplo, um ACO) chama repetidamente o método `run(k, anisotropia)`
    com diferentes combinações de parâmetros.

    A configuração do comportamento da classe depende de um objeto
    `SeepProjectConfig`, que informa, entre outros pontos:
    - caminho do projeto;
    - nome da análise;
    - objeto do material a ser alterado;
    - nomes dos campos de `k` e anisotropia;
    - parâmetros de consulta dos resultados.

    Attributes:
        config (SeepProjectConfig):
            Objeto de configuração com os metadados do projeto, análise,
            material e parâmetros de resultado.

        project (gsi.Project | None):
            Referência para o projeto aberto via API gRPC.
            Permanece `None` até que `open_project()` seja chamado.
    """

    def __init__(self, config: SeepProjectConfig):
        """
        Inicializa o modelo SEEP com uma configuração específica.

        Args:
            config (SeepProjectConfig):
                Configuração contendo o caminho do projeto, nome da análise,
                objeto do material, campos hidráulicos e parâmetros de consulta
                dos resultados.
        """
        self.config = config
        self.project = None

    def open_project(self) -> None:
        """
        Abre o projeto GeoStudio, se ele ainda não estiver aberto.

        Este método cria a sessão gRPC com o projeto usando o caminho definido
        em `self.config.project_path`. Se o projeto já estiver aberto,
        o método não faz nada.

        Returns:
            None
        """
        if self.project is None:
            print("[DEBUG] Abrindo projeto...")
            self.project = gsi.OpenProject(self.config.project_path)
            print("[DEBUG] Projeto aberto com sucesso.")

    def close_project(self) -> None:
        """
        Fecha o projeto GeoStudio atualmente aberto.

        Este método tenta encerrar a sessão do projeto via `project.Close()`.
        Mesmo que ocorra erro no fechamento, a referência local `self.project`
        é limpa no bloco `finally`.

        Returns:
            None

        Notes:
            Em alguns ambientes, o fechamento do projeto pode travar ou falhar.
            Nesses casos, pode ser preferível manter a sessão aberta até o final
            do processamento e não chamar este método entre execuções.
        """
        if self.project is not None:
            try:
                print("[DEBUG] Fechando projeto...")
                self.project.Close()
                print("[DEBUG] Projeto fechado.")
            except Exception as e:
                print(f"[DEBUG] Erro ao fechar projeto: {repr(e)}")
            finally:
                self.project = None

    def _require_project(self) -> None:
        """
        Garante que o projeto esteja aberto antes de executar operações gRPC.

        Raises:
            RuntimeError:
                Se `self.project` for `None`, indicando que `open_project()`
                ainda não foi chamado.
        """
        if self.project is None:
            raise RuntimeError("Projeto não está aberto. Chame open_project() antes.")

    def _python_to_gsi_value(self, obj):
        """
        Converte objetos Python para `gsi.Value`.

        Este método faz a serialização recursiva de tipos Python para o tipo
        dinâmico `gsi.Value`, que é usado pela API gRPC do GeoStudio em
        chamadas como `Set`.

        Tipos suportados:
        - `None`
        - `bool`
        - `int`
        - `float`
        - `str`
        - `list`
        - `dict`

        Args:
            obj (Any):
                Objeto Python a ser convertido.

        Returns:
            gsi.Value:
                Estrutura equivalente no formato aceito pela API GeoStudio.

        Raises:
            TypeError:
                Se o tipo do objeto não for suportado.
        """
        value = gsi.Value()

        if obj is None:
            value.null_value = 0
            return value

        if isinstance(obj, bool):
            value.bool_value = obj
            return value

        if isinstance(obj, (int, float)):
            value.number_value = float(obj)
            return value

        if isinstance(obj, str):
            value.string_value = obj
            return value

        if isinstance(obj, list):
            for item in obj:
                value.list_value.values.add().CopyFrom(self._python_to_gsi_value(item))
            return value

        if isinstance(obj, dict):
            for k, v in obj.items():
                value.struct_value.fields[k].CopyFrom(self._python_to_gsi_value(v))
            return value

        raise TypeError(f"Tipo não suportado para conversão em gsi.Value: {type(obj)}")

    def inspect_object(self, object_path: str):
        """
        Consulta um objeto qualquer da árvore do projeto via `Get`.

        Este método é útil para exploração e depuração da árvore interna exposta
        pela API gRPC, permitindo inspecionar:
        - materiais;
        - subcampos hidráulicos;
        - parâmetros individuais;
        - outros objetos do projeto.

        Args:
            object_path (str):
                Caminho do objeto a ser consultado na árvore do GeoStudio.

        Returns:
            dict:
                Conteúdo do objeto retornado pela API, convertido para `dict`
                com `json_format.MessageToDict`.

        Raises:
            RuntimeError:
                Se o projeto não estiver aberto.

            grpc.RpcError:
                Se a API retornar erro para o objeto consultado.
        """
        self.open_project()
        self._require_project()

        print(f"[DEBUG] Executando Get para object={object_path}")
        response = self.project.Get(
            gsi.GetRequest(
                analysis=self.config.analysis_name,
                object=object_path,
            )
        )
        print("[DEBUG] Get concluído com sucesso.")

        data = json_format.MessageToDict(response)
        print("[DEBUG] Conversão para dict concluída.")
        print("[DEBUG] DADOS:")
        print(data)
        return data

    def _set_single_field(self, field_object_path: str, value_payload: dict) -> None:
        """
        Escreve um único campo da árvore do projeto via `Set`.

        Este método é usado para gravar objetos simples, normalmente do tipo:
        `{"Value": ..., "Units": ...}`.

        Exemplo de uso:
        - `Materials["Material X"].Hydraulic.KSat`
        - `Materials["Material X"].Hydraulic.KYXRatio`

        Args:
            field_object_path (str):
                Caminho completo do campo a ser escrito.

            value_payload (dict):
                Payload no formato esperado pela API, tipicamente contendo
                chaves como `Value` e `Units`.

        Returns:
            None

        Raises:
            RuntimeError:
                Se o projeto não estiver aberto.

            grpc.RpcError:
                Se a API rejeitar a escrita do campo.
        """
        self._require_project()

        value = self._python_to_gsi_value(value_payload)

        self.project.Set(
            gsi.SetRequest(
                analysis=self.config.analysis_name,
                object=field_object_path,
                data=value,
            )
        )

    def debug_test_set_individual_fields(self, k: float, anisotropia: float) -> None:
        """
        Executa um teste de escrita dos campos hidráulicos do material alvo.

        Este método foi criado para depuração. Ele:
        1. consulta o valor atual de `KSat`;
        2. monta e escreve o payload correspondente;
        3. se anisotropia estiver ativa, faz o mesmo para o campo de anisotropia.

        O método imprime os valores atuais e os payloads enviados.

        Args:
            k (float):
                Novo valor de `k` a ser gravado no campo hidráulico configurado.

            anisotropia (float):
                Novo valor de anisotropia a ser gravado, caso
                `self.config.use_anisotropy` seja True.

        Returns:
            None

        Notes:
            Este método é orientado a debug e validação de integração com a API.
            Não deve ser o único caminho usado em produção para calibrar parâmetros.
        """
        self.open_project()
        self._require_project()

        k_path = self.config.material_object + ".Hydraulic." + self.config.k_field_name

        print("=" * 80)
        print("DEBUG - TESTE DE SET DOS CAMPOS INDIVIDUAIS")
        print("=" * 80)

        k_current = self.inspect_object(k_path)["data"]
        print("[DEBUG] K atual:")
        print(k_current)

        k_payload = {
            "Value": float(k),
            "Units": k_current["Units"],
        }

        print("[DEBUG] Payload K:")
        print(k_payload)

        self._set_single_field(k_path, k_payload)
        print("[SUCESSO] KSat atualizado.")

        if self.config.use_anisotropy:
            a_path = self.config.material_object + ".Hydraulic." + self.config.anisotropy_field_name
            a_current = self.inspect_object(a_path)["data"]

            print("[DEBUG] Anisotropia atual:")
            print(a_current)

            a_payload = {
                "Value": float(anisotropia),
                "Units": a_current["Units"],
            }

            print("[DEBUG] Payload Anisotropia:")
            print(a_payload)

            self._set_single_field(a_path, a_payload)
            print("[SUCESSO] Anisotropia atualizada.")

    def _set_material_params(self, k: float, anisotropia: float) -> None:
        """
        Atualiza os parâmetros hidráulicos do material alvo antes da simulação.

        Este método é o caminho interno usado por `run()` e `debug_single_run()`
        para aplicar os parâmetros que estão sendo calibrados.

        Atualmente:
        - sempre atualiza o campo `k`;
        - atualiza a anisotropia somente se `self.config.use_anisotropy` for True.

        Args:
            k (float):
                Valor de `k` a ser aplicado ao material alvo.

            anisotropia (float):
                Valor de anisotropia a ser aplicado ao material alvo,
                caso a anisotropia esteja habilitada.

        Returns:
            None

        Raises:
            RuntimeError:
                Se o projeto não estiver aberto.

            grpc.RpcError:
                Se a API rejeitar algum `Set`.
        """
        self._require_project()

        k_path = self.config.material_object + ".Hydraulic." + self.config.k_field_name

        k_current = self.project.Get(
            gsi.GetRequest(
                analysis=self.config.analysis_name,
                object=k_path,
            )
        )
        k_data = json_format.MessageToDict(k_current)["data"]

        self._set_single_field(
            k_path,
            {
                "Value": float(k),
                "Units": k_data["Units"],
            }
        )

        if self.config.use_anisotropy:
            a_path = self.config.material_object + ".Hydraulic." + self.config.anisotropy_field_name

            a_current = self.project.Get(
                gsi.GetRequest(
                    analysis=self.config.analysis_name,
                    object=a_path,
                )
            )
            a_data = json_format.MessageToDict(a_current)["data"]

            self._set_single_field(
                a_path,
                {
                    "Value": float(anisotropia),
                    "Units": a_data["Units"],
                }
            )

    def run(self, k: float, anisotropia: float) -> np.ndarray:
        """
        Executa um ciclo completo de simulação com os parâmetros fornecidos.

        Fluxo executado:
        1. abre o projeto, se necessário;
        2. atualiza os parâmetros do material alvo;
        3. resolve a análise;
        4. carrega os resultados;
        5. verifica se os resultados estão disponíveis;
        6. consulta os resultados e devolve em formato NumPy.

        Args:
            k (float):
                Valor de `k` a ser testado no modelo.

            anisotropia (float):
                Valor de anisotropia a ser testado no modelo.

        Returns:
            np.ndarray:
                Array com shape `(n, 3)` no formato:
                `[x, y, valor_modelado]`.

        Raises:
            RuntimeError:
                Se ocorrer erro gRPC ou erro geral durante a execução.
        """
        try:
            self.open_project()

            self._set_material_params(k=k, anisotropia=anisotropia)
            self._solve()
            self._load_results()
            self._assert_results_available()

            return self._query_results()

        except grpc.RpcError as e:
            raise RuntimeError(f"Erro gRPC no GeoStudio: {e.code()} - {e.details()}") from e
        except Exception as e:
            raise RuntimeError(f"Erro ao executar modelo SEEP: {e}") from e

    def debug_single_run(self, k: float, anisotropia: float) -> np.ndarray:
        """
        Executa uma simulação única com logs detalhados de depuração.

        Este método é equivalente a `run()`, mas imprime informações de cada etapa:
        - atualização do material;
        - solução da análise;
        - carregamento dos resultados;
        - consulta final dos resultados.

        Args:
            k (float):
                Valor de `k` a ser aplicado.

            anisotropia (float):
                Valor de anisotropia a ser aplicado.

        Returns:
            np.ndarray:
                Array com shape `(n, 3)` no formato:
                `[x, y, valor_modelado]`.

        Notes:
            Este método é útil para validar a integração antes de rodar
            processos iterativos como ACO.
        """
        self.open_project()
        self._require_project()

        print("=" * 80)
        print("DEBUG - EXECUÇÃO ÚNICA")
        print("=" * 80)

        self._set_material_params(k=k, anisotropia=anisotropia)
        print("[DEBUG] Campos do material atualizados com sucesso.")

        self._solve()
        print("[DEBUG] Solve concluído.")

        self._load_results()
        print("[DEBUG] LoadResults concluído.")

        self._assert_results_available()
        print("[DEBUG] Resultados disponíveis.")

        result = self._query_results()
        print(f"[DEBUG] QueryResults retornou {result.shape[0]} linhas.")
        print(result[:10])

        return result

    def _solve(self) -> None:
        """
        Resolve a análise configurada no projeto.

        Usa `SolveAnalysesRequest` com o nome da análise em
        `self.config.analysis_name` e com a opção de resolver dependências
        conforme `self.config.solve_dependencies`.

        Returns:
            None
        """
        self._require_project()
        request = gsi.SolveAnalysesRequest(
            analyses=[self.config.analysis_name],
            solve_dependencies=self.config.solve_dependencies,
        )
        self.project.SolveAnalyses(request)

    def _load_results(self) -> None:
        """
        Carrega os resultados da análise configurada.

        Este método deve ser chamado após a resolução da análise
        para permitir consultas posteriores via `QueryResults`.

        Returns:
            None
        """
        self._require_project()
        request = gsi.LoadResultsRequest(
            analysis=self.config.analysis_name
        )
        self.project.LoadResults(request)

    def _assert_results_available(self) -> None:
        """
        Verifica se há resultados disponíveis para a análise atual.

        Returns:
            None

        Raises:
            RuntimeError:
                Se a análise tiver sido executada, mas os resultados
                não estiverem disponíveis para consulta.
        """
        self._require_project()
        request = gsi.QueryResultsAvailabilityRequest(
            analysis=self.config.analysis_name
        )
        response = self.project.QueryResultsAvailability(request)
        if not response.has_results:
            raise RuntimeError("A análise foi executada, mas não há resultados disponíveis.")

    def _query_results(self) -> np.ndarray:
        """
        Consulta os resultados numéricos da análise.

        O método consulta três parâmetros definidos em `self.config`:
        - coordenada X;
        - coordenada Y;
        - valor da variável de interesse (por exemplo, `eWaterTotalHead`).

        A saída é um array NumPy com três colunas no formato:

            [x, y, valor_modelado]

        Args:
            None

        Returns:
            np.ndarray:
                Array com shape `(n, 3)` contendo os resultados consultados.

        Raises:
            RuntimeError:
                Se os vetores retornados tiverem tamanhos diferentes.
        """
        self._require_project()

        query_request = gsi.QueryResultsRequest(
            analysis=self.config.analysis_name,
            table=self._resolve_result_table(),
            dataparams=[
                self._resolve_data_param(self.config.x_param),
                self._resolve_data_param(self.config.y_param),
                self._resolve_data_param(self.config.value_param),
            ],
            step=self.config.step,
        )

        if self.config.run is not None:
            query_request.run = self.config.run

        if self.config.instance is not None:
            query_request.instance = self.config.instance

        response = self.project.QueryResults(query_request)

        x_enum = self._resolve_data_param(self.config.x_param)
        y_enum = self._resolve_data_param(self.config.y_param)
        v_enum = self._resolve_data_param(self.config.value_param)

        x = np.array(response.results[x_enum].values, dtype=float)
        y = np.array(response.results[y_enum].values, dtype=float)
        v = np.array(response.results[v_enum].values, dtype=float)

        if not (len(x) == len(y) == len(v)):
            raise RuntimeError("Os vetores retornados por QueryResults têm tamanhos diferentes.")

        return np.column_stack([x, y, v])

    def _resolve_result_table(self):
        """
        Resolve o nome textual da tabela de resultados para o enum do GeoStudio.

        Exemplo:
            `"Nodes"` -> `gsi.ResultType.Nodes`

        Returns:
            Any:
                Enum correspondente da tabela de resultados.

        Raises:
            ValueError:
                Se a tabela configurada não existir em `gsi.ResultType`.
        """
        if not hasattr(gsi.ResultType, self.config.result_table):
            raise ValueError(
                f"ResultType '{self.config.result_table}' não encontrado em gsi.ResultType."
            )
        return getattr(gsi.ResultType, self.config.result_table)

    def _resolve_data_param(self, param_name: str):
        """
        Resolve o nome textual de um parâmetro de resultado para o enum do GeoStudio.

        Exemplo:
            `"eXCoord"` -> `gsi.DataParamType.eXCoord`

        Args:
            param_name (str):
                Nome textual do parâmetro de resultado.

        Returns:
            Any:
                Enum correspondente do parâmetro em `gsi.DataParamType`.

        Raises:
            ValueError:
                Se o parâmetro informado não existir em `gsi.DataParamType`.
        """
        if not hasattr(gsi.DataParamType, param_name):
            raise ValueError(
                f"DataParamType '{param_name}' não encontrado em gsi.DataParamType."
            )
        return getattr(gsi.DataParamType, param_name)