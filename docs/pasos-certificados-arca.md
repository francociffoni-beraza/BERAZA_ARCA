# Pasos Manuales ARCA - Nuevos Certificados `wscpe`

Fecha: 2026-03-13
Scope: tareas que se hacen si o si en la web de ARCA para homologacion (`dev`) y produccion (`prod`).

## 1) Regla base
1. Homologacion y produccion se gestionan por separado.
2. Un certificado valido en `dev` no habilita `prod` (y viceversa).
3. No subir nunca la key privada a ARCA.

## 2) Antes de entrar a ARCA
1. Tener generado localmente el par `key + csr` del CUIT objetivo.
2. Confirmar el ambiente que vas a operar primero (`dev` o `prod`).
3. Definir CUIT de autenticacion y CUIT representada que deben quedar habilitados.

## 3) Paso a paso en ARCA (por ambiente)
1. Ingresar con Clave Fiscal del CUIT que administra relaciones.
2. Ir a `WSASS` del ambiente seleccionado.
3. Alta/renovacion de certificado:
   - Cargar el CSR nuevo.
   - Emitir el certificado.
   - Descargar el `.crt` emitido.
4. Asociar el certificado al Computador Fiscal correspondiente (alias/DN correcto).
5. Ir a `Administrador de Relaciones`.
6. Crear o actualizar relacion para servicio `ws://wscpe`:
   - Servicio: `ws://wscpe`.
   - CUIT representada: la que va a operar en las consultas.
   - Computador fiscal: el del certificado nuevo.
7. Confirmar la relacion y dejarla activa.

## 4) Datos que tenes que guardar de ARCA
1. Ambiente (`dev` o `prod`).
2. Alias/DN del computador fiscal.
3. Fecha de emision y vencimiento del certificado.
4. Evidencia de relacion activa (`ws://wscpe` + CUIT representada).
5. Fecha/hora de alta o renovacion y usuario que la hizo.

## 5) Checklist de cierre manual
- [ ] Certificado emitido y descargado en el ambiente correcto.
- [ ] Certificado asociado a computador fiscal correcto.
- [ ] Relacion `ws://wscpe` activa para la CUIT representada correcta.
- [ ] Evidencia guardada (captura, ID, fecha, responsable).
- [ ] Mismos pasos repetidos en el otro ambiente si aplica.

## 6) Handoff al backend (despues de ARCA)
1. Compartir `crt` emitido y alias/DN confirmado.
2. Confirmar CUIT auth y CUIT representada habilitadas.
3. Ejecutar validacion tecnica local:
   - `wscpe_dummy.py`
   - `wscpe_consultar_ult_nro_orden.py --force-create-ta`
