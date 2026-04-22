# GeoStudio / SEEP – Guia passo a passo em Python

Este guia é um **início prático** para começar a consumir a API Python/gRPC do GeoStudio, com foco em **SEEP** e na biblioteca `gsi` fornecida pela Seequent/Bentley. Ele foi montado a partir do README, da wheel `gsi`, dos arquivos protobuf e dos exemplos oficiais enviados.

---

## 1) O que você recebeu da GeoStudio

Pelos arquivos enviados, o fluxo oficial é este:

- instalar a biblioteca `gsi` a partir do `.whl`
- usar Python **>= 3.12.1 e < 3.13.0**
- abrir um projeto GeoStudio com `gsi.OpenProject(...)`
- fazer chamadas via objeto `project`
- para resultados, normalmente seguir esta sequência:
  1. `SolveAnalyses(...)`
  2. `LoadResults(...)`
  3. `QueryResults(...)`

Além disso, a própria wheel `gsi` encapsula a conexão gRPC com o GeoStudio usando `gsipy.ConnectionManager(...)`, então no uso normal você **não precisa criar o canal gRPC manualmente**. Você trabalha com `gsi.Project`, `gsi.OpenProject`, `gsi.GetRequest`, `gsi.SetRequest`, `gsi.QueryResultsRequest` etc.

---

## 2) Pré-requisitos

Antes de codar, garanta:

- Windows com GeoStudio 2025.1 instalado
- GeoStudio licenciado
- Python **3.12.x**
- acesso ao diretório de API do GeoStudio, normalmente:

```text
C:\Program Files\Seequent\GeoStudio 2025.1\API\
```

Arquivos relevantes:

- `requirements.txt`
- `gsi-2025.1.0-py3-none-any.whl`

---

## 3) Criando o ambiente Python

### 3.1 Criar o ambiente virtual

No PowerShell ou CMD:

```bash
python -m venv .venv
```

### 3.2 Ativar o ambiente

PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

CMD:

```bash
.\.venv\Scripts\activate.bat
```

---

## 4) Instalando a biblioteca da GeoStudio

Pelo README oficial, o caminho recomendado é instalar pelo `requirements.txt`.

Exemplo:

```bash
pip install -r "C:\Program Files\Seequent\GeoStudio 2025.1\API\requirements.txt"
```

No seu caso, o `requirements.txt` basicamente aponta para a wheel local `gsi-2025.1.0-py3-none-any.whl`.

### 4.1 Instalação alternativa direta da wheel

Também pode ser:

```bash
pip install "C:\Program Files\Seequent\GeoStudio 2025.1\API\gsi-2025.1.0-py3-none-any.whl"
```

---

## 5) Testando se a instalação funcionou

Crie um arquivo `test_installation.py`:

```python
import gsi

print("Installation successful!")
```

Execute:

```bash
python test_installation.py
```

Se funcionar, a biblioteca está importando corretamente.

---

## 6) Como a biblioteca funciona por baixo

A wheel `gsi` mostra uma estrutura importante:

- `gsi.OpenProject(project_path)` retorna um `gsi.Project`
- `gsi.Project` herda do `ProjectStub` gerado pelo gRPC
- internamente a biblioteca cria a conexão com o servidor GeoStudio
- você chama métodos RPC como se fossem métodos Python normais:
  - `project.Get(...)`
  - `project.Set(...)`
  - `project.SolveAnalyses(...)`
  - `project.LoadResults(...)`
  - `project.QueryResults(...)`

Ou seja: para você, o uso é simples. A parte de gRPC já vem “embrulhada”.

---

## 7) Estrutura mínima de um script GeoStudio

Quase todo script vai seguir esta base:

```python
import gsi
import grpc

project = None

try:
    project = gsi.OpenProject(r"C:\caminho\para\seu_projeto.gsz")

    # chamadas da API aqui

except grpc.RpcError as e:
    print(f"Erro gRPC: {e.code()} - {e.details()}")
except Exception as e:
    print(f"Erro geral: {e}")
finally:
    if project:
        project.Close()
```

Isso é importante porque o fechamento do projeto libera recursos e evita vazamento de memória ou conexões abertas.

---

## 8) Primeiro passo real: abrir e fechar um projeto

```python
import gsi

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")
print("Projeto aberto com sucesso")
project.Close()
print("Projeto fechado")
```

---

## 9) Entendendo os dois grandes tipos de operação

Na prática, você vai fazer duas coisas com frequência:

### 9.1 Ler ou alterar dados do modelo

Usa:

- `Get`
- `Set`
- `Add`
- `Delete`

### 9.2 Resolver análise e ler resultados

Usa:

- `SolveAnalyses`
- `LoadResults`
- `QueryResultsAvailability`
- `QueryTableParamsInfo`
- `QueryResults`

---

## 10) Como ler dados de um objeto do modelo com `Get`

`Get` recebe um `GetRequest` com:

- `analysis`: nome da análise
- `object`: caminho/nome do objeto dentro do modelo

Exemplo:

```python
import gsi
from google.protobuf import json_format

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")

request = gsi.GetRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Materials.Soil1"
)

response = project.Get(request)
print(response)

# Converter protobuf para dicionário Python
response_dict = json_format.MessageToDict(response)
print(response_dict)

project.Close()
```

### O que esperar no retorno

O retorno é um `GetResponse` com o campo:

- `data: google.protobuf.Value`

Ou seja, o dado vem em um `Value`, que pode conter:

- número
- string
- bool
- lista
- struct/objeto
- null

---

## 11) Como alterar dados do modelo com `Set`

`Set` recebe:

- `analysis`
- `object`
- `data`

O campo `data` é um `google.protobuf.Value`.

### 11.1 Exemplo simples: setar um número

Nos exemplos oficiais, o coeficiente sísmico horizontal é enviado assim:

```python
import gsi

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")

set_request = gsi.SetRequest(
    analysis="SLOPE/W Analysis",
    object="CurrentAnalysis.Objects.Seismic.Horizontal",
    data=gsi.Value(number_value=0.15)
)

project.Set(set_request)
project.Close()
```

### 11.2 Exemplo: setar um objeto/struct com vários campos

Nos exemplos oficiais, propriedades de material são passadas por `struct_value.update(...)`:

```python
import gsi

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")

material_params = gsi.Value()
material_params.struct_value.update({
    "PhiPrime": 30.0,
    "CohesionPrime": 12.0
})

set_request = gsi.SetRequest(
    analysis="SLOPE/W Analysis",
    object="CurrentAnalysis.Materials.Material1",
    data=material_params
)

project.Set(set_request)
project.Close()
```

### 11.3 Exemplo: setar lista de pontos (muito útil em funções do SEEP)

Nos exemplos de SEEP, eles montam listas de pontos usando `ListValue`:

```python
import gsi
from google.protobuf.struct_pb2 import ListValue


def points_to_value(points: list[list[float]]) -> gsi.Value:
    values = []
    for x, y in points:
        point = gsi.Value(
            list_value=ListValue(values=[
                gsi.Value(number_value=x),
                gsi.Value(number_value=y),
            ])
        )
        values.append(point)

    return gsi.Value(list_value=ListValue(values=values))


project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")

points = [
    [0.0, 0.42],
    [10.0, 0.38],
    [20.0, 0.31],
]

set_request = gsi.SetRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Objects.MyFunction",
    data=points_to_value(points)
)

project.Set(set_request)
project.Close()
```

Esse padrão é especialmente importante quando o objeto do GeoStudio espera **curvas, tabelas ou funções discretizadas**.

---

## 12) Como resolver uma análise com `SolveAnalyses`

Exemplo básico:

```python
import gsi

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")

solve_request = gsi.SolveAnalysesRequest(
    analyses=["SEEP/W Analysis"]
)

project.SolveAnalyses(solve_request)
project.Close()
```

### Parâmetros possíveis

- `analyses`: lista de nomes de análises
- `step`: opcional
- `solve_dependencies`: opcional

Exemplo com dependências:

```python
solve_request = gsi.SolveAnalysesRequest(
    analyses=["SEEP/W Analysis"],
    solve_dependencies=True
)
```

---

## 13) Como carregar resultados com `LoadResults`

Depois de resolver, normalmente você carrega os resultados:

```python
load_request = gsi.LoadResultsRequest(analysis="SEEP/W Analysis")
project.LoadResults(load_request)
```

---

## 14) Como verificar se há resultados disponíveis

```python
availability_request = gsi.QueryResultsAvailabilityRequest(
    analysis="SEEP/W Analysis"
)

availability_response = project.QueryResultsAvailability(availability_request)
print("Tem resultados?", availability_response.has_results)
```

---

## 15) Como descobrir quais parâmetros existem em uma tabela de resultados

Antes de consultar resultados, é excelente descobrir quais `DataParamType` estão disponíveis naquela tabela.

Use `QueryTableParamsInfo`:

```python
import gsi

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")
project.LoadResults(gsi.LoadResultsRequest(analysis="SEEP/W Analysis"))

request = gsi.QueryTableParamsInfoRequest(
    analysis="SEEP/W Analysis",
    table=gsi.ResultType.Nodes
)

response = project.QueryTableParamsInfo(request)

for item in response.params_info:
    print("dataparam:", item.dataparam)
    print("key:", item.key)
    print("display:", item.display)
    print("unit_category:", item.unit_category)
    print("vector_components:", list(item.vector_components))
    print("units:", item.units)
    print("-" * 40)

project.Close()
```

Isso te ajuda a descobrir:

- quais parâmetros podem ser consultados
- nome de exibição
- categoria de unidade
- unidades
- componentes vetoriais relacionados

---

## 16) Como consultar resultados com `QueryResults`

Esse é o coração do consumo de resultados.

### Fluxo básico

1. abrir projeto
2. resolver análise
3. carregar resultados
4. consultar resultados

### Exemplo mínimo

```python
import gsi

project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")

project.LoadResults(gsi.LoadResultsRequest(analysis="SEEP/W Analysis"))

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

print("Quantidade de nós:", len(x))
print("Primeiro nó:", x[0], y[0], pwp[0])

project.Close()
```

### O que entra em `QueryResultsRequest`

Campos possíveis:

- `analysis`: nome da análise
- `step`: passo
- `run`: execução/run
- `instance`: instância
- `table`: tabela de resultados (`gsi.ResultType`)
- `dataparams`: lista de parâmetros (`gsi.DataParamType`)
- `result_ids`: IDs específicos dos resultados

---

## 17) Quando usar `step`, `instance`, `run` e `result_ids`

### `step`
Use quando a análise tem múltiplos passos/saved time steps.

### `instance`
Use quando a tabela depende de instância específica, como alguns resultados de coluna.

### `run`
Use quando existe mais de uma execução associada.

### `result_ids`
Use quando você quer consultar somente IDs específicos em vez da tabela inteira.

Exemplo:

```python
request = gsi.QueryResultsRequest(
    analysis="SEEP/W Analysis",
    table=gsi.ResultType.History,
    dataparams=[gsi.DataParamType.eTime, gsi.DataParamType.eWaterPressure],
    result_ids=[1, 2, 3],
)
```

---

## 18) Como transformar o retorno em estruturas Python úteis

### 18.1 Converter para listas

```python
values = list(response.results[gsi.DataParamType.eWaterPressure].values)
```

### 18.2 Converter para NumPy

```python
import numpy as np

x = np.array(response.results[gsi.DataParamType.eXCoord].values)
y = np.array(response.results[gsi.DataParamType.eYCoord].values)
pwp = np.array(response.results[gsi.DataParamType.eWaterPressure].values)
```

### 18.3 Converter para pandas DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "x": response.results[gsi.DataParamType.eXCoord].values,
    "y": response.results[gsi.DataParamType.eYCoord].values,
    "pwp": response.results[gsi.DataParamType.eWaterPressure].values,
})

print(df.head())
```

---

## 19) Exemplo completo: alterar parâmetro, resolver e ler resultado

```python
import gsi
import pandas as pd
import grpc

project = None

try:
    project = gsi.OpenProject(r"C:\Projetos\modelo_seep.gsz")
    analysis_name = "SEEP/W Analysis"

    # 1) Alterar um objeto simples
    set_request = gsi.SetRequest(
        analysis=analysis_name,
        object="CurrentAnalysis.Objects.SomeParameter",
        data=gsi.Value(number_value=10.0)
    )
    project.Set(set_request)

    # 2) Resolver
    project.SolveAnalyses(gsi.SolveAnalysesRequest(analyses=[analysis_name]))

    # 3) Carregar resultados
    project.LoadResults(gsi.LoadResultsRequest(analysis=analysis_name))

    # 4) Consultar resultados nodais
    query_request = gsi.QueryResultsRequest(
        analysis=analysis_name,
        table=gsi.ResultType.Nodes,
        dataparams=[
            gsi.DataParamType.eXCoord,
            gsi.DataParamType.eYCoord,
            gsi.DataParamType.eWaterPressure,
        ],
        step=1,
    )

    response = project.QueryResults(query_request)

    df = pd.DataFrame({
        "x": response.results[gsi.DataParamType.eXCoord].values,
        "y": response.results[gsi.DataParamType.eYCoord].values,
        "water_pressure": response.results[gsi.DataParamType.eWaterPressure].values,
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

## 20) Como descobrir os nomes corretos de `analysis` e `object`

Esse é um ponto prático importante.

A API exige strings como:

- `analysis="SEEP/W Analysis"`
- `object="CurrentAnalysis.Objects.Seismic.Horizontal"`
- `object="CurrentAnalysis.Materials.Material1"`

Esses caminhos precisam existir no modelo.

### Estratégia recomendada

1. comece com objetos que você já conhece no projeto
2. use `Get` para validar se o caminho existe
3. só depois use `Set`

Exemplo de teste:

```python
test_request = gsi.GetRequest(
    analysis="SEEP/W Analysis",
    object="CurrentAnalysis.Materials.Material1"
)

response = project.Get(test_request)
print(response)
```

Se esse `Get` funcionar, o caminho provavelmente está correto para `Set` também.

---

## 21) Padrões de dados que você vai usar no dia a dia

### número

```python
gsi.Value(number_value=123.45)
```

### string

```python
gsi.Value(string_value="abc")
```

### booleano

```python
gsi.Value(bool_value=True)
```

### struct/objeto

```python
value = gsi.Value()
value.struct_value.update({
    "CampoA": 1.0,
    "CampoB": "texto",
    "CampoC": True,
})
```

### lista simples

```python
from google.protobuf.struct_pb2 import ListValue

value = gsi.Value(
    list_value=ListValue(values=[
        gsi.Value(number_value=1.0),
        gsi.Value(number_value=2.0),
        gsi.Value(number_value=3.0),
    ])
)
```

### lista de pares `(x, y)`

```python
from google.protobuf.struct_pb2 import ListValue

value = gsi.Value(
    list_value=ListValue(values=[
        gsi.Value(list_value=ListValue(values=[
            gsi.Value(number_value=0.0),
            gsi.Value(number_value=10.0),
        ])),
        gsi.Value(list_value=ListValue(values=[
            gsi.Value(number_value=1.0),
            gsi.Value(number_value=11.0),
        ])),
    ])
)
```

---

## 22) Sequência recomendada para começar de verdade no SEEP

### Etapa 1 — Validar ambiente

- instalar `gsi`
- importar `gsi`
- abrir e fechar projeto

### Etapa 2 — Ler algo do projeto

- usar `GetRequest`
- converter retorno com `json_format.MessageToDict`
- entender a estrutura do objeto

### Etapa 3 — Alterar algo simples

- usar `SetRequest` com `number_value`
- validar com `Get`

### Etapa 4 — Alterar algo mais complexo

- usar `struct_value.update(...)`
- ou `ListValue` para curvas/funções

### Etapa 5 — Resolver a análise

- usar `SolveAnalysesRequest`

### Etapa 6 — Carregar e ler resultados

- `LoadResultsRequest`
- `QueryResultsAvailabilityRequest`
- `QueryTableParamsInfoRequest`
- `QueryResultsRequest`

### Etapa 7 — Exportar para análise externa

- NumPy
- pandas
- CSV
- gráficos

---

## 23) Erros comuns no começo

### 1. Python fora da versão suportada
A documentação recebida indica Python **>= 3.12.1 e < 3.13.0**.

### 2. GeoStudio sem licença
O README avisa para garantir que o GeoStudio esteja licenciado.

### 3. Caminho do projeto inválido
Verifique o `.gsz`.

### 4. Nome da análise incorreto
A string precisa bater com o nome real no projeto.

### 5. Caminho do objeto incorreto
Exemplo: `CurrentAnalysis.Materials.Material1` pode variar conforme o projeto.

### 6. Mandar `data` no formato errado
Muitos campos exigem `gsi.Value`, `struct_value`, `list_value`.

### 7. Tentar consultar resultado sem carregar
Normalmente o fluxo correto é:

```python
project.SolveAnalyses(...)
project.LoadResults(...)
project.QueryResults(...)
```

---

## 24) Estrutura de pasta recomendada para seu projeto Python

```text
meu_projeto_geostudio/
│
├─ .venv/
├─ data/
│  ├─ entrada/
│  └─ saida/
├─ scripts/
│  ├─ 01_testar_instalacao.py
│  ├─ 02_abrir_projeto.py
│  ├─ 03_ler_objeto.py
│  ├─ 04_alterar_objeto.py
│  ├─ 05_resolver_analise.py
│  └─ 06_consultar_resultados.py
├─ utils/
│  └─ geostudio_helpers.py
└─ README.md
```

---

## 25) Próximo passo recomendado

Para começar do jeito certo, eu seguiria esta ordem:

1. `01_testar_instalacao.py`
2. `02_abrir_projeto.py`
3. `03_ler_objeto.py`
4. `04_alterar_objeto.py`
5. `05_resolver_analise.py`
6. `06_consultar_resultados.py`

Essa sequência te dá uma base sólida antes de entrar em calibração, otimização, SciPy, pandas e pós-processamento.

---

## 26) Exemplo de script inicial ideal

```python
import gsi
import grpc
from google.protobuf import json_format

project = None

try:
    project = gsi.OpenProject(r"C:\Projetos\modelo_seep.gsz")
    analysis_name = "SEEP/W Analysis"
    object_name = "CurrentAnalysis.Materials.Material1"

    # Ler objeto
    get_request = gsi.GetRequest(
        analysis=analysis_name,
        object=object_name,
    )
    get_response = project.Get(get_request)
    print(json_format.MessageToDict(get_response))

    # Resolver análise
    solve_request = gsi.SolveAnalysesRequest(analyses=[analysis_name])
    project.SolveAnalyses(solve_request)

    # Carregar resultados
    load_request = gsi.LoadResultsRequest(analysis=analysis_name)
    project.LoadResults(load_request)

    # Verificar disponibilidade
    avail_request = gsi.QueryResultsAvailabilityRequest(analysis=analysis_name)
    avail_response = project.QueryResultsAvailability(avail_request)
    print("Resultados disponíveis:", avail_response.has_results)

    # Consultar parâmetros disponíveis da tabela de nós
    info_request = gsi.QueryTableParamsInfoRequest(
        analysis=analysis_name,
        table=gsi.ResultType.Nodes,
    )
    info_response = project.QueryTableParamsInfo(info_request)
    print("Quantidade de parâmetros disponíveis:", len(info_response.params_info))

except grpc.RpcError as e:
    print(f"Erro gRPC: {e.code()} - {e.details()}")
except Exception as e:
    print(f"Erro geral: {e}")
finally:
    if project:
        project.Close()
```

---

## 27) Resumo operacional

Para trabalhar com SEEP/GeoStudio em Python, pense sempre neste pipeline:

```text
Instalar gsi
-> Abrir projeto
-> Ler objetos (Get)
-> Alterar objetos (Set)
-> Resolver análise (SolveAnalyses)
-> Carregar resultados (LoadResults)
-> Descobrir parâmetros disponíveis (QueryTableParamsInfo)
-> Consultar resultados (QueryResults)
-> Converter para NumPy / pandas / CSV
```

Esse é o caminho-base para qualquer automação mais avançada.
