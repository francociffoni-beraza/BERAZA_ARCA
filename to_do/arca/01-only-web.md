# Step by Step ONLY ARCA (Manual Web) - Activo

Fecha: 2026-03-18  
Scope: solo tareas manuales en la pagina de ARCA (altas, relaciones y autorizaciones).  
No incluye comandos locales, scripts ni configuracion `.env`.

Uso: marcar cada item con `[x]` cuando este completado.

## 1) Definir contexto antes de entrar
- [ ] Ambiente a operar: `dev` o `prod`.
- [ ] CUIT de autenticacion (quien entra y firma).
- [ ] CUIT representada (sobre quien se consulta/emite).
- [ ] Servicio a habilitar (ej: `wscpe`, `wsfev1`, `wscdc`, `ws_sr_constancia_inscripcion`, `ws_sr_padron_a13`, `wsfecred`, `wslpg`).

## 2) Ingreso a ARCA
- [ ] Entrar con Clave Fiscal del CUIT administrador de relaciones.
- [ ] Verificar que estas en el ambiente correcto antes de hacer cambios.

## 3) Alta/renovacion de certificado en WSASS (si corresponde)
- [ ] Ir a `WSASS` del ambiente.
- [ ] Cargar CSR del computador fiscal.
- [ ] Emitir certificado.
- [ ] Descargar `.crt`.
- [ ] Asociar el certificado al computador fiscal correcto (alias/DN correcto).

Nota: si el certificado ya esta vigente y correcto para ese ambiente, este bloque se omite.

## 4) Alta de relacion del servicio (Administrador de Relaciones)
- [ ] Ir a `Administrador de Relaciones`.
- [ ] Seleccionar la CUIT representada correcta.
- [ ] Crear `Nueva Relacion` (o editar existente).
- [ ] Elegir servicio exacto (nombre tecnico del WS).
- [ ] Seleccionar computador fiscal asociado al certificado vigente del ambiente.
- [ ] Confirmar y dejar la relacion activa.

## 5) Repetir por cada servicio que vayas a operar
Orden sugerido:
- [ ] `wscpe` (base actual).
- [ ] `wsfev1`.
- [ ] `wscdc`.
- [ ] `ws_sr_constancia_inscripcion`.
- [ ] `ws_sr_padron_a13`.
- [ ] `wsfecred` (si aplica).
- [ ] `wslpg` (si aplica).

## 6) Evidencia manual minima que hay que guardar
- [ ] Ambiente (`dev`/`prod`).
- [ ] Servicio habilitado.
- [ ] CUIT auth y CUIT representada.
- [ ] Computador fiscal usado.
- [ ] Fecha/hora de alta.
- [ ] Usuario que hizo la gestion.
- [ ] Captura o comprobante de relacion activa.

## 7) Criterio de cerrado (manual ARCA)
- [ ] Relacion activa visible en ARCA para el servicio correcto.
- [ ] Relacion hecha sobre la CUIT representada correcta.
- [ ] Computador fiscal correcto para el ambiente correcto.
- [ ] Evidencia guardada y lista para registrar en bitacora tecnica.
