# Metodos WSCPE a Explorar (Prod)

Fecha: 2026-03-06  
Contexto: CUIT productivo operativo para `wscpe` y flujo base ya validado en este repo.

## Metodos ya operativos en el proyecto
- `dummy`
- `consultarUltNroOrden`
- `consultarCPEPorDestino`
- `consultarCPEAutomotor`

## Metodos adicionales recomendados (ordenados por simplicidad e impacto)

### 1) Catalogos y maestros (baja complejidad, alto valor)
- `consultarPlantas`
- `consultarPlantasDG`
- `consultarTiposGrano`
- `consultarDerivadosGranarios`
- `consultarTiposEmbalaje`
- `consultarUnidadesMedida`
- `consultarProvincias`
- `consultarLocalidadesPorProvincia`
- `consultarLocalidadesProductor`
- `consultarDomiciliosPorCUIT`
- `consultarRenspa`

Para que sirve: limpiar validaciones, evitar errores de datos y mantener tablas maestras locales.

### 2) Pendientes y visibilidad operativa
- `consultarCPEPPendientesDeResolucion`
- `consultarCPEEmitidasDestinoDGPendientesActivacion`
- `consultarCPEDGPendienteActivacion`

Para que sirve: detectar casos que no aparecen bien en consultas generales y construir alertas operativas.

### 3) Flujo de recibidas (acciones de negocio)
- `confirmarArriboCPE`
- `rechazoCPE`
- `descargadoDestinoCPE`

Para que sirve: cerrar el ciclo de recepcion sin salir a ARCA manualmente.

### 4) Incidencias de traslado (acciones de negocio)
- `nuevoDestinoDestinatarioCPEAutomotor`
- `desvioCPEAutomotor`
- `regresoOrigenCPEAutomotor`
- `confirmacionDefinitivaCPEAutomotor`

Para que sirve: resolver excepciones reales de operacion (desvio, cambio de destino, regreso, cierre definitivo).

### 5) Emision y mantenimiento de CPE
- `autorizarCPEAutomotor`
- `editarCPEAutomotor`
- `editarCPEConfirmadaAutomotor`
- `anularCPE`

Para que sirve: cubrir ciclo completo de vida de la carta, no solo consulta.

### 6) Contingencia
- `informarContingencia`
- `cerrarContingenciaCPE`

Para que sirve: operar continuidad cuando hay problemas de disponibilidad o contingencias formales.

## Backlog corto sugerido (simple y realista)
1. Integrar catalogos (`consultarPlantas`, `consultarTiposGrano`, `consultarLocalidadesPorProvincia`) con cache local.
2. Integrar pendientes (`consultarCPEPPendientesDeResolucion`) para tablero de excepciones.
3. Integrar una accion de ciclo de recibidas (`confirmarArriboCPE`) con auditoria.
4. Integrar una accion de incidencias (`desvioCPEAutomotor`) con aprobacion interna previa.

## Fuentes oficiales consultadas
- https://afipsdk.com/docs/api-reference/web-services/wscpe/
- https://afipsdk.com/docs/api-reference/web-services/wscpe/consultarCPEAutomotor/prod/api/
- https://afipsdk.com/docs/api-reference/web-services/wscpe/consultarCPEPorDestino/dev/api/
- https://afipsdk.com/docs/api-reference/web-services/wscpe/consultarPlantas/dev/api/
