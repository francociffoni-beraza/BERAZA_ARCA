# Step by Step DEV - CPE Emitidas y Recibidas (ARCA Directo)

Fecha: 2026-03-13  
Scope: homologacion (`AFIP_ENV=dev`) para bajar CPE emitidas y recibidas del CUIT de `.env`.

## 0) Objetivo y aclaracion clave
- Objetivo: obtener y mantener actualizado el universo operativo de CPE emitidas y recibidas.
- Integracion actual: ARCA directo (`WSAA + SOAP + wscpe`) sin dependencia operativa de AfipSDK.
- Aclaracion: no necesitas un token de AfipSDK.  
  En ARCA directo se usa **TA de WSAA** (`token/sign`), generado localmente desde certificado + key.

## 1) Preparacion local (`.env` DEV)
1. Verificar variables minimas:
   - `AFIP_ENV=dev`
   - `AFIP_WSID=wscpe`
   - `AFIP_CUIT=<cuit_dev>`
   - `AFIP_CUIT_REPRESENTADA=<mismo_cuit_dev>`
   - `AFIP_CERT_PATH=<ruta_crt_homo>`
   - `AFIP_KEY_PATH=<ruta_key_homo>`
2. Opcional recomendado:
   - `ARCA_TIMEOUT_SECONDS=90`
   - `ARCA_VERIFY_TLS=true`
   - `ARCA_TA_CACHE_DIR=.arca-ta-cache`
3. Validar que CRT/KEY existan y correspondan al CUIT.

## 2) Alta y validaciones en ARCA (homologacion)
1. Certificado:
   - Si no existe, generar CSR local y emitir certificado en ARCA homologacion.
   - Asociar certificado al computador fiscal correspondiente.
2. Relacion de servicios:
   - En Administrador de Relaciones de ARCA, asociar `ws://wscpe` al CUIT representado.
   - Confirmar que el conjunto auth/representada incluya el CUIT de `.env`.
3. Gate manual:
   - Si falla autenticacion por relacion/certificado, no continuar con consultas de negocio.
   - Registrar evidencia en `docs/work-log.md`.

## 3) Smoke tecnico (obligatorio)
1. `dummy`:
```powershell
py -3 scripts/wscpe_dummy.py --env-file .env --fallback-env-file .env
```
2. `consultarUltNroOrden`:
```powershell
py -3 scripts/wscpe_consultar_ult_nro_orden.py --env-file .env --fallback-env-file .env --tipo 74 --sucursal 2 --force-create-ta
```
3. Criterio de pase:
   - `dummy` con `appserver/authserver/dbserver=Ok`.
   - `consultarUltNroOrden` sin `soap:Fault`.

## 4) Flujo emitidas (CPE del emisor)
1. Barrido base por orden descendente:
```powershell
py -3 scripts/prod_consultar_cpe_ultimos_dias.py --env-file .env --fallback-env-file .env --days 3 --tipo 74 --sucursal 2 --scan-limit 500 --stop-after-older-streak 50 --force-create-ta
```
2. Ajustar para backfill historico:
   - subir `scan-limit` y `stop-after-older-streak` gradualmente.
   - repetir corridas hasta cubrir el periodo objetivo.
3. Si necesitas detalle puntual por CTG:
```powershell
py -3 scripts/prod_consultar_cpe_por_ctg.py --env-file .env --fallback-env-file .env --ctgs <ctg1,ctg2,...>
```

## 5) Flujo recibidas (destino)
1. Consulta por plantas (ventanas maximas de 3 dias):
```powershell
py -3 scripts/prod_consultar_cpe_por_destino.py --env-file .env --fallback-env-file .env --plants 20217,20218,20219,519447,700011 --from-date 2026-03-10 --to-date 2026-03-12 --force-create-ta
```
2. Enriquecimiento y consolidacion de catalogo:
```powershell
py -3 scripts/prod_actualizar_bitacora_ctg_recibidas.py --env-file .env --fallback-env-file .env --from-date 2026-03-10 --to-date 2026-03-12 --plants 20217,20218,20219,519447,700011 --force-create-ta
```
3. Para traer "todas" las recibidas:
   - iterar por periodos hasta cubrir historia completa.
   - mantener corridas incrementales diarias (delta).

## 6) Convencion de nombres de datos (vigente)
Regla unica:
- `<proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>`

Mapeo inicial de sufijos:
- `wscpe -> cpe`
- reservado: `misComprobantes -> misComp`, `wsfe -> facturas`

Carpeta por corrida:
- `output/runs/YYYY/MM/DD/run_YYYYMMDD_HHMMSS/`

Metadata comun agregada en JSON:
- `run_id`
- `ws_suffix`
- `output_file_pattern`
- `transport`

## 7) Troubleshooting rapido
1. `soap:Client` por autenticacion/relacion:
   - revisar relacion ARCA de `ws://wscpe`.
   - confirmar `AFIP_CUIT_REPRESENTADA`.
2. `cms.cert.untrusted` o errores de certificado:
   - revisar CRT/KEY de homologacion y matching.
3. TA vencido/cache:
   - reintentar con `--force-create-ta`.
   - validar `.arca-ta-cache`.
4. `codigo 800` sin datos:
   - validar planta, rango y tipo.
   - ampliar ventana (respetando limite de 3 dias por request en destino).

## 8) Checklist de corrida completa OK
- [ ] Gate ARCA homologacion (certificado + relacion `wscpe`) validado.
- [ ] `dummy` OK.
- [ ] `consultarUltNroOrden` OK.
- [ ] Emitidas extraidas y guardadas con naming estandar.
- [ ] Recibidas extraidas y guardadas con naming estandar.
- [ ] Catalogo/bitacora actualizados.
- [ ] Evidencia en `output/` y registro en `docs/work-log.md`.

## 9) Evidencia minima a guardar
- Archivo de salida de `dummy`.
- Archivo de salida de `consultarUltNroOrden`.
- Al menos un archivo de emitidas y uno de recibidas con `run_id` y sufijo `_cpe`.
- Registro de la corrida en `docs/work-log.md`.
