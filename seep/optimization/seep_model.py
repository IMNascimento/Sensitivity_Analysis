import grpc
import numpy as np
import gsi
from google.protobuf import json_format

from config import SeepProjectConfig


class SeepModel:
    def __init__(self, config: SeepProjectConfig):
        self.config = config
        self.project = None

    def open_project(self) -> None:
        if self.project is None:
            print("[DEBUG] Abrindo projeto...")
            self.project = gsi.OpenProject(self.config.project_path)
            print("[DEBUG] Projeto aberto com sucesso.")

    def close_project(self) -> None:
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
        if self.project is None:
            raise RuntimeError("Projeto não está aberto. Chame open_project() antes.")

    def _python_to_gsi_value(self, obj):
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
        self._require_project()
        request = gsi.SolveAnalysesRequest(
            analyses=[self.config.analysis_name],
            solve_dependencies=self.config.solve_dependencies,
        )
        self.project.SolveAnalyses(request)

    def _load_results(self) -> None:
        self._require_project()
        request = gsi.LoadResultsRequest(
            analysis=self.config.analysis_name
        )
        self.project.LoadResults(request)

    def _assert_results_available(self) -> None:
        self._require_project()
        request = gsi.QueryResultsAvailabilityRequest(
            analysis=self.config.analysis_name
        )
        response = self.project.QueryResultsAvailability(request)
        if not response.has_results:
            raise RuntimeError("A análise foi executada, mas não há resultados disponíveis.")

    def _query_results(self) -> np.ndarray:
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
        if not hasattr(gsi.ResultType, self.config.result_table):
            raise ValueError(
                f"ResultType '{self.config.result_table}' não encontrado em gsi.ResultType."
            )
        return getattr(gsi.ResultType, self.config.result_table)

    def _resolve_data_param(self, param_name: str):
        if not hasattr(gsi.DataParamType, param_name):
            raise ValueError(
                f"DataParamType '{param_name}' não encontrado em gsi.DataParamType."
            )
        return getattr(gsi.DataParamType, param_name)