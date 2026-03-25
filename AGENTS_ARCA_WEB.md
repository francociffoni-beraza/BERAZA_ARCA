# AGENTS_ARCA_WEB.md
Ultima revision: 2026-03-25
Depende de: CLAUDE.md, REGLAS_DE_ORO.md, to_do/arca/, docs/manuales/servicios-cuit/

## Funcion del sub-agente
Gestionar operaciones manuales en el portal web de ARCA: certificados, alta de relaciones por servicio, re-onboarding, y cualquier acción que requiera intervención humana en el sistema ARCA de AFIP.

## Contexto
- ARCA tiene dos ambientes con acceso web distinto: `homologacion` (dev) y `produccion`.
- Las operaciones de certificados y alta de servicios son manuales — Claude documenta los pasos, Franco ejecuta en el portal.
- CUIT operativo: Beraza (`20049687495`).

## Regla de oro de ejecucion
1. Siempre confirmar el ambiente (`dev`/`prod`) antes de describir cualquier acción manual.
2. Un error en producción (alta de servicio equivocado, certificado incorrecto) puede bloquear operaciones reales de Beraza.
3. Nunca asumir que un certificado está vigente — verificar primero.
4. Todo bloqueo de autenticación ARCA debe registrarse en `docs/ops/bitacora_fallos.md` al detectarse, no al resolverse.
5. Si una operación de portal falla o queda incompleta: registrar evidencia del estado en `docs/work-log.md`.

## Regla de documentacion obligatoria
Toda operacion manual completada debe tener evidencia en el mismo commit/registro:
1. Registrar en `docs/ops/CHANGELOG_FIXES.md`.
2. Si fue un incidente (cert expirado, relación inactiva, autorización denegada): registrar en `docs/ops/bitacora_fallos.md` con dominio `auth`.
3. Registrar checkpoint en `docs/work-log.md`.
4. Guardar evidencia mínima: fecha/hora, ambiente, servicio, resultado.

Ningun hito de portal ARCA se considera cerrado sin referencia a al menos una de estas rutas:
- `docs/chat-context/`
- `docs/ops/bitacora_fallos.md`
- `docs/ops/CHANGELOG_FIXES.md`
- `docs/work-log.md`

## Guia de operaciones del portal ARCA

Ver carpeta `to_do/arca/` para el paso a paso activo y actualizado:

| Archivo | Contiene |
|---|---|
| `to_do/arca/README.md` | Índice y orden de ejecución recomendado |
| `to_do/arca/01-only-web.md` | Operaciones puras de portal: contexto, ingreso, cert, relaciones |
| `to_do/arca/02-certificados.md` | Generación y renovación de certificados (CSR, WSASS) |
| `to_do/arca/03-servicios-cuit.md` | Alta de relaciones por servicio (Administrador de Relaciones) |
| `to_do/arca/04-reonboarding-checklist.md` | Checklist de validación de cierre por ambiente |

## Flujo completo de alta de servicio (resumen ejecutivo)

```
1. DEFINIR CONTEXTO
   - Ambiente: dev o prod
   - CUIT autenticador (quien entra y firma)
   - CUIT representada (sobre quien se emite/consulta)
   - Servicio a habilitar (nombre técnico: wscpe, wsfev1, etc.)

2. CERTIFICADO
   - Verificar vigencia del cert para ese ambiente
   - Si vencido o faltante: generar CSR → cargar en WSASS → emitir cert → descargar .crt
   - Guardar cert en certs/ local (git-ignored)

3. ALTA DE RELACION
   - Ir a Administrador de Relaciones en el portal ARCA
   - Seleccionar CUIT representada correcta
   - Nueva Relación → elegir servicio exacto → seleccionar computador fiscal correcto
   - Confirmar → verificar que queda activa

4. VERIFICACION
   - Correr wscpe_dummy.py (o el dummy del servicio correspondiente)
   - Si devuelve OK: servicio habilitado, auth completa
   - Si devuelve "falta de autorizacion": relación no activa o cert incorrecto → revisar paso 3

5. EVIDENCIA
   - Fecha/hora, ambiente, servicio, resultado
   - Registrar en docs/work-log.md
```

## Orden de prioridad de servicios

1. `wscpe` — Carta de Porte Electrónica (módulo base, actualmente en operación)
2. `wsfev1` — Facturación Electrónica
3. `wscdc` — Constancia de depósito de combustibles
4. `ws_sr_constancia_inscripcion` — Consulta de inscripción AFIP
5. `ws_sr_padron_a13` — Padrón de contribuyentes

## Incidentes recurrentes y respuesta estándar

1. **"Falta de autorización" al llamar un servicio:**
   - Síntoma: `loginCms` funciona pero la llamada SOAP devuelve error de autorización.
   - Causa probable: la relación del servicio no está activa para ese CUIT en ese ambiente.
   - Respuesta: ir al Administrador de Relaciones → verificar que la relación existe y está activa → si no: crear Nueva Relación → re-verificar con dummy.

2. **Certificado expirado o inválido:**
   - Síntoma: `loginCms` falla con error de certificado.
   - Verificar: `openssl x509 -in certs/<cert>.crt -noout -dates`
   - Respuesta: seguir `to_do/arca/02-certificados.md` para generar y cargar nuevo cert.

3. **Ambiente incorrecto:**
   - Síntoma: el dummy funciona en homologación pero no en producción (o viceversa).
   - Verificar: variable `ARCA_ENV` en `.env` y URLs de endpoints (`ARCA_WSAA_URL`, `ARCA_WSCPE_URL`).
   - Respuesta: corregir `.env` para el ambiente correspondiente y limpiar cache TA.

4. **Computador fiscal mal asociado:**
   - Síntoma: cert válido, relación activa, pero loginCms sigue fallando.
   - Causa: el cert del `certs/` local no es el mismo que está cargado en WSASS para ese computador fiscal.
   - Respuesta: verificar el DN del cert local contra el computador fiscal en WSASS → si no coincide, re-emitir cert.

5. **Cache TA desactualizado tras cambio de cert:**
   - Síntoma: error de auth después de renovar cert, aunque el nuevo cert es correcto.
   - Respuesta: borrar `.arca-ta-cache/<env>/<servicio>/` y volver a correr el dummy para forzar un nuevo loginCms.

## Arbol de decision ante bloqueos de auth

Bloqueo de autenticacion
├─ loginCms falla (WSAA)
│  1. Verificar vigencia del cert: `openssl x509 -in certs/<cert>.crt -noout -dates`
│  2. Verificar que ARCA_ENV, ARCA_WSAA_URL y ARCA_CUIT coinciden con el ambiente buscado.
│  3. Limpiar cache TA: borrar `.arca-ta-cache/<env>/<servicio>/`.
│  4. Si sigue fallando: el cert puede estar mal asociado en WSASS → seguir to_do/arca/02-certificados.md.
├─ loginCms OK, pero servicio devuelve "falta de autorización"
│  1. Verificar en Administrador de Relaciones que la relación está activa.
│  2. Si no existe: seguir to_do/arca/03-servicios-cuit.md.
│  3. Si existe pero inactiva: renovar relación.
│  4. Verificar que el CUIT representado en la relación coincide con ARCA_CUIT del .env.
└─ Auth OK en homologación, falla en producción
   1. Comparar .env.example con el .env activo para producción.
   2. Verificar que el cert en certs/ es el de producción (no el de homologación).
   3. Verificar Administrador de Relaciones en el portal de PRODUCCIÓN (son entornos separados).

## Criterio de cierre de operacion manual

Una operación de portal ARCA se considera completa cuando:
1. El smoke test (`wscpe_dummy.py` o equivalente) pasa sin error de auth ni de autorización.
2. El ambiente está documentado (dev o prod).
3. Hay evidencia registrada en `docs/work-log.md`.
4. Si había un incidente abierto en `docs/ops/bitacora_fallos.md`: cerrado con validación verificable.

## Referencias
- Procedimientos activos: `to_do/arca/`
- Manuales oficiales ARCA: `docs/manuales/servicios-cuit/` (WSAA, WSCPE, WSFE, etc.)
- Historial de procedimientos: `docs/step-by-step-arca-servicios-cuit.md`, `docs/pasos-certificados-arca.md`
