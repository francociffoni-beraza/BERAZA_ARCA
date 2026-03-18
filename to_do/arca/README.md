# ARCA Web - Flujo Activo (to_do)

Fecha base: 2026-03-18
Scope: operacion manual en la web oficial de ARCA, separando `dev` y `prod`.

## Objetivo
Centralizar en `to_do/arca/` el paso a paso operativo actual para tareas manuales ARCA:
- altas/renovaciones de certificados,
- altas de relaciones por servicio,
- validaciones por ambiente,
- checklist de cierre y evidencia minima.

## Orden de ejecucion recomendado
1. [01-only-web.md](./01-only-web.md)
2. [02-certificados.md](./02-certificados.md)
3. [03-servicios-cuit.md](./03-servicios-cuit.md)
4. [04-reonboarding-checklist.md](./04-reonboarding-checklist.md)

## Criterio de cierre por corrida manual
1. Ambiente correcto (`dev`/`prod`) validado antes de operar.
2. Certificado/computador fiscal correcto para el ambiente.
3. Relacion activa del servicio sobre CUIT representada correcta.
4. Evidencia minima guardada (fecha/hora, usuario, servicio, captura/comprobante).
5. Registro tecnico en `docs/work-log.md`.

## Fuentes historicas relacionadas (en `docs/`)
- `docs/step-by-step-only-arca-web.md`
- `docs/pasos-certificados-arca.md`
- `docs/step-by-step-arca-servicios-cuit.md`
- `docs/arca-reonboarding-checklist.md`
