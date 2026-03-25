# Plan: Guía step-by-step — Conectarse a ARCA y usar métodos WSCPE (CPE)

> Generado: 2026-03-25
> Hito activo: Hito 2 — Operaciones manuales ARCA web
> Contexto: Franco necesita una guía completa desde "tengo el repo" hasta "puedo llamar métodos en producción".

---

## Contexto de la decisión

El repo ya tiene el stack completo (WSAA + SOAP + WSCPE service), 4 métodos de consulta operativos, y scripts de producción listos. Esta guía consolida los procedimientos dispersos en `to_do/arca/` en un único flujo ordenado para conectarse a ARCA y empezar a usar los métodos CPE.

---

## FASE 0 — Prerequisitos (local)

1. **Instalar dependencias Python:**
   ```bash
   pip install -r requirements.txt
   pip install tiktoken
   ```

2. **Generar el par clave + CSR** (si no existe para el ambiente target):
   ```bash
   # Generar key privada
   openssl genrsa -out certs/<alias>.key 2048

   # Generar CSR con el DN correcto (CUIT del emisor)
   openssl req -new -key certs/<alias>.key \
     -subj "/C=AR/O=<Razon Social>/CN=<alias>/serialNumber=CUIT <CUIT>" \
     -out certs/<alias>.csr
   ```
   > La `key` nunca sale de `certs/` local (git-ignored). Solo el `.csr` se sube a ARCA.

3. **Verificar cert existente** (si ya tenés uno):
   ```bash
   openssl x509 -in certs/<cert>.crt -noout -dates
   # notBefore / notAfter → si expiró o falta, necesitás renovar
   ```

---

## FASE 1 — Portal ARCA: Certificado (manual, por ambiente)

> Repetir para `homologacion` y para `produccion` por separado.

1. Ingresar con **Clave Fiscal del CUIT administrador de relaciones**.
2. Ir a **WSASS** del ambiente correspondiente.
3. Cargar el **CSR generado localmente** (solo el `.csr`, nunca la `.key`).
4. Emitir el certificado → descargar el `.crt`.
5. Asociar el `.crt` al **Computador Fiscal** correcto (alias/DN debe coincidir).
6. Guardar el `.crt` descargado en `certs/` local.

> Si el cert ya existe y no está expirado: saltear esta fase.

---

## FASE 2 — Portal ARCA: Alta de servicio WSCPE (manual, por ambiente)

> Repetir para cada ambiente. `homologacion` primero, validar, luego `produccion`.

1. Ir a **Administrador de Relaciones** (en el portal del ambiente correcto).
2. Seleccionar la **CUIT representada** (la que va a operar: emitir/consultar CPEs).
3. Crear **Nueva Relación**:
   - **Servicio**: `ws://wscpe`
   - **Computador fiscal**: el asociado al `.crt` del paso anterior
4. Confirmar → verificar que queda en estado **Activa**.
5. Guardar evidencia: ambiente, servicio, CUITs, computador fiscal, fecha.

> Para agregar otros servicios después: mismo proceso con `wsfev1`, `wscdc`, etc.

---

## FASE 3 — Configuración local (`.env`)

Crear `.env` (dev) y/o `.env.prod` (prod) basándose en `.env.example`:

```env
# Ambiente
AFIP_ENV=dev              # o: prod
AFIP_WSID=wscpe

# CUITs
AFIP_CUIT=<CUIT autenticador>
AFIP_CUIT_REPRESENTADA=<CUIT que opera>

# Certificado (paths relativos al repo)
AFIP_CERT_PATH=certs/<cert>.crt
AFIP_KEY_PATH=certs/<cert>.key

# Opcional (defaults razonables)
ARCA_TIMEOUT_SECONDS=90
ARCA_VERIFY_TLS=true
ARCA_TA_CACHE_DIR=.arca-ta-cache
```

---

## FASE 4 — Verificación técnica (local)

```bash
# 1. Smoke test — verifica auth completo (TRA → loginCms → TA → dummy())
py -3 scripts/wscpe_dummy.py --env-file .env.prod

# 2. Si falla loginCms → problema de cert o de ambiente
#    Borrar cache TA y reintentar:
rm -rf .arca-ta-cache/prod/wscpe/
py -3 scripts/wscpe_dummy.py --env-file .env.prod --force-create-ta

# 3. Si loginCms OK pero devuelve "falta de autorización" →
#    La relación en ARCA no está activa. Volver a Fase 2.

# 4. Primera consulta real: siguiente número de orden
py -3 scripts/wscpe_consultar_ult_nro_orden.py \
   --env-file .env.prod --tipo 74 --sucursal 2 --force-create-ta
```

---

## FASE 5 — Métodos disponibles y cómo usarlos

### Operativos hoy (implementados en `src/arca/services/wscpe.py`)

| Método | Script | Descripción |
|--------|--------|-------------|
| `dummy()` | `wscpe_dummy.py` | Smoke test de conectividad |
| `consultarUltNroOrden()` | `wscpe_consultar_ult_nro_orden.py` | Último nro de orden (para emitir CPEs) |
| `consultarCPEAutomotor()` | `prod_consultar_cpe_por_ctg.py` | CPE por CTG o nro de orden |
| `consultarCPEPorDestino()` | `prod_consultar_cpe_por_destino.py` | CPEs recibidas por planta destino + rango de fechas |

**Comandos de uso diario:**
```bash
# CPEs emitidas últimos N días
py -3 scripts/prod_consultar_cpe_ultimos_dias.py \
   --env-file .env.prod --days 3 --tipo 74 --sucursal 2

# CPEs recibidas por planta destino
py -3 scripts/prod_consultar_cpe_por_destino.py \
   --env-file .env.prod --plants 20217,20218 --from-date 2026-03-22 --to-date 2026-03-25

# Bitácora de CTGs recibidas (actualización incremental)
py -3 scripts/prod_actualizar_bitacora_ctg_recibidas.py \
   --env-file .env.prod --days 3 --force-create-ta
```

### Próximos métodos recomendados (backlog priorizado)

**Fase A — Catálogos maestros (baja complejidad, alto valor):**
- `consultarPlantas`, `consultarTiposGrano`, `consultarLocalidadesPorProvincia`
- Útiles para validar datos antes de emitir y mantener tablas locales

**Fase B — Visibilidad operativa (pendientes):**
- `consultarCPEPendientesDeResolucion` — CPEs que necesitan acción
- `consultarCPEEmitidasDestinoDGPendientesActivacion`

**Fase C — Ciclo de recepción (acciones de negocio):**
- `confirmarArriboCPE`, `rechazoCPE`, `descargadoDestinoCPE`
- Cierra el ciclo de recepción sin entrar manualmente a ARCA

**Fase D — Incidencias y desvíos:**
- `desvioCPEAutomotor`, `nuevoDestinoDestinatarioCPEAutomotor`

**Fase E — Emisión completa:**
- `autorizarCPEAutomotor`, `editarCPEAutomotor`, `anularCPE`

---

## Árbol de decisión ante fallas

```
¿loginCms falla?
├─ Verificar vigencia cert: openssl x509 -in certs/<c>.crt -noout -dates
├─ Verificar AFIP_ENV, AFIP_WSAA_URL, AFIP_CUIT en .env
├─ Limpiar cache TA: rm -rf .arca-ta-cache/<env>/wscpe/
└─ Si sigue fallando: cert mal asociado en WSASS → Fase 1

¿loginCms OK pero "falta de autorización"?
├─ Ir a Administrador de Relaciones → verificar relación activa
├─ Si no existe o inactiva: Fase 2
└─ Verificar que CUIT representada en relación = AFIP_CUIT_REPRESENTADA del .env

¿Auth OK en homologación pero falla en producción?
├─ .env de prod apunta al cert de homologación? → corregir AFIP_CERT_PATH
└─ Verificar Administrador de Relaciones en el portal de PRODUCCIÓN (son entornos separados)
```

---

## Output esperado al completar esta guía

- Dummy test pasa en ambos ambientes
- `consultarUltNroOrden` devuelve un número válido
- Los 4 métodos de consulta funcionan con datos reales de producción
- Base lista para implementar los métodos del backlog (Fases A–E)

---

## Archivos críticos de referencia

| Propósito | Ruta |
|-----------|------|
| Checklist portal ARCA | `to_do/arca/01-only-web.md` |
| Generación de certs | `to_do/arca/02-certificados.md` |
| Alta de relaciones | `to_do/arca/03-servicios-cuit.md` |
| Árbol de decisión auth | `AGENTS_ARCA_WEB.md` |
| Implementación del servicio | `src/arca/services/wscpe.py` |
| Roadmap completo de métodos | `docs/metodos-wscpe-a-explotar.md` |
