# cartas_de_porte

Integracion ARCA directa para Carta de Porte (`wscpe`) con backend propio en Python (`WSAA + SOAP`) y foco en paridad operativa.

## Arquitectura vigente
- `src/arca/wsaa`: TRA, firma CMS/PKCS7, `loginCms`, parse TA.
- `src/arca/cache`: cache local de TA por `ambiente/servicio/cuit`.
- `src/arca/soap`: envelope, transporte, parseo de fault, retries.
- `src/arca/services/wscpe.py`: adapter de negocio (`dummy`, `consultarUltNroOrden`, `consultarCPEAutomotor`, `consultarCPEPorDestino`).
- `scripts/`: CLI operativas con contrato compatible.

## Requisitos
- Python 3.11+
- Dependencias: `requests`, `cryptography`
- Certificado y key ARCA activos para el CUIT de autenticacion.

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

Nota: `AFIPSDK_ACCESS_TOKEN` queda solo como variable legacy de regresion; no es requerida para operacion diaria.

## Comandos principales
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
- Fase 1 (`wscpe` directo) implementada en codigo.
- Dependencias manuales ARCA (altas/relaciones/certificados) se gestionan por checklist.
- Fase 2 (`wsfe`, `wscdc`, padron) queda para despues de consolidar paridad operativa diaria.
