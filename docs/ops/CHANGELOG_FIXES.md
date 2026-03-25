# Changelog de fixes

Este archivo registra correcciones operativas y ajustes de código, scripts e integración ARCA.

El formato se inspira en "Keep a Changelog" (sin versionado semver).

## Reglas de uso

1. Agregar entrada en el mismo commit que produce el cambio.
2. Usar secciones: `Added`, `Changed`, `Removed`, `Fixed`, `Governance`.
3. Este archivo es append-only: no borrar historial.
4. Si el cambio corresponde a un hito cerrado: referenciar el checkpoint.

---

## [2026-03-25 — init-repo: framework operativo]

### Added
- `CLAUDE.md`: entry point de sesión con startup protocol, estructura del repo, governance y guardrails.
- `REGLAS_DE_ORO.md`: manual de operación de Claude — quién es quién, stack ARCA, loop de convergencia, docs obligatorias.
- `AGENTS_LIBRARY.md`: sub-agente para `src/arca/` — arquitectura, extensión a nuevos servicios, árbol de decisión ante problemas del core.
- `AGENTS_SCRIPTS.md`: sub-agente para `scripts/` — convenciones de output, contrato de compatibilidad, árbol de decisión.
- `AGENTS_ARCA_WEB.md`: sub-agente para operaciones manuales del portal ARCA — certificados, relaciones, incidentes recurrentes.
- `docs/ops/CHANGELOG_FIXES.md`: este archivo.
- `docs/ops/bitacora_fallos.md`: registro centralizado de incidentes auth/infra/scripts.

### Changed
- `AGENTS.md`: reescrito como agente raíz coordinador — árbol de delegación a los tres sub-agentes, reglas transversales y governance.

### Governance
- Framework operativo basado en el sistema de governance del datalake Beraza, adaptado al dominio ARCA (Python + SOAP + WSAA, sin DAGs ni dbt).
- Segmentación de AGENTS files: Library / Scripts / ARCA Web.
