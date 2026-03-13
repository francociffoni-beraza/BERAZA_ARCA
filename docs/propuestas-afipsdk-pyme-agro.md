# Propuestas AFIP SDK para PyME Agro (ademas de Carta de Porte)

Fecha: 2026-03-06  
Objetivo: priorizar integraciones simples, utiles y aplicables a cualquier CUIT PyME.

## Criterio de seleccion
- Alto impacto operativo o administrativo.
- Baja complejidad de implementacion inicial.
- Metodos estables y comunes en empresas con trabajo diario en ARCA.

## 1) Factura electronica (WSFE) - prioridad alta
Servicio: `wsfe`

Metodos recomendados:
- `FECompUltimoAutorizado`
- `FECompConsultar`
- `FECAESolicitar`
- `FEParamGetPtosVenta`
- `FEParamGetTiposCbte`
- `FEParamGetTiposIva`
- `FEParamGetTiposMonedas`

Uso practico:
- Emitir comprobantes.
- Reconciliar numeracion/autorizaciones.
- Consultar estado de comprobantes ya emitidos (CAE, fechas, estado).

## 2) Factura de credito electronica MiPyME (WSFECRED) - prioridad media
Servicio: `wsfecred`

Metodos recomendados:
- `consultarComprobantes`
- `consultarCtaCte`
- `consultarCtasCtes`
- `aceptarFECred`
- `rechazarFECred`
- `informarCancelacionTotalFECred`

Uso practico:
- Seguir cuentas corrientes de FCE.
- Aceptar/rechazar comprobantes desde sistemas propios.
- Evitar gestion manual en ARCA para creditos y cancelaciones.

## 3) Constatacion de comprobantes (WSCDC) - prioridad alta
Servicio: `wscdc`

Metodos recomendados:
- `ComprobanteConstatar`
- `ComprobantesTipoConsultar`
- `DocumentosTipoConsultar`
- `ComprobanteDummy`

Uso practico:
- Validar facturas de terceros antes de pagar.
- Disminuir riesgo administrativo y fiscal en compras.

## 4) Padron / constancia para alta y validacion de terceros - prioridad alta
Servicios:
- `ws_sr_constancia_inscripcion`
- `ws_sr_padron_a13` (si se requiere mayor profundidad)

Metodos recomendados:
- `getPersona_v2`
- `getPersonaList_v2`
- `getIdPersonaListByDocumento`

Uso practico:
- Enriquecer legajo de clientes/proveedores.
- Validar CUIT y situacion registral al alta.

## 5) Descargar comprobantes desde ARCA (automatizacion) - prioridad alta
Automatizacion AFIP SDK:
- `mis-comprobantes`

Uso practico:
- Bajar lotes de comprobantes para conciliacion interna.
- Cubrir necesidad operativa de "bajarse facturas" sin desarrollo complejo inicial.

## 6) Agro opcional: Liquidacion Primaria de Granos (WSLPG)
Servicio: `wslpg`

Metodos sugeridos (si aplica al negocio):
- `liquidacionUltimoNroOrdenConsultar`
- `liquidacionXNroOrdenConsultar`
- `liquidacionXCoeConsultar`
- `tipoGranoConsultar`

Uso practico:
- Consultar liquidaciones y sus datos clave desde API en lugar de gestion manual.

## Roadmap minimo recomendado (sin volverse loco)
1. `wsfe`: consulta + conciliacion (`FECompUltimoAutorizado` y `FECompConsultar`).
2. `mis-comprobantes`: descarga periodica de comprobantes.
3. `wscdc`: validacion de facturas de terceros previo a pagos.
4. `ws_sr_constancia_inscripcion`: validacion automatica en alta de proveedores/clientes.
5. `wsfecred` solo si ya hay volumen real de FCE MiPyME.

## Fuentes oficiales consultadas
- https://afipsdk.com/docs/api-reference/web-services/wsfe/
- https://afipsdk.com/docs/api-reference/web-services/wsfe/FECAESolicitar/prod/api/
- https://afipsdk.com/docs/api-reference/web-services/wsfecred/
- https://afipsdk.com/docs/api-reference/web-services/wsfecred/consultarComprobantes/prod/api/
- https://afipsdk.com/docs/api-reference/web-services/wscdc/
- https://afipsdk.com/docs/api-reference/web-services/wscdc/ComprobanteConstatar/prod/api/
- https://afipsdk.com/docs/api-reference/web-services/ws_sr_constancia_inscripcion/
- https://afipsdk.com/docs/api-reference/web-services/ws_sr_padron_a13/
- https://afipsdk.com/docs/api-reference/automations/mis-comprobantes/api/
- https://afipsdk.com/docs/api-reference/web-services/wslpg/
