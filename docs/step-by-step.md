# Step by step - Carta de Porte (ARCA / Afip SDK)

> Nota 2026-03-12: este documento queda como historico de la fase AfipSDK.
> La ejecucion vigente se opera por hitos de migracion ARCA directa (`WSAA + SOAP + wscpe`), con trazabilidad en `docs/work-log.md`, contrato en `docs/wscpe-compatibilidad-parcial.md` y checklist en `docs/arca-reonboarding-checklist.md`.

Fecha base: 2026-03-04
WS: `wscpe`
CUIT objetivo: `20049687495`
Ambiente objetivo: `dev`

## Estado global
- [x] 1. Obtener `access_token` de Afip SDK (`app.afipsdk.com`).
- [x] 2. Definir ambiente de trabajo (`dev` o `prod`).
- [x] 3. Obtener `cert` + `key` del CUIT para el ambiente elegido.
- [x] 4. Autorizar web service `wscpe` para el certificado.
- [x] 5. Obtener TA (`token` + `sign`) para `wscpe`.
- [x] 6. Prueba tecnica minima (`dummy` + `consultarUltNroOrden`).
- [x] 7. Consultar cartas emitidas (metodos de emision).

## Seguimiento detallado

### 1) access_token
Objetivo: habilitar autenticacion con Afip SDK.
Estado: COMPLETADO
Terminado cuando:
- Existe `AFIPSDK_ACCESS_TOKEN` cargado en `.env` local.
- Se verifica que no se versiona en git.
Evidencia:
- Fecha: 2026-03-04
- Responsable: Codex
- Nota: `AFIPSDK_ACCESS_TOKEN` validado como presente en `.env` (sin exponer valor) y `.env` confirmado en `.gitignore`.

### 2) Ambiente
Objetivo: fijar `AFIP_ENV` (`dev` o `prod`).
Estado: COMPLETADO
Terminado cuando:
- Queda definido un ambiente por defecto para iteracion.
- El CUIT de trabajo queda documentado.
Evidencia:
- Fecha: 2026-03-04
- Responsable: Codex
- Nota: Configuracion actual validada en `.env`: `AFIP_ENV=dev`, `AFIP_CUIT=20049687495`. Pruebas puntuales en `prod` del 2026-03-05: (a) primer probe devolvio `ns1:cms.cert.untrusted` con certificado de desarrollo (`output/prod_probe_wscpe_20260305_125525.json`), (b) segundo probe con certificado productivo devolvio `ns1:coe.notAuthorized` (`output/prod_probe_wscpe_20260305_131335.json`), confirmando bloqueo por autorizacion de servicio, (c) tras alta de relacion en ARCA prod, `auth` y `dummy` respondieron OK, y para `consultarUltNroOrden` se confirmo que debe usarse `cuitRepresentada=20042908720` (respuesta `HTTP 200` en `output/prod_ultnro_with_related_cuit_20260305_132853.json`). Se creo `.env.prod` separado para aislar configuracion productiva. Validacion posterior del certificado productivo (`certs/CPE_4ace6a8e9a979c89.crt`) mostro `SERIALNUMBER=CUIT 30547090523`; al probar `AFIP_CUIT=30547090523` y `AFIP_CUIT_REPRESENTADA=30547090523` se obtuvo bloqueo de AfipSDK por limite de CUITs (salida en `output/prod_auth_attempt_cuit30547090523_20260305.txt`), por lo que queda pendiente habilitar ese CUIT en el plan antes de ajustar configuracion definitiva. El usuario renovo `AFIPSDK_ACCESS_TOKEN` y el CUIT auth `30547090523` quedo operativo; se actualizo `.env.prod` con ese `AFIP_CUIT` y se valido una corrida productiva con `cuitRepresentada=20042908720` (`output/prod_after_envprod_switch_cuit30547090523_20260305.json`). Verificacion de `pricing` AfipSDK del 2026-03-05: plan `Free` incluye `1 CUIT` y el conteo se define por "usuario de ARCA" (evidencia local: `output/_afipsdk_pricing_raw.html` y `output/_afipsdk_faq_section.js`). Luego de la nueva autorizacion informada por el usuario en ARCA, se confirmo que `cuitRepresentada=30547090523` ya autentica en metodo de negocio cuando se fuerza TA nuevo (`force_create=true`) en `output/prod_post_arca_auth_force_ta_repr30547090523_20260305.json`; se dejo `.env.prod` en `AFIP_CUIT=30547090523` y `AFIP_CUIT_REPRESENTADA=30547090523` y se valido corrida final en `output/prod_after_envprod_repr30547090523_force_ta_20260305.json`. Barrido adicional de control (planta `518477`, fechas `2026-03-03` a `2026-03-05`) en `output/prod_after_arca_auth_barrido_518477_20260303_20260305.json` devolvio `HTTP 200` con `codigo 800`.

### 3) Certificado y key
Objetivo: disponer de credenciales criptograficas validas del CUIT objetivo.
Estado: COMPLETADO
Terminado cuando:
- Certificado y key del CUIT `20049687495` estan generados/descargados.
- Rutas cargadas en `.env` local (`AFIP_CERT_PATH`, `AFIP_KEY_PATH`) apuntan al mismo CUIT.
Evidencia:
- Fecha: 2026-03-05
- Responsable: Codex
- Nota: Certificado `certs/cuit_20049687495_eduardoberazawscpe.crt` disponible, validado contra `certs/cuit_20049687495_dev_20260303.key` con resultado `CRT_KEY_MATCH=OK`, y rutas activas cargadas en `.env` (`AFIP_CERT_PATH`, `AFIP_KEY_PATH`) para CUIT `20049687495`. Para migracion a produccion se genero nuevo par `key/csr` en `certs/cuit_20049687495_wscpe_prod_20260305.key` y `certs/cuit_20049687495_wscpe_prod_20260305.csr`; luego se recibio `certs/CPE_4ace6a8e9a979c89.crt` desde ARCA y se valido `CRT_KEY_MATCH=OK` contra la key productiva (evidencia: `output/prod_cert_key_validation_20260305_131430.json`).

### 4) Autorizacion ws `wscpe`
Objetivo: habilitar el certificado definitivo para usar Carta de Porte.
Estado: COMPLETADO
Terminado cuando:
- El servicio `wscpe` queda autorizado en ARCA para el certificado del CUIT `20049687495`.
Evidencia:
- Fecha: 2026-03-05
- Responsable: Codex + usuario
- Nota: Autorizacion creada informada por el usuario con datos `CUITCOMPUTADOR=20049687495`, `ALIASCOMPUTADOR=eduardoberazawscpe`, `CUITREPRESENTADO=20049687495`, `SERVICIO=ws://wscpe`, `CUITAUTORIZANTE=20049687495`; validez confirmada tecnicamente al obtener TA exitoso en el paso 5.

### 5) TA (`token` + `sign`)
Objetivo: obtener credenciales de sesion para invocar metodos.
Estado: COMPLETADO
Terminado cuando:
- Se obtiene TA valido en el ambiente elegido.
- Se guarda evidencia de respuesta (sin exponer secretos).
Evidencia:
- Fecha: 2026-03-05
- Responsable: Codex
- Nota: Solicitud ejecutada contra `https://app.afipsdk.com/api/v1/afip/auth` con `AFIP_ENV=dev` y `wsid=wscpe`; respuesta `HTTP 200` con TA valido y expiracion `2026-03-06T03:29:33.538Z`. Evidencia sanitizada en `output/ta_wscpe_dev_20260305_122933.json`.

### 6) Prueba tecnica minima
Objetivo: validar conectividad y sanidad del servicio.
Estado: COMPLETADO
Terminado cuando:
- `dummy` responde OK.
- `consultarUltNroOrden` responde sin error tecnico.
Evidencia:
- Fecha: 2026-03-05
- Responsable: Codex
- Nota: Prueba ejecutada via Afip SDK (`/api/v1/afip/requests`) con `AFIP_ENV=dev` y `wsid=wscpe`: `dummy` retorno `appserver/authserver/dbserver=Ok` y `consultarUltNroOrden` retorno `HTTP 200` con `nroOrden=0` y sin error tecnico. Evidencia en `output/step6_sanity_wscpe_dev_20260305_123125.json`.

### 7) Cartas emitidas
Objetivo: empezar explotacion de metodos de emision.
Estado: COMPLETADO
Metodos iniciales sugeridos:
- `consultarCPEPorDestino`
- `consultarCPEAutomotor`
- `consultarCPEEmitidasDestinoDGPendientesActivacion`
Terminado cuando:
- Se ejecuta al menos una consulta real por rango de fechas.
- La salida se guarda en `output/` (json/csv).
Evidencia:
- Fecha: 2026-03-05
- Responsable: Codex
- Nota: Se ejecuto `consultarCPEPorDestino` por rango de fechas y se guardaron salidas en `output/`: primer intento (`2026-02-03` a `2026-03-05`) devolvio validacion `codigo 2152` (rango maximo 3 dias), segundo intento corregido (`2026-03-03` a `2026-03-05`) devolvio `HTTP 200` con respuesta funcional `codigo 800` (sin solicitudes para esos parametros). Adicionalmente se consultaron plantas informadas por el usuario (`20217`, `20218`, `20219`, `519447`, `700011`) con `tipoCartaPorte=74` y el mismo rango de 3 dias, todas con `HTTP 200` y `codigo 800`; luego se realizo barrido completo de febrero 2026 en ventanas de 3 dias (50 consultas) para esas plantas y `tipoCartaPorte=74`, sin CPE encontradas (`found_any_cpe=false`). En prod se dejo script reutilizable `scripts/prod_consultar_cpe_por_destino.py` y se ejecuto una corrida con `cuitRepresentada=20042908720` (autenticacion `tax_id=20049687495`) obteniendo `HTTP 200` en todas las plantas con `codigo 800`. Como contraste, se inspecciono la CPE emitida `00002-00012419` (fecha `2026-03-04`) y se probaron consultas puntuales en prod por planta `20219` (procedencia) y `518477` (destino), ambas sin resultados para `cuitRepresentada=20042908720`; al forzar `cuitRepresentada=30547090523` el servicio devolvio error de autenticacion por relacion faltante (`La Cuit 30547090523 no esta relacionada con el conjunto { 20042908720 }`). Tras la nueva autorizacion en ARCA y forzando TA nuevo (`force_create=true`), se repitio la prueba en planta `20219` con `cuitRepresentada=30547090523` para fecha `2026-03-04`, obteniendo `HTTP 200` con `codigo 800`. Finalmente se confirmo la existencia de la CPE `00002-00012419` con `consultarCPEAutomotor` (consulta por identificador de carta) obteniendo `HTTP 200` y datos completos de cabecera/origen/destino. Luego se implemento y ejecuto un barrido por `consultarCPEAutomotor` de los ultimos 3 dias (`tipo=74`, `sucursal=2`) con resultado `MATCHES=18` sobre `SCANNED=38`, incluyendo la carta `12419`. Como definicion operativa, `consultarCPEAutomotor` queda para `emitidas`/consulta por identificador; para `recibidas` se debe usar `consultarCPEPorDestino` (calidad de destino) con plantas de destino propias. Se confirmo con corrida de recibidas en prod para `2026-03-03..2026-03-05` sobre plantas `20217,20218,20219,519447,700011`, donde la planta `20219` devolvio 5 cartas y el resto `codigo 800`. Para un CTG recibido puntual (`10129907277`), el detalle disponible por `consultarCPEPorDestino` es `tipoCartaPorte, nroCTG, fechaPartida, estado, fechaUltimaModificacion`; para ampliar detalle en `consultarCPEAutomotor` se puede consultar por `solicitud.nroCTG` (en raiz, no dentro de `cartaPorte`) como se valido luego con CTG `10129920861`. Evidencias: `output/step7_consultarCPEPorDestino_dev_20260305_123237.json`, `output/step7_consultarCPEPorDestino_dev_20260305_123306.json`, `output/step7_consultarCPEPorDestino_plantas74_dev_20260305_124526.json`, `output/step7_consultarCPEPorDestino_feb2026_plantas74_dev_20260305_124943.json`, `output/prod_consultarCPEPorDestino_20260305_133313.json`, `output/pdf_extract_cpe_00002_00012419.txt`, `output/prod_match_test_cpe_00002_00012419.json`, `output/prod_match_test_cpe_00002_00012419_destino518477.json`, `output/prod_match_test_cpe_00002_00012419_repr30547090523.json`, `output/prod_test_planta20219_20260304_20260305.json`, `output/prod_consultarCPEAutomotor_00002_00012419_20260305_163335.json`, `output/prod_consultarCPEAutomotor_ultimos3dias_tipo74_suc2_20260305.json` y `output/prod_recibidas_por_destino_ult3dias_plantas_conocidas_20260305.json`.
- Nota adicional: Se incorporo `--include-statuses` en `scripts/prod_consultar_cpe_por_destino.py` y se ejecuto filtro `AC,CF,CO,CN` para `2026-03-03..2026-03-05` en `output/prod_recibidas_estados_AC_CF_CO_CN_ult3dias_20260305.json`; resultado: 5 cartas (todas `AC`), sin registros `CF/CO/CN` en esa ventana.
- Nota adicional 2: Se realizo barrido extendido de 30 dias (`2026-02-04..2026-03-05`) en ventanas de 3 dias sobre plantas `20217,20218,20219,519447,700011` (archivo `output/prod_recibidas_status_scan_30dias_20260305.json`) y el acumulado de estados fue `AC=5`, `CF=0`, `CO=0`, `CN=0`.
- Nota adicional 3: Se valido inconsistencia reportada para `CN`: `consultarCPEPorDestino` en `2026-03-05` y planta `20219` devolvio solo 4 registros `AC` (`output/prod_recibidas_all_planta20219_20260305.json`), mientras que `consultarCPEAutomotor` por `nroCTG` sobre el mismo CUIT representado devolvio `10129920861` en estado `CN` (`output/prod_consultarCPEAutomotor_ctg_10129920861_20260305.json`). Para este escenario se agrego `scripts/prod_consultar_cpe_por_ctg.py` (consulta batch por CTG).
- Nota adicional 4: Se agrego bitacora nueva de control en `docs/bitacora-ctg-recibidas.md`, actualizada por `scripts/prod_actualizar_bitacora_ctg_recibidas.py`, con catalogo persistente en `output/ctg_recibidas_catalogo.json` y snapshots de corrida (`output/prod_bitacora_ctg_recibidas_run_20260305_173725.json`, `output/prod_bitacora_ctg_recibidas_run_20260305_173831.json`, `output/prod_bitacora_ctg_recibidas_run_20260305_174132.json`). En la ventana `2026-03-03..2026-03-05` el metodo detecto 4 CTG (`AC`) por `consultarCPEPorDestino`; adicionalmente se habilito carga manual `--seed-ctgs` para incorporar CTG vistas en ARCA y en la ultima corrida quedaron consolidadas 6 CTG (4 `AC` + 2 `CN`).
- Nota adicional 5: Se documento un backlog de metodos `wscpe` adicionales en `docs/metodos-wscpe-a-explotar.md` y un backlog complementario de integraciones AFIP SDK para pyme agro en `docs/propuestas-afipsdk-pyme-agro.md`, priorizados por simplicidad e impacto operativo.
- Nota adicional 6: Corrida de control solicitada para ultimos 3 dias en `prod` con `consultarCPEAutomotor` (`py -3 scripts/prod_consultar_cpe_ultimos_dias.py --days 3 --tipo 74 --sucursal 2 --force-create-ta`) genero `output/prod_consultarCPEAutomotor_ultimos3dias_20260312_180930.json` con rango `2026-03-10..2026-03-12`, `ULT_NRO=12439`, `SCANNED=24`, `MATCHES=4` y estados detectados `CN,CN,CF,CN` (nros `12436..12439`, origen `20219`).
- Nota adicional 7: Se versiono la bitacora markdown de CTG recibidas para dejar historial prolijo por corrida. El script `scripts/prod_actualizar_bitacora_ctg_recibidas.py` ahora mantiene `docs/bitacora-ctg-recibidas.md` como vista actual y ademas guarda copia timestamp en `docs/bitacora-ctg-recibidas-versiones/` (opcionalmente desactivable con `--skip-versioned-bitacora`). Corrida de validacion del 2026-03-12 (`--days 3 --force-create-ta`) en `output/prod_bitacora_ctg_recibidas_run_20260312_181402.json`: `CTG_DETECTED=3`, `NEW=3`, `STATUS={'AC': 3}` y copia versionada `docs/bitacora-ctg-recibidas-versiones/bitacora-ctg-recibidas_20260312_181402.md`.
- Nota adicional 8: Se evaluo integracion con Context7 y luego se desestimo por decision del usuario (cita textual: "es una poronga y encima hay que pagar para conseguir la API key"). Se removieron los cambios asociados: script `scripts/prod_corrida_completa_context7.py`, configuracion `context7.json`, carpeta `context7/` y variables `CONTEXT7_*` en `.env.example/.env.prod`; `README.md` y `AGENTS.md` quedaron nuevamente sin flujo Context7.


## Nota de transicion (2026-03-12)
- Se implemento backend propio ARCA directo (`src/arca`) con `WSAA + SOAP + wscpe` y scripts migrados sin dependencia operativa de `AFIPSDK_ACCESS_TOKEN`.
- Evidencias de smoke/paridad inicial en `output/`: `wscpe_dummy_20260312_225227.json`, `wscpe_consultarUltNroOrden_20260312_225311.json`, `prod_consultarCPEAutomotor_porCTG_20260312_225320.json`, `prod_consultarCPEPorDestino_20260312_225427.json`, `prod_consultarCPEAutomotor_ultimos3dias_20260312_225438.json`, `prod_bitacora_ctg_recibidas_run_20260312_225446.json`.
- Regresion estructural contra baseline: `output/homologacion/regresion_baseline_20260312.txt` (`OK` en 4/4 flujos).
- Contrato de compatibilidad parcial: `docs/wscpe-compatibilidad-parcial.md`.
- Checklist operativo obligatorio de altas/certificados/validaciones: `docs/arca-reonboarding-checklist.md`.
- Paso a paso DEV operativo para emitidas/recibidas: `docs/step-by-step-cpe-dev.md`.
- Naming operativo de datos por corrida: `<proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>` en `output/runs/YYYY/MM/DD/run_<timestamp>/`.

