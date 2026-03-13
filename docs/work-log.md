# Work log

Bitacora cronologica obligatoria del proyecto.

## Plantilla de entrada
- Fecha:
- Paso:
- Cambios:
- Evidencia:
- Siguiente accion:

---

- Fecha: 2026-03-03
- Paso: general
- Cambios: Creacion de estructura base del repo (`src/`, `scripts/`, `output/`, `certs/`) y documentacion inicial (`README.md`, `AGENTS.md`, `docs/step-by-step.md`, `.env.example`, `.gitignore`).
- Evidencia: Archivos y carpetas creados en el workspace.
- Siguiente accion: Completar Paso 1 cargando `AFIPSDK_ACCESS_TOKEN` en `.env`.

- Fecha: 2026-03-03
- Paso: general
- Cambios: Se establece regla obligatoria de documentacion continua y se agrega esta bitacora para registrar todo avance.
- Evidencia: Actualizacion de `README.md` y `AGENTS.md`; alta de `docs/work-log.md`.
- Siguiente accion: Mantener registro por cada cambio tecnico o funcional.

- Fecha: 2026-03-03
- Paso: 1
- Cambios: Cierre formal del Paso 1 (`access_token`) con verificacion de presencia de variable y proteccion de secretos.
- Evidencia: `.env` contiene `AFIPSDK_ACCESS_TOKEN` (validado sin exponer valor) y `.env` esta ignorado por `.gitignore`.
- Siguiente accion: Avanzar Paso 2 validando ambiente y CUIT operativo para iteracion.

- Fecha: 2026-03-03
- Paso: 2
- Cambios: Actualizacion de credenciales operativas locales (`AFIP_CUIT` y password de acceso ARCA) y cierre formal del Paso 2 con ambiente `dev`.
- Evidencia: Variables presentes en `.env` (verificadas sin exponer valores); `docs/step-by-step.md` actualizado a Paso 2 COMPLETADO y Paso 3 EN CURSO.
- Siguiente accion: Iniciar Paso 3 gestionando certificado y key del CUIT para `wscpe`.

- Fecha: 2026-03-03
- Paso: 3
- Cambios: Generacion local de clave privada y CSR para homologacion `wscpe` del CUIT 20049687495.
- Evidencia: Archivos creados `certs/cuit_20049687495_dev_20260303.key` y `certs/cuit_20049687495_dev_20260303.csr`; CSR validado con subject `C=AR, O=Eduardo Beraza, CN=wscpe-dev, serialNumber=CUIT 20049687495`.
- Siguiente accion: Subir el CSR en WSASS homologacion de ARCA para emitir y descargar el certificado `.crt`.

- Fecha: 2026-03-03
- Paso: 3
- Cambios: Se normalizaron en `.env` los valores activos posteriores a `--` para `AFIP_CUIT` y `ARCA_PASSWORD`, y se genero un nuevo par `key/csr` para el CUIT activo 20392084267.
- Evidencia: `.env` sin sufijos `--` en esas variables; archivos creados `certs/cuit_20392084267_dev_20260303.key` y `certs/cuit_20392084267_dev_20260303.csr`; CSR validado con serial `CUIT 20392084267`.
- Siguiente accion: Cargar el CSR activo en ARCA (WSASS homologacion) y descargar el `.crt` correspondiente.

- Fecha: 2026-03-03
- Paso: 3
- Cambios: Bloqueo detectado en ARCA al crear DN por formato invalido de `Nombre simbolico` (acepta solo letras y numeros).
- Evidencia: Mensaje de ARCA: `El Nombre simbólico del DN sólo puede contener números y/o letras`.
- Siguiente accion: Reintentar usando alias alfanumerico sin espacios, guiones, guion bajo ni simbolos.

- Fecha: 2026-03-03
- Paso: 3
- Cambios: Validacion del certificado emitido y cierre formal del paso. Se configuro `.env` con rutas activas de certificado y clave privada.
- Evidencia: Certificado `certs/cuit_20392084267_francociffoniDNARCA.crt` leido correctamente (issuer AFIP testing, vigencia 2026-03-04 a 2028-03-03) y comprobacion `CRT_KEY_MATCH` contra `certs/cuit_20392084267_dev_20260303.key`; `AFIP_CERT_PATH` y `AFIP_KEY_PATH` cargados en `.env`.
- Siguiente accion: Ejecutar Paso 4 autorizando `wscpe` en WSASS para este certificado.

- Fecha: 2026-03-04
- Paso: general
- Cambios: Rehacer del plan operativo para CUIT definitivo `20049687495`; se reinicia estado activo en Paso 3 por mismatch entre CUIT y rutas de certificado/clave en `.env`.
- Evidencia: `docs/step-by-step.md` actualizado (Fecha base 2026-03-04, Paso 3 EN CURSO), `README.md` actualizado (Paso activo 3), validacion local de `.env` sin exponer secretos.
- Siguiente accion: Completar Paso 3 cargando `AFIP_CERT_PATH` y `AFIP_KEY_PATH` del CUIT `20049687495` y registrar evidencia.

- Fecha: 2026-03-05
- Paso: 4
- Cambios: Diagnostico de bloqueo de adhesion en ARCA por "falta de autorizacion" para SA con multiples CUIT representados y registro de precondiciones operativas para continuar.
- Evidencia: `docs/step-by-step.md` actualizado en Paso 4 con estado de bloqueo; respaldo oficial consultado en ARCA/AFIP (`/clavefiscal/ayuda/administrador-de-relaciones.asp`, `/clavefiscal/ayuda/vinculacion-pj.asp`, `/ws/documentacion/certificados.asp`).
- Siguiente accion: Validar vinculacion vigente como Administrador de Relaciones para CUIT `20049687495`, adherir `WSASS` con CUIT persona fisica (homologacion) y luego autorizar `wscpe` para el certificado correcto del CUIT objetivo.

- Fecha: 2026-03-05
- Paso: 3
- Cambios: Cierre formal del paso con certificado definitivo del CUIT `20049687495` y actualizacion de rutas activas en `.env`.
- Evidencia: Archivo `certs/cuit_20049687495_eduardoberazawscpe.crt` presente; validacion tecnica de par contra `certs/cuit_20049687495_dev_20260303.key` con `CRT_KEY_MATCH=OK`; `.env` actualizado con `AFIP_CERT_PATH` y `AFIP_KEY_PATH`.
- Siguiente accion: Cerrar Paso 4 y avanzar a la obtencion de TA para `wscpe`.

- Fecha: 2026-03-05
- Paso: 4
- Cambios: Cierre formal del paso por confirmacion de adhesion del servicio `wscpe` en ARCA.
- Evidencia: Confirmacion del usuario sobre alta/adhesion y actualizacion de estado a COMPLETADO en `docs/step-by-step.md`.
- Siguiente accion: Ejecutar Paso 5 obteniendo TA (`token` + `sign`) para `wscpe` en `dev`.

- Fecha: 2026-03-05
- Paso: 5
- Cambios: Primer intento de obtencion de TA con Afip SDK usando el certificado definitivo del CUIT `20049687495`.
- Evidencia: Llamada `POST https://app.afipsdk.com/api/v1/afip/auth` con `AFIP_ENV=dev` y `wsid=wscpe`; respuesta `HTTP 400` con `ns1:coe.notAuthorized`; evidencia sanitizada en `output/ta_wscpe_dev_20260305_122357.json`.
- Siguiente accion: Reabrir Paso 4 y autorizar efectivamente `wscpe` para el DN/certificado en ARCA (WSASS), luego reintentar TA.

- Fecha: 2026-03-05
- Paso: 4
- Cambios: Reapertura del paso por falta de autorizacion efectiva detectada en prueba tecnica de TA.
- Evidencia: `docs/step-by-step.md` actualizado a `Estado: EN CURSO (BLOQUEADO POR ns1:coe.notAuthorized)` y `README.md` actualizado a Paso activo `4`.
- Siguiente accion: Completar autorizacion de `wscpe` en ARCA para el certificado `cuit_20049687495_eduardoberazawscpe.crt` y repetir solicitud de TA.

- Fecha: 2026-03-05
- Paso: 4
- Cambios: Cierre efectivo de autorizacion para `wscpe` con parametros reportados por el usuario y validacion tecnica posterior.
- Evidencia: Confirmacion de autorizacion creada (`CUITCOMPUTADOR=20049687495`, `ALIASCOMPUTADOR=eduardoberazawscpe`, `CUITREPRESENTADO=20049687495`, `SERVICIO=ws://wscpe`, `CUITAUTORIZANTE=20049687495`) y TA exitoso en el intento siguiente.
- Siguiente accion: Cerrar Paso 5 con evidencia de TA y avanzar a pruebas tecnicas minimas del Paso 6.

- Fecha: 2026-03-05
- Paso: 5
- Cambios: Reintento de obtencion de TA con Afip SDK luego de la nueva autorizacion en ARCA.
- Evidencia: `POST https://app.afipsdk.com/api/v1/afip/auth` respondio `HTTP 200`; expiracion `2026-03-06T03:29:33.538Z`; evidencia sanitizada en `output/ta_wscpe_dev_20260305_122933.json`.
- Siguiente accion: Iniciar Paso 6 ejecutando `dummy` y `consultarUltNroOrden`.

- Fecha: 2026-03-05
- Paso: 6
- Cambios: Ejecucion de prueba tecnica minima del servicio `wscpe` usando TA valido en `dev`.
- Evidencia: `dummy` respondio `appserver/authserver/dbserver=Ok` y `consultarUltNroOrden` respondio `HTTP 200` con `nroOrden=0`; detalle en `output/step6_sanity_wscpe_dev_20260305_123125.json`.
- Siguiente accion: Iniciar Paso 7 consultando cartas emitidas por rango de fechas y guardar salida en `output/`.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Ejecucion de consultas de cartas emitidas por rango de fechas con `consultarCPEPorDestino` y ajuste de ventana por validacion del servicio.
- Evidencia: Primer intento `2026-02-03` a `2026-03-05` devolvio `codigo 2152` (rango maximo 3 dias) en `output/step7_consultarCPEPorDestino_dev_20260305_123237.json`; segundo intento `2026-03-03` a `2026-03-05` devolvio `HTTP 200` con `codigo 800` (sin solicitudes para los parametros indicados) en `output/step7_consultarCPEPorDestino_dev_20260305_123306.json`.
- Siguiente accion: Si se requiere data, iterar Paso 7 con otras plantas/tipos/rangos de 3 dias para ubicar emisiones reales y exportarlas en `output/`.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Consulta puntual por plantas operativas informadas por el usuario (`20217`, `20218`, `20219`, `519447`, `700011`) con `tipoCartaPorte=74` y ventana de 3 dias.
- Evidencia: `output/step7_consultarCPEPorDestino_plantas74_dev_20260305_124526.json` con respuesta `HTTP 200` en todas las plantas y `codigo 800` (sin solicitudes para los parametros indicados) en cada caso.
- Siguiente accion: Repetir la misma grilla planta/tipo con nuevos rangos de 3 dias hacia atras hasta detectar emisiones reales.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Barrido completo de febrero 2026 para plantas (`20217`, `20218`, `20219`, `519447`, `700011`) con `tipoCartaPorte=74`, en ventanas de 3 dias para cumplir restriccion de rango.
- Evidencia: `output/step7_consultarCPEPorDestino_feb2026_plantas74_dev_20260305_124943.json` con `total_requests=50`, `found_any_cpe=false`; todas las respuestas `HTTP 200` con `codigo 800` (sin solicitudes para los parametros indicados).
- Siguiente accion: Probar periodos anteriores (enero 2026 y diciembre 2025) con la misma estrategia o cambiar metodo a `consultarCPEAutomotor` para contraste.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Ejecucion de probe controlado en ambiente `prod` sin alterar `.env` para validar factibilidad inmediata de migracion.
- Evidencia: `output/prod_probe_wscpe_20260305_125525.json` con `auth_http_status=400` y mensaje `ns1:cms.cert.untrusted` (se detecta certificado de desarrollo en modo produccion).
- Siguiente accion: Gestionar certificado productivo del CUIT `20049687495` y autorizar `wscpe` para ese DN en ARCA prod antes de reintentar.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Se define instructivo operativo para alta en `prod` replicando flujo validado en `dev`, incluyendo precondiciones, emision de certificado productivo, autorizacion `wscpe` y validaciones tecnicas.
- Evidencia: Respuesta operativa entregada al usuario en esta sesion con checklist secuencial de migracion `DEV -> PROD`.
- Siguiente accion: Ejecutar el instructivo en ARCA produccion y luego repetir prueba tecnica (`auth`, `dummy`, `consultarUltNroOrden`) en `AFIP_ENV=prod`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Alta de archivo `.env.prod` separado para configuracion de produccion, actualizacion de `.gitignore` para protegerlo y ajuste de `README.md` con seccion de uso en PROD.
- Evidencia: Archivo `.env.prod` creado con placeholders (`AFIP_ENV=prod`), `.gitignore` actualizado con `.env.prod`, `README.md` actualizado con seccion `Ambiente PROD`.
- Siguiente accion: Generar key/CSR productivos del CUIT `20049687495`, emitir certificado en ARCA prod y completar variables reales en `.env.prod`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Generacion local de credenciales criptograficas para produccion (`key + csr`) del CUIT `20049687495` para `wscpe` y alineacion de rutas en `.env.prod`.
- Evidencia: Archivos creados `certs/cuit_20049687495_wscpe_prod_20260305.key` y `certs/cuit_20049687495_wscpe_prod_20260305.csr`; subject CSR `C=AR, O=Eduardo Beraza, CN=wscpe-prod, serialNumber=CUIT 20049687495`; `.env.prod` actualizado a `AFIP_CERT_PATH=certs/cuit_20049687495_wscpe_prod_20260305.crt` y `AFIP_KEY_PATH=certs/cuit_20049687495_wscpe_prod_20260305.key`.
- Siguiente accion: Subir el CSR productivo en ARCA (WSASS prod), descargar el `.crt` y validar `CRT_KEY_MATCH` antes de probar `AFIP_ENV=prod`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Integracion del certificado productivo descargado desde ARCA y validacion de par criptografico en entorno local; probe tecnico en `prod` con el nuevo certificado.
- Evidencia: Archivo `certs/CPE_4ace6a8e9a979c89.crt` validado contra `certs/cuit_20049687495_wscpe_prod_20260305.key` con `CRT_KEY_MATCH=OK` (detalle en `output/prod_cert_key_validation_20260305_131430.json`); `.env.prod` actualizado (`AFIP_CUIT=20049687495`, `AFIP_CERT_PATH=certs/CPE_4ace6a8e9a979c89.crt`); probe en `output/prod_probe_wscpe_20260305_131335.json` devolvio `ns1:coe.notAuthorized`.
- Siguiente accion: Autorizar `wscpe` en ARCA produccion para el certificado `CPE_4ace6a8e9a979c89.crt` y reintentar `auth` en `prod`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Se define instructivo paso a paso para autorizar `wscpe` en ARCA produccion desde Administrador de Relaciones, usando el certificado productivo vigente.
- Evidencia: Respuesta operativa entregada al usuario con secuencia de alta de relacion en ARCA y checks de estado para desbloquear `ns1:coe.notAuthorized`.
- Siguiente accion: Ejecutar la alta en ARCA prod y volver a probar `auth` con `.env.prod`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Validacion post-autorizacion en ARCA prod: `auth` y `dummy` OK; ajuste funcional detectado para operaciones de negocio (`cuitRepresentada` esperada por el servicio).
- Evidencia: `output/prod_sanity_wscpe_20260305_132715.json` con `auth_http_status=200`, `dummy.http_status=200` y error de autenticacion de negocio para `cuitRepresentada=20049687495` indicando conjunto `{20042908720}`; prueba confirmatoria en `output/prod_ultnro_with_related_cuit_20260305_132853.json` con `cuitRepresentada=20042908720` devolvio `HTTP 200`.
- Siguiente accion: Usar `cuitRepresentada=20042908720` en llamadas productivas de `wscpe` y continuar con consultas reales en prod.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Formalizacion de variable de configuracion para separar CUIT de autenticacion y CUIT representada en prod.
- Evidencia: `.env.prod` actualizado con `AFIP_CUIT_REPRESENTADA=20042908720`; `.env.example` ampliado con la misma variable; `README.md` actualizado en seccion `Ambiente PROD`.
- Siguiente accion: Adaptar llamadas productivas para tomar `AFIP_CUIT_REPRESENTADA` al construir `params.auth.cuitRepresentada`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Creacion de script reutilizable para consultas productivas por destino y ejecucion de primera corrida real en prod usando `AFIP_CUIT_REPRESENTADA`.
- Evidencia: Script `scripts/prod_consultar_cpe_por_destino.py` creado; corrida `py -3 scripts/prod_consultar_cpe_por_destino.py` con salida en `output/prod_consultarCPEPorDestino_20260305_133313.json` (`HTTP 200` en todas las plantas, `codigo 800`); `README.md` actualizado con comando rapido.
- Siguiente accion: Repetir el script cambiando rango/plantas segun necesidad operativa hasta detectar emisiones reales.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Inspeccion de CPE emitida `00002-00012419` en PDF y contraste con consultas productivas de `consultarCPEPorDestino` para fecha `2026-03-04`.
- Evidencia: Extraccion textual en `output/pdf_extract_cpe_00002_00012419.txt` (titular `30547090523`, planta procedencia `20219`, planta destino `518477`); pruebas en prod `output/prod_match_test_cpe_00002_00012419.json` (planta `20219`, `codigo 800`), `output/prod_match_test_cpe_00002_00012419_destino518477.json` (planta `518477`, `codigo 800`) y `output/prod_match_test_cpe_00002_00012419_repr30547090523.json` (forzando `cuitRepresentada=30547090523`, error de autenticacion `La Cuit 30547090523 no esta relacionada con el conjunto { 20042908720 }`).
- Siguiente accion: Dar de alta la relacion/autorizacion productiva para operar `wscpe` con `cuitRepresentada=30547090523` y repetir consulta por planta `518477` en rango `2026-03-04`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Validacion de identidad real del certificado productivo y deteccion de desalineacion con `AFIP_CUIT` configurado en `.env.prod`.
- Evidencia: `certutil -dump certs\\CPE_4ace6a8e9a979c89.crt` informo `SERIALNUMBER=CUIT 30547090523`; `.env.prod` contiene `AFIP_CUIT=20049687495`; prueba controlada con env temporal (`AFIP_CUIT=30547090523`, `AFIP_CUIT_REPRESENTADA=30547090523`) devolvio `HTTP 400` de AfipSDK por limite de CUITs (salida en `output/prod_auth_attempt_cuit30547090523_20260305.txt`).
- Siguiente accion: Habilitar en AfipSDK el uso del CUIT `30547090523` (upgrade/reset de cupo) y luego fijar `AFIP_CUIT`/`AFIP_CUIT_REPRESENTADA` en `30547090523` para repetir consulta de la CPE `00002-00012419`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Confirmacion del usuario de `access_token` nuevo en AfipSDK y continuidad del bloqueo para alta del CUIT empresa.
- Evidencia: Intercambio operativo en sesion (token renovado, sin alta efectiva del CUIT adicional en plan actual).
- Siguiente accion: Gestionar alta del CUIT `30547090523` desde `Billing`/plan en AfipSDK o solicitar desbloqueo a soporte con el `request ID` del error de limite.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Verificacion de reglas de cupo de CUITs en AfipSDK para explicar bloqueo en plan Free.
- Evidencia: Fuente oficial `https://afipsdk.com/pricing/` (plan `Free` incluye `1 CUIT`) y FAQ client-side de AfipSDK (`/_astro/faq-section.Bc9UoEEO.js`) indicando que el conteo de CUIT se realiza por "usuario de ARCA que use tu app"; respaldos locales en `output/_afipsdk_pricing_raw.html` y `output/_afipsdk_faq_section.js`.
- Siguiente accion: Si el contador del periodo ya esta consumido, subir a plan con mayor cupo o pedir reset manual a soporte AfipSDK indicando el error `27706cc4-f521-4eb1-a830-42a74333fa81`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Alta efectiva del CUIT auth productivo `30547090523` en AfipSDK (token nuevo) y actualizacion de `.env.prod` para autenticar con ese CUIT.
- Evidencia: Prueba con env temporal `tax_id=30547090523` + `cuitRepresentada=30547090523` en `output/prod_cuit30547090523_auth_probe_20260305.json` (auth OK, rechazo de negocio por relacion de representada); prueba con `cuitRepresentada=20042908720` en `output/prod_cuit30547090523_repr20042908720_probe_20260305.json` (`HTTP 200`, `codigo 800`); corrida final con `.env.prod` actualizado en `output/prod_after_envprod_switch_cuit30547090523_20260305.json`.
- Siguiente accion: Gestionar en ARCA la relacion para que el conjunto de `cuitRepresentada` incluya `30547090523`; luego cambiar `AFIP_CUIT_REPRESENTADA` en `.env.prod` y repetir consulta de CPE.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Preparacion de instructivo operativo para habilitar en ARCA la relacion faltante de `cuitRepresentada=30547090523` en `wscpe`.
- Evidencia: Referencias oficiales consultadas: `https://www.arca.gob.ar/ws/WSAA/ADMINREL.DelegarWS.pdf` (delegacion de webservices desde Administrador de Relaciones), `https://arca.gob.ar/ws/documentacion/wsaa.asp` (asociacion de certificado a WSN en produccion via Administrador de Relaciones), `https://www.arca.gob.ar/claveFiscal/ayuda/administrador-de-relaciones.asp` (vinculacion del administrador de relaciones).
- Siguiente accion: Ejecutar en ARCA: seleccionar representado `30547090523`, crear/ajustar `Nueva Relacion` para `ws://wscpe` autorizando el Computador Fiscal del certificado productivo y validar con corrida API usando `AFIP_CUIT_REPRESENTADA=30547090523`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Correccion operativa sobre CUIT de ingreso a ARCA informada por usuario.
- Evidencia: Confirmacion del usuario: el ingreso a ARCA se realiza con `20049687495` (no `20042908720`).
- Siguiente accion: Ejecutar el alta/ajuste de relacion `ws://wscpe` ingresando con `20049687495` y operando sobre el representado/alcance correcto para habilitar `cuitRepresentada=30547090523`.

- Fecha: 2026-03-05
- Paso: general
- Cambios: Validacion post-alta en ARCA de `wscpe` para `cuitRepresentada=30547090523`; ajuste del script productivo para permitir forzar TA nuevo y evitar cache de AfipSDK.
- Evidencia: Se agrego flag `--force-create-ta` en `scripts/prod_consultar_cpe_por_destino.py` (envia `force_create=true` en `/afip/auth`) y se actualizo `README.md` con el nuevo uso. Prueba con env temporal y `cuitRepresentada=30547090523` en `output/prod_post_arca_auth_force_ta_repr30547090523_20260305.json` devolvio `HTTP 200` (sin error de autenticacion). `.env.prod` actualizado a `AFIP_CUIT=30547090523` y `AFIP_CUIT_REPRESENTADA=30547090523`; corrida final `output/prod_after_envprod_repr30547090523_force_ta_20260305.json` con `HTTP 200`; barrido adicional de 3 dias en planta `518477` (`2026-03-03` a `2026-03-05`) en `output/prod_after_arca_auth_barrido_518477_20260303_20260305.json` con `codigo 800`.
- Siguiente accion: Continuar consultas funcionales de CPE en prod con la nueva representada (iterar plantas/rangos/metodos para ubicar la CPE esperada `00002-00012419`).

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Prueba puntual adicional en prod para planta `20219` solicitada por el usuario, manteniendo `cuitRepresentada=30547090523` y TA forzado.
- Evidencia: `output/prod_test_planta20219_20260304_20260305.json` con `tax_id_auth=30547090523`, `cuit_representada=30547090523`, `fechaPartida=2026-03-04` y respuesta `HTTP 200` con `codigo 800` (sin solicitudes para parametros indicados).
- Siguiente accion: Probar metodo alternativo (`consultarCPEAutomotor`) o ampliar fechas en ventanas de 3 dias para detectar la CPE esperada.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Verificacion de la CPE puntual `00002-00012419` con metodo alternativo `consultarCPEAutomotor` en prod.
- Evidencia: `output/prod_consultarCPEAutomotor_00002_00012419_20260305_163335.json` con `auth_http=200`, `request_http=200`, `tax_id=30547090523`, `cuit_representada=30547090523`; la respuesta devuelve la carta (`tipoCartaPorte=74`, `sucursal=2`, `nroOrden=12419`, `nroCTG=10229887213`, origen `planta=20219`, destino `planta=518477`) y `pdf` en base64.
- Siguiente accion: Mantener `consultarCPEAutomotor` como metodo de contraste/recupero por identificador de carta cuando `consultarCPEPorDestino` responda `codigo 800`.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Implementacion de script de barrido en prod por `consultarCPEAutomotor` para recuperar cartas de los ultimos N dias (sin depender de `consultarCPEPorDestino`).
- Evidencia: Nuevo script `scripts/prod_consultar_cpe_ultimos_dias.py`; corrida `--days 3 --tipo 74 --sucursal 2 --scan-limit 200 --force-create-ta` con salida `output/prod_consultarCPEAutomotor_ultimos3dias_tipo74_suc2_20260305.json` y resumen `RANGE=2026-03-03..2026-03-05 ULT_NRO=12425 SCANNED=38 MATCHES=18` (incluye `nroOrden 12419`).
- Siguiente accion: Explotar el JSON generado para analisis operativo y, si se requiere, exportar a CSV con campos clave (nroOrden, fecha, estado, origen/destino, CTG).

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Confirmacion funcional de alcance de metodos para separar `emitidas` vs `recibidas`.
- Evidencia: Prueba de `consultarCPEAutomotor` para `nroOrden=12419` variando `cuitSolicitante`: con `30547090523` devuelve la carta (`HTTP 200`), con `30709590894` y `30546689979` devuelve `codigo 800` (sin solicitudes), demostrando que el metodo responde por emisor/solicitante y no por receptor.
- Siguiente accion: Para `recibidas`, usar `consultarCPEPorDestino` (calidad de destino) con plantas de destino propias y ventana maxima de 3 dias; opcionalmente complementar con `consultarCPEPendientesDeResolucion`.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Ejecucion de consulta de CPE recibidas (ultimos 3 dias) por `consultarCPEPorDestino` y correccion de robustez del script ante `errores=null`.
- Evidencia: `scripts/prod_consultar_cpe_por_destino.py` ajustado para no fallar al imprimir codigos de error cuando `respuesta.errores` es `null`; corrida `--force-create-ta --plants 20217,20218,20219,519447,700011 --from-date 2026-03-03 --to-date 2026-03-05` en `output/prod_recibidas_por_destino_ult3dias_plantas_conocidas_20260305.json`: planta `20219` devolvio 5 cartas (`HTTP 200` sin codigo de error) y el resto `codigo 800`.
- Siguiente accion: Enriquecer esas 5 recibidas con detalle adicional (si se requiere) y confirmar si las plantas de destino objetivo del negocio son solo `20219` o existe una lista adicional.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Consulta puntual de detalle para CTG recibido `10129907277` y validacion de limites de busqueda por CTG en `consultarCPEAutomotor`.
- Evidencia: En `output/prod_recibidas_por_destino_ult3dias_plantas_conocidas_20260305.json`, el registro CTG `10129907277` devuelve `tipoCartaPorte=74`, `fechaPartida=2026-03-05T11:08:31.000Z`, `estado=AC`, `fechaUltimaModificacion=2026-03-05T10:53:31.000Z`. Se valido posteriormente que `consultarCPEAutomotor` si permite buscar por `nroCTG` a nivel raiz de `solicitud` (no dentro de `cartaPorte`), con ejemplo exitoso para `10129920861` en `output/prod_consultarCPEAutomotor_ctg_10129920861_20260305.json`.
- Siguiente accion: Para detalle extendido de recibidas/confirmadas, consultar por `nroCTG` (raiz `solicitud.nroCTG`) en batch.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Se agrego filtrado por estado en `consultarCPEPorDestino` para traer recibidas por conjunto de estados (ej. `AC,CF,CO,CN`).
- Evidencia: `scripts/prod_consultar_cpe_por_destino.py` actualizado con flag `--include-statuses`; corrida `--include-statuses AC,CF,CO,CN --force-create-ta --plants 20217,20218,20219,519447,700011 --from-date 2026-03-03 --to-date 2026-03-05` en `output/prod_recibidas_estados_AC_CF_CO_CN_ult3dias_20260305.json` devolvio `TOTAL_CARTAS_FILTERED=5`, todas en estado `AC` (planta `20219`), sin `CF/CO/CN` en esa ventana.
- Siguiente accion: Si se requieren `CF/CO/CN`, ampliar el horizonte temporal iterando ventanas de 3 dias o consultar pendientes de resolucion por perfil para capturar no confirmadas.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Barrido extendido de recibidas en prod para validar presencia de estados `CF/CO/CN` mas alla de la ventana de 3 dias.
- Evidencia: Scan de 30 dias (`2026-02-04` a `2026-03-05`) en ventanas de 3 dias sobre plantas `20217,20218,20219,519447,700011` guardado en `output/prod_recibidas_status_scan_30dias_20260305.json`; acumulado de estados: `{'AC': 5}` (sin ocurrencias de `CF`, `CO` ni `CN` en el periodo barrido).
- Siguiente accion: Para detectar `CF/CO/CN`, ampliar barrido historico o incorporar consulta `consultarCPEPendientesDeResolucion` con perfiles operativos correspondientes.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Validacion del caso reportado de confirmadas no visibles por `consultarCPEPorDestino` y alta de script para consultar por lista de `nroCTG`.
- Evidencia: Corrida `consultarCPEPorDestino` en planta `20219` y fecha `2026-03-05` (`output/prod_recibidas_all_planta20219_20260305.json`) devolvio 4 cartas, todas `AC`, sin incluir `10129920861`; corrida del nuevo script `scripts/prod_consultar_cpe_por_ctg.py` con `--ctgs 10129920861` (`output/prod_consultarCPEAutomotor_ctg_10129920861_20260305.json`) devolvio `HTTP 200`, `estado=CN`, `tipo=74`, `sucursal=0`, `nroOrden=13`.
- Siguiente accion: Cargar la lista de 12 CTG confirmadas y consultarlas en batch con `scripts/prod_consultar_cpe_por_ctg.py` para obtener detalle completo (estado, origen, destino, fechas) sin depender de `consultarCPEPorDestino`.

- Fecha: 2026-03-05
- Paso: 7
- Cambios: Creacion de bitacora operativa nueva para control de CTG recibidas con actualizacion automatica.
- Evidencia: Nuevo script `scripts/prod_actualizar_bitacora_ctg_recibidas.py` (consulta `consultarCPEPorDestino` + enriquecimiento por `consultarCPEAutomotor(nroCTG)` + persistencia de catalogo historico); corridas en `output/prod_bitacora_ctg_recibidas_run_20260305_173725.json`, `output/prod_bitacora_ctg_recibidas_run_20260305_173831.json` y `output/prod_bitacora_ctg_recibidas_run_20260305_174132.json`; catalogo historico en `output/ctg_recibidas_catalogo.json`; bitacora legible en `docs/bitacora-ctg-recibidas.md`. En la ultima corrida con `--seed-ctgs 10129907121,10129920861` se consolidaron 6 CTG (4 `AC` + 2 `CN`).
- Siguiente accion: Ejecutar la actualizacion de bitacora de forma periodica (ej. cada 30/60 min en horario operativo) y seguir inyectando con `--seed-ctgs` las CTG visibles en ARCA que aun no aparezcan por `consultarCPEPorDestino`.

- Fecha: 2026-03-06
- Paso: general
- Cambios: Documentacion de backlog tecnico en archivos separados: metodos adicionales de `wscpe` y propuestas de otros servicios AFIP SDK para pyme agro (incluyendo facturacion, validacion de comprobantes, padron y descarga de comprobantes).
- Evidencia: Nuevos archivos `docs/metodos-wscpe-a-explotar.md` y `docs/propuestas-afipsdk-pyme-agro.md`; actualizacion de evidencia en `docs/step-by-step.md` (Nota adicional 5 del Paso 7).
- Siguiente accion: Priorizar el primer bloque de integracion (catalogos `wscpe` + consulta/reconciliacion en `wsfe` + descarga por `mis-comprobantes`) y definir scripts de prueba por servicio.

- Fecha: 2026-03-12
- Paso: 7
- Cambios: Corrida operativa solicitada por el usuario para revisar cartas de porte de los ultimos 3 dias en prod, usando barrido por `consultarCPEAutomotor`.
- Evidencia: Comando `py -3 scripts/prod_consultar_cpe_ultimos_dias.py --days 3 --tipo 74 --sucursal 2 --force-create-ta`; salida `output/prod_consultarCPEAutomotor_ultimos3dias_20260312_180930.json`; resumen `RANGE=2026-03-10..2026-03-12 ULT_NRO=12439 SCANNED=24 MATCHES=4` (nros 12436,12437,12438,12439 con estados CN/CF).
- Siguiente accion: Si se necesita detalle puntual por carta/CTG, correr `scripts/prod_consultar_cpe_por_ctg.py` sobre los CTG encontrados para ampliar trazabilidad operativa.

- Fecha: 2026-03-12
- Paso: 7
- Cambios: Mejora de prolijidad documental con bitacora CTG recibidas versionada en markdown por corrida, manteniendo archivo actual + copia timestamp.
- Evidencia: `scripts/prod_actualizar_bitacora_ctg_recibidas.py` actualizado con `--versioned-dir` y `--skip-versioned-bitacora`; `README.md` actualizado con uso. Corrida de validacion `py -3 scripts/prod_actualizar_bitacora_ctg_recibidas.py --env-file .env.prod --fallback-env-file .env --days 3 --force-create-ta` genero `output/prod_bitacora_ctg_recibidas_run_20260312_181402.json`, actualizo `docs/bitacora-ctg-recibidas.md` y creo `docs/bitacora-ctg-recibidas-versiones/bitacora-ctg-recibidas_20260312_181402.md` (`CTG_DETECTED=3`, `NEW=3`, `STATUS={'AC': 3}`).
- Siguiente accion: Seguir ejecutando la bitacora periodicamente para mantener el catalogo vivo y sumar versiones markdown por corrida para auditoria operativa.

- Fecha: 2026-03-12
- Paso: general
- Cambios: Rollback completo de Context7 por decision del usuario (cita textual: "es una poronga y encima hay que pagar para conseguir la API key").
- Evidencia: Eliminados `scripts/prod_corrida_completa_context7.py`, `context7.json` y carpeta `context7/`; removidas variables `CONTEXT7_*` de `.env.example` y `.env.prod`; limpieza de referencias en `README.md`, `AGENTS.md` y `docs/step-by-step.md`.
- Siguiente accion: Continuar operacion con el flujo actual de scripts AFIP/ARCA sin integracion Context7.

- Fecha: 2026-03-12
- Paso: general
- Cambios: Migracion tecnica a backend ARCA directo completada para `wscpe` (Hitos 1..5): baseline congelado, core `src/arca` (`WSAA + SOAP + wscpe`), scripts operativos migrados, pruebas unitarias base y actualizacion documental (README/AGENTS/checklist/step-by-step).
- Evidencia: `docs/wscpe-compatibilidad-parcial.md`, `output/baseline/`, `src/arca/**`, `scripts/wscpe_dummy.py`, `scripts/wscpe_consultar_ult_nro_orden.py`, `scripts/prod_consultar_cpe_por_destino.py`, `scripts/prod_consultar_cpe_por_ctg.py`, `scripts/prod_consultar_cpe_ultimos_dias.py`, `scripts/prod_actualizar_bitacora_ctg_recibidas.py`, `tests/unit/*`, `output/wscpe_dummy_20260312_225227.json`, `output/wscpe_consultarUltNroOrden_20260312_225311.json`, `output/prod_consultarCPEAutomotor_porCTG_20260312_225320.json`, `output/prod_consultarCPEPorDestino_20260312_225427.json`, `output/prod_consultarCPEAutomotor_ultimos3dias_20260312_225438.json`, `output/prod_bitacora_ctg_recibidas_run_20260312_225446.json`.
- Siguiente accion: Ejecutar gate manual ARCA por ambiente con `docs/arca-reonboarding-checklist.md` (relaciones/certificados), y luego correr regresion diaria comparando contra `output/baseline/`.

- Fecha: 2026-03-12
- Paso: general
- Cambios: Corrida de regresion estructural baseline vs backend ARCA directo para los 4 flujos (`dummy`, `ultNro`, `porCTG`, `porDestino`).
- Evidencia: `output/homologacion/regresion_baseline_20260312.txt` (todos los checks de campos obligatorios en estado `OK`).
- Siguiente accion: Completar validaciones funcionales de negocio por ambiente usando `docs/arca-reonboarding-checklist.md`.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Se creo `docs/step-by-step-cpe-dev.md` con flujo DEV detallado (ARCA manual + emitidas/recibidas + troubleshooting + checklist) y se estandarizo naming de salidas por corrida en scripts (`run_id`, `ws_suffix`, `output_file_pattern` y carpeta `output/runs/YYYY/MM/DD/run_<timestamp>`).
- Evidencia: `docs/step-by-step-cpe-dev.md`, `scripts/_arca_runtime.py`, `scripts/wscpe_dummy.py`, `scripts/wscpe_consultar_ult_nro_orden.py`, `scripts/prod_consultar_cpe_por_destino.py`, `scripts/prod_consultar_cpe_por_ctg.py`, `scripts/prod_consultar_cpe_ultimos_dias.py`, `scripts/prod_actualizar_bitacora_ctg_recibidas.py`, `README.md`, `docs/step-by-step.md`.
- Siguiente accion: Ejecutar corridas DEV y validar que los nombres cumplan `<proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>` y registrar evidencia funcional.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Validacion funcional post-estandarizacion de naming en scripts ARCA directo.
- Evidencia: `output/runs/2026/03/13/run_20260313_093044/wscpe_dummy_20260313_093044_cpe.json`, `output/runs/2026/03/13/run_20260313_093044/wscpe_consultarUltNroOrden_20260313_093044_cpe.json`, `output/runs/2026/03/13/run_20260313_093056/prod_consultarCPEPorDestino_20260313_093056_cpe.json`, `output/runs/2026/03/13/run_20260313_093056/prod_consultarCPEAutomotor_porCTG_20260313_093056_cpe.json`, `output/runs/2026/03/13/run_20260313_093112/prod_consultarCPEAutomotor_ultimos3dias_20260313_093112_cpe.json`, `output/runs/2026/03/13/run_20260313_093107/prod_bitacora_ctg_recibidas_run_20260313_093107_cpe.json`.
- Siguiente accion: Ejecutar el nuevo `docs/step-by-step-cpe-dev.md` completo en homologacion y registrar bloqueos ARCA si aparecieran.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Generacion local de nuevo par criptografico (`key + CSR`) para homologacion ARCA del CUIT DEV, para autenticacion WSAA sin dependencia de AfipSDK.
- Evidencia: `certs/cuit_20049687495_wscpe_dev_20260313.key`, `certs/cuit_20049687495_wscpe_dev_20260313.csr`; verificacion de subject con `certutil -dump` (`SERIALNUMBER=CUIT 20049687495`, `CN=wscpe-dev`, `O=Eduardo Beraza`, `C=AR`).
- Siguiente accion: Subir el CSR en ARCA homologacion, descargar el CRT emitido, actualizar `.env` (`AFIP_CERT_PATH`/`AFIP_KEY_PATH`) y validar TA con `--force-create-ta`.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Habilitacion de OpenSSL en entorno local Windows sin instalar paquetes externos, reutilizando binario provisto por Git for Windows y agregando `C:\\Program Files\\Git\\mingw64\\bin` al `PATH` de usuario.
- Evidencia: `openssl version` => `OpenSSL 3.2.4 11 Feb 2025 (Library: OpenSSL 3.2.4 11 Feb 2025)`.
- Siguiente accion: Usar OpenSSL para validaciones de `CRT/KEY/CSR` durante onboarding ARCA y troubleshooting de WSAA.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Inicializacion de versionado Git local (`git init`) para el repo ARCA y ajuste de `.gitignore` para excluir carpeta temporal `_tmp_context7_repo_*`.
- Evidencia: `git init` creo `.git/` en `D:\\OneDrive - Grupo Eduardo Beraza\\Desktop\\cartas_de_porte`; `git status --short` confirmo estructura inicial a versionar sin secretos (`.env`, `.env.prod`, `certs/*`, `.arca-ta-cache/*` y `output/*` siguen ignorados).
- Siguiente accion: Crear commit inicial y vincular `origin` para primer push.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Cierre del arranque de versionado con commit raiz y normalizacion de rama principal a `main`.
- Evidencia: `git commit` genero `d51d0c3` (`59 files changed, 3863 insertions`); `git branch --show-current` devuelve `main`; `git status --short` sin cambios pendientes.
- Siguiente accion: Configurar `origin` y ejecutar `git push -u origin main`.

- Fecha: 2026-03-13
- Paso: general
- Cambios: Intento de alta automatica de remoto GitHub para proyecto nuevo y validacion de prerequisitos de credenciales desde terminal.
- Evidencia: `gh` no esta instalado; variables `GITHUB_TOKEN/GH_TOKEN` no configuradas; `git credential-manager get` para `github.com` devuelve `NOT_FOUND`; intentos de `git credential-manager github login --device` sin credencial persistida en esta sesion.
- Siguiente accion: Obtener autenticacion GitHub valida (PAT o login interactivo), crear repo remoto `cartas_de_porte`, setear `origin` y ejecutar `git push -u origin main`.
