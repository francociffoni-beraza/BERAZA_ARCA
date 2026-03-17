# Step by Step ARCA - Alta Manual de Servicios del CUIT

Fecha: 2026-03-16  
Scope: tareas manuales en ARCA para habilitar servicios SOAP del CUIT (base `wscpe` + fase 2), separando `dev` y `prod`.

## 0) Objetivo
Dejar habilitados en ARCA los servicios necesarios para iterar integraciones del CUIT sin bloqueos de autorizacion.

## 1) Precondiciones (antes de entrar a ARCA)
1. Definir ambiente a operar (`dev` o `prod`).
2. Confirmar CUIT de autenticacion y CUIT representada.
3. Confirmar que el certificado del ambiente ya esta emitido y asociado al computador fiscal.
4. Tener a mano el listado de servicios a habilitar (prioridad sugerida abajo).

Nota: el flujo de certificados ya esta documentado en `docs/pasos-certificados-arca.md`.

## 2) Alta manual por servicio (repetir por cada WS y ambiente)
1. Ingresar con Clave Fiscal del CUIT que administra relaciones.
2. Ir a `Administrador de Relaciones`.
3. Seleccionar la CUIT representada correcta.
4. Crear o editar una relacion para el servicio objetivo:
   - Servicio: usar el nombre tecnico exacto del manual oficial del WS.
   - Computador fiscal: seleccionar el asociado al certificado vigente del ambiente.
5. Confirmar la relacion y dejarla activa.
6. Guardar evidencia minima:
   - servicio,
   - CUIT auth,
   - CUIT representada,
   - ambiente,
   - fecha/hora,
   - usuario que hizo el alta.

## 3) Orden de habilitacion recomendado
1. `wscpe` (control base ya operativo).
2. `wsfev1`.
3. `wscdc`.
4. `ws_sr_constancia_inscripcion`.
5. `ws_sr_padron_a13`.
6. `wsfecred` (si aplica al negocio).
7. `wslpg` (si aplica al negocio).

## 4) Manuales oficiales ya descargados (repo)
Base documental local: `docs/manuales/servicios-cuit/`

Archivos clave:
- `wscpe_manual_desarrollador.pdf`
- `wsfev1_manual_desarrollador_v4.1.pdf`
- `wscdc_manual_desarrollador_v0.4.pdf`
- `ws_sr_constancia_inscripcion_manual_v4.1.pdf`
- `ws_sr_padron_a13_manual_v1.3.pdf`
- `wsfecred_manual_desarrollador_v2.0.0.pdf`
- `wslpg_manual_desarrollador_v1.24.pdf`

## 5) Criterio de salida del gate ARCA (por servicio)
- Relacion activa visible en ARCA para la CUIT representada correcta.
- Certificado/computador fiscal correcto para el ambiente.
- Evidencia registrada en `docs/work-log.md`.

## 6) Que hacer si aparece bloqueo
1. No inventar configuraciones.
2. Registrar mensaje exacto del bloqueo y contexto (ambiente, servicio, CUITs).
3. Guardar evidencia y dejar constancia en `docs/work-log.md`.
4. Continuar con el siguiente servicio no bloqueado del mismo hito.

## 7) Donde quedo el paso a paso viejo de AfipSDK
No quedo como archivo unico separado en esta version del repo. La trazabilidad historica esta en:
- `docs/work-log.md` (entradas historicas de alta ARCA + pruebas via AfipSDK).
- `docs/step-by-step.md` (documento historico/transicion).
- `docs/step-by-step-cpe-dev.md` (flujo vigente ARCA directo).
