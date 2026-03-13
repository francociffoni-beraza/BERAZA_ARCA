# ARCA Re-Onboarding Checklist

Fecha ultima actualizacion: 2026-03-12

## 1) Identidad
- [ ] CUIT integrador confirmado (`AFIP_CUIT`):
- [ ] CUIT representada confirmada (`AFIP_CUIT_REPRESENTADA`):
- [ ] Ambiente validado (`dev`/`prod`):
- [ ] Responsable tecnico identificado:

## 2) Certificados
- [ ] Certificado homologacion vigente (X.509):
- [ ] Certificado produccion vigente (X.509):
- [ ] Key privada asociada verificada:
- [ ] Fecha de emision registrada:
- [ ] Fecha de vencimiento registrada:
- [ ] Procedimiento de rotacion documentado:

## 3) Relaciones y autorizaciones
- [ ] Servicio `ws://wscpe` asociado al certificado correcto en ARCA.
- [ ] Relacion de representacion activa para CUIT operativa.
- [ ] Evidencia de alta/renovacion guardada (captura, ID, fecha).
- [ ] Responsable de alta identificado.

## 4) Validaciones tecnicas minimas
- [ ] `WSAA loginCms` devuelve TA valido.
- [ ] Cache TA funciona (`ARCA_TA_CACHE_DIR`) y `--force-create-ta` regenera.
- [ ] `wscpe_dummy.py` devuelve `appserver/authserver/dbserver=Ok`.
- [ ] `wscpe_consultar_ult_nro_orden.py` responde sin fault tecnico.
- [ ] `prod_consultar_cpe_por_ctg.py` responde con caso valido.
- [ ] `prod_consultar_cpe_por_destino.py` responde con rango/planta validos.

## 5) Evidencias obligatorias
- [ ] XML request sanitizado (sin token/sign) guardado cuando aplica.
- [ ] XML/JSON response sanitizada guardada cuando aplica.
- [ ] Salida JSON final por corrida guardada en `output/`.
- [ ] Entrada registrada en `docs/work-log.md`.
- [ ] Nota de estado agregada en `docs/step-by-step.md` (historico/transicion).

## 6) Gate de avance a nuevos servicios
- [ ] Paridad operativa de `wscpe` confirmada (corridas diarias estables).
- [ ] Incidentes abiertos de WSAA/SOAP cerrados.
- [ ] Recién con esto habilitar fase 2 (`wsfe`, `wscdc`, padron).
