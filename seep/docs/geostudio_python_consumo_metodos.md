# GeoStudio / SEEP – Consumo dos métodos e passagem de parâmetros em Python

Este guia é uma referência de **como consumir cada método principal da API `gsi`**, quais parâmetros entram, o que sai, e como montar os dados corretamente em Python.

O foco aqui é operacional: **como chamar**, **como montar o request**, **como ler o response** e **quando usar cada campo**.

---

## 1) Imports base

```python
import gsi
import grpc
from google.protobuf import json_format
from google.protobuf.struct_pb2 import ListValue
import pandas as pd
import numpy as np
```

---

## 2) Abertura de projeto

### Método

```python
gsi.OpenProject(project_path: str) -> gsi.Project
```

### Exemplo

```python
project = gsi.OpenProject(r"C:\Projetos\modelo_seep.gsz")
```

### Observações

- retorna um objeto `gsi.Project`
- esse objeto expõe os métodos RPC
- no final use `project.Close()`

---

## 3) Fechamento e salvamento

### Fechar

```python
project.Close()
```

### Salvar

```python
project.Save()
```

Use `Save()` quando quiser persistir as alterações feitas por `Set`, `Add` ou `Delete`.

---

## 4) Método `Get`

### Assinatura lógica

```python
project.Get(gsi.GetRequest(...)) -> gsi.GetResponse
```

### Request

```python
gsi.GetRequest(
    analysis: str | None = ...,
    object: str | None = ...,
)
```

### Campos do request

- `analysis`: nome da análise
- `object`: caminho do objeto dentro do modelo

### Response

```python
gsi.GetResponse(
    data: google.protobuf.Value
)
```

### Exemplo

```python
request = gsi.GetRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Materials.Material1"
)

response = project.Get(request)
print(response)
```

### Converter para dicionário

```python
response_dict = json_format.MessageToDict(response)
print(response_dict)
```

### Quando usar

- inspecionar propriedades atuais de um objeto
- validar se o caminho do objeto está certo
- conferir se um `Set` realmente funcionou

---

## 5) Método `Set`

### Assinatura lógica

```python
project.Set(gsi.SetRequest(...)) -> gsi.SetResponse
```

### Request

```python
gsi.SetRequest(
    analysis: str | None = ...,
    object: str | None = ...,
    data: gsi.Value | dict | None = ...,
)
```

### Campos do request

- `analysis`: nome da análise
- `object`: caminho do objeto
- `data`: valor a ser escrito

### Response

`SetResponse` não traz campos relevantes no contrato atual.

### Formas de enviar `data`

#### número

```python
gsi.Value(number_value=0.15)
```

#### string

```python
gsi.Value(string_value="abc")
```

#### bool

```python
gsi.Value(bool_value=True)
```

#### struct/objeto

```python
value = gsi.Value()
value.struct_value.update({
    "PhiPrime": 30.0,
    "CohesionPrime": 10.0,
})
```

#### lista

```python
value = gsi.Value(
    list_value=ListValue(values=[
        gsi.Value(number_value=1.0),
        gsi.Value(number_value=2.0),
    ])
)
```

### Exemplo 1: setar número

```python
request = gsi.SetRequest(
    analysis="SLOPE/W Analysis",
    object="CurrentAnalysis.Objects.Seismic.Horizontal",
    data=gsi.Value(number_value=0.15)
)
project.Set(request)
```

### Exemplo 2: setar struct

```python
material_params = gsi.Value()
material_params.struct_value.update({
    "PhiPrime": 32.0,
    "CohesionPrime": 15.0
})

request = gsi.SetRequest(
    analysis="SLOPE/W Analysis",
    object="CurrentAnalysis.Materials.Material1",
    data=material_params
)
project.Set(request)
```

### Exemplo 3: setar lista de pontos `(x, y)`

```python
def xy_points_to_value(points: list[list[float]]) -> gsi.Value:
    rows = []
    for x, y in points:
        rows.append(
            gsi.Value(
                list_value=ListValue(values=[
                    gsi.Value(number_value=x),
                    gsi.Value(number_value=y),
                ])
            )
        )
    return gsi.Value(list_value=ListValue(values=rows))

request = gsi.SetRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Objects.MyFunction",
    data=xy_points_to_value([
        [0.0, 0.42],
        [10.0, 0.38],
        [20.0, 0.31],
    ])
)
project.Set(request)
```

### Quando usar

- alterar parâmetros de material
- alterar parâmetros escalares
- atualizar funções hidráulicas
- trocar curvas tabeladas

---

## 6) Método `Add`

### Assinatura lógica

```python
project.Add(gsi.AddRequest(...)) -> gsi.AddResponse
```

### Request

```python
gsi.AddRequest(
    analysis: str | None = ...,
    object: str | None = ...,
    data: gsi.Value | dict | None = ...,
)
```

### Response

```python
gsi.AddResponse(
    object: str
)
```

### Campos do request

- `analysis`: nome da análise
- `object`: local/coleção onde o novo item deve ser adicionado
- `data`: conteúdo do novo item

### Exemplo genérico

```python
new_item = gsi.Value()
new_item.struct_value.update({
    "Name": "NovoObjeto",
    "SomeValue": 123.0,
})

request = gsi.AddRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Objects",
    data=new_item,
)

response = project.Add(request)
print("Objeto criado em:", response.object)
```

### Observação importante

Nos exemplos enviados não apareceu um caso concreto de `Add`. Então a forma do `request` está clara pelo contrato protobuf, mas o **caminho exato do `object` e o formato do `data` dependem do tipo de item que o GeoStudio aceita naquela coleção específica**.

### Estratégia segura

- primeiro use `Get` em objetos já existentes
- observe a estrutura retornada
- replique essa estrutura ao fazer `Add`

---

## 7) Método `Delete`

### Assinatura lógica

```python
project.Delete(gsi.DeleteRequest(...)) -> gsi.DeleteResponse
```

### Request

```python
gsi.DeleteRequest(
    analysis: str | None = ...,
    object: str | None = ...,
    force_delete: bool = ...,
)
```

### Campos do request

- `analysis`: nome da análise
- `object`: caminho do objeto a remover
- `force_delete`: força remoção, quando aplicável

### Exemplo

```python
request = gsi.DeleteRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Objects.ObjetoTemporario",
    force_delete=True,
)

project.Delete(request)
```

### Quando usar

- limpar objetos temporários
- remover entidades adicionadas por automação

### Atenção

Use `Delete` com cautela. Em automações, o ideal é testar primeiro em cópia do projeto.

---

## 8) Método `SolveAnalyses`

### Assinatura lógica

```python
project.SolveAnalyses(gsi.SolveAnalysesRequest(...)) -> gsi.SolveAnalysesResponse
```

### Request

```python
gsi.SolveAnalysesRequest(
    analyses: list[str] = ...,
    step: int | None = ...,
    solve_dependencies: bool = ...,
)
```

### Campos do request

- `analyses`: lista de análises a resolver
- `step`: passo específico, se aplicável
- `solve_dependencies`: resolver dependências também

### Exemplo mínimo

```python
request = gsi.SolveAnalysesRequest(
    analyses=["SEEP/W Analysis"]
)
project.SolveAnalyses(request)
```

### Exemplo com dependências

```python
request = gsi.SolveAnalysesRequest(
    analyses=["SEEP/W Analysis"],
    solve_dependencies=True,
)
project.SolveAnalyses(request)
```

### Quando usar

- depois de `Set`
- antes de `LoadResults`
- quando parâmetros foram alterados e você precisa recalcular

---

## 9) Método `QueryResultsAvailability`

### Assinatura lógica

```python
project.QueryResultsAvailability(
    gsi.QueryResultsAvailabilityRequest(...)
) -> gsi.QueryResultsAvailabilityResponse
```

### Request

```python
gsi.QueryResultsAvailabilityRequest(
    analysis: str | None = ...,
)
```

### Response

```python
gsi.QueryResultsAvailabilityResponse(
    has_results: bool
)
```

### Exemplo

```python
request = gsi.QueryResultsAvailabilityRequest(
    analysis="SEEP/W Analysis"
)
response = project.QueryResultsAvailability(request)
print(response.has_results)
```

### Quando usar

- antes de tentar ler resultados
- como checagem rápida em pipelines automatizados

---

## 10) Método `LoadResults`

### Assinatura lógica

```python
project.LoadResults(gsi.LoadResultsRequest(...)) -> gsi.LoadResultsResponse
```

### Request

```python
gsi.LoadResultsRequest(
    analysis: str | None = ...,
)
```

### Exemplo

```python
request = gsi.LoadResultsRequest(
    analysis="SEEP/W Analysis"
)
project.LoadResults(request)
```

### Quando usar

- depois de resolver
- antes de `QueryTableParamsInfo`
- antes de `QueryResults`

---

## 11) Método `QueryTableParamsInfo`

### Assinatura lógica

```python
project.QueryTableParamsInfo(
    gsi.QueryTableParamsInfoRequest(...)
) -> gsi.QueryTableParamsInfoResponse
```

### Request

```python
gsi.QueryTableParamsInfoRequest(
    analysis: str | None = ...,
    table: gsi.ResultType | None = ...,
)
```

### Response

```python
gsi.QueryTableParamsInfoResponse(
    params_info: list[gsi.ParamInfo]
)
```

### Estrutura de `ParamInfo`

Cada item de `params_info` traz:

- `dataparam`: enum `gsi.DataParamType`
- `key`: chave textual
- `display`: nome de exibição
- `unit_category`: enum `gsi.UnitCategoryType`
- `vector_components`: lista de `gsi.DataParamType`
- `units`: string das unidades

### Exemplo

```python
request = gsi.QueryTableParamsInfoRequest(
    analysis="SEEP/W Analysis",
    table=gsi.ResultType.Nodes,
)

response = project.QueryTableParamsInfo(request)

for p in response.params_info:
    print({
        "dataparam": p.dataparam,
        "key": p.key,
        "display": p.display,
        "unit_category": p.unit_category,
        "vector_components": list(p.vector_components),
        "units": p.units,
    })
```

### Quando usar

- para descobrir quais parâmetros estão disponíveis por tabela
- para saber unidades
- para montar interfaces dinâmicas
- para evitar consultar `DataParamType` inválido

---

## 12) Método `QueryResults`

### Assinatura lógica

```python
project.QueryResults(gsi.QueryResultsRequest(...)) -> gsi.QueryResultsResponse
```

### Request

```python
gsi.QueryResultsRequest(
    analysis: str | None = ...,
    step: int | None = ...,
    run: int | None = ...,
    instance: int | None = ...,
    table: gsi.ResultType | None = ...,
    dataparams: list[gsi.DataParamType] = ...,
    result_ids: list[int] = ...,
)
```

### Campos do request

- `analysis`: nome da análise
- `step`: passo/saved time step
- `run`: run específico
- `instance`: instância específica
- `table`: tabela de resultado
- `dataparams`: lista de parâmetros a consultar
- `result_ids`: IDs específicos

### Response

```python
gsi.QueryResultsResponse(
    results: Mapping[int, gsi.ParamResults]
)
```

Onde:

```python
gsi.ParamResults(
    values: list[float]
)
```

Ou seja: para cada `DataParamType`, você recebe um vetor de valores.

### Exemplo básico

```python
request = gsi.QueryResultsRequest(
    analysis="SEEP/W Analysis",
    table=gsi.ResultType.Nodes,
    dataparams=[
        gsi.DataParamType.eXCoord,
        gsi.DataParamType.eYCoord,
        gsi.DataParamType.eWaterPressure,
    ],
    step=1,
)

response = project.QueryResults(request)

x = response.results[gsi.DataParamType.eXCoord].values
y = response.results[gsi.DataParamType.eYCoord].values
pwp = response.results[gsi.DataParamType.eWaterPressure].values
```

### Exemplo com `result_ids`

```python
request = gsi.QueryResultsRequest(
    analysis="SEEP/W Analysis",
    table=gsi.ResultType.History,
    dataparams=[
        gsi.DataParamType.eTime,
        gsi.DataParamType.eWaterPressure,
    ],
    result_ids=[1, 2, 3],
)
```

### Exemplo com `instance`

```python
request = gsi.QueryResultsRequest(
    analysis="SEEP/W Analysis",
    table=gsi.ResultType.Column,
    dataparams=[
        gsi.DataParamType.eXCoord,
        gsi.DataParamType.eWaterPressure,
    ],
    instance=1,
    step=1,
)
```

### Converter resposta para DataFrame

```python
df = pd.DataFrame({
    "x": response.results[gsi.DataParamType.eXCoord].values,
    "y": response.results[gsi.DataParamType.eYCoord].values,
    "water_pressure": response.results[gsi.DataParamType.eWaterPressure].values,
})
```

### Quando usar

- ler resultados nodais
- ler resultados em colunas
- ler históricos
- exportar para CSV
- pós-processamento com NumPy/pandas

---

## 13) Ordem correta de chamada para resultados

O padrão mais seguro é:

```python
project.SolveAnalyses(...)
project.LoadResults(...)
project.QueryResults(...)
```

E, quando útil:

```python
project.QueryResultsAvailability(...)
project.QueryTableParamsInfo(...)
project.QueryResults(...)
```

---

## 14) Enum `ResultType`: qual tabela consultar

Do contrato protobuf, os principais valores incluem:

- `gsi.ResultType.Nodes`
- `gsi.ResultType.Elements`
- `gsi.ResultType.Gauss`
- `gsi.ResultType.ElementNodes`
- `gsi.ResultType.Time`
- `gsi.ResultType.NodePair`
- `gsi.ResultType.History`
- `gsi.ResultType.TimeStep`
- `gsi.ResultType.FlowPath`
- `gsi.ResultType.Slip`
- `gsi.ResultType.CriticalSlip`
- `gsi.ResultType.Column`
- `gsi.ResultType.Intercolumn`
- `gsi.ResultType.LambdaFOS`
- `gsi.ResultType.Reinforcement`
- `gsi.ResultType.Sample`
- `gsi.ResultType.Probabilistic`
- `gsi.ResultType.Iteration`
- `gsi.ResultType.BeamGauss`
- `gsi.ResultType.ParticleAir`
- `gsi.ResultType.ParticleWater`
- `gsi.ResultType.SavedTimeStep`

### Regra prática

- se quer resultados por nó: `Nodes`
- se quer histórico: `History`
- se quer caminho de fluxo: `FlowPath`
- se quer coluna: `Column`
- se quer superfície crítica: `CriticalSlip`

---

## 15) Enum `DataParamType`: o que consultar

Esse enum é muito grande. Alguns parâmetros muito úteis e visíveis nos protobuf enviados incluem:

### coordenadas

- `gsi.DataParamType.eXCoord`
- `gsi.DataParamType.eYCoord`
- `gsi.DataParamType.eZCoord`
- `gsi.DataParamType.eXZCoord`

### hidráulica / SEEP

- `gsi.DataParamType.eWaterTotalHead`
- `gsi.DataParamType.eWaterPressureHead`
- `gsi.DataParamType.eWaterPressure`
- `gsi.DataParamType.eWaterPressureCalculated`
- `gsi.DataParamType.eVolWC`
- `gsi.DataParamType.eXVelocity`
- `gsi.DataParamType.eYVelocity`
- `gsi.DataParamType.eXYVelocity`
- `gsi.DataParamType.eWaterGradientX`
- `gsi.DataParamType.eWaterGradientY`
- `gsi.DataParamType.eWaterGradientZ`
- `gsi.DataParamType.eWaterGradient`
- `gsi.DataParamType.eWaterConductivityX`
- `gsi.DataParamType.eWaterConductivityY`
- `gsi.DataParamType.eWaterConductivityZ`

### tempo / temperatura / concentração

- `gsi.DataParamType.eTime`
- `gsi.DataParamType.eTemperature`
- `gsi.DataParamType.eConcentration`

### estabilidade / FOS

- `gsi.DataParamType.eRawSlipFOS`
- `gsi.DataParamType.eSlipFOSMean`
- `gsi.DataParamType.eSlipFOSMin`
- `gsi.DataParamType.eSlipFOSMax`
- `gsi.DataParamType.eSlipProbOfFailure`
- `gsi.DataParamType.eStabilityFactor`

### deslocamentos e deformações

- `gsi.DataParamType.eXDisplacement`
- `gsi.DataParamType.eYDisplacement`
- `gsi.DataParamType.eZDisplacement`
- `gsi.DataParamType.eXYDisplacement`
- `gsi.DataParamType.eXStrain`
- `gsi.DataParamType.eYStrain`
- `gsi.DataParamType.eZStrain`

### tensões

- `gsi.DataParamType.eXTotalStress`
- `gsi.DataParamType.eYTotalStress`
- `gsi.DataParamType.eZTotalStress`
- `gsi.DataParamType.eXEffectiveStress`
- `gsi.DataParamType.eYEffectiveStress`
- `gsi.DataParamType.eZEffectiveStress`

### regra prática

Antes de escolher `DataParamType` no escuro, rode:

```python
project.QueryTableParamsInfo(...)
```

Assim você consulta apenas parâmetros realmente disponíveis naquela tabela.

---

## 16) Enum `UnitCategoryType`: como interpretar unidades

O contrato protobuf traz categorias como:

- `gsi.UnitCategoryType.Length`
- `gsi.UnitCategoryType.Time`
- `gsi.UnitCategoryType.Force`
- `gsi.UnitCategoryType.Temperature`
- `gsi.UnitCategoryType.Mass`
- `gsi.UnitCategoryType.Energy`
- `gsi.UnitCategoryType.Angle`
- `gsi.UnitCategoryType.HydraulicHead`
- `gsi.UnitCategoryType.Pressure`
- `gsi.UnitCategoryType.Strength`
- `gsi.UnitCategoryType.Stiffness`
- `gsi.UnitCategoryType.UnitWeight`
- `gsi.UnitCategoryType.Velocity`
- `gsi.UnitCategoryType.Acceleration`
- `gsi.UnitCategoryType.Density`
- `gsi.UnitCategoryType.Concentration`
- `gsi.UnitCategoryType.Area`
- `gsi.UnitCategoryType.Volume`
- `gsi.UnitCategoryType.Displacement`

Essas categorias aparecem no `ParamInfo.unit_category` e ajudam a interpretar o `ParamInfo.units`.

---

## 17) Funções utilitárias recomendadas

### Converter resposta de `Get` para dicionário

```python
def get_as_dict(project: gsi.Project, analysis: str, object_name: str) -> dict:
    response = project.Get(
        gsi.GetRequest(analysis=analysis, object=object_name)
    )
    return json_format.MessageToDict(response)
```

### Consultar resultados e montar matriz NumPy

```python
def query_values(project: gsi.Project, request: gsi.QueryResultsRequest, data_params: list) -> np.ndarray:
    response = project.QueryResults(request)
    return np.column_stack([
        response.results[param].values
        for param in data_params
    ])
```

### Converter pontos `(x, y)` em `Value`

```python
def points_to_value(points: list[list[float]]) -> gsi.Value:
    rows = []
    for x, y in points:
        rows.append(
            gsi.Value(
                list_value=ListValue(values=[
                    gsi.Value(number_value=x),
                    gsi.Value(number_value=y),
                ])
            )
        )
    return gsi.Value(list_value=ListValue(values=rows))
```

---

## 18) Exemplo de pipeline completo

```python
import gsi
import grpc
import pandas as pd
from google.protobuf import json_format

project = None

try:
    project = gsi.OpenProject(r"C:\Projetos\modelo_seep.gsz")
    analysis = "SEEP/W Analysis"

    # 1) Ler objeto
    get_response = project.Get(
        gsi.GetRequest(
            analysis=analysis,
            object="CurrentAnalysis.Materials.Material1"
        )
    )
    print(json_format.MessageToDict(get_response))

    # 2) Alterar objeto
    params = gsi.Value()
    params.struct_value.update({
        "SomeParameter": 123.0
    })
    project.Set(
        gsi.SetRequest(
            analysis=analysis,
            object="CurrentAnalysis.Materials.Material1",
            data=params,
        )
    )

    # 3) Resolver
    project.SolveAnalyses(
        gsi.SolveAnalysesRequest(
            analyses=[analysis]
        )
    )

    # 4) Carregar resultados
    project.LoadResults(
        gsi.LoadResultsRequest(
            analysis=analysis
        )
    )

    # 5) Descobrir parâmetros da tabela de nós
    params_info = project.QueryTableParamsInfo(
        gsi.QueryTableParamsInfoRequest(
            analysis=analysis,
            table=gsi.ResultType.Nodes,
        )
    )
    print("Parâmetros disponíveis:", len(params_info.params_info))

    # 6) Consultar resultados
    query_request = gsi.QueryResultsRequest(
        analysis=analysis,
        table=gsi.ResultType.Nodes,
        dataparams=[
            gsi.DataParamType.eXCoord,
            gsi.DataParamType.eYCoord,
            gsi.DataParamType.eWaterPressure,
        ],
        step=1,
    )

    query_response = project.QueryResults(query_request)

    df = pd.DataFrame({
        "x": query_response.results[gsi.DataParamType.eXCoord].values,
        "y": query_response.results[gsi.DataParamType.eYCoord].values,
        "water_pressure": query_response.results[gsi.DataParamType.eWaterPressure].values,
    })

    print(df.head())

except grpc.RpcError as e:
    print(f"Erro gRPC: {e.code()} - {e.details()}")
except Exception as e:
    print(f"Erro geral: {e}")
finally:
    if project:
        project.Close()
```

---

## 19) Como pensar a passagem de parâmetros na prática

### Cenário A — valor escalar

Use:

```python
gsi.Value(number_value=...)
```

### Cenário B — várias propriedades nomeadas

Use:

```python
value = gsi.Value()
value.struct_value.update({...})
```

### Cenário C — curva, tabela ou pares de pontos

Use:

```python
gsi.Value(list_value=ListValue(...))
```

### Cenário D — leitura de resultados

Use:

```python
gsi.QueryResultsRequest(...)
```

e depois leia:

```python
response.results[gsi.DataParamType.AlgumParametro].values
```

---

## 20) Recomendação prática de uso

No seu caso, eu separaria o consumo em quatro módulos Python:

```text
01_conexao.py
02_modelo_get_set.py
03_solver.py
04_resultados.py
```

### `01_conexao.py`
- abrir/fechar projeto

### `02_modelo_get_set.py`
- `Get`, `Set`, `Add`, `Delete`
- helpers para `Value`, `Struct`, `ListValue`

### `03_solver.py`
- `SolveAnalyses`, `LoadResults`, disponibilidade

### `04_resultados.py`
- `QueryTableParamsInfo`
- `QueryResults`
- exportação para pandas/CSV

Assim seu projeto fica organizado e escalável.

---

## 21) Resumo final

### leitura/escrita de modelo

- `Get`: lê objeto
- `Set`: altera objeto
- `Add`: cria objeto
- `Delete`: remove objeto

### solução e resultados

- `SolveAnalyses`: resolve análise
- `LoadResults`: carrega resultados
- `QueryResultsAvailability`: checa disponibilidade
- `QueryTableParamsInfo`: descobre parâmetros e unidades
- `QueryResults`: lê os vetores numéricos

### tipos de dado importantes

- `gsi.Value(number_value=...)`
- `gsi.Value(string_value=...)`
- `gsi.Value(bool_value=...)`
- `value.struct_value.update({...})`
- `gsi.Value(list_value=ListValue(...))`

Esse é o núcleo do consumo da API GeoStudio/SEEP em Python.
