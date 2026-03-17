# Step by step - Carta de Porte (ARCA directo / wscpe)

> Nota 2026-03-16: este documento conserva el formato historico del paso a paso original y usa como base operativa el flujo vigente de `docs/step-by-step-cpe-dev.md`.
> La ejecucion actual se sigue por hitos y trazabilidad en `docs/work-log.md`, con checklist de alta/validacion en `docs/arca-reonboarding-checklist.md`.

Fecha base: 2026-03-13
WS: `wscpe`
CUIT objetivo: `AFIP_CUIT` de `.env`
Ambiente objetivo: `dev` (homologacion)

## Estado global
- [ ] 1. Preparar entorno local (`.env` + certificado + key).
- [ ] 2. Validar altas y relaciones manuales en ARCA homologacion.
- [ ] 3. Ejecutar smoke tecnico (`dummy` + `consultarUltNroOrden`).
- [ ] 4. Ejecutar extraccion de CPE emitidas.
- [ ] 5. Ejecutar extraccion de CPE recibidas.
- [ ] 6. Guardar salidas con naming estandar por corrida.
- [ ] 7. Resolver bloqueos tecnicos con troubleshooting controlado.
- [ ] 8. Cerrar corrida con evidencia minima y registro en bitacora.

## Seguimiento detallado

### 1) Preparacion local
Objetivo: dejar operativo el entorno DEV para WSAA + SOAP + `wscpe`.
Estado: OPERATIVO (plantilla vigente)
Terminado cuando:
- `.env` define: `AFIP_ENV=dev`, `AFIP_WSID=wscpe`, `AFIP_CUIT`, `AFIP_CUIT_REPRESENTADA`, `AFIP_CERT_PATH`, `AFIP_KEY_PATH`.
- `AFIP_CUIT` y `AFIP_CUIT_REPRESENTADA` estan alineados para homologacion.
- Certificado y key existen localmente y corresponden al mismo CUIT.
Evidencia:
- Corrida base documentada en `docs/work-log.md` (entrada 2026-03-13, generacion y validacion de credenciales DEV).

### 2) Alta y validaciones ARCA (manual)
Objetivo: asegurar precondiciones de ARCA antes de consultas de negocio.
Estado: OPERATIVO (gate obligatorio)
Terminado cuando:
- El certificado de homologacion esta emitido y asociado al computador fiscal correcto.
- La relacion `ws://wscpe` esta dada de alta en Administrador de Relaciones para el CUIT representado.
- No quedan errores de autenticacion por relacion/certificado en la validacion inicial.
Evidencia:
- Registrar cualquier bloqueo o desbloqueo en `docs/work-log.md` antes de pasar al paso 3.

### 3) Smoke tecnico minimo
Objetivo: validar conectividad tecnica y sanidad del servicio.
Estado: OPERATIVO
Terminado cuando:
- `dummy` responde `appserver/authserver/dbserver=Ok`.
- `consultarUltNroOrden` responde `HTTP 200` sin `soap:Fault`.
Comandos:
```powershell
py -3 scripts/wscpe_dummy.py --env-file .env --fallback-env-file .env
py -3 scripts/wscpe_consultar_ult_nro_orden.py --env-file .env --fallback-env-file .env --tipo 74 --sucursal 2 --force-create-ta
```
Evidencia:
- Baseline de referencia: `output/runs/2026/03/13/run_20260313_093044/wscpe_dummy_20260313_093044_cpe.json`.
- Baseline de referencia: `output/runs/2026/03/13/run_20260313_093044/wscpe_consultarUltNroOrden_20260313_093044_cpe.json`.

### 4) Emitidas (consulta del emisor)
Objetivo: extraer CPE emitidas por barrido y por identificador puntual.
Estado: OPERATIVO
Terminado cuando:
- Se ejecuta barrido de ultimos dias con salida persistida en `output/runs/...`.
- Si aplica, se consulta detalle por CTG para casos puntuales.
Comandos:
```powershell
py -3 scripts/prod_consultar_cpe_ultimos_dias.py --env-file .env --fallback-env-file .env --days 3 --tipo 74 --sucursal 2 --scan-limit 500 --stop-after-older-streak 50 --force-create-ta
py -3 scripts/prod_consultar_cpe_por_ctg.py --env-file .env --fallback-env-file .env --ctgs <ctg1,ctg2,...>
```
Evidencia:
- Baseline de referencia: `output/runs/2026/03/13/run_20260313_093112/prod_consultarCPEAutomotor_ultimos3dias_20260313_093112_cpe.json`.
- Baseline de referencia: `output/runs/2026/03/13/run_20260313_093056/prod_consultarCPEAutomotor_porCTG_20260313_093056_cpe.json`.

### 5) Recibidas (consulta por destino)
Objetivo: extraer CPE recibidas por plantas de destino y consolidar catalogo.
Estado: OPERATIVO
Terminado cuando:
- Se ejecuta `consultarCPEPorDestino` con ventanas maximas de 3 dias por request.
- Se actualiza bitacora/catalogo de CTG recibidas.
Comandos:
```powershell
py -3 scripts/prod_consultar_cpe_por_destino.py --env-file .env --fallback-env-file .env --plants 20217,20218,20219,519447,700011 --from-date 2026-03-10 --to-date 2026-03-12 --force-create-ta
py -3 scripts/prod_actualizar_bitacora_ctg_recibidas.py --env-file .env --fallback-env-file .env --from-date 2026-03-10 --to-date 2026-03-12 --plants 20217,20218,20219,519447,700011 --force-create-ta
```
Evidencia:
- Baseline de referencia: `output/runs/2026/03/13/run_20260313_093056/prod_consultarCPEPorDestino_20260313_093056_cpe.json`.
- Baseline de referencia: `output/runs/2026/03/13/run_20260313_093107/prod_bitacora_ctg_recibidas_run_20260313_093107_cpe.json`.

### 6) Naming estandar de salidas
Objetivo: asegurar trazabilidad y consistencia de archivos por corrida.
Estado: OPERATIVO
Terminado cuando:
- Las salidas cumplen la regla `<proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>`.
- Cada corrida guarda archivos en `output/runs/YYYY/MM/DD/run_YYYYMMDD_HHMMSS/`.
- Los JSON incluyen metadata comun (`run_id`, `ws_suffix`, `output_file_pattern`, `transport`).
Evidencia:
- Estandarizacion documentada en `docs/work-log.md` (entrada 2026-03-13).

### 7) Troubleshooting controlado
Objetivo: resolver fallas recurrentes sin romper el flujo operativo.
Estado: OPERATIVO
Terminado cuando:
- Ante `soap:Client` por autenticacion: se valida relacion ARCA y `AFIP_CUIT_REPRESENTADA`.
- Ante `cms.cert.untrusted`: se valida par `CRT/KEY`, ambiente y certificado homologacion.
- Ante TA vencido/cache: se reintenta con `--force-create-ta` y se valida cache local.
- Ante `codigo 800` sin datos: se revisan planta, tipo y rango (maximo 3 dias en destino).
Evidencia:
- Cada incidente se registra en `docs/work-log.md` con comando, salida y accion correctiva.

### 8) Cierre de corrida y evidencia minima
Objetivo: cerrar cada corrida con evidencia auditable.
Estado: OPERATIVO
Terminado cuando:
- Se guarda salida de `dummy`.
- Se guarda salida de `consultarUltNroOrden`.
- Se guarda al menos una salida de emitidas y una de recibidas.
- Se actualiza `docs/work-log.md` con fecha, cambios, evidencia y siguiente accion.
Evidencia:
- Plantilla y ejemplos de registro disponibles en `docs/work-log.md`.

## Nota de transicion
- `docs/step-by-step-cpe-dev.md` queda como version expandida para uso diario.
- Este archivo (`docs/step-by-step.md`) queda como version resumida en formato historico para seguimiento rapido por pasos.
- Paso a paso ONLY ARCA (solo web/manual): `docs/step-by-step-only-arca-web.md`.
- Paso a paso manual ARCA por servicio (base `wscpe` + fase 2): `docs/step-by-step-arca-servicios-cuit.md`.
- Manuales oficiales para base `wscpe` y fase 2 (`wsfe`, `wscdc`, padron, `wsfecred`, `wslpg`) disponibles en `docs/manuales/servicios-cuit/`.
