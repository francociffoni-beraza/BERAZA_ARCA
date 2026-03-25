# Reglas de Oro — Manual de operación de Claude para este repo

> Lectura obligatoria al inicio de **toda sesión**, antes de los context files.
> Aquí vive lo que Claude necesita saber para operar bien en este proyecto.
> Complementa CLAUDE.md (protocolo) y docs/metodos-wscpe-a-explotar.md (roadmap).
> Última actualización: 2026-03-25

---

## 1. Quién es quién

**Franco Ciffoni** — analista funcional, arquitecto del sistema y desarrollador. Actúa los tres roles a la vez. Es la única fuente de verdad sobre reglas de negocio y decisiones de integración con ARCA. Cuando hay ambigüedad funcional, preguntarle a él. No asumir.

**Claude** — ejecuta lo técnico, implementa, documenta. No define reglas de integración. Puede proponer, pero Franco decide.

**Regla:** si una decisión de integración (qué método llamar, qué campo es canónico, qué flujo de CPE aplicar) no está en los docs del repo ni en los manuales oficiales de ARCA, no existe. Preguntar antes de inventar.

---

## 2. Cómo opero en este repo

### 2.1 Antes de tocar cualquier cosa

1. Leer el contexto de sesión (`context_t.md`, `work-log.md`) — no operar sobre un hito cerrado.
2. Si el hito está `closed`: crear un checkpoint nuevo antes de iterar.
3. Si no tengo claro cuál es el hito activo: preguntar a Franco.

### 2.2 Cambio mínimo por iteración

- Una hipótesis por iteración. Cambiar X, correr, medir. No cambiar X+Y+Z juntos.
- Si después de 3 intentos no avanzo, parar y replantear con Franco. No brute-force.
- Prefiero una corrida que confirme algo malo (y sé qué arreglar) que N cambios simultáneos que dejan estado indeterminado.

### 2.3 Lo que NO hago sin confirmación de Franco

| Acción | Por qué |
|--------|---------|
| Modificar el flujo WSAA (TRA, signer, token_provider) | Es el corazón de la autenticación; un error rompe todos los servicios |
| Cambiar el contrato de compatibilidad de scripts (`docs/wscpe-compatibilidad-parcial.md`) | Tiene firma acordada con dependencias externas |
| Modificar `output/baseline/` | Es el baseline de referencia congelado; si cambia, pierde valor |
| Commitear sin `CHANGELOG_FIXES.md` + `work-log.md` actualizados | Regla de governance obligatoria |
| Force push a `main` | Nunca |
| Agregar un nuevo servicio ARCA (wsfe, wscdc) sin un plan aprobado | El diseño de extensión tiene que estar discutido con Franco primero |

### 2.4 Ante cualquier ambigüedad funcional

Preguntar antes de implementar. El costo de preguntar es 0. El costo de implementar la lógica equivocada es rehacer todo el ciclo de verificación contra ARCA.

---

## 3. El stack

### 3.1 Flujo de autenticación ARCA (WSAA)

```
Certificado X.509 (certs/ local)
  → TRA (Ticket Request & Access — XML firmado con plazo de vigencia)
  → CMS/PKCS7 signing (cryptography — firma el TRA con la clave privada del cert)
  → loginCms (SOAP call a WSAA de AFIP)
  → TA (Token de Acceso: token + sign, válido 12h)
  → TA Cache local (.arca-ta-cache/ — por env/servicio/CUIT)
```

**Fuente canónica del flujo:** `src/arca/wsaa/` + `src/arca/cache/ta_cache.py`

### 3.2 Flujo de llamada a servicios (SOAP)

```
TA (token + sign vigente)
  → SOAP envelope (src/arca/soap/envelope.py)
  → HTTP transport con retries (src/arca/soap/transport.py)
  → Servicio ARCA (ej: WSCPE en homologación o producción)
  → XML response → parser → modelo Python
```

**Fuente canónica:** `src/arca/soap/` + `src/arca/services/wscpe.py`

### 3.3 Arquitectura de `src/arca/`

```
src/arca/
├── wsaa/          — autenticación: todo lo relacionado con TRA, CMS, loginCms
├── cache/         — TA cache: un archivo JSON por (env, servicio, CUIT)
├── models/        — modelos de datos: auth.py, common.py, wscpe.py
├── services/      — un archivo por servicio ARCA: wscpe.py, (wsfe.py, wscdc.py futuros)
└── soap/          — capa de transporte genérica: envelope, transport, faults, xml
```

**Regla de extensión:** para agregar un nuevo servicio (ej: wsfe), crear `src/arca/services/wsfe.py` reutilizando el core existente (`wsaa`, `cache`, `soap`). No duplicar lógica de autenticación ni transporte.

### 3.4 Ambientes y configuración

| Variable | Descripción |
|---|---|
| `ARCA_ENV` | `homologacion` o `produccion` |
| `ARCA_CUIT` | CUIT del emisor (ej: `20049687495`) |
| `ARCA_CERT_PATH` | Ruta al certificado X.509 (.crt) |
| `ARCA_KEY_PATH` | Ruta a la clave privada (.key) |
| `ARCA_TA_CACHE_DIR` | Directorio de cache TA (default: `.arca-ta-cache/`) |

Cargados desde `.env` (local, git-ignored). Ver `.env.example` para el template completo.

---

## 4. El loop de convergencia script → output → baseline

Para cualquier script operativo, el patrón estándar de validación es:

```
1. SCRIPT
   Correr script operativo (ej: prod_consultar_cpe_por_destino.py)

2. OUTPUT
   Genera JSON en output/runs/<YYYY>/<MM>/<DD>/
   Naming: <proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>

3. COMPARAR
   Si hay un output equivalente en output/baseline/:
   → Comparar estructura y valores clave
   → Si diverge: investigar antes de commitear o cerrar hito

4. RESULTADO
   - Mismo conteo + misma estructura → output compatible, se puede cerrar hito
   - Diferencia en conteo → revisar filtros del script o cambio en datos ARCA
   - Error de autenticación → verificar vigencia del TA, renovar si expiró
   - Error SOAP → revisar logs, validar con wscpe_dummy.py primero
```

### 4.1 Reglas del loop

- Una hipótesis por iteración. Cambiar solo una cosa, correr, medir.
- Nunca modificar `output/baseline/` para que coincida — si hay diferencia, el script está mal, no el baseline.
- Registrar cada corrida significativa en `output/runs/`.
- Si un script falla repetidamente: documentar en `docs/ops/bitacora_fallos.md` antes de continuar.

### 4.2 Cierre de hito

Cuando el script produce output equivalente al baseline o cumple su criterio de aceptación:
1. Actualizar `CLAUDE.md` sección 4a/4b con el nuevo estado.
2. Correr `context_checkpoint.py checkpoint` para cerrar el hito.
3. Commit con CHANGELOG + work-log.

---

## 5. Documentación obligatoria — resumen ejecutivo

Todo commit debe tener, en el mismo commit:

| Qué cambié | Qué documento toco |
|------------|--------------------|
| Cualquier cosa | `docs/ops/CHANGELOG_FIXES.md` |
| Contrato operativo o flujo | `README.md` |
| Incidente auth/soap/script | `docs/ops/bitacora_fallos.md` |
| Cierre de hito | `context_checkpoint.py checkpoint` → `docs/work-log.md` |

**Frase de control:** antes de hacer git add, preguntarme: ¿actualizé CHANGELOG? Si no → hacerlo ahora.

### 5.1 Planes aprobados — persistir siempre

Cada vez que Franco aprueba un plan de implementación, Claude guarda inmediatamente el plan en `docs/plans/YYYY-MM-DD_<slug>.md`.

El archivo incluye:
1. El plan completo tal como fue aprobado.
2. El hito activo según `work-log.md` al momento de la aprobación.
3. El contexto de por qué se tomó la decisión.

**Frase de control:** cuando Franco dice "aprobado" o acepta un plan → guardar en `docs/plans/` antes de arrancar a implementar.

---

## 6. Archivos que nunca toco sin permiso explícito

| Archivo/ruta | Restricción |
|---|---|
| `output/baseline/` | Read-only absoluto. Baseline de referencia congelado. |
| `src/arca/wsaa/` | No modificar flujo de autenticación sin convergencia documentada y aprobada. |
| `docs/chat-context/legacy_worklog.md` | Solo lo actualiza `legacy-init`. |
| `docs/wscpe-compatibilidad-parcial.md` | El contrato de compatibilidad es solo-lectura salvo decisión explícita de Franco. |

---

## 7. Dónde buscar qué

| Necesito saber... | Dónde leer |
|---|---|
| Estado del hito activo | `docs/chat-context/context_t.md` |
| Qué pasó en sesiones anteriores | `docs/chat-context/context_t-1.md` + `docs/work-log.md` |
| Hitos activos y subhitos | `to_do/step-by-step-actual.md` |
| Procedimientos manuales portal ARCA | `to_do/arca/` |
| Roadmap de métodos WSCPE | `docs/metodos-wscpe-a-explotar.md` |
| Contrato de compatibilidad scripts | `docs/wscpe-compatibilidad-parcial.md` |
| Manuales oficiales ARCA (WSAA, WSCPE, etc.) | `docs/manuales/servicios-cuit/` |
| Arquitectura del core ARCA | `AGENTS_LIBRARY.md` |
| Convenciones de scripts y outputs | `AGENTS_SCRIPTS.md` |
| Procedimientos de certificados y auth ARCA | `AGENTS_ARCA_WEB.md` |
| Outputs de referencia congelados | `output/baseline/` |
