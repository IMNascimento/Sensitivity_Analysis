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
    - escrever parâmetros hidráulicos em formatos distintos;
    - atualizar parâmetros do material alvo;
    - resolver a análise;
    - carregar e consultar resultados;
    - devolver os resultados do modelo em formato NumPy.
    """

    def __init__(self, config: SeepProjectConfig):
        """
        Inicializa o modelo SEEP com uma configuração específica.

        Args:
            config:
                Configuração do projeto, análise, material alvo e parâmetros
                de consulta dos resultados.
        """
        self.config = config
        self.project = None

    # ============================================================
    # Sessão
    # ============================================================
    def open_project(self) -> None:
        """
        Abre o projeto GeoStudio, se ele ainda não estiver aberto.
        """
        if self.project is None:
            print("[DEBUG] Abrindo projeto...")
            self.project = gsi.OpenProject(self.config.project_path)
            print("[DEBUG] Projeto aberto com sucesso.")

    def close_project(self) -> None:
        """
        Fecha o projeto GeoStudio atualmente aberto.

        Notes:
            Se o seu ambiente travar ao fechar, este método pode ser evitado
            entre execuções intermediárias e usado apenas no final, ou sequer
            chamado, deixando o processo Python encerrar a sessão.
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
        Garante que o projeto esteja aberto.

        Raises:
            RuntimeError:
                Se `open_project()` ainda não tiver sido chamado.
        """
        if self.project is None:
            raise RuntimeError("Projeto não está aberto. Chame open_project() antes.")

    # ============================================================
    # Conversão Python -> gsi.Value
    # ============================================================
    def _python_to_gsi_value(self, obj):
        """
        Converte objetos Python para `gsi.Value`.

        Suporta:
        - None
        - bool
        - int / float
        - str
        - list
        - dict

        Args:
            obj:
                Objeto Python a ser convertido.

        Returns:
            gsi.Value correspondente.

        Raises:
            TypeError:
                Se o tipo não for suportado.
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

    # ============================================================
    # Leitura / inspeção
    # ============================================================
    def inspect_object(self, object_path: str):
        """
        Consulta um objeto da árvore do GeoStudio via `Get`.

        Args:
            object_path:
                Caminho do objeto na árvore do GeoStudio.

        Returns:
            Dict convertido da resposta da API.
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

    # ============================================================
    # Escrita - dois formatos
    # ============================================================
    def _set_single_struct_field(self, field_object_path: str, value_payload: dict) -> None:
        """
        Escreve um campo via `Set` usando payload estruturado.

        Esse formato é adequado para campos que esperam algo como:
            {"Value": ..., "Units": ...}

        Exemplo típico:
            KSat

        Args:
            field_object_path:
                Caminho do campo a ser escrito.

            value_payload:
                Payload estruturado.
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

    def _set_single_number_field(self, field_object_path: str, value_number: float) -> None:
        """
        Escreve um campo via `Set` usando `number_value` puro.

        Esse formato é adequado para campos que aceitam escalar simples,
        como observado no exemplo funcional para:
        - KYXRatio
        - KZXRatio
        - DipAngle
        - DipDirection

        Args:
            field_object_path:
                Caminho do campo a ser escrito.

            value_number:
                Valor escalar a ser enviado.
        """
        self._require_project()

        self.project.Set(
            gsi.SetRequest(
                analysis=self.config.analysis_name,
                object=field_object_path,
                data=gsi.Value(number_value=float(value_number)),
            )
        )

    # ============================================================
    # Debug de escrita
    # ============================================================
    def debug_test_set_individual_fields(self, k: float, anisotropia: float) -> None:
        """
        Testa a escrita dos campos individuais do material alvo.

        Regras atuais:
        - KSat é escrito via struct {Value, Units}
        - anisotropia é escrita via number_value puro

        Args:
            k:
                Valor de KSat a ser testado.

            anisotropia:
                Valor de anisotropia a ser testado.
        """
        self.open_project()
        self._require_project()

        print("=" * 80)
        print("DEBUG - TESTE DE SET DOS CAMPOS INDIVIDUAIS")
        print("=" * 80)

        # --------------------------------------------------------
        # KSat -> struct
        # --------------------------------------------------------
        k_path = self.config.material_object + ".Hydraulic." + self.config.k_field_name
        k_current = self.inspect_object(k_path)["data"]

        print("[DEBUG] K atual:")
        print(k_current)

        k_payload = {
            "Value": float(k),
            "Units": k_current["Units"],
        }

        print("[DEBUG] Payload K (struct):")
        print(k_payload)

        self._set_single_struct_field(k_path, k_payload)
        print("[SUCESSO] KSat atualizado.")

        # --------------------------------------------------------
        # Anisotropia -> number_value
        # --------------------------------------------------------
        if self.config.use_anisotropy:
            a_path = self.config.material_object + ".Hydraulic." + self.config.anisotropy_field_name
            a_current = self.inspect_object(a_path)["data"]

            print("[DEBUG] Anisotropia atual:")
            print(a_current)

            print("[DEBUG] Payload Anisotropia (number_value):")
            print(float(anisotropia))

            self._set_single_number_field(a_path, float(anisotropia))
            print("[SUCESSO] Anisotropia atualizada.")

    # ============================================================
    # Atualização de parâmetros do material
    # ============================================================
    def _set_material_params(self, k: float, anisotropia: float) -> None:
        """
        Atualiza os parâmetros hidráulicos do material alvo.

        Estratégia adotada:
        - KSat: struct `{Value, Units}`
        - anisotropia: `number_value` puro

        Args:
            k:
                Valor de `k` a aplicar ao material alvo.

            anisotropia:
                Valor de anisotropia a aplicar ao material alvo.
        """
        self._require_project()

        # --------------------------------------------------------
        # KSat -> struct com units
        # --------------------------------------------------------
        k_path = self.config.material_object + ".Hydraulic." + self.config.k_field_name

        k_current = self.project.Get(
            gsi.GetRequest(
                analysis=self.config.analysis_name,
                object=k_path,
            )
        )
        k_data = json_format.MessageToDict(k_current)["data"]

        self._set_single_struct_field(
            k_path,
            {
                "Value": float(k),
                "Units": k_data["Units"],
            }
        )

        # --------------------------------------------------------
        # Anisotropia -> number_value puro
        # --------------------------------------------------------
        if self.config.use_anisotropy:
            a_path = self.config.material_object + ".Hydraulic." + self.config.anisotropy_field_name
            self._set_single_number_field(a_path, float(anisotropia))

    # ============================================================
    # Execução do modelo
    # ============================================================
    def run(self, k: float, anisotropia: float) -> np.ndarray:
        """
        Executa um ciclo completo de simulação com os parâmetros fornecidos.

        Fluxo:
        1. abre o projeto, se necessário;
        2. atualiza os parâmetros do material alvo;
        3. resolve a análise;
        4. carrega os resultados;
        5. verifica disponibilidade dos resultados;
        6. consulta os resultados e devolve NumPy array.

        Args:
            k:
                Valor de `k` a testar.

            anisotropia:
                Valor de anisotropia a testar.

        Returns:
            Array com shape `(n, 3)` no formato:
            `[x, y, valor_modelado]`.
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
        Executa uma simulação única com logs detalhados.

        Args:
            k:
                Valor de `k` a aplicar.

            anisotropia:
                Valor de anisotropia a aplicar.

        Returns:
            Array com shape `(n, 3)` no formato:
            `[x, y, valor_modelado]`.
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

    # ============================================================
    # Solve / results
    # ============================================================
    def _solve(self) -> None:
        """
        Resolve a análise configurada.
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
        """
        self._require_project()
        request = gsi.LoadResultsRequest(
            analysis=self.config.analysis_name
        )
        self.project.LoadResults(request)

    def _assert_results_available(self) -> None:
        """
        Verifica se há resultados disponíveis para consulta.

        Raises:
            RuntimeError:
                Se a análise não tiver resultados disponíveis.
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

        Returns:
            Array com shape `(n, 3)` no formato:
            `[x, y, valor_modelado]`.
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

    # ============================================================
    # Resolução de enums
    # ============================================================
    def _resolve_result_table(self):
        """
        Resolve o nome textual da tabela de resultados para enum do GeoStudio.
        """
        if not hasattr(gsi.ResultType, self.config.result_table):
            raise ValueError(
                f"ResultType '{self.config.result_table}' não encontrado em gsi.ResultType."
            )
        return getattr(gsi.ResultType, self.config.result_table)

    def _resolve_data_param(self, param_name: str):
        """
        Resolve o nome textual de um parâmetro de resultado para enum do GeoStudio.
        """
        if not hasattr(gsi.DataParamType, param_name):
            raise ValueError(
                f"DataParamType '{param_name}' não encontrado em gsi.DataParamType."
            )
        return getattr(gsi.DataParamType, param_name)