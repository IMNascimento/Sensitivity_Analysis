# Documentação técnica da API protobuf/gRPC — SEEP / GeoStudio

> Documento gerado a partir dos arquivos `gsi_project_pb2.py`, `gsi_project_pb2_grpc.py`, `gsi_Result_Type_pb2.py`, `gsi_UnitCategory_Type_pb2.py` e `gsi_DataParam_Type_pb2.py`.

## 1. Visão geral

- **Serviço gRPC:** `gsi.pb.project.Project`
- **Estilo das chamadas:** unary-unary
- **Origem da estrutura:** código Python gerado a partir de arquivos `.proto`

## 2. Métodos disponíveis

| Método | Request | Response | Descrição inferida |
|---|---|---|---|
| `Get` | `GetRequest` | `GetResponse` | Missing associated documentation comment in .proto file. |
| `Set` | `SetRequest` | `SetResponse` | Missing associated documentation comment in .proto file. |
| `Add` | `AddRequest` | `AddResponse` | Missing associated documentation comment in .proto file. |
| `Delete` | `DeleteRequest` | `DeleteResponse` | Missing associated documentation comment in .proto file. |
| `SolveAnalyses` | `SolveAnalysesRequest` | `SolveAnalysesResponse` | Solves a list of analyses at a given step number. |
| `QueryTableParamsInfo` | `QueryTableParamsInfoRequest` | `QueryTableParamsInfoResponse` | Query metadata for all DataParams stored in a requested DataTable. |
| `QueryResults` | `QueryResultsRequest` | `QueryResultsResponse` | Query results for an analysis. |
| `QueryResultsAvailability` | `QueryResultsAvailabilityRequest` | `QueryResultsAvailabilityResponse` | Query whether an analysis has results available |
| `LoadResults` | `LoadResultsRequest` | `LoadResultsResponse` | Missing associated documentation comment in .proto file. |

## 3.1 `Get`

**RPC path:** `/gsi.pb.project.Project/Get`

**Request:** `GetRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |
| `object` | 2 | `string` | `optional` | opcional (proto3 optional) |

**Response:** `GetResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `data` | 1 | `google.protobuf.Value` | `optional` | opcional (proto3 optional), objeto |

**Descrição encontrada:** Missing associated documentation comment in .proto file.

## 3.2 `Set`

**RPC path:** `/gsi.pb.project.Project/Set`

**Request:** `SetRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |
| `object` | 2 | `string` | `optional` | opcional (proto3 optional) |
| `data` | 3 | `google.protobuf.Value` | `optional` | opcional (proto3 optional), objeto |

**Response:** `SetResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| _(sem campos)_ |  |  |  |  |

**Descrição encontrada:** Missing associated documentation comment in .proto file.

## 3.3 `Add`

**RPC path:** `/gsi.pb.project.Project/Add`

**Request:** `AddRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |
| `object` | 2 | `string` | `optional` | opcional (proto3 optional) |
| `data` | 3 | `google.protobuf.Value` | `optional` | opcional (proto3 optional), objeto |

**Response:** `AddResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `object` | 1 | `string` | `optional` | opcional (proto3 optional) |

**Descrição encontrada:** Missing associated documentation comment in .proto file.

## 3.4 `Delete`

**RPC path:** `/gsi.pb.project.Project/Delete`

**Request:** `DeleteRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |
| `object` | 2 | `string` | `optional` | opcional (proto3 optional) |
| `force_delete` | 3 | `bool` | `optional` | opcional (proto3 optional) |

**Response:** `DeleteResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| _(sem campos)_ |  |  |  |  |

**Descrição encontrada:** Missing associated documentation comment in .proto file.

## 3.5 `SolveAnalyses`

**RPC path:** `/gsi.pb.project.Project/SolveAnalyses`

**Request:** `SolveAnalysesRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analyses` | 1 | `string` | `repeated` | lista |
| `step` | 2 | `uint32` | `optional` | opcional (proto3 optional) |
| `solve_dependencies` | 3 | `bool` | `optional` | opcional (proto3 optional) |

**Response:** `SolveAnalysesResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| _(sem campos)_ |  |  |  |  |

**Descrição encontrada:** Solves a list of analyses at a given step number.

## 3.6 `QueryTableParamsInfo`

**RPC path:** `/gsi.pb.project.Project/QueryTableParamsInfo`

**Request:** `QueryTableParamsInfoRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |
| `table` | 2 | `gsi.pb.Result.Type` | `optional` | opcional (proto3 optional), enum |

**Response:** `QueryTableParamsInfoResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `params_info` | 1 | `gsi.pb.project.ParamInfo` | `repeated` | lista, objeto |

**Descrição encontrada:** Query metadata for all DataParams stored in a requested DataTable.

## 3.7 `QueryResults`

**RPC path:** `/gsi.pb.project.Project/QueryResults`

**Request:** `QueryResultsRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |
| `step` | 2 | `uint32` | `optional` | opcional (proto3 optional) |
| `run` | 3 | `uint32` | `optional` | opcional (proto3 optional) |
| `instance` | 4 | `uint32` | `optional` | opcional (proto3 optional) |
| `table` | 5 | `gsi.pb.Result.Type` | `optional` | opcional (proto3 optional), enum |
| `dataparams` | 6 | `gsi.pb.DataParam.Type` | `repeated` | lista, enum |
| `result_ids` | 7 | `uint32` | `repeated` | lista |

**Response:** `QueryResultsResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `results` | 1 | `gsi.pb.project.QueryResultsResponse.ResultsEntry` | `repeated` | lista, objeto |

**Descrição encontrada:** Query results for an analysis.

## 3.8 `QueryResultsAvailability`

**RPC path:** `/gsi.pb.project.Project/QueryResultsAvailability`

**Request:** `QueryResultsAvailabilityRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |

**Response:** `QueryResultsAvailabilityResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `has_results` | 1 | `bool` | `optional` | opcional (proto3 optional) |

**Descrição encontrada:** Query whether an analysis has results available

## 3.9 `LoadResults`

**RPC path:** `/gsi.pb.project.Project/LoadResults`

**Request:** `LoadResultsRequest`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `analysis` | 1 | `string` | `optional` | opcional (proto3 optional) |

**Response:** `LoadResultsResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| _(sem campos)_ |  |  |  |  |

**Descrição encontrada:** Missing associated documentation comment in .proto file.

## 4. Mensagens auxiliares

### `ParamInfo`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `dataparam` | 1 | `gsi.pb.DataParam.Type` | `optional` | opcional (proto3 optional), enum |
| `key` | 2 | `string` | `optional` | opcional (proto3 optional) |
| `display` | 3 | `string` | `optional` | opcional (proto3 optional) |
| `unit_category` | 4 | `gsi.pb.UnitCategory.Type` | `optional` | opcional (proto3 optional), enum |
| `vector_components` | 5 | `gsi.pb.DataParam.Type` | `repeated` | lista, enum |
| `units` | 6 | `string` | `optional` | opcional (proto3 optional) |

### `ParamResults`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `values` | 1 | `double` | `repeated` | lista |

### `QueryResultsResponse`

| Campo | Nº | Tipo | Regra | Observações |
|---|---:|---|---|---|
| `results` | 1 | `gsi.pb.project.QueryResultsResponse.ResultsEntry` | `repeated` | lista, objeto |

## 5. Enum `gsi.pb.Result.Type`

Usado principalmente para indicar a tabela/conjunto de resultados consultado em `QueryTableParamsInfoRequest.table` e `QueryResultsRequest.table`.

| Valor | Número |
|---|---:|
| `Undefined` | 0 |
| `Nodes` | 1000 |
| `Elements` | 1002 |
| `Gauss` | 1003 |
| `ElementNodes` | 1004 |
| `Time` | 1005 |
| `NodePair` | 1006 |
| `Cover` | 1008 |
| `History` | 1009 |
| `TimeStep` | 1010 |
| `FlowPath` | 1011 |
| `Slip` | 1013 |
| `CriticalSlip` | 1014 |
| `Column` | 1015 |
| `Intercolumn` | 1016 |
| `LambdaFOS` | 1017 |
| `Reinforcement` | 1018 |
| `Sample` | 1023 |
| `Probabilistic` | 1024 |
| `Iteration` | 1025 |
| `BeamGauss` | 1026 |
| `ParticleAir` | 1027 |
| `ParticleWater` | 1028 |
| `SavedTimeStep` | 1102 |

## 6. Enum `gsi.pb.UnitCategory.Type`

Usado em `ParamInfo.unit_category` para classificar a categoria física da unidade.

| Valor | Número |
|---|---:|
| `Undefined` | 0 |
| `Length` | 1 |
| `Time` | 2 |
| `Force` | 3 |
| `Temperature` | 4 |
| `Mass` | 5 |
| `Energy` | 6 |
| `Angle` | 7 |
| `HydraulicHead` | 8 |
| `MassAir` | 9 |
| `MassWater` | 10 |
| `MassSolute` | 11 |
| `MassGas` | 12 |
| `ForcePerLength` | 13 |
| `SpringConstant` | 14 |
| `FactoredPullout` | 15 |
| `Pressure` | 16 |
| `Strength` | 17 |
| `Stiffness` | 18 |
| `UnitWeight` | 19 |
| `Velocity` | 20 |
| `ClimateVolumeFlux` | 21 |
| `FluidConductivity` | 22 |
| `Acceleration` | 23 |
| `DispersionCoefficient` | 24 |
| `DiffusionCoefficient` | 25 |
| `VolumeRateWater` | 26 |
| `VolumeRateAir` | 27 |
| `Density` | 28 |
| `Concentration` | 29 |
| `MassRate` | 30 |
| `MassRateAir` | 31 |
| `MassRateWater` | 32 |
| `MassRateSolute` | 33 |
| `MassRateGas` | 34 |
| `EnergyRate` | 35 |
| `VolumetricSpecificHeat` | 36 |
| `Moment` | 37 |
| `Compressibility` | 38 |
| `PerDensity` | 39 |
| `Frequency` | 40 |
| `ReactionRate` | 41 |
| `ThermalConductivity` | 42 |
| `Area` | 43 |
| `Volume` | 44 |
| `VolumeWater` | 45 |
| `VolumeAir` | 46 |
| `UnitMassFlux` | 52 |
| `LatentHeat` | 53 |
| `MomentOfInertia` | 54 |
| `GradientEnergy` | 55 |
| `SpecificHeat` | 57 |
| `MassPerMass` | 62 |
| `StrengthPerDepth` | 63 |
| `ConvectiveHeatTransferCoefficient` | 64 |
| `VolumeFluxWater` | 65 |
| `VolumeFluxAir` | 66 |
| `EnergyFlux` | 67 |
| `MassFlux` | 68 |
| `MassFluxAir` | 69 |
| `MassFluxWater` | 70 |
| `MassFluxSolute` | 71 |
| `MassFluxGas` | 72 |
| `SnowDepth` | 73 |
| `RootDepth` | 74 |
| `VegetationHeight` | 75 |
| `Displacement` | 77 |
| `DeltaTemperature` | 78 |

## 7. Enum `gsi.pb.DataParam.Type`

Usado em `ParamInfo.dataparam`, `ParamInfo.vector_components` e `QueryResultsRequest.dataparams`. A lista abaixo foi extraída do enum protobuf gerado.

| Valor | Número |
|---|---:|
| `eUndefined` | 0 |
| `eNodeNum` | 1 |
| `eElemNum` | 2 |
| `eElemNumAtGroundSurface` | 3 |
| `eXCoord` | 4 |
| `eYCoord` | 5 |
| `eZCoord` | 6 |
| `eWaterTotalHead` | 7 |
| `eElevation` | 8 |
| `eWaterPressureHead` | 9 |
| `eXVelocity` | 10 |
| `eYVelocity` | 11 |
| `eXYVelocity` | 12 |
| `eWaterGradientX` | 13 |
| `eWaterGradientY` | 14 |
| `eWaterGradientZ` | 15 |
| `eWaterGradient` | 16 |
| `eWaterConductivityX` | 17 |
| `eWaterConductivityY` | 18 |
| `eWaterConductivityZ` | 19 |
| `eVolWC` | 20 |
| `eDistance` | 21 |
| `eTime` | 22 |
| `eTemperature` | 23 |
| `eConcentration` | 24 |
| `eAdsorption` | 25 |
| `eXPeclet` | 26 |
| `eYPeclet` | 27 |
| `eZPeclet` | 28 |
| `ePeclet` | 29 |
| `eXCourant` | 30 |
| `eYCourant` | 31 |
| `eZCourant` | 32 |
| `eCourant` | 33 |
| `eXXDispersionCoef` | 34 |
| `eYYDispersionCoef` | 35 |
| `eZZDispersionCoef` | 36 |
| `eDispersionCoef` | 37 |
| `eXYDispersionCoef` | 38 |
| `eXZDispersionCoef` | 39 |
| `eYZDispersionCoef` | 40 |
| `eXDisplacement` | 41 |
| `eYDisplacement` | 42 |
| `eZDisplacement` | 43 |
| `eXYDisplacement` | 44 |
| `eXAcceleration` | 45 |
| `eYAcceleration` | 46 |
| `eXYAcceleration` | 47 |
| `eXBoundaryForce` | 48 |
| `eYBoundaryForce` | 49 |
| `eZBoundaryForce` | 50 |
| `eXYBoundaryForce` | 51 |
| `eXTotalStress` | 52 |
| `eYTotalStress` | 53 |
| `eZTotalStress` | 54 |
| `eMaxTotalStress` | 55 |
| `eMinTotalStress` | 56 |
| `eMeanTotalStress` | 57 |
| `eXEffectiveStress` | 58 |
| `eYEffectiveStress` | 59 |
| `eZEffectiveStress` | 60 |
| `eMaxEffectiveStress` | 61 |
| `eMinEffectiveStress` | 62 |
| `eMeanEffectiveStress` | 63 |
| `eNormalEffectiveStress` | 64 |
| `eXYShearStress` | 65 |
| `eMaxShearStress` | 66 |
| `eDeviatoricStress` | 67 |
| `eWaterPressure` | 68 |
| `eWaterPressureCalculated` | 69 |
| `eXStrain` | 70 |
| `eYStrain` | 71 |
| `eZStrain` | 72 |
| `eXYShearStrain` | 73 |
| `eMaxStrain` | 74 |
| `eMinStrain` | 75 |
| `eMaxShearStrain` | 76 |
| `ePeakShearStress` | 77 |
| `ePeakShearStrain` | 78 |
| `eEQShearModulus` | 79 |
| `eEQDampingRatio` | 80 |
| `eVolumetricStrain` | 81 |
| `eDeviatoricStrain` | 82 |
| `ePoissonsRatio` | 83 |
| `eUndrainedShearStrength` | 84 |
| `eVoidRatio` | 85 |
| `eTanModulus` | 86 |
| `eAxialForce` | 87 |
| `eShearForce` | 88 |
| `eMoment` | 89 |
| `eRotation` | 90 |
| `eStepNum` | 91 |
| `ePeriod` | 92 |
| `eFrequency` | 93 |
| `eXSpectralAcc` | 94 |
| `eYSpectralAcc` | 95 |
| `eXSpectralVel` | 96 |
| `eYSpectralVel` | 97 |
| `eXSpectralDisp` | 98 |
| `eYSpectralDisp` | 99 |
| `eThermalConductivity` | 100 |
| `eXXEffectiveThermalConductivity` | 101 |
| `eYYEffectiveThermalConductivity` | 102 |
| `eZZEffectiveThermalConductivity` | 103 |
| `eEffectiveThermalConductivity` | 104 |
| `eXYEffectiveThermalConductivity` | 105 |
| `eXZEffectiveThermalConductivity` | 106 |
| `eYZEffectiveThermalConductivity` | 107 |
| `eUnfrozenWC` | 108 |
| `eVolHeatCapacity` | 109 |
| `eXThermalPeclet` | 110 |
| `eYThermalPeclet` | 111 |
| `eZThermalPeclet` | 112 |
| `eThermalPeclet` | 113 |
| `eXThermalCourant` | 114 |
| `eYThermalCourant` | 115 |
| `eZThermalCourant` | 116 |
| `eThermalCourant` | 117 |
| `eSnowDepth` | 118 |
| `eNetRad` | 119 |
| `eGasConcentration` | 120 |
| `eGasDiffCoeff` | 121 |
| `eCSR` | 122 |
| `eFlowPath` | 123 |
| `eFlowPathDist` | 124 |
| `eFlowPathAirFlux` | 125 |
| `eFlowPathHeatFlux` | 126 |
| `eFlowPathWaterFlux` | 127 |
| `eCamClayHardening` | 128 |
| `eTanStiffness` | 129 |
| `eYield_deprecated` | 130 |
| `ePlasticState` | 131 |
| `eFailureSurface` | 132 |
| `eCapSurface` | 133 |
| `eShearSurface` | 134 |
| `eTensionSurface` | 135 |
| `eJointShearSurface` | 136 |
| `eJointTensionSurface` | 137 |
| `eKModifier` | 138 |
| `eAirTotalHead` | 139 |
| `eAirPressure` | 140 |
| `eColumnTau` | 141 |
| `eAirGradientX` | 142 |
| `eAirGradientY` | 143 |
| `eAirGradientZ` | 144 |
| `eAirGradient` | 145 |
| `eAirDensity` | 146 |
| `eAirConductivityX` | 147 |
| `eAirConductivityY` | 148 |
| `eAirConductivityZ` | 149 |
| `eAirVolumetricContent` | 150 |
| `eMatricSuction` | 151 |
| `eGasRate` | 152 |
| `eThermalGradientX` | 153 |
| `eThermalGradientY` | 154 |
| `eThermalGradientZ` | 155 |
| `eThermalGradient` | 156 |
| `eXPeakAcceleration` | 157 |
| `eYPeakAcceleration` | 158 |
| `eXPeakVelocity` | 159 |
| `eYPeakVelocity` | 160 |
| `eXPeakDisplacement` | 161 |
| `eYPeakDisplacement` | 162 |
| `eGaussPointNum` | 163 |
| `eStepIterationCount` | 164 |
| `eTotalIterationCount` | 165 |
| `eLambdaStage0` | 166 |
| `eLambdaStage1` | 167 |
| `eLambdaXStage0` | 168 |
| `eLambdaXStage1` | 169 |
| `eLambdaZStage0` | 170 |
| `eLambdaZStage1` | 171 |
| `eLambdaXZStage0` | 172 |
| `eLambdaXZStage1` | 173 |
| `eRawSlipFOSXStage0` | 174 |
| `eRawSlipFOSXStage1` | 175 |
| `ePWP_Excess` | 176 |
| `eYInitialEffective` | 177 |
| `eSoilVolume` | 178 |
| `eAxialStress` | 179 |
| `eAxialStrain` | 180 |
| `eAxialIncForce` | 181 |
| `ePreForce` | 182 |
| `eNodePairNum` | 183 |
| `eBeamGaussNum` | 184 |
| `ePWPRatio` | 185 |
| `eModifierFactor` | 186 |
| `eLeafAreaIndex` | 187 |
| `eLimitingFactor` | 188 |
| `eGasFlux` | 189 |
| `eXBoundaryStress` | 190 |
| `eYBoundaryStress` | 191 |
| `eZBoundaryStress` | 192 |
| `eNormalBoundaryStress` | 193 |
| `eTanBoundaryStress` | 194 |
| `eFluidBoundaryElevation` | 195 |
| `eCyclicNumber` | 196 |
| `eGGMaxRatio` | 197 |
| `eKalpha` | 198 |
| `eKsigma` | 199 |
| `eProbability` | 200 |
| `eEModulus` | 201 |
| `eGmax` | 202 |
| `eVolume` | 203 |
| `eMass` | 204 |
| `eShearStressRatio` | 205 |
| `eCyclicNumberRatio` | 206 |
| `eCyclicShearStrain` | 207 |
| `eOverburdenPressure` | 208 |
| `eInclination` | 209 |
| `eDegSaturation` | 210 |
| `eTotalCohesion` | 211 |
| `eEffectiveCohesion` | 212 |
| `eEffectivePhi` | 213 |
| `eTanModulusInit` | 214 |
| `ePx` | 215 |
| `eLoadPath` | 216 |
| `eTensionSig3` | 217 |
| `eMaxDeviatoricStress` | 218 |
| `eIncVolStrain` | 219 |
| `eAccVolStrain` | 220 |
| `eRecModulus` | 221 |
| `eDiffusionCoef` | 222 |
| `eNormalStress` | 223 |
| `eShearStress` | 224 |
| `eGammaCC` | 225 |
| `eXRelVelocity` | 226 |
| `eYRelVelocity` | 227 |
| `eXYRelVelocity` | 228 |
| `eFS_Liquifaction` | 229 |
| `eXRelDisplacement` | 230 |
| `eYRelDisplacement` | 231 |
| `eXYRelDisplacement` | 232 |
| `eStrengthCohesive` | 233 |
| `eStrengthFrictional` | 234 |
| `eStrengthSuction` | 235 |
| `eShearStrength` | 236 |
| `eShearMob` | 237 |
| `eBaseCohesion` | 238 |
| `eBasePhi` | 239 |
| `eBasePhiB` | 240 |
| `eBaseNormalStress` | 241 |
| `eIntersliceAppliedFn` | 242 |
| `eIntersliceSpecifiedFn` | 243 |
| `eIntersliceNormalForce` | 244 |
| `eIntersliceShearForce` | 245 |
| `eIntercolumnNormalForceX` | 246 |
| `eIntercolumnVerticalShearForceX` | 247 |
| `eIntercolumnHorizontalShearForceX` | 248 |
| `eIntercolumnNormalForceZ` | 249 |
| `eIntercolumnVerticalShearForceZ` | 250 |
| `eIntercolumnHorizontalShearForceZ` | 251 |
| `eIntercolumnNormalForce` | 252 |
| `eIntercolumnVerticalShearForce` | 253 |
| `eIntercolumnHorizontalShearForce` | 254 |
| `emAlphaX` | 255 |
| `eStabilityFactor` | 256 |
| `eSliceNum` | 257 |
| `eIntersliceNum` | 258 |
| `eColumnNum` | 259 |
| `eIntercolumnNum` | 260 |
| `eReinfLineNum` | 261 |
| `eMaxPulloutForce` | 262 |
| `eBondLength` | 263 |
| `eForceOrientation` | 264 |
| `eIsFOSDependent` | 265 |
| `eWithAnchorage` | 266 |
| `eInterfaceShearAngle` | 267 |
| `eInterfaceCohesion` | 268 |
| `eMaxBondLength` | 269 |
| `eSurfaceAreaFactor` | 270 |
| `eFactoredPulloutResistance` | 271 |
| `eReinfLineLength` | 272 |
| `eReinfLineTrend` | 273 |
| `eReinfLinePlunge` | 274 |
| `eSlipXIntersect` | 275 |
| `eSlipYIntersect` | 276 |
| `eSlipZIntersect` | 277 |
| `eReinfLineAvailableLength` | 278 |
| `ePulloutForce` | 279 |
| `ePulloutForceDirectionX` | 280 |
| `ePulloutForceDirectionY` | 281 |
| `ePulloutForceDirectionZ` | 282 |
| `eReinfLineShearForce` | 283 |
| `eReinfLineShearForceDirectionX` | 284 |
| `eReinfLineShearForceDirectionY` | 285 |
| `eReinfLineShearForceDirectionZ` | 286 |
| `eGoverningComponent` | 287 |
| `eFactoredTensileCapacityUnits` | 288 |
| `eFactoredPulloutResistanceGeoUnits` | 289 |
| `eFactoredPulloutResistanceUnits` | 290 |
| `eFinalDisplacementNorm` | 291 |
| `eSlipNum` | 292 |
| `eSlipNumUnsorted` | 293 |
| `eRawSlipFOS` | 294 |
| `eOptimizedFosProgression` | 295 |
| `eSlipVolume` | 296 |
| `eSlipWeight` | 297 |
| `eResistingMoment` | 298 |
| `eResistingMomentX` | 299 |
| `eResistingMomentZ` | 300 |
| `eActivatingMoment` | 301 |
| `eActivatingMomentX` | 302 |
| `eActivatingMomentZ` | 303 |
| `eResistingForce` | 304 |
| `eResistingForceX` | 305 |
| `eResistingForceZ` | 306 |
| `eActivatingForce` | 307 |
| `eActivatingForceX` | 308 |
| `eActivatingForceZ` | 309 |
| `eSlipOutlinePointNum` | 310 |
| `eSlipOptimizationPtNum` | 311 |
| `eShearForceUnitVectorX` | 312 |
| `eShearForceUnitVectorY` | 313 |
| `eShearForceUnitVectorZ` | 314 |
| `eBaseNormalizedAngleInDegree` | 315 |
| `eModifier` | 316 |
| `eDegreeOfUtilization` | 317 |
| `eXRelAcceleration` | 318 |
| `eYRelAcceleration` | 319 |
| `eXYRelAcceleration` | 320 |
| `eQPRatio` | 321 |
| `eEtaOverMu` | 322 |
| `eParentElementId` | 323 |
| `eRelativeId` | 324 |
| `eWaterPrevIterConductivityX` | 325 |
| `eUnitWeight` | 326 |
| `eSlopeCohesion` | 327 |
| `eSlopePhi` | 328 |
| `eLiquefied` | 329 |
| `eSlipFOSMean` | 330 |
| `eSlipFOSMin` | 331 |
| `eSlipFOSMax` | 332 |
| `eSlipFOSStdDev` | 333 |
| `eSlipReliabilityIndex` | 334 |
| `eSlipLogReliabilityIndex` | 335 |
| `eSlipProbOfFailure` | 336 |
| `eCustomParam1` | 337 |
| `eCustomParam2` | 338 |
| `eCustomParam3` | 339 |
| `eCustomParam4` | 340 |
| `eCustomParam5` | 341 |
| `eCustomParam6` | 342 |
| `eCustomParam7` | 343 |
| `eCustomParam8` | 344 |
| `eCustomParam9` | 345 |
| `eRelSurfaceAngle` | 346 |
| `eRelBaseAngle` | 347 |
| `eXZCoord` | 348 |
| `eYGroundSurface` | 349 |
| `eRatio` | 350 |
| `eSeismicForceX` | 351 |
| `eSeismicForceY` | 352 |
| `eSeismicForceZ` | 353 |
| `eSeismicForce` | 354 |
| `eColumnForceX` | 355 |
| `eColumnForceY` | 356 |
| `eColumnForceZ` | 357 |
| `eColumnForce` | 358 |
| `eColumnForceLocationX` | 359 |
| `eColumnForceLocationY` | 360 |
| `eColumnForceLocationZ` | 361 |
| `eSeismicForceXZ` | 362 |
| `eSurchargeForceX` | 363 |
| `eSurchargeForceY` | 364 |
| `eSurchargeForceZ` | 365 |
| `eSurchargeForce` | 366 |
| `ePointForceX` | 367 |
| `ePointForceY` | 368 |
| `ePointForceZ` | 369 |
| `ePointForce` | 370 |
| `eReinforcementForceX` | 371 |
| `eReinforcementForceY` | 372 |
| `eReinforcementForceZ` | 373 |
| `eReinforcementForce` | 374 |
| `eReinforcementShearForceX` | 375 |
| `eReinforcementShearForceY` | 376 |
| `eReinforcementShearForceZ` | 377 |
| `eReinforcementShearForce` | 378 |
| `eKMax` | 379 |
| `eBaseLength` | 380 |
| `eBaseArea` | 381 |
| `eColumnWidth` | 382 |
| `eColumnArea` | 383 |
| `eTopAlphaX` | 384 |
| `eTopAlphaZ` | 385 |
| `eBotAlphaX` | 386 |
| `eBotAlphaZ` | 387 |
| `eColumnDipAngle` | 388 |
| `eColumnDipDirection` | 389 |
| `eIsMidPlaneColumn` | 390 |
| `eAnisotropicSurfaceDipAngle` | 391 |
| `eAnisotropicSurfaceDipDirection` | 392 |
| `eLambdaEntryNum` | 393 |
| `eLambda` | 394 |
| `eLambdaX` | 395 |
| `eLambdaZ` | 396 |
| `eLambdaXZ` | 397 |
| `eFOSByForce` | 398 |
| `eFOSByMoment` | 399 |
| `eFOSX` | 400 |
| `eFOSZ` | 401 |
| `eLambdaAxisDirection` | 402 |
| `eMobilizedShearDirectionNum` | 403 |
| `eXLeft` | 404 |
| `eXRight` | 405 |
| `eZFront` | 406 |
| `eZBack` | 407 |
| `eYBackBotLeft` | 408 |
| `eYBackBotRight` | 409 |
| `eYBackTopLeft` | 410 |
| `eYBackTopRight` | 411 |
| `eYFrontBotLeft` | 412 |
| `eYFrontBotRight` | 413 |
| `eYFrontTopLeft` | 414 |
| `eYFrontTopRight` | 415 |
| `eLeftColumnId` | 416 |
| `eRightColumnId` | 417 |
| `eBackColumnId` | 418 |
| `eFrontColumnId` | 419 |
| `ePrevColumnId` | 420 |
| `eNextColumnId` | 421 |
| `eAxisXZ` | 422 |
| `eSlipCenterX` | 423 |
| `eSlipCenterY` | 424 |
| `eSlipCenterZ` | 425 |
| `eSlipCenterUI` | 426 |
| `eSlipRadius` | 427 |
| `eSlipRadiusX` | 428 |
| `eSlipRadiusY` | 429 |
| `eSlipRadiusZ` | 430 |
| `eSlipRadiusUI` | 431 |
| `eSlipRotation1` | 432 |
| `eSlipRotation2` | 433 |
| `eSlipRotation3` | 434 |
| `eSlipRotationUI` | 435 |
| `eSlipRotationOrder` | 436 |
| `eSlipNExponent` | 437 |
| `eSlipSearchPtX` | 438 |
| `eSlipSearchPtZ` | 439 |
| `eSlipOrigSearchMethod` | 440 |
| `eSlipSurfUINum` | 441 |
| `eTotalActiveColumns` | 442 |
| `eTotalSlidingSurfaceArea` | 443 |
| `eProjectedFailureSurfaceArea` | 444 |
| `eProjectedFailureSurfaceCentroidX` | 445 |
| `eProjectedFailureSurfaceCentroidZ` | 446 |
| `eProjectedFailureSurfaceCentroidUI` | 447 |
| `eSlipMaximumDepth` | 448 |
| `eSlipAspectRatioY` | 449 |
| `eSlipAspectRatioZ` | 450 |
| `eSlipAspectRatioUI` | 451 |
| `eYTopLayer` | 452 |
| `eAverageAcceleration` | 453 |
| `eYieldAcceleration` | 454 |
| `eVelocity` | 455 |
| `eDeformation` | 456 |
| `eColumnWeight` | 457 |
| `eColumnWeightWithSeismic` | 458 |
| `ePoreWaterForce` | 459 |
| `eAirForce` | 460 |
| `eBaseNormalForce` | 461 |
| `eShearMobForce` | 462 |
| `eSliceMidHeight` | 463 |
| `eBasePhiInDegree` | 464 |
| `eBaseNormalizedAngle` | 465 |
| `eBasePhiBInDegree` | 466 |
| `eRunNum` | 467 |
| `ePressureHeadDelta` | 468 |
| `ePressureHeadConvSigDigits` | 469 |
| `eTemperatureDelta` | 470 |
| `eTemperatureConvSigDigits` | 471 |
| `eXYDisplacementDelta_deprecated` | 472 |
| `eConcentrationDelta` | 473 |
| `eConcentrationConvSigDigits` | 474 |
| `eReviewStatus` | 475 |
| `eIterationNum` | 476 |
| `eReviewNum` | 477 |
| `eConvIterationNum` | 478 |
| `ePressureHeadUnconvNodes` | 479 |
| `eTemperatureUnconvNodes` | 480 |
| `eXYDisplacementUnconvNodes` | 481 |
| `eConcentrationUnconvNodes` | 482 |
| `eAirTemperature` | 483 |
| `eWindSpeed` | 484 |
| `eVegetationHeight` | 485 |
| `eEvaporation` | 486 |
| `eConvectiveCoefficient` | 487 |
| `eSolarRadiationFlux` | 488 |
| `eNetRadiationFlux` | 489 |
| `eTimeDelta` | 490 |
| `eAlbedo` | 491 |
| `eColumnBbarWeight` | 492 |
| `eViewSlipFOS` | 493 |
| `eWaterUnitWeight` | 494 |
| `eAirUnitWeight` | 495 |
| `eAirPressureHead` | 496 |
| `eXSurchargeWaterForce` | 497 |
| `eYSurchargeWaterForce` | 498 |
| `eZSurchargeWaterForce` | 499 |
| `eElemNodeTableNum` | 500 |
| `eAirPressureUnconvNodes` | 501 |
| `eAirPressureDelta` | 502 |
| `eAirPressureConvSigDigits` | 503 |
| `eAirIterationCount` | 504 |
| `eHeatIterationCount` | 505 |
| `eWaterIterationCount` | 506 |
| `ePorosity` | 507 |
| `eWaterDensity` | 508 |
| `eWaterStorageCoefficient` | 509 |
| `eWaterCoupledAirLambda` | 510 |
| `eWaterCoupledHeatLambda` | 511 |
| `eWaterCoupledStressLambda` | 512 |
| `eAirCoupledHeatLambda` | 513 |
| `eAirCoupledWaterLambda` | 514 |
| `eVolHeatCapacityWater` | 515 |
| `eInsituYTotalStress` | 516 |
| `eInsituPWP` | 517 |
| `eMaterialID` | 518 |
| `eMaterialModel` | 519 |
| `eColumnBaseMaterial` | 520 |
| `eTransPWP` | 521 |
| `ePrimaryBoundary0` | 522 |
| `ePrimaryBoundary1` | 523 |
| `ePrimaryBoundary2` | 524 |
| `ePrimaryBoundary3` | 525 |
| `eHeatBoundaryStoredForcing` | 526 |
| `eWaterBoundaryStoredForcing` | 527 |
| `eAirBoundaryStoredForcing` | 528 |
| `eSoluteBoundaryStoredForcing` | 529 |
| `eVolHeatCapacityAir` | 530 |
| `eWaterRate` | 531 |
| `eWaterVolume` | 532 |
| `eWaterCumulativeVolume` | 533 |
| `eWaterMassRate` | 534 |
| `eWaterMass` | 535 |
| `eWaterCumulativeMass` | 536 |
| `eHeatRate` | 537 |
| `eHeatTransfer` | 538 |
| `eHeatCumulativeTransfer` | 539 |
| `eAirMassRate` | 540 |
| `eAirMass` | 541 |
| `eAirCumulativeMass` | 542 |
| `eAirRate` | 543 |
| `eAirVolume` | 544 |
| `eAirCumulativeVolume` | 545 |
| `eHeatFluxX` | 546 |
| `eHeatFluxY` | 547 |
| `eHeatFluxZ` | 548 |
| `eHeatFlux` | 549 |
| `eWaterFluxX` | 550 |
| `eWaterFluxY` | 551 |
| `eWaterFluxZ` | 552 |
| `eWaterFlux` | 553 |
| `eWaterMassFluxX` | 554 |
| `eWaterMassFluxY` | 555 |
| `eWaterMassFluxZ` | 556 |
| `eWaterMassFlux` | 557 |
| `eAirFluxX` | 558 |
| `eAirFluxY` | 559 |
| `eAirFluxZ` | 560 |
| `eAirFlux` | 561 |
| `eAirMassFluxX` | 562 |
| `eAirMassFluxY` | 563 |
| `eAirMassFluxZ` | 564 |
| `eAirMassFlux` | 565 |
| `eFrozenSoilMatricSuction` | 566 |
| `eDryDensity` | 567 |
| `eDecayConstant` | 568 |
| `eSoluteMassRate` | 569 |
| `eSoluteMass` | 570 |
| `eSoluteCumulativeMass` | 571 |
| `eSoluteMassFluxX` | 572 |
| `eSoluteMassFluxY` | 573 |
| `eSoluteMassFluxZ` | 574 |
| `eSoluteMassFlux` | 575 |
| `eXConcentrationGradient` | 576 |
| `eYConcentrationGradient` | 577 |
| `eZConcentrationGradient` | 578 |
| `eConcentrationGradient` | 579 |
| `eSoluteIterationCount` | 580 |
| `eVolWaterContentChordSlope` | 581 |
| `eWaterUnitGradientFluxX` | 582 |
| `eWaterUnitGradientFluxY` | 583 |
| `eWaterUnitGradientFluxZ` | 584 |
| `eWaterUnitGradientFlux` | 585 |
| `eGasMassRate` | 586 |
| `eGasMass` | 587 |
| `eGasCumulativeMass` | 588 |
| `eGasMassFluxX` | 589 |
| `eGasMassFluxY` | 590 |
| `eGasMassFluxZ` | 591 |
| `eGasMassFlux` | 592 |
| `eGasConcentrationGradientX` | 593 |
| `eGasConcentrationGradientY` | 594 |
| `eGasConcentrationGradientZ` | 595 |
| `eGasConcentrationGradient` | 596 |
| `eGasIterationCount` | 597 |
| `eEquivalentDiffusionPorosity` | 598 |
| `eSolubilityCoefficient` | 599 |
| `eGasDecayConstant` | 600 |
| `eReactionRate` | 601 |
| `eGasPecletX` | 602 |
| `eGasPecletY` | 603 |
| `eGasPecletZ` | 604 |
| `eGasPeclet` | 605 |
| `eGasCourantX` | 606 |
| `eGasCourantY` | 607 |
| `eGasCourantZ` | 608 |
| `eGasCourant` | 609 |
| `eVapourFluxX` | 610 |
| `eVapourFluxY` | 611 |
| `eVapourFluxZ` | 612 |
| `eVapourFlux` | 613 |
| `eVapourMassFluxX` | 614 |
| `eVapourMassFluxY` | 615 |
| `eVapourMassFluxZ` | 616 |
| `eVapourMassFlux` | 617 |
| `eVapourDensity` | 618 |
| `eVapourDeltaMassPerTotalVolume` | 619 |
| `eSampleCount` | 620 |
| `eOffset` | 621 |
| `eWaterVelocityX` | 622 |
| `eWaterVelocityY` | 623 |
| `eWaterVelocityZ` | 624 |
| `eWaterVelocity` | 625 |
| `eAirVelocityX` | 626 |
| `eAirVelocityY` | 627 |
| `eAirVelocityZ` | 628 |
| `eAirVelocity` | 629 |
| `eGasSourceConcentration` | 630 |
| `eColumnWeightUnfactored` | 631 |
| `eMobilizedShearDirection` | 632 |
| `eSlidingDirection` | 633 |
| `eTanPhi` | 634 |
| `eColumnInclination` | 635 |
| `eGasBoundaryStoredForcing` | 636 |
| `eGasConcentrationUnconvNodes` | 637 |
| `eGasConcentrationDelta` | 638 |
| `eGasConcentrationConvSigDigits` | 639 |
| `eGasDissolvedConcentration` | 640 |
| `eGasXXDispersionCoef` | 641 |
| `eGasYYDispersionCoef` | 642 |
| `eGasZZDispersionCoef` | 643 |
| `eGasDispersionCoef` | 644 |
| `eGasXYDispersionCoef` | 645 |
| `eGasXZDispersionCoef` | 646 |
| `eGasYZDispersionCoef` | 647 |
| `eGasDissolvedXXDispersionCoef` | 648 |
| `eGasDissolvedYYDispersionCoef` | 649 |
| `eGasDissolvedZZDispersionCoef` | 650 |
| `eGasDissolvedDispersionCoef` | 651 |
| `eGasDissolvedXYDispersionCoef` | 652 |
| `eGasDissolvedXZDispersionCoef` | 653 |
| `eGasDissolvedYZDispersionCoef` | 654 |
| `eGasDissolvedPecletX` | 655 |
| `eGasDissolvedPecletY` | 656 |
| `eGasDissolvedPecletZ` | 657 |
| `eGasDissolvedPeclet` | 658 |
| `eGasDissolvedCourantX` | 659 |
| `eGasDissolvedCourantY` | 660 |
| `eGasDissolvedCourantZ` | 661 |
| `eGasDissolvedCourant` | 662 |
| `eGasDissolvedDiffusionCoefficient` | 663 |
| `eRelativeHumidity` | 664 |
| `eXSurchargeLoadForce` | 665 |
| `eYSurchargeLoadForce` | 666 |
| `eZSurchargeLoadForce` | 667 |
| `eNormRootDensity` | 668 |
| `eNormRootDepth` | 669 |
| `eSoilCoverFraction` | 670 |
| `eRootDepthMagnitude` | 671 |
| `ePrecipitation` | 672 |
| `eIsothermalVapourMassFluxX` | 673 |
| `eIsothermalVapourMassFluxY` | 674 |
| `eIsothermalVapourMassFluxZ` | 675 |
| `eIsothermalVapourMassFlux` | 676 |
| `ePhaseChangeTemperature` | 677 |
| `eSoluteDispersiveMassFluxX` | 678 |
| `eSoluteDispersiveMassFluxY` | 679 |
| `eSoluteDispersiveMassFluxZ` | 680 |
| `eSoluteDispersiveMassFlux` | 681 |
| `eGasDispersiveMassFluxX` | 682 |
| `eGasDispersiveMassFluxY` | 683 |
| `eGasDispersiveMassFluxZ` | 684 |
| `eGasDispersiveMassFlux` | 685 |
| `eCosineAngleFromHorizontal` | 686 |
| `eWaterFluxNormal` | 687 |
| `eAirFluxNormal` | 688 |
| `eWaterDomainMassChange` | 689 |
| `eWaterCumulativeDomainMassChange` | 690 |
| `eWaterDomainMass` | 691 |
| `eWaterDomainVolumeChange` | 692 |
| `eWaterDomainCumulativeVolumeChange` | 693 |
| `eWaterDomainVolume` | 694 |
| `eSoluteDomainDissolvedMass` | 695 |
| `eSoluteDomainAdsorbedMass` | 696 |
| `eWaterRainfallFlux` | 697 |
| `eWaterRainfall` | 698 |
| `eWaterCumulativeRainfall` | 699 |
| `eWaterSnowMeltFlux` | 700 |
| `eWaterSnowMelt` | 701 |
| `eWaterCumulativeSnowMelt` | 702 |
| `eWaterEvaporativeFlux` | 703 |
| `eWaterEvaporation` | 704 |
| `eWaterCumulativeEvaporation` | 705 |
| `eWaterRunoffFlux` | 706 |
| `eWaterRunoff` | 707 |
| `eWaterCumulativeRunoff` | 708 |
| `eWaterNetInfiltrationFlux` | 709 |
| `eWaterNetInfiltration` | 710 |
| `eWaterCumulativeNetInfiltration` | 711 |
| `eWaterPotentialEvapFlux` | 712 |
| `eWaterPotentialEvap` | 713 |
| `eWaterCumulativePotentialEvap` | 714 |
| `eWaterTranspirationFlux` | 715 |
| `eWaterTranspiration` | 716 |
| `eWaterCumulativeTranspiration` | 717 |
| `eWaterBalanceError` | 718 |
| `eWaterRelativeBalanceError` | 719 |
| `eWaterRainfallRate` | 720 |
| `eWaterSnowMeltRate` | 721 |
| `eWaterEvaporativeRate` | 722 |
| `eWaterRunoffRate` | 723 |
| `eWaterNetInfiltrationRate` | 724 |
| `eWaterPotentialEvapRate` | 725 |
| `eWaterTranspirationRate` | 726 |
| `eNetRadiationRate` | 727 |
| `eWaterCorrectedRainfallRate` | 728 |
| `eWaterCorrectedSnowMeltRate` | 729 |
| `eWaterCorrectedEvaporativeRate` | 730 |
| `eWaterCorrectedRunoffRate` | 731 |
| `eWaterCorrectedNetInfiltrationRate` | 732 |
| `eWaterCorrectedPotentialEvapRate` | 733 |
| `eWaterCorrectedTranspirationRate` | 734 |
| `eAirTemperatureDailyMin` | 735 |
| `eAirTemperatureDailyMax` | 736 |
| `eRelativeHumidityDailyMin` | 737 |
| `eRelativeHumidityDailyMax` | 738 |
| `eWaterSurfaceNodalRunoffRate` | 739 |
| `eWaterSurfaceNodalEvaporativeRate` | 740 |
| `eGlobalNodeNum` | 741 |
| `eGlobalElemNum` | 742 |
| `eStressIterationCount` | 743 |
| `eBulkModulusSoilSkeleton` | 744 |
| `eEquivalentBulkModulusPoreFluid` | 745 |
| `eAverageEffectiveSaturation` | 746 |
| `eXDisplacementIncrement` | 747 |
| `eYDisplacementIncrement` | 748 |
| `eZDisplacementIncrement` | 749 |
| `eDisplacementIncrement` | 750 |
| `eXForceIncrement` | 751 |
| `eYForceIncrement` | 752 |
| `eZForceIncrement` | 753 |
| `eForceIncrement` | 754 |
| `eXForce` | 755 |
| `eYForce` | 756 |
| `eZForce` | 757 |
| `eForce` | 758 |
| `eXAssembledForceIncrement` | 759 |
| `eYAssembledForceIncrement` | 760 |
| `eZAssembledForceIncrement` | 761 |
| `eAssembledForceIncrement` | 762 |
| `eXAssembledMomentIncrement` | 763 |
| `eYAssembledMomentIncrement` | 764 |
| `eZAssembledMomentIncrement` | 765 |
| `eAssembledMomentIncrement` | 766 |
| `eXResidualForceIncrement` | 767 |
| `eYResidualForceIncrement` | 768 |
| `eZResidualForceIncrement` | 769 |
| `eResidualForceIncrement` | 770 |
| `eXResidualMomentIncrement` | 771 |
| `eYResidualMomentIncrement` | 772 |
| `eZResidualMomentIncrement` | 773 |
| `eResidualMomentIncrement` | 774 |
| `eXResidualFirstIteration` | 775 |
| `eYResidualFirstIteration` | 776 |
| `eZResidualFirstIteration` | 777 |
| `eResidualFirstIteration` | 778 |
| `eXResidualMomentFirstIteration` | 779 |
| `eYResidualMomentFirstIteration` | 780 |
| `eZResidualMomentFirstIteration` | 781 |
| `eResidualMomentFirstIteration` | 782 |
| `eXLinearForceIncrement` | 783 |
| `eYLinearForceIncrement` | 784 |
| `eZLinearForceIncrement` | 785 |
| `eXGravityForceIncrement` | 786 |
| `eYGravityForceIncrement` | 787 |
| `eZGravityForceIncrement` | 788 |
| `eXStrainIncrement` | 789 |
| `eYStrainIncrement` | 790 |
| `eZStrainIncrement` | 791 |
| `eXYShearStrainIncrement` | 792 |
| `eYZShearStrainIncrement` | 793 |
| `eZXShearStrainIncrement` | 794 |
| `ePWPIncrement` | 795 |
| `eStrainIncrements` | 796 |
| `ePartialMaterialFactor` | 797 |
| `eNormalizedDomainStiffness_deprecated` | 798 |
| `eVectorNormDisplacements` | 799 |
| `eDeviatoricStrainIncrement` | 800 |
| `eDeviatoricStrainIncrementDEJ` | 801 |
| `eDeviatoricStrainEJ` | 802 |
| `eUnbalancedEnergy` | 803 |
| `eTolerableRelativeErrorStress` | 804 |
| `eRelativeUnbalancedEnergyError` | 805 |
| `eRelativeDisplacementError` | 806 |
| `eRelativeResidualForceError` | 807 |
| `eYZShearStress` | 808 |
| `eZXShearStress` | 809 |
| `eYZShearStrain` | 810 |
| `eZXShearStrain` | 811 |
| `eEffectiveStresses` | 812 |
| `eTotalStresses` | 813 |
| `eStrains` | 814 |
| `eXTotalStressIncrement` | 815 |
| `eYTotalStressIncrement` | 816 |
| `eZTotalStressIncrement` | 817 |
| `eCohesion` | 818 |
| `eFrictionAngle` | 819 |
| `eDilationAngle` | 820 |
| `eFluidPressureIncrement` | 821 |
| `eMatrixTensileStrength` | 822 |
| `eJointCohesion` | 823 |
| `eJointFrictionAngle` | 824 |
| `eJointDilationAngle` | 825 |
| `eJointTensileStrength` | 826 |
| `eXJointNormalDirection` | 827 |
| `eYJointNormalDirection` | 828 |
| `eZJointNormalDirection` | 829 |
| `eJointNormalDirection` | 830 |
| `eDeviatoricPlasticStrainJointShear` | 831 |
| `eDeviatoricPlasticStrainJointTension` | 832 |
| `eDeviatoricPlasticStrainShear` | 833 |
| `eDeviatoricPlasticStrainTension` | 834 |
| `eGeneralizedHoekBrownParameter_Sigci` | 835 |
| `eGeneralizedHoekBrownParameter_m` | 836 |
| `eGeneralizedHoekBrownParameter_s` | 837 |
| `eGeneralizedHoekBrownParameter_a` | 838 |
| `eStateParam1` | 839 |
| `eStateParam2` | 840 |
| `eStateParam3` | 841 |
| `eStateParam4` | 842 |
| `eStateParam5` | 843 |
| `eStateParam6` | 844 |
| `eStateParam7` | 845 |
| `eStateParam8` | 846 |
| `eStateParam9` | 847 |
| `eStateParam10` | 848 |
| `eStateParam11` | 849 |
| `eStateParam12` | 850 |
| `eStateParam13` | 851 |
| `eStateParam14` | 852 |
| `eStateParam15` | 853 |
| `eStateParam16` | 854 |
| `eStateParam17` | 855 |
| `eStateParam18` | 856 |
| `eStateParam19` | 857 |
| `eStateParam20` | 858 |
| `eStateParam21` | 859 |
| `eStateParam22` | 860 |
| `eStateParam23` | 861 |
| `eStateParam24` | 862 |
| `eStateParam25` | 863 |
| `eStateParam26` | 864 |
| `eStateParam27` | 865 |
| `eStateParam28` | 866 |
| `eStateParam29` | 867 |
| `eStateParam30` | 868 |
| `eStateParam31` | 869 |
| `eStateParam32` | 870 |
| `eStateParam33` | 871 |
| `eStateParam34` | 872 |
| `eStateParam35` | 873 |
| `eStateParam36` | 874 |
| `eStateParam37` | 875 |
| `eStateParam38` | 876 |
| `eStateParam39` | 877 |
| `eStateParam40` | 878 |
| `eStateParam41` | 879 |
| `eStateParam42` | 880 |
| `eStateParam43` | 881 |
| `eStateParam44` | 882 |
| `eStateParam45` | 883 |
| `eStateParam46` | 884 |
| `eStateParam47` | 885 |
| `eStateParam48` | 886 |
| `eStateParam49` | 887 |
| `eStateParam50` | 888 |
| `eGradientOfTheYieldSurface` | 889 |
| `eGradientOfThePlasticPotential` | 890 |
| `eSizeOfYieldSurface` | 891 |
| `eImageM` | 892 |
| `eNorSandStateParam` | 893 |
| `ePotEvapotranspiration` | 894 |
| `eMeshThickness` | 895 |
| `eAirAbsolutePressure` | 896 |
| `eCommonNodeNum` | 897 |
| `eCommonGaussPointNum` | 898 |
| `eCommonElemNum` | 899 |
| `eCommonElemNodeNum` | 900 |
| `eOverconsolidationRatio` | 901 |
| `eApparentVolumetricHeatCapacity` | 902 |
| `eStressBoundaryStoredForcingX` | 903 |
| `eStressBoundaryStoredForcingY` | 904 |
| `eStressBoundaryStoredForcingZ` | 905 |
| `eStressBoundaryStoredMomentX` | 906 |
| `eStressBoundaryStoredMomentY` | 907 |
| `eStressBoundaryStoredMomentZ` | 908 |
| `ePrincipalTotalStresses` | 909 |
| `ePrincipalTotalStress1` | 910 |
| `ePrincipalTotalStress2` | 911 |
| `ePrincipalTotalStress3` | 912 |
| `ePrincipalEffectiveStresses` | 913 |
| `ePrincipalEffectiveStress1` | 914 |
| `ePrincipalEffectiveStress2` | 915 |
| `ePrincipalEffectiveStress3` | 916 |
| `ePrincipalStrains` | 917 |
| `ePrincipalStrain1` | 918 |
| `ePrincipalStrain2` | 919 |
| `ePrincipalStrain3` | 920 |
| `ePrincipalDirections` | 921 |
| `ePrincipalDirection11` | 922 |
| `ePrincipalDirection12` | 923 |
| `ePrincipalDirection13` | 924 |
| `ePrincipalDirection21` | 925 |
| `ePrincipalDirection22` | 926 |
| `ePrincipalDirection23` | 927 |
| `ePrincipalDirection31` | 928 |
| `ePrincipalDirection32` | 929 |
| `ePrincipalDirection33` | 930 |
| `eVolumetricStrainIncrement` | 931 |
| `eVolumetricStrainOnSolve` | 932 |
| `eVoidRatioIncrementOnSolve` | 933 |
| `eIsUndrainedResponse` | 934 |
| `eActivationState` | 935 |
| `eStressDeviatoricPlasticStrain` | 936 |
| `eWaterPressureAtGroundSurface` | 937 |
| `eXRotationIncrement` | 938 |
| `eYRotationIncrement` | 939 |
| `eZRotationIncrement` | 940 |
| `eRotationIncrement` | 941 |
| `eXRotation` | 942 |
| `eYRotation` | 943 |
| `eZRotation` | 944 |
| `eRotations` | 945 |
| `eXMomentIncrement` | 946 |
| `eYMomentIncrement` | 947 |
| `eZMomentIncrement` | 948 |
| `eMomentIncrement` | 949 |
| `eXMoment` | 950 |
| `eYMoment` | 951 |
| `eZMoment` | 952 |
| `eMoments` | 953 |
| `e1AxialStrain` | 954 |
| `e1AxialForce` | 955 |
| `e2AxialStrain` | 956 |
| `e2AxialForce` | 957 |
| `eTorsionalStrain` | 958 |
| `e11BendingStrain` | 959 |
| `e11BendingMoment` | 960 |
| `e22BendingStrain` | 961 |
| `e22BendingMoment` | 962 |
| `e12ShearStrain` | 963 |
| `e12ShearForce` | 964 |
| `e13ShearStrain` | 965 |
| `e13ShearForce` | 966 |
| `e23ShearStrain` | 967 |
| `e23ShearForce` | 968 |
| `e3BendingStrain` | 969 |
| `e3BendingMoment` | 970 |
| `e2BendingStrain` | 971 |
| `e2BendingMoment` | 972 |
| `e3AxialStrain` | 973 |
| `e3AxialForce` | 974 |
| `e1AxialForceBeam` | 975 |
| `e3AxialForceBeam` | 976 |
| `e12ShearForceBeam` | 977 |
| `e3BendingMomentBeam` | 978 |
| `e2BendingMomentBeam` | 979 |
| `e1AxialStrainBeam` | 980 |
| `e3AxialStrainBeam` | 981 |
| `e12ShearStrainBeam` | 982 |
| `e3BendingStrainBeam` | 983 |
| `e2BendingStrainBeam` | 984 |
| `e1AxialStrainMembrane` | 985 |
| `e3AxialStrainMembrane` | 986 |
| `e1AxialForceMembrane` | 987 |
| `e3AxialForceMembrane` | 988 |
| `eDirectionalBaseShearMobForce` | 989 |
| `eDirectionalSeismicForceX` | 990 |
| `eDirectionalPressLineForce` | 991 |
| `eDirectionalPointForceX` | 992 |
| `eDirectionalReinfForceX` | 993 |
| `eDirectionalReinfForceZ` | 994 |
| `eDirectionalSurchargeForceX` | 995 |
| `eDirectionalReinfShearForceX` | 996 |
| `eDirectionalReinfShearForceZ` | 997 |
| `eDirectionalLeftIntersliceShearForce` | 998 |
| `eDirectionalRightIntersliceShearForce` | 999 |
| `eLeftIntersliceID` | 1000 |
| `eRightIntersliceID` | 1001 |
| `eSlipSafetyMapGridNum` | 1002 |
| `eGridRowId` | 1003 |
| `eGridColumnId` | 1004 |

## 8. Relação prática entre métodos e atributos

- `Get`, `Set`, `Add` e `Delete` trabalham com pares `analysis` + `object`, com `data` presente em `Set` e `Add`.
- `SolveAnalyses` recebe uma lista de análises (`analyses`) e pode opcionalmente receber `step` e `solve_dependencies`.
- `QueryTableParamsInfo` recebe `analysis` e um `table` do enum `gsi.pb.Result.Type`, e retorna `params_info`, uma lista de `ParamInfo`.
- `ParamInfo` descreve cada parâmetro disponível na tabela: tipo de dado (`dataparam`), chave (`key`), rótulo de exibição (`display`), categoria de unidade (`unit_category`), componentes vetoriais (`vector_components`) e string textual de unidades (`units`).
- `QueryResults` permite consultar valores para uma análise filtrando por `step`, `run`, `instance`, `table`, lista de `dataparams` e lista de `result_ids`.
- `QueryResultsResponse.results` é um mapa: a chave é um `result_id` inteiro e o valor é um `ParamResults`, que contém uma lista de `double` em `values`.
- `QueryResultsAvailability` verifica se uma análise possui resultados carregáveis/consultáveis.
- `LoadResults` aceita somente `analysis` e retorna uma resposta vazia, sugerindo um gatilho de carregamento/preparação de resultados.

## 9. Observações importantes

- Os arquivos enviados são artefatos gerados automaticamente pelo compilador protobuf. Portanto, esta documentação reflete **a interface contratual** da API, não a lógica interna do servidor.
- Alguns métodos não possuem comentário descritivo no `.proto` original; nesses casos, o nome do método e a estrutura dos campos foram usados para inferir o propósito.
- Campos marcados como `proto3 optional` têm presença explícita no contrato protobuf, o que é relevante para clientes que precisam distinguir “não enviado” de “valor padrão”.
- O campo `data` em `GetResponse`, `SetRequest` e `AddRequest` usa `google.protobuf.Value`, permitindo payload genérico/dinâmico.
