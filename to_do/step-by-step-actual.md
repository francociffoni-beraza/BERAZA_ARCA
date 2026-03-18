# Step by step actual (hitos / subhitos / mini-hitos)

Fecha base: 2026-03-18
Estado: EN CURSO
Objetivo vigente: consolidar backend ARCA propio y eliminar dependencias legacy.

## Hito 1 - BORRAR cualquier cosa relacionada con proveedor legacy
Estado: EN CURSO
Criterio de salida:
- No quedan referencias operativas al proveedor legacy en codigo, scripts ni configuracion activa.
- La documentacion operativa no requiere proveedor legacy para correr `wscpe`.
- Queda evidencia de limpieza en `docs/work-log.md`.

### Subhito 1.1 - Inventario total del proveedor legacy
Estado: COMPLETADO (2026-03-18)
Mini-hitos:
- [x] 1.1.1 Buscar referencias del proveedor legacy (`access token`, dominio legacy, nombre de proveedor).
- [x] 1.1.2 Clasificar hallazgos por tipo (`codigo`, `scripts`, `env`, `docs`, `tests`).
- [x] 1.1.3 Definir impacto y orden de borrado por riesgo.

Resultado inventario (2026-03-18):
- Total detectado: 64 referencias en 14 archivos versionados (sin contar este archivo `to_do`).
- Configuracion: `.env.example`.
- Codigo y tests: `scripts/context_checkpoint.py`, `tests/unit/test_context_checkpoint.py`.
- Documentacion operativa/backlog: `README.md`, `README_integral.md`, `AGENTS.md`, `docs/step-by-step-cpe-dev.md`, `docs/step-by-step-arca-servicios-cuit.md`, `docs/wscpe-compatibilidad-parcial.md`, `docs/metodos-wscpe-a-explotar.md`, `docs/propuestas-servicios-pyme-agro.md`.
- Documentacion historica/snapshots: `docs/work-log.md`, `docs/chat-context/legacy_worklog.md`, `docs/chat-context/bootstrap_prompt.md`.

Orden de borrado por riesgo:
1. Configuracion y codigo activo (`.env.example`, `scripts/context_checkpoint.py`).
2. Tests asociados al sanitizado (`tests/unit/test_context_checkpoint.py`).
3. Documentacion operativa actual (`README*`, `AGENTS.md`, `docs/step-by-step-*.md`, `docs/wscpe-compatibilidad-parcial.md`).
4. Documentacion backlog con enlaces legacy (`docs/metodos-wscpe-a-explotar.md`, `docs/propuestas-servicios-pyme-agro.md`).
5. Historicos y snapshots (`docs/work-log.md`, `docs/chat-context/*`) con estrategia de preservacion de trazabilidad.

### Subhito 1.2 - Limpieza de codigo y configuracion
Estado: COMPLETADO (2026-03-18)
Mini-hitos:
- [x] 1.2.1 Eliminar variables/env legacy no usadas por backend ARCA directo.
- [x] 1.2.2 Borrar helpers/adaptadores legacy si todavia existen.
- [x] 1.2.3 Ajustar scripts para que operen solo con `WSAA + SOAP` propio.
Resultado:
- `.env.example` ya no define `LEGACY_ACCESS_TOKEN`.
- `scripts/context_checkpoint.py` usa sanitizado generico de claves sensibles (`*_TOKEN`, `*_PASSWORD`, etc.) sin referencia al proveedor legacy.
- Tests actualizados y verdes (`tests/unit/test_context_checkpoint.py`, `py -3 -m unittest discover -s tests -p "test_*.py"`).
- Barrido operativo (config/codigo/docs activas) en 0 referencias legacy.

### Subhito 1.3 - Limpieza documental
Estado: COMPLETADO (2026-03-18)
Mini-hitos:
- [x] 1.3.1 Actualizar `README.md` removiendo instrucciones o notas legacy.
- [x] 1.3.2 Actualizar `docs/step-by-step.md` y checklists para reflejar flujo 100% ARCA directo.
- [x] 1.3.3 Registrar decisiones y cambios en `docs/work-log.md`.
- [x] 1.3.4 Limpiar docs backlog con enlaces legacy (`docs/metodos-wscpe-a-explotar.md`, `docs/propuestas-servicios-pyme-agro.md`).
- [x] 1.3.5 Definir tratamiento de historicos (`docs/work-log.md`, `docs/chat-context/*`) preservando trazabilidad.
Resultado parcial:
- `docs/metodos-wscpe-a-explotar.md` ya no usa enlaces de proveedor externo legacy.
- `docs/propuestas-servicios-pyme-agro.md` quedo alineado a fuentes ARCA/manuales locales.
- Historicos (`docs/work-log.md` y `docs/chat-context/*`) quedaron anonimizados sin perder secuencia de hechos.

### Subhito 1.4 - Verificacion y cierre
Estado: EN CURSO (con bloqueo de entorno local)
Mini-hitos:
- [x] 1.4.1 Ejecutar suite de tests (`py -3 -m unittest discover -s tests -p "test_*.py"`).
- [!] 1.4.2 Ejecutar smoke `wscpe` (`dummy` + `consultarUltNroOrden`) en ambiente activo.
- [ ] 1.4.3 Documentar evidencia final y marcar hito como COMPLETADO.
Bloqueo actual:
- `AFIP_CERT_PATH` apunta a `certs/CPE_4ace6a8e9a979c89.crt` y el archivo no existe en este entorno, por lo que los scripts de smoke abortan en carga de configuracion.

## Hito 2 - Operacion manual ARCA web
Estado: EN CURSO
Criterio de salida:
- Existe paquete operativo activo en `to_do/arca/` con indice y guias por tema.
- El flujo manual por ambiente (`dev`/`prod`) queda claro y usable sin depender de `docs/`.
- Cada corrida manual deja evidencia minima en `docs/work-log.md`.

### Subhito 2.1 - Preparar paquete `to_do/arca`
Estado: COMPLETADO (2026-03-18)
Mini-hitos:
- [x] 2.1.1 Crear `to_do/arca/README.md` como indice operativo.
- [x] 2.1.2 Crear guias activas `01-only-web`, `02-certificados`, `03-servicios-cuit`, `04-reonboarding-checklist`.
- [x] 2.1.3 Marcar documentos fuente de `docs/` como historicos y enlazados al flujo activo.

### Subhito 2.2 - Validar flujo manual por ambiente
Estado: TODO
Mini-hitos:
- [ ] 2.2.1 Ejecutar checklist manual completo en `dev` usando solo `to_do/arca/`.
- [ ] 2.2.2 Ejecutar checklist manual completo en `prod` usando solo `to_do/arca/`.
- [ ] 2.2.3 Registrar bloqueos manuales por ambiente/servicio en `docs/work-log.md`.

### Subhito 2.3 - Registrar evidencia minima por corrida manual
Estado: TODO
Mini-hitos:
- [ ] 2.3.1 Guardar ambiente, servicio, CUIT auth/representada, computador fiscal, fecha/hora, usuario.
- [ ] 2.3.2 Guardar captura/comprobante de relacion activa por servicio.
- [ ] 2.3.3 Consolidar resumen de corrida manual y proximo paso en `docs/work-log.md`.

## Hito 3 - Consolidacion diaria de `wscpe` (post-limpieza)
Estado: PENDIENTE
Nota: iniciar solo cuando el Hito 1 este COMPLETADO.
