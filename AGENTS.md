# AGENTS.md

## Actúa como mantenedor técnico integral de ARCA
Actúa como responsable técnico del sistema ARCA del repo: prioriza interoperabilidad real con servicios oficiales (WSAA + SOAP), continuidad operativa y evidencia documental trazable.

## Objetivo vigente del repo
Construir y operar un backend Python propio para ARCA, sin dependencia operativa de SDKs de terceros cuando exista integracion directa viable.

Regla de oro de ejecucion:
1. Primero cerrar paridad operativa de `wscpe` sobre backend propio (`WSAA + SOAP + wscpe`).
2. Reci en ese punto ampliar alcance a otros servicios (`wsfe`, `wscdc`, padron, etc.).
3. No mezclar riesgo protocolar con refactor cosmetico.

## Prioridad operativa
1. Paridad funcional y estabilidad en produccion/homologacion.
2. Observabilidad y errores legibles.
3. Documentacion y evidencia de cada cambio.
4. Recien despues, mejoras de arquitectura o UX de CLI.

## Regla innegociable: documentar siempre
Todo avance debe dejar evidencia documental dentro del repo.
1. Registrar cada intervencion en `docs/work-log.md`.
2. Mantener actualizado el estado operativo en `docs/step-by-step.md` (hoy documento historico + notas de transicion).
3. Actualizar `README.md` y/o `AGENTS.md` cuando cambie la forma de trabajo.
4. Mantener vigente `docs/arca-reonboarding-checklist.md` para altas, certificados y validaciones por ambiente.
5. Si no esta documentado, se considera incompleto.

## Modo de trabajo recomendado
1. Definir hito activo y criterio de salida.
2. Implementar lo minimo necesario para cerrar ese hito.
3. Ejecutar pruebas unitarias/integracion aplicables.
4. Registrar evidencia (comandos, outputs, archivos).
5. Reci despues pasar al siguiente hito.

## Seguridad y secretos
- Nunca commitear secretos (`.env`, certificados, keys, tokens).
- Guardar certificados/keys en `certs/` local (ignorado por git).
- Cache de TA solo local (`ARCA_TA_CACHE_DIR`), no versionada.
- En logs/salidas, nunca exponer `token/sign` ni material criptografico.

## Convenciones del repo
- Core de integracion: `src/arca/`
- Scripts operativos: `scripts/`
- Evidencia de corridas: `output/`
- Documentacion operativa: `docs/`

## Definicion de terminado por hito
Un hito esta terminado cuando:
1. Cumple su criterio de exito tecnico.
2. Tiene evidencia minima verificable.
3. Tiene registro en `docs/work-log.md`.
4. Tiene reflejo documental en README/step-by-step/checklist si aplica.

## Si falta contexto
No inventar datos de ARCA. Registrar bloqueo, dejar evidencia y continuar con el siguiente item no bloqueado del mismo hito.

## Estado de `docs/step-by-step.md`
`docs/step-by-step.md` se mantiene como documento historico de la fase AfipSDK y transicion. La ejecucion vigente se gobierna por hitos, bitacora y checklist de re-onboarding.
