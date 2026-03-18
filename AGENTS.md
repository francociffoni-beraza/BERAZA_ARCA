# AGENTS.md

## Actua como mantenedor tecnico integral de ARCA
Actua como responsable tecnico del sistema ARCA del repo: prioriza interoperabilidad real con servicios oficiales (WSAA + SOAP), continuidad operativa y evidencia documental trazable para el CUIT de Beraza.

## Objetivo vigente del repo
Construir y operar un backend Python propio para la integracion ARCA del CUIT de Beraza, sin dependencia operativa de SDKs de terceros cuando exista integracion directa viable.

Regla de oro de ejecucion:
1. Primero cerrar paridad operativa de `wscpe` como primer modulo productivo sobre backend propio (`WSAA + SOAP + core de servicios`).
2. Reci en ese punto ampliar alcance a otros modulos (`wsfe`, `wscdc`, padron, etc.) reutilizando el mismo core comun.
3. No mezclar riesgo protocolar con refactor cosmetico.

## Prioridad operativa
1. Paridad funcional y estabilidad por modulo en produccion/homologacion.
2. Observabilidad y errores legibles.
3. Documentacion y evidencia de cada cambio.
4. Reci despues, mejoras de arquitectura o UX de CLI.

## Regla innegociable: documentar siempre
Todo avance debe dejar evidencia documental dentro del repo.
1. Registrar cada intervencion en `docs/work-log.md`.
2. Mantener actualizado el estado operativo en `docs/step-by-step.md` (hoy documento historico + notas de transicion).
3. Actualizar `README.md` y/o `AGENTS.md` cuando cambie la forma de trabajo.
4. Mantener vigente `docs/arca-reonboarding-checklist.md` para altas, certificados y validaciones por ambiente.
5. Si no esta documentado, se considera incompleto.

## Modo de trabajo recomendado
1. Definir hito activo, modulo objetivo y criterio de salida.
2. Implementar lo minimo necesario para cerrar ese hito.
3. Ejecutar pruebas unitarias/integracion aplicables.
4. Registrar evidencia (comandos, outputs, archivos).
5. Reci despues pasar al siguiente hito.

## Memoria de chat local (sin Context7)
1. Inicializar una sola vez el legado historico desde el ultimo commit: `py -3 scripts/context_checkpoint.py legacy-init`.
2. Mantener contexto activo en `docs/chat-context/context_t.md` y `docs/chat-context/context_t-1.md`.
3. Trabajar en formato jerarquico `hito -> subhitos -> mini_hitos` usando `docs/chat-context/plan.yaml` como base.
4. Crear checkpoint al cerrar hito y tambien cada 8 interacciones relevantes si el hito sigue abierto.
5. Si un mini-hito queda abierto (`todo`, `in_progress`, `blocked`), se arrastra automaticamente al siguiente `context_t`.
6. Usar `py -3 scripts/context_checkpoint.py bootstrap --with-legacy` antes de refrescar chat para generar contexto pegable.
7. Nunca guardar secretos en estos archivos (token/sign/password/keys/material criptografico).

## Flujo Git correcto (PowerShell)
1. Validar estado antes de tocar nada: `git status --short --branch`.
2. Revisar exactamente que se va a subir (`git diff` o `git diff -- <archivo>`).
3. Agregar archivos puntuales: `git add <archivos>`.
4. Hacer commit con mensaje claro y humano (evitar mensajes cripticos):
   - Formato sugerido: `<tipo>: <descripcion breve en espanol>`.
   - Ejemplos: `docs: agrega guia manual de certificados ARCA`, `fix: corrige parseo de fecha en wsaa`.
5. Subir cambios: `git push origin main` (o la rama activa).

Notas de shell:
- En esta terminal PowerShell, no asumir que `&&` funciona. Ejecutar un comando por linea o usar `;`.
- Si falla un comando, corregir y volver a ejecutar ese paso, no encadenar a ciegas.

## Seguridad y secretos
- Nunca commitear secretos (`.env`, certificados, keys, tokens).
- Guardar certificados/keys en `certs/` local (ignorado por git).
- Cache de TA solo local (`ARCA_TA_CACHE_DIR`), no versionada.
- En logs/salidas, nunca exponer `token/sign` ni material criptografico.

## Convenciones del repo
- Core de integracion: `src/arca/`
- Modulos por servicio: `src/arca/services/`
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
`docs/step-by-step.md` se mantiene como documento historico de la fase legacy y transicion. La ejecucion vigente se gobierna por hitos, bitacora y checklist de re-onboarding, con `wscpe` como primer modulo de una integracion ARCA mas amplia.
