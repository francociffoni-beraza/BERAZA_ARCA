# BERAZA_ARCA

Integracion ARCA directa con backend propio en Python (`WSAA + SOAP`) para el CUIT de Beraza, con foco en construir una base comun reusable por servicio y cerrar primero la paridad operativa de Carta de Porte (`wscpe`) como primer modulo productivo.

## Arquitectura vigente
- `src/arca/wsaa`: TRA, firma CMS/PKCS7, `loginCms`, parse TA.
- `src/arca/cache`: cache local de TA por `ambiente/servicio/cuit`.
- `src/arca/soap`: envelope, transporte, parseo de fault, retries.
- `src/arca/services/`: modulos de negocio por servicio ARCA montados sobre el core comun.
- `src/arca/services/wscpe.py`: primer modulo operativo (`dummy`, `consultarUltNroOrden`, `consultarCPEAutomotor`, `consultarCPEPorDestino`).
- `scripts/`: CLI operativas con contrato compatible y base reutilizable para nuevos servicios.

## Requisitos
- Python 3.11+
- Dependencias: `requests`, `cryptography`
- Certificado y key ARCA activos para el CUIT de autenticacion de Beraza.

## Configuracion
1. Copiar `.env.example` a `.env` o completar `.env.prod`.
2. Definir:
   - `AFIP_ENV` (`dev`/`prod`)
   - `AFIP_CUIT`, `AFIP_CUIT_REPRESENTADA`
   - `AFIP_CERT_PATH`, `AFIP_KEY_PATH`
3. Opcionales ARCA direct:
   - `ARCA_WSAA_URL`, `ARCA_WSCPE_URL`
   - `ARCA_TIMEOUT_SECONDS`, `ARCA_VERIFY_TLS`
   - `ARCA_TA_CACHE_DIR`

Nota: no se usa access token externo; la autenticacion diaria se resuelve con TA de WSAA (`token/sign`).

## Comandos principales
Los comandos vigentes corresponden al modulo `wscpe`, que hoy es el primer WIN operativo dentro de la integracion ARCA del CUIT de Beraza.

Smoke:
`py -3 scripts/wscpe_dummy.py --env-file .env.prod --fallback-env-file .env`

Ultimo nro de orden:
`py -3 scripts/wscpe_consultar_ult_nro_orden.py --env-file .env.prod --fallback-env-file .env --tipo 74 --sucursal 2 --force-create-ta`

Consulta por destino:
`py -3 scripts/prod_consultar_cpe_por_destino.py --env-file .env.prod --fallback-env-file .env --plants 20217,20218,20219,519447,700011 --from-date 2026-03-10 --to-date 2026-03-12 --force-create-ta`

Consulta por CTG:
`py -3 scripts/prod_consultar_cpe_por_ctg.py --env-file .env.prod --fallback-env-file .env --ctgs 10129920861`

Barrido ultimos dias:
`py -3 scripts/prod_consultar_cpe_ultimos_dias.py --env-file .env.prod --fallback-env-file .env --days 3 --tipo 74 --sucursal 2 --force-create-ta`

Actualizar bitacora CTG:
`py -3 scripts/prod_actualizar_bitacora_ctg_recibidas.py --env-file .env.prod --fallback-env-file .env --days 3 --force-create-ta`

## Baseline y regresion
- Baseline congelado: `output/baseline/`.
- Contrato de compatibilidad parcial: `docs/wscpe-compatibilidad-parcial.md`.
- Evidencia de homologacion/operacion: `output/`.
- Naming de datos por corrida: `<proceso>_<YYYYMMDD_HHMMSS>_<ws_sufijo>.<ext>` en `output/runs/YYYY/MM/DD/run_YYYYMMDD_HHMMSS/`.

## Documentacion operativa
- Reglas de colaboracion: `AGENTS.md`
- Bitacora obligatoria: `docs/work-log.md`
- Estado historico y transicion: `docs/step-by-step.md`
- Paso a paso DEV emitidas/recibidas: `docs/step-by-step-cpe-dev.md`
- Checklist de altas/certificados/validaciones: `docs/arca-reonboarding-checklist.md`
- Paso a paso manual ARCA para certificados nuevos: `docs/pasos-certificados-arca.md`

## Estado actual
- Existe un core transversal de integracion ARCA en codigo (`WSAA`, cache de TA, SOAP y estructura de servicios) para operar el CUIT de Beraza con backend propio.
- `wscpe` es el primer modulo implementado y el primer WIN operativo sobre esa base comun.
- Dependencias manuales ARCA (altas, relaciones, certificados y validaciones) se gestionan por checklist.
- La incorporacion de `wsfe`, `wscdc`, padron y otros servicios queda prevista sobre el mismo core, despues de consolidar la paridad operativa diaria de `wscpe`.
