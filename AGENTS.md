# AGENTS.md

> Leído automáticamente por Claude Code al iniciar sesión.
> Leído automáticamente por Codex al iniciar sesión.

Ultima revision: 2026-03-25
Depende de: README.md, CLAUDE.md, AGENTS_LIBRARY.md, AGENTS_SCRIPTS.md, AGENTS_ARCA_WEB.md

## Rol del agente raiz
Coordinar la ejecucion end-to-end de la integracion ARCA y delegar por especialidad, manteniendo foco en continuidad operativa, autenticacion estable y evidencia documental trazable.

## Contexto minimo del proyecto
1. Backend Python propio para integracion ARCA del CUIT de Beraza, sin dependencia de SDKs de terceros.
2. Protocolo: WSAA (autenticacion con TRA + CMS/PKCS7) + SOAP/XML (servicios).
3. Ambientes: `homologacion` y `produccion`. Certificados y cache TA son locales (git-ignored).
4. Modulo base operativo: `wscpe` (Carta de Porte Electronica). Proximos: `wsfe`, `wscdc`, padron.
5. Foco funcional vigente: cerrar paridad de `wscpe` + consolidar operacion diaria antes de expandir a nuevos servicios.

## Arquitectura end-to-end
`.env + certs/ → src/arca/wsaa/ (TRA → CMS → loginCms → TA) → src/arca/soap/ → src/arca/services/ → scripts/ → output/`

## Arbol de delegacion
Tipo de tarea
├─ Modificar o extender el core: wsaa/, soap/, models/, services/, config, errors
│  └─ `AGENTS_LIBRARY.md`
├─ Modificar o agregar scripts operativos, naming de outputs, contrato de compatibilidad
│  └─ `AGENTS_SCRIPTS.md`
├─ Certificados, alta de relaciones en portal ARCA, bloqueos de autorizacion, re-onboarding
│  └─ `AGENTS_ARCA_WEB.md`
└─ Criterios transversales, priorizacion y gobierno documental
   └─ `AGENTS.md` (raiz)

## Reglas de decision transversales
Ante dudas:
1. Priorizar continuidad operativa del modulo wscpe en produccion.
2. No mezclar riesgo protocolar (auth, transporte) con refactor cosmetico.
3. Preferir cambios pequenos y verificables — una hipotesis por iteracion.
4. No agregar dependencias nuevas sin evaluacion de costo operativo y aprobacion de Franco.
5. No inventar datos de ARCA — si falta contexto, registrar bloqueo y preguntar.

## Regla de oro de ejecucion
1. Primero sostener los metodos operativos de wscpe sin regresiones.
2. Luego cerrar la paridad operativa completa (escritura: autorizar, editar, confirmar).
3. Recien despues expandir a nuevos servicios (wsfe, wscdc, padron) reutilizando el core.
4. Todo fallo de `auth`, `scripts` o `library` debe quedar en `docs/ops/bitacora_fallos.md` con causa raiz, accion aplicada, validacion de cierre y accion preventiva.

## Guardrail de continuidad de sesion
Para toda sesion de trabajo:
1. Iniciar con `py -3 scripts/context_checkpoint.py session-preflight`.
2. Leer `docs/chat-context/context_t.md` y `docs/chat-context/context_t-1.md`.
3. Validar el ultimo hito en `docs/work-log.md`.
4. Abrir el AGENTS file del area de trabajo (Library / Scripts / ARCA Web).
5. Si `context_t` esta `closed` o no coincide con el ultimo hito del work-log, generar `checkpoint` nuevo antes de iterar.

## Regla de documentacion obligatoria
Todo cambio debe quedar documentado en el mismo commit:
1. `docs/ops/CHANGELOG_FIXES.md` — siempre, para cualquier cambio.
2. `docs/ops/bitacora_fallos.md` — para cada incidente `auth`, `scripts` o `library`.
3. `docs/work-log.md` via `scripts/context_checkpoint.py checkpoint` — al cerrar hito.
4. `README.md` — cuando cambia flujo operativo o interfaz de scripts.

Ningun hito se considera cerrado sin referencia explicita en al menos una de estas rutas:
- `docs/chat-context/`
- `docs/ops/bitacora_fallos.md`
- `docs/ops/CHANGELOG_FIXES.md`
- `docs/work-log.md`

## Documentacion de gobernanza (lectura obligatoria)
- `CLAUDE.md` — startup protocol, guardrails, governance
- `REGLAS_DE_ORO.md` — manual de operacion: stack ARCA, loop de convergencia
- `docs/metodos-wscpe-a-explotar.md` — roadmap de metodos WSCPE
- `docs/wscpe-compatibilidad-parcial.md` — contrato de compatibilidad de scripts

## Sub-agentes disponibles
- `AGENTS_LIBRARY.md`: core `src/arca/` — protocolo WSAA/SOAP, arquitectura, extension a nuevos servicios.
- `AGENTS_SCRIPTS.md`: scripts operativos, output naming, contrato de compatibilidad, validacion de baseline.
- `AGENTS_ARCA_WEB.md`: portal ARCA manual — certificados, alta de relaciones, bloqueos de auth.

## Convenciones del repo
- Core de integracion: `src/arca/`
- Modulos por servicio: `src/arca/services/`
- Scripts operativos: `scripts/`
- Evidencia de corridas: `output/runs/`
- Baseline de referencia (read-only): `output/baseline/`
- Documentacion operativa: `docs/`
- Procedimientos manuales activos: `to_do/arca/`
- Contexto de sesion: `docs/chat-context/`

## Seguridad y secretos
- Nunca commitear secretos (`.env`, certificados, keys, tokens).
- Certificados/keys en `certs/` local (git-ignored).
- Cache de TA en `.arca-ta-cache/` (git-ignored).
- En logs/salidas, nunca exponer `token/sign` ni material criptografico.

## Flujo Git correcto (PowerShell)
1. Validar estado antes de tocar nada: `git status --short --branch`.
2. Revisar que se sube: `git diff` o `git diff -- <archivo>`.
3. Agregar solo archivos puntuales: `git add <archivos>`.
4. Commit con mensaje claro:
   - Formato sugerido: `<tipo>: <descripcion breve en espanol>`.
   - Ejemplos: `docs: agrega guia manual de certificados ARCA`, `fix: corrige parseo de fecha en wsaa`.
5. Subir cambios: `git push origin main` (o la rama activa).

Notas de shell:
- En PowerShell no asumir `&&`; ejecutar por linea o usar `;`.
- Si falla un comando, corregir y reintentar ese paso.
