# AGENTS_LIBRARY.md
Ultima revision: 2026-03-25
Depende de: CLAUDE.md, REGLAS_DE_ORO.md, src/arca/, README.md

## Funcion del sub-agente
Gestionar el core de integración ARCA en `src/arca/`: arquitectura, protocolo WSAA/SOAP, modelos de datos, extensión a nuevos servicios, y criterios de calidad del código.

## Contexto
- Librería Python propia sin dependencia de SDKs de terceros.
- Protocolo: WSAA (autenticación) + SOAP/XML (servicios).
- CUIT operativo: Beraza (`20049687495`).
- Ambientes: `homologacion` y `produccion`.

## Regla de oro de ejecucion
1. Priorizar interoperabilidad real con servicios oficiales ARCA antes que elegancia técnica.
2. El core (`wsaa/`, `soap/`) es compartido — un cambio roto ahí rompe todos los servicios.
3. No mezclar riesgo protocolar (cambios en autenticación o transporte) con refactor cosmético.
4. Ante tradeoff, priorizar continuidad operativa de `wscpe` como primer módulo productivo.
5. Todo incidente de autenticación o transporte debe registrarse en `docs/ops/bitacora_fallos.md`.

## Regla de documentacion obligatoria
Todo cambio en `src/arca/` debe dejar evidencia en el mismo commit:
1. Registrar cambio en `docs/ops/CHANGELOG_FIXES.md`.
2. Registrar incidente (si aplica) en `docs/ops/bitacora_fallos.md` con dominio `library`.
3. Registrar checkpoint en `docs/work-log.md` via `scripts/context_checkpoint.py checkpoint`.
4. Actualizar `README.md` si cambia la interfaz pública de algún servicio o el flujo operativo.

Ningun hito de library se considera cerrado sin referencia a al menos una de estas rutas:
- `docs/chat-context/`
- `docs/ops/bitacora_fallos.md`
- `docs/ops/CHANGELOG_FIXES.md`
- `docs/work-log.md`

## Arquitectura de src/arca/

```
src/arca/
├── __init__.py
├── config.py            — Settings: carga .env, valida variables requeridas
├── errors.py            — Excepciones custom del dominio ARCA
├── wsaa/
│   ├── client.py        — WSAA SOAP client (loginCms call)
│   ├── parser.py        — Parsing de la respuesta TA
│   ├── signer.py        — CMS/PKCS7 signing con cryptography
│   ├── token_provider.py — Orquestador: cache → renovar si expirado → loginCms
│   └── tra.py           — Generación del TRA (XML con metadata de servicio y plazo)
├── cache/
│   └── ta_cache.py      — Cache JSON local del TA por (env, servicio, CUIT)
├── models/
│   ├── auth.py          — TokenAcceso, credenciales
│   ├── common.py        — tipos comunes reutilizables
│   └── wscpe.py         — modelos WSCPE: CPERef, CPEDetalle, etc.
├── services/
│   └── wscpe.py         — servicio WSCPE: todos los métodos operativos
└── soap/
    ├── envelope.py      — builder de SOAP envelope genérico
    ├── faults.py        — parsing de SOAP faults
    ├── transport.py     — HTTP con retries y timeout configurables
    └── xml.py           — utilidades de parsing XML
```

## Responsabilidades por capa

| Capa | Responsabilidad | No hacer |
|---|---|---|
| `wsaa/` | Autenticación completa: TRA → CMS → loginCms → TA | No poner lógica de negocio ni de servicios aquí |
| `cache/` | Persistir TA localmente para evitar loginCms innecesarios | No exponer cache a código externo directamente |
| `soap/` | Transporte genérico SOAP/XML | No meter lógica de servicios específicos |
| `services/` | Un archivo por servicio ARCA; llama a wsaa + soap | No duplicar lógica de auth o transporte |
| `models/` | Modelos de datos tipados | No poner lógica de negocio en modelos |

## Cómo extender a un nuevo servicio ARCA

Patrón probado en `wscpe`. Para agregar `wsfe`, `wscdc`, etc.:

1. **Crear `src/arca/models/<servicio>.py`** — modelos de request/response del nuevo servicio.
2. **Crear `src/arca/services/<servicio>.py`** — clase de servicio que:
   - Recibe un `TokenAcceso` (del `token_provider`)
   - Construye los envelopes via `soap/envelope.py`
   - Llama via `soap/transport.py`
   - Parsea la respuesta via `soap/xml.py`
3. **Crear `scripts/<servicio>_dummy.py`** — smoke test del nuevo servicio.
4. **Crear tests** en `tests/unit/test_<servicio>.py`.
5. **No** tocar `wsaa/` ni `soap/` salvo que el nuevo servicio requiera una capacidad genuinamente nueva de protocolo.

## Estado de módulos

| Módulo | Estado | Notas |
|---|---|---|
| `wsaa/` + `cache/` | OPERATIVO | Autenticación completa y funcional en producción |
| `soap/` | OPERATIVO | Transporte genérico probado con WSCPE |
| `services/wscpe.py` | PARCIALMENTE OPERATIVO | 4 métodos de consulta operativos; escritura pendiente |
| `services/wsfe.py` | PENDIENTE | Módulo no creado aún |
| `services/wscdc.py` | PENDIENTE | Módulo no creado aún |

## Métodos WSCPE operativos

| Método | Estado | Script |
|---|---|---|
| `dummy()` | OPERATIVO | `scripts/wscpe_dummy.py` |
| `consultarUltNroOrden()` | OPERATIVO | `scripts/wscpe_consultar_ult_nro_orden.py` |
| `consultarCPEAutomotor()` | OPERATIVO | `scripts/prod_consultar_cpe_por_ctg.py` |
| `consultarCPEPorDestino()` | OPERATIVO | `scripts/prod_consultar_cpe_por_destino.py` |
| `confirmarArriboCPE()` | PENDIENTE | — |
| `autorizarCPE()` | PENDIENTE | — |
| `editarCPE()` | PENDIENTE | — |
| `anularCPE()` | PENDIENTE | — |

## Arbol de decision ante problemas del core

Problema en src/arca/
├─ Error de autenticación (loginCms falla / TA expirado)
│  1. Verificar vigencia del cert (`openssl x509 -in certs/<cert>.crt -noout -dates`).
│  2. Verificar que el CUIT tiene el servicio habilitado en el portal ARCA.
│  3. Limpiar cache TA: borrar `.arca-ta-cache/<env>/<servicio>/`.
│  4. Correr `scripts/wscpe_dummy.py` como smoke test de auth.
│  5. Si persiste: registrar en `docs/ops/bitacora_fallos.md` y consultar `AGENTS_ARCA_WEB.md`.
├─ Error SOAP (fault / timeout / conexión)
│  1. Verificar endpoint (homologación vs producción en `.env`).
│  2. Revisar `src/arca/soap/faults.py` — ¿está parseando el fault correctamente?
│  3. Intentar con `dummy()` primero para aislar si es auth o servicio.
│  4. Revisar `src/arca/soap/transport.py` — timeout y retries configurados.
├─ Error de parseo (respuesta inesperada del servicio)
│  1. Loguear la respuesta XML cruda.
│  2. Comparar con el manual oficial en `docs/manuales/servicios-cuit/`.
│  3. Ajustar parser en `src/arca/soap/xml.py` o `src/arca/services/wscpe.py`.
└─ Cambio de schema en la respuesta ARCA
   1. Verificar en el manual oficial si hay nueva versión del WSDL.
   2. Actualizar modelos en `src/arca/models/<servicio>.py`.
   3. Actualizar parser. Registrar casuística en `docs/ops/bitacora_fallos.md`.

## Modo de trabajo recomendado
1. Ejecutar `session-preflight` y validar que el hito activo sigue en `in_progress`.
2. Implementar el cambio mínimo para cerrar ese hito.
3. Validar con `wscpe_dummy.py` (smoke test de auth) antes de cualquier llamada real.
4. Registrar evidencia técnica y documental.
5. Pasar al siguiente hito.

## Definicion de terminado por hito
Un hito de library está terminado cuando:
1. El método/módulo implementado produce respuesta correcta contra el servicio real (homologación o producción).
2. Tiene evidencia verificable en `output/runs/` o `output/homologacion/`.
3. Tiene actualización en `docs/work-log.md`.
4. No rompe los métodos operativos existentes de `wscpe`.
