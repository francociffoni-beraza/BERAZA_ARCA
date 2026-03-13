# Matriz de Compatibilidad Parcial - Migracion AfipSDK a ARCA Directo

Fecha: 2026-03-12  
Scope Fase 1: `wscpe` (`dummy`, `consultarUltNroOrden`, `consultarCPEAutomotor`, `consultarCPEPorDestino`)

## Baseline congelado
- `output/baseline/baseline_dummy_20260305.json`
- `output/baseline/baseline_ult_nro_orden_20260305.json`
- `output/baseline/baseline_por_ctg_20260305.json`
- `output/baseline/baseline_por_destino_20260305.json`

## Variables de configuracion operativa (nuevo contrato)
- `ARCA_WSAA_URL`
- `ARCA_WSCPE_URL`
- `ARCA_TIMEOUT_SECONDS`
- `ARCA_VERIFY_TLS`
- `ARCA_TA_CACHE_DIR`

Compatibilidad transitoria:
- Se mantienen `AFIP_ENV`, `AFIP_CUIT`, `AFIP_CUIT_REPRESENTADA`, `AFIP_CERT_PATH`, `AFIP_KEY_PATH`.
- `AFIPSDK_ACCESS_TOKEN` deja de ser requerido en runtime.

## Matriz script por script

| Script | Metodo ARCA | Flags que se conservan | Campos JSON obligatorios | Diferencias permitidas |
| --- | --- | --- | --- | --- |
| `scripts/wscpe_dummy.py` | `dummy` | `--env-file`, `--fallback-env-file`, `--output-file` | `generated_at`, `environment`, `method`, `http_status`, `ok`, `body` | agregar `transport`, `ta_source` |
| `scripts/wscpe_consultar_ult_nro_orden.py` | `consultarUltNroOrden` | `--env-file`, `--fallback-env-file`, `--tipo`, `--sucursal`, `--force-create-ta`, `--output-file` | `generated_at`, `environment`, `method`, `request_solicitud`, `http_status`, `ok`, `body` | agregar `transport`, `ta_source`, `ta_expiration` |
| `scripts/prod_consultar_cpe_por_ctg.py` | `consultarCPEAutomotor` (por `nroCTG`) | `--env-file`, `--fallback-env-file`, `--ctgs`, `--ctg-file`, `--cuit-solicitante`, `--force-create-ta`, `--output-file` | `generated_at`, `environment`, `ctgs_query`, `rows_count`, `rows` | agregar `transport`, sanitizado de `pdf` |
| `scripts/prod_consultar_cpe_por_destino.py` | `consultarCPEPorDestino` | `--env-file`, `--fallback-env-file`, `--plants`, `--tipo`, `--from-date`, `--to-date`, `--include-statuses`, `--force-create-ta`, `--output-file` | `generated_at`, `environment`, `plants`, `fechaPartidaDesde`, `fechaPartidaHasta`, `results` | agregar `transport`, `ta_source`, `ta_expiration` |
| `scripts/prod_consultar_cpe_ultimos_dias.py` | `consultarUltNroOrden` + `consultarCPEAutomotor` | `--env-file`, `--fallback-env-file`, `--tipo`, `--sucursal`, `--days`, `--scan-limit`, `--stop-after-older-streak`, `--force-create-ta`, `--output-file` | `generated_at`, `environment`, `ult_nro_orden`, `attempts`, `matches` | agregar `transport`, `ta_source` |
| `scripts/prod_actualizar_bitacora_ctg_recibidas.py` | `consultarCPEPorDestino` + `consultarCPEAutomotor` | flags actuales sin cambios | `generated_at`, `environment`, `por_destino_requests`, `ctg_details`, `run_summary` | agregar `transport`, `ta_source` |

## Definicion de paridad aceptable (fase 1)
- Se preserva estructura principal de salida JSON y flags principales de ejecucion.
- Se permite:
  - metadata tecnica adicional (`transport=arca_direct`, origen de TA, timestamps de cache),
  - diferencias menores de texto de error (siempre legibles),
  - cambios no disruptivos de orden de campos JSON.
- No se permite:
  - eliminar campos clave existentes,
  - cambiar semantica de filtros/flags operativos,
  - reintroducir dependencia operativa en `AFIPSDK_ACCESS_TOKEN`.
