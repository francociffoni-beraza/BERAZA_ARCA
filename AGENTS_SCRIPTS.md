# AGENTS_SCRIPTS.md
Ultima revision: 2026-03-25
Depende de: CLAUDE.md, REGLAS_DE_ORO.md, scripts/, output/baseline/, docs/wscpe-compatibilidad-parcial.md

## Funcion del sub-agente
Gestionar los scripts operativos (`scripts/`), convenciones de output, contrato de compatibilidad y gestión de evidencias en `output/`.

## Contexto
- Scripts son CLI operativos que llaman a `src/arca/` y producen JSON en `output/`.
- Hay un contrato de compatibilidad con outputs del legacy provider: `docs/wscpe-compatibilidad-parcial.md`.
- El baseline congelado en `output/baseline/` es la referencia de paridad.

## Regla de oro de ejecucion
1. Preservar el contrato de compatibilidad de outputs (estructura JSON, flags) antes que cualquier mejora.
2. Nunca modificar `output/baseline/` — es read-only absoluto.
3. Todo script operativo debe producir output verificable y trazable.
4. No introducir dependencias nuevas en scripts sin aprobación explícita de Franco.
5. Todo incidente de script (error inesperado, output incorrecto) debe registrarse en `docs/ops/bitacora_fallos.md`.

## Regla de documentacion obligatoria
Todo cambio en `scripts/` debe dejar evidencia en el mismo commit:
1. Registrar cambio en `docs/ops/CHANGELOG_FIXES.md`.
2. Registrar incidente (si aplica) en `docs/ops/bitacora_fallos.md` con dominio `scripts`.
3. Registrar checkpoint en `docs/work-log.md` via `scripts/context_checkpoint.py checkpoint`.
4. Actualizar `README.md` si cambia la interfaz de un script operativo o sus flags.
5. Actualizar `docs/wscpe-compatibilidad-parcial.md` si cambia el contrato de un script existente.

Ningun hito de scripts se considera cerrado sin referencia a al menos una de estas rutas:
- `docs/chat-context/`
- `docs/ops/bitacora_fallos.md`
- `docs/ops/CHANGELOG_FIXES.md`
- `docs/work-log.md`

## Scripts operativos actuales

| Script | Método ARCA | Propósito |
|---|---|---|
| `wscpe_dummy.py` | `dummy` | Smoke test: verifica auth + conectividad WSCPE |
| `wscpe_consultar_ult_nro_orden.py` | `consultarUltNroOrden` | Consulta el próximo número de orden CPE |
| `prod_consultar_cpe_por_ctg.py` | `consultarCPEAutomotor` | Consulta CPEs por número de CTG |
| `prod_consultar_cpe_por_destino.py` | `consultarCPEPorDestino` | Consulta CPEs por planta de destino y rango de fechas |
| `prod_consultar_cpe_ultimos_dias.py` | `consultarUltNroOrden` + `consultarCPEAutomotor` | Escanea CPEs de los últimos N días |
| `prod_actualizar_bitacora_ctg_recibidas.py` | `consultarCPEPorDestino` + `consultarCPEAutomotor` | Actualiza el catálogo de CTGs recibidas |
| `context_checkpoint.py` | — | Gestión de contexto de sesión (no operativo ARCA) |

## Convenciones de output

### Naming de archivos
Todo output generado por `_arca_runtime.build_output_naming()`:

```
<proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>
```

Ejemplos:
- `consultar_cpe_por_destino_20260325_143022_cpe.json`
- `dummy_20260325_143022_cpe.json`
- `bitacora_20260325_143022_cpe.json`

Sufijos por servicio (`_arca_runtime.WS_SUFFIX_BY_WSID`):
- `wscpe` → `cpe`
- `wsfe` → `facturas`

### Estructura de directorios de output

```
output/
├── baseline/                     — READ-ONLY. Baseline congelado (2026-03-05)
│   ├── baseline_dummy_20260305.json
│   ├── baseline_ult_nro_orden_20260305.json
│   ├── baseline_por_ctg_20260305.json
│   └── baseline_por_destino_20260305.json
├── homologacion/                 — Corridas en ambiente homologación
└── runs/
    └── YYYY/MM/DD/               — Corridas de producción por fecha
        └── <proceso>_<ts>_<ws>.json
```

## Contrato de compatibilidad (fase 1)

Baseline congelado: `output/baseline/` (2026-03-05).
Referencia completa: `docs/wscpe-compatibilidad-parcial.md`.

### Qué se permite en outputs nuevos
- Metadata técnica adicional (`transport`, `ta_source`, `ta_expiration`, timestamps de cache)
- Diferencias menores en texto de error (siempre legibles)
- Cambios de orden de campos JSON no disruptivos

### Qué NO se permite
- Eliminar campos clave existentes
- Cambiar semántica de filtros u flags operativos
- Reintroducir dependencia en access token externo (legacy provider)

### Campos obligatorios por script

| Script | Campos JSON obligatorios |
|---|---|
| `wscpe_dummy.py` | `generated_at`, `environment`, `method`, `http_status`, `ok`, `body` |
| `wscpe_consultar_ult_nro_orden.py` | `generated_at`, `environment`, `method`, `request_solicitud`, `http_status`, `ok`, `body` |
| `prod_consultar_cpe_por_ctg.py` | `generated_at`, `environment`, `ctgs_query`, `rows_count`, `rows` |
| `prod_consultar_cpe_por_destino.py` | `generated_at`, `environment`, `plants`, `fechaPartidaDesde`, `fechaPartidaHasta`, `results` |
| `prod_consultar_cpe_ultimos_dias.py` | `generated_at`, `environment`, `ult_nro_orden`, `attempts`, `matches` |
| `prod_actualizar_bitacora_ctg_recibidas.py` | `generated_at`, `environment`, `por_destino_requests`, `ctg_details`, `run_summary` |

## Rutina de validacion antes de cerrar hito de scripts

1. Correr `wscpe_dummy.py` — smoke test de auth. Si falla, no seguir.
2. Correr el script modificado con args de prueba.
3. Comparar output generado con el baseline correspondiente en `output/baseline/`.
4. Verificar que los campos obligatorios estén presentes.
5. Verificar que no se eliminaron campos del contrato.
6. Guardar evidencia en `output/runs/<YYYY>/<MM>/<DD>/`.

## Arbol de decision ante problemas de scripts

Problema en scripts/
├─ Script no corre (import error, dependencia faltante)
│  1. Verificar que `py -3 scripts/wscpe_dummy.py` corre (aisla auth de lógica de script).
│  2. Verificar requirements.txt e instalación.
│  3. Verificar que el script usa `_arca_runtime.load_wscpe_service()`.
├─ Script falla con error de autenticación
│  1. Ir a `AGENTS_LIBRARY.md` → árbol de auth.
│  2. Verificar cert y `.env` correctos para el ambiente.
├─ Script produce output diferente al baseline
│  1. Comparar campo por campo con el baseline de `output/baseline/`.
│  2. Verificar si la diferencia es en campos permitidos (metadata adicional) o no permitidos.
│  3. Si es un campo obligatorio que falta: buscar en `src/arca/services/wscpe.py` dónde se genera.
│  4. Si la diferencia es de datos (ARCA devuelve distinto): verificar si cambió el ambiente o los datos.
├─ Script nuevo a crear
│  1. Usar `_arca_runtime.load_wscpe_service()` para cargar el servicio.
│  2. Usar `_arca_runtime.build_output_naming()` para el nombre de archivo de salida.
│  3. Seguir el patrón de un script existente (ej: `prod_consultar_cpe_por_ctg.py`).
│  4. Definir los campos obligatorios del output ANTES de implementar.
└─ context_checkpoint.py falla
   1. Ver sección "Fallback" en `CLAUDE.md`.

## Utiles de _arca_runtime

```python
# Cargar el servicio WSCPE (WSAA + config)
from scripts._arca_runtime import load_wscpe_service
service, settings = load_wscpe_service()

# Generar nombre de output estandarizado
from scripts._arca_runtime import build_output_naming
naming = build_output_naming(
    process_name="consultar_cpe_por_destino",
    wsid="wscpe",
    extension="json",
)
# → output/runs/YYYY/MM/DD/consultar_cpe_por_destino_YYYYMMDD_HHMMSS_cpe.json
```

## Modo de trabajo recomendado
1. Smoke test primero: `py -3 scripts/wscpe_dummy.py`.
2. Implementar cambio mínimo en el script.
3. Correr script con args de prueba y verificar output.
4. Comparar con baseline si aplica.
5. Registrar evidencia en `output/runs/` y documentar en `docs/work-log.md`.

## Definicion de terminado por hito
Un hito de scripts está terminado cuando:
1. El script produce output correcto y completo.
2. El contrato de compatibilidad se respeta (campos obligatorios presentes, nada eliminado).
3. La evidencia de corrida está en `output/runs/`.
4. Tiene actualización en `docs/work-log.md`.
