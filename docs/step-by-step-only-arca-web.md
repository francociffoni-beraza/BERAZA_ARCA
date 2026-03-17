# Step by Step ONLY ARCA (Manual Web)

Fecha: 2026-03-16  
Scope: solo tareas manuales en la pagina de ARCA (altas, relaciones y autorizaciones).  
No incluye comandos locales, scripts ni configuracion `.env`.

## 1) Definir contexto antes de entrar
1. Ambiente a operar: `dev` o `prod`.
2. CUIT de autenticacion (quien entra y firma).
3. CUIT representada (sobre quien se consulta/emite).
4. Servicio a habilitar (ej: `wscpe`, `wsfev1`, `wscdc`, `ws_sr_constancia_inscripcion`, `ws_sr_padron_a13`, `wsfecred`, `wslpg`).

## 2) Ingreso a ARCA
1. Entrar con Clave Fiscal del CUIT administrador de relaciones.
2. Verificar que estas en el ambiente correcto antes de hacer cambios.

## 3) Alta/renovacion de certificado en WSASS (si corresponde)
1. Ir a `WSASS` del ambiente.
2. Cargar CSR del computador fiscal.
3. Emitir certificado.
4. Descargar `.crt`.
5. Asociar el certificado al computador fiscal correcto (alias/DN correcto).

Nota: si el certificado ya esta vigente y correcto para ese ambiente, este bloque se omite.

## 4) Alta de relacion del servicio (Administrador de Relaciones)
1. Ir a `Administrador de Relaciones`.
2. Seleccionar la CUIT representada correcta.
3. Crear `Nueva Relacion` (o editar existente).
4. Elegir servicio exacto (nombre tecnico del WS).
5. Seleccionar computador fiscal asociado al certificado vigente del ambiente.
6. Confirmar y dejar la relacion activa.

## 5) Repetir por cada servicio que vayas a operar
Orden sugerido:
1. `wscpe` (base actual).
2. `wsfev1`.
3. `wscdc`.
4. `ws_sr_constancia_inscripcion`.
5. `ws_sr_padron_a13`.
6. `wsfecred` (si aplica).
7. `wslpg` (si aplica).

## 6) Evidencia manual minima que hay que guardar
1. Ambiente (`dev`/`prod`).
2. Servicio habilitado.
3. CUIT auth y CUIT representada.
4. Computador fiscal usado.
5. Fecha/hora de alta.
6. Usuario que hizo la gestion.
7. Captura o comprobante de relacion activa.

## 7) Criterio de cerrado (manual ARCA)
1. Relacion activa visible en ARCA para el servicio correcto.
2. Relacion hecha sobre la CUIT representada correcta.
3. Computador fiscal correcto para el ambiente correcto.
4. Evidencia guardada y lista para registrar en bitacora tecnica.
