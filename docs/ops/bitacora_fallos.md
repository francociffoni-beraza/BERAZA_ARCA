# Bitacora de fallos (Auth + Scripts + Library)

Ultima revision: 2026-03-25

## Objetivo

Centralizar en un unico lugar los incidentes de autenticación ARCA, scripts operativos y core library, incluyendo:
- sintoma e impacto,
- causa raiz,
- accion aplicada,
- validacion de cierre,
- accion preventiva para evitar recurrencia.

## Regla de oro operativa

Ningun incidente se considera resuelto sin entrada en estado `closed` en este archivo.

## Reglas de uso

1. Registrar la entrada al detectar el incidente (no esperar al fix).
2. Clasificar dominio: `auth` | `scripts` | `library` | `portal`.
3. Cerrar solo con validacion verificable de recuperacion (ej: dummy.py OK, corrida exitosa).
4. Agregar referencias cruzadas a `docs/ops/CHANGELOG_FIXES.md` y `docs/work-log.md`.
5. Este archivo es append-only: no borrar historico.

## Plantilla obligatoria

Copiar y completar:

```md
### INC-YYYYMMDD-XX | estado: open|in_progress|closed
- Fecha deteccion (AR):
- Dominio: auth|scripts|library|portal
- Severidad: critica|alta|media|baja
- Componente:
- Sintoma:
- Impacto:
- Causa raiz:
- Accion aplicada:
- Validacion de cierre:
- Accion preventiva:
- Owner:
- Fecha cierre (AR):
- Referencias:
```

## Incidentes activos

_ninguno_

## Historial de incidentes

_Sin entradas aun. Los incidentes se documentan a medida que ocurren._
