# CLAUDE.md — BERAZA_ARCA

> Leído automáticamente por Claude Code al iniciar sesión.
> Última actualización: 2026-03-25

---

## 1) Startup protocol (OBLIGATORIO)

Antes de cualquier trabajo:

1. `py -3 scripts/context_checkpoint.py session-preflight`
   - Si falla con "hito closed": correr primero `checkpoint` con el hito/estado actual.
2. **Leer `REGLAS_DE_ORO.md`** — manual de operación: cómo opero, el stack ARCA, y el loop de convergencia. Obligatorio en toda sesión.
3. Leer `docs/chat-context/bootstrap_prompt.md` — resumen generado por session-preflight, punto de entrada más eficiente.
4. Leer `docs/chat-context/context_t.md` — contexto activo completo.
5. Leer `docs/chat-context/context_t-1.md` — sesión anterior (para continuidad).
6. Validar último hito en `docs/work-log.md`.
7. Abrir el AGENTS file correspondiente al área de trabajo:
   - `AGENTS_LIBRARY.md` — si se trabaja en `src/arca/`
   - `AGENTS_SCRIPTS.md` — si se trabaja en `scripts/` u `output/`
   - `AGENTS_ARCA_WEB.md` — si se resuelve auth, certificados o alta de servicios en el portal ARCA

> Regla: si `context_t` está `closed` o no coincide con el último hito del work-log,
> generar `checkpoint` nuevo antes de iterar. No seguir sobre un hito cerrado.

---

## 2) Estructura del repo

```
BERAZA_ARCA/
├── CLAUDE.md                  — entry point de sesión (este archivo)
├── REGLAS_DE_ORO.md           — manual de operación
├── AGENTS_LIBRARY.md          — sub-agente: src/arca/ (core, protocolo, extensión)
├── AGENTS_SCRIPTS.md          — sub-agente: scripts/ y outputs
├── AGENTS_ARCA_WEB.md         — sub-agente: portal ARCA (certs, auth, servicios)
├── AGENTS.md                  — DEPRECATED (ver AGENTS_*.md)
├── src/arca/
│   ├── wsaa/                  — TRA, signer, token_provider, parser
│   ├── cache/                 — TA cache local por env/servicio/CUIT
│   ├── models/                — modelos Pydantic/dataclasses: auth, common, wscpe
│   ├── services/              — módulos por servicio ARCA: wscpe.py, (wsfe, wscdc futuros)
│   └── soap/                  — envelope, transport, faults, xml
├── scripts/
│   ├── _arca_runtime.py       — utilidades compartidas: load_service, output_naming
│   ├── context_checkpoint.py  — gestión de contexto de sesión
│   ├── wscpe_dummy.py         — smoke test
│   └── prod_*.py              — scripts operativos de producción
├── tests/unit/                — tests unitarios
├── docs/
│   ├── ops/
│   │   ├── CHANGELOG_FIXES.md — audit trail de cambios
│   │   └── bitacora_fallos.md — incidentes abiertos/cerrados
│   ├── work-log.md            — historial de hitos
│   ├── chat-context/          — contexto de sesión (local, salvo legacy_worklog.md)
│   ├── manuales/servicios-cuit/ — PDFs oficiales ARCA
│   └── metodos-wscpe-a-explotar.md — roadmap de métodos WSCPE
├── to_do/
│   ├── step-by-step-actual.md — hitos activos y subhitos
│   └── arca/                  — procedimientos manuales portal ARCA
├── output/
│   ├── baseline/              — outputs de referencia (READ-ONLY ABSOLUTO)
│   └── runs/                  — evidencias de corridas por fecha
└── certs/                     — certificados locales (NO versionados)
```

---

## 3) Governance (OBLIGATORIO por commit)

Todo cambio va documentado **en el mismo commit**:

| Tipo de cambio | Doc requerido |
|---|---|
| Cualquier cambio | `docs/ops/CHANGELOG_FIXES.md` |
| Cambio en flujo/contrato operativo | `README.md` |
| Incidente infra/auth/script | `docs/ops/bitacora_fallos.md` (abrir al detectar, cerrar con validación) |
| Cierre de hito | `py -3 scripts/context_checkpoint.py checkpoint ...` |
| **Plan aprobado por Franco** | **`docs/plans/YYYY-MM-DD_<slug>.md`** — guardar plan completo + hito activo + contexto de la decisión |

**Ningun hito se considera cerrado** sin referencia explícita en al menos uno de:
- `docs/chat-context/`
- `docs/ops/bitacora_fallos.md`
- `docs/ops/CHANGELOG_FIXES.md`
- `docs/work-log.md`

---

## 4a) Estado operativo actual (módulos productivos)

| Módulo | Estado |
|---|---|
| `wscpe` — dummy, consultarUltNroOrden, consultarCPEAutomotor, consultarCPEPorDestino | OPERATIVO |
| `wscpe` — escritura (autorizar, editar, confirmar, anular) | PENDIENTE |
| `wsfe`, `wscdc`, `padron` | PENDIENTE — diseñados para reutilizar el mismo core |

---

## 4b) Estado de desarrollo (hitos activos)

- **Hito 1 — Remover legacy provider:** 3/4 subhitos cerrados. Bloqueado por cert faltante para verificación final.
- **Hito 2 — Operaciones manuales ARCA web:** en progreso. Ver `to_do/arca/` y `to_do/step-by-step-actual.md`.
- **Hito 3 — Consolidar wscpe diario:** pendiente.

---

## 5) Referencias clave

| Propósito | Ruta |
|---|---|
| Context activo sesión | `docs/chat-context/context_t.md` |
| Work-log operativo | `docs/work-log.md` |
| Hitos activos | `to_do/step-by-step-actual.md` |
| Procedimientos manuales ARCA | `to_do/arca/` |
| Roadmap métodos WSCPE | `docs/metodos-wscpe-a-explotar.md` |
| Contrato compatibilidad scripts | `docs/wscpe-compatibilidad-parcial.md` |
| Outputs baseline (referencia) | `output/baseline/` |
| Manuales oficiales ARCA | `docs/manuales/servicios-cuit/` |
| **Reglas de oro Claude** | `REGLAS_DE_ORO.md` |
| Sub-agente core library | `AGENTS_LIBRARY.md` |
| Sub-agente scripts | `AGENTS_SCRIPTS.md` |
| Sub-agente portal ARCA | `AGENTS_ARCA_WEB.md` |

---

## 6) Guardrails — restricciones duras

| Recurso | Regla |
|---|---|
| `output/baseline/` | **Read-only absoluto.** Son los outputs de referencia congelados. Nunca modificar, mover ni sobrescribir. |
| `src/arca/wsaa/` | No modificar el flujo TRA → CMS/PKCS7 → loginCms → TA sin una convergencia documentada y aprobada por Franco. |
| `docs/chat-context/legacy_worklog.md` | Read-only operativo. Solo lo actualiza `legacy-init`. |
| Módulo `wscpe` — métodos operativos | No refactorizar sin criterio de aceptación explícito y baseline verificado. |

---

## 7) Seguridad

**Regla principal:** nunca commitear secretos (`.env`, keys, tokens, passwords, certificados PEM).

**Si detectás un secreto en un diff o archivo staged:**
1. Abortar el commit inmediatamente.
2. Remover el valor y reemplazar por placeholder (`<REDACTED>` o variable de entorno).
3. Si ya fue commiteado: notificar al usuario de inmediato — requiere rotación del secreto y rewrite de historia.

**Otros controles:**
- Certificados/keys en `certs/` local (git-ignored).
- Cache de TA en `.arca-ta-cache/` (git-ignored).
- En logs/outputs, nunca exponer `token/sign` ni material criptográfico.
- `context_checkpoint.py` sanitiza automáticamente patrones de credenciales en persistencia.

---

## 8) Branching strategy

- **Trabajo operativo y de biblioteca:** directo en `main` (commits pequeños y verificables).
- **Cambios de alto riesgo** (restructuración de `src/arca/`, cambios en el flujo WSAA): branch nombrada `<tipo>/<descripcion>`.
- Nunca force-push a `main`.

---

## 9) Fallback si context_checkpoint.py falla

Si el script no corre:

1. Verificar que `tiktoken` está instalado: `pip install tiktoken`.
2. Leer manualmente `docs/chat-context/context_t.md` y `docs/work-log.md` para reconstruir estado.
3. Antes de iterar, confirmar con Franco cuál es el hito activo y su estado.
4. Al cierre, documentar el estado en `docs/work-log.md` manualmente si el script sigue sin funcionar.
