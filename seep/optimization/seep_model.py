import copy
from typing import Dict, Any, List

import grpc
import numpy as np
import gsi
from google.protobuf import json_format

from config import SeepProjectConfig


class SeepModel:
    def __init__(self, config: SeepProjectConfig):
        self.config = config

    def run(self, k: float, anisotropia: float) -> np.ndarray:
        """
        Executa uma simulação:
        - abre o projeto
        - altera k e anisotropia
        - resolve a análise
        - carrega resultados
        - consulta resultados
        - retorna array shape (n, 3): [x, y, value]
        """
        project = None
        try:
            project = gsi.OpenProject(self.config.project_path)

            self._set_material_params(
                project=project,
                k=k,
                anisotropia=anisotropia,
            )

            self._solve(project)
            self._load_results(project)
            self._assert_results_available(project)

            return self._query_results(project)

        except grpc.RpcError as e:
            raise RuntimeError(f"Erro gRPC no GeoStudio: {e.code()} - {e.details()}") from e
        except Exception as e:
            raise RuntimeError(f"Erro ao executar modelo SEEP: {e}") from e
        finally:
            if project:
                project.Close()

    def inspect_material(self) -> Dict[str, Any]:
        """
        Lê o objeto do material para você descobrir a estrutura real
        dos campos antes de usar o Set definitivo.
        """
        project = None
        try:
            project = gsi.OpenProject(self.config.project_path)
            response = project.Get(
                gsi.GetRequest(
                    analysis=self.config.analysis_name,
                    object=self.config.material_object,
                )
            )
            return json_format.MessageToDict(response)
        finally:
            if project:
                project.Close()

    def list_available_result_params(self) -> List[Dict[str, Any]]:
        """
        Lista os parâmetros disponíveis na tabela de resultados.
        Isso é importante para descobrir o DataParamType correto antes de consultar.
        """
        project = None
        try:
            project = gsi.OpenProject(self.config.project_path)

            self._load_results_if_possible(project)

            response = project.QueryTableParamsInfo(
                gsi.QueryTableParamsInfoRequest(
                    analysis=self.config.analysis_name,
                    table=self._resolve_result_table(),
                )
            )

            result = []
            for p in response.params_info:
                result.append({
                    "dataparam": int(p.dataparam),
                    "key": p.key,
                    "display": p.display,
                    "unit_category": int(p.unit_category),
                    "vector_components": list(p.vector_components),
                    "units": p.units,
                })
            return result
        finally:
            if project:
                project.Close()

    def _set_material_params(self, project, k: float, anisotropia: float) -> None:
        """
        Estratégia segura:
        - primeiro tenta ler a estrutura atual do material
        - depois aplica/update nos campos configurados
        """
        get_response = project.Get(
            gsi.GetRequest(
                analysis=self.config.analysis_name,
                object=self.config.material_object,
            )
        )

        material_dict = json_format.MessageToDict(get_response)

        # o GetResponse costuma vir como {"data": {...}}
        base_data = material_dict.get("data", {})
        if not isinstance(base_data, dict):
            base_data = {}

        updated = copy.deepcopy(base_data)
        updated[self.config.k_field_name] = float(k)
        updated[self.config.anisotropy_field_name] = float(anisotropia)

        value = gsi.Value()
        value.struct_value.update(updated)

        set_request = gsi.SetRequest(
            analysis=self.config.analysis_name,
            object=self.config.material_object,
            data=value,
        )
        project.Set(set_request)

    def _solve(self, project) -> None:
        request = gsi.SolveAnalysesRequest(
            analyses=[self.config.analysis_name],
            solve_dependencies=self.config.solve_dependencies,
        )
        project.SolveAnalyses(request)

    def _load_results(self, project) -> None:
        request = gsi.LoadResultsRequest(
            analysis=self.config.analysis_name
        )
        project.LoadResults(request)

    def _load_results_if_possible(self, project) -> None:
        try:
            self._load_results(project)
        except Exception:
            pass

    def _assert_results_available(self, project) -> None:
        request = gsi.QueryResultsAvailabilityRequest(
            analysis=self.config.analysis_name
        )
        response = project.QueryResultsAvailability(request)
        if not response.has_results:
            raise RuntimeError("A análise foi executada, mas não há resultados disponíveis.")

    def _query_results(self, project) -> np.ndarray:
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

        response = project.QueryResults(query_request)

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
        Resolve string -> enum do ResultType.
        Ex.: "Nodes" => gsi.ResultType.Nodes
        """
        if not hasattr(gsi.ResultType, self.config.result_table):
            raise ValueError(
                f"ResultType '{self.config.result_table}' não encontrado em gsi.ResultType."
            )
        return getattr(gsi.ResultType, self.config.result_table)

    def _resolve_data_param(self, param_name: str):
        """
        Resolve string -> enum do DataParamType.
        Ex.: "eXCoord" => gsi.DataParamType.eXCoord
        """
        if not hasattr(gsi.DataParamType, param_name):
            raise ValueError(
                f"DataParamType '{param_name}' não encontrado em gsi.DataParamType."
            )
        return getattr(gsi.DataParamType, param_name)