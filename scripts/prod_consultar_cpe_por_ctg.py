#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from _arca_runtime import build_output_naming, extract_first_error, load_wscpe_service



def parse_ctg_values(ctgs_arg: str, ctg_file: str):
    raw_values = []
    if ctgs_arg:
        raw_values.extend([x.strip() for x in ctgs_arg.split(",") if x.strip()])
    if ctg_file:
        path = Path(ctg_file)
        if not path.exists():
            raise SystemExit(f"CTG file does not exist: {path}")
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            raw_values.append(line)

    if not raw_values:
        raise SystemExit("Debes informar --ctgs o --ctg-file")

    seen = set()
    out = []
    for value in raw_values:
        if not value.isdigit():
            raise SystemExit(f"CTG invalido (no numerico): {value}")
        ctg = int(value)
        if ctg <= 0:
            raise SystemExit(f"CTG invalido (<=0): {value}")
        if ctg in seen:
            continue
        seen.add(ctg)
        out.append(ctg)
    return out



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consulta WSCPE PROD por lista de nroCTG (consultarCPEAutomotor)."
    )
    parser.add_argument("--env-file", default=".env.prod")
    parser.add_argument("--fallback-env-file", default=".env")
    parser.add_argument(
        "--ctgs",
        default="",
        help="Lista de CTG separada por comas (ej: 10129906706,10129920861).",
    )
    parser.add_argument(
        "--ctg-file",
        default="",
        help="Archivo con un CTG por linea.",
    )
    parser.add_argument(
        "--cuit-solicitante",
        default="",
        help="Opcional: CUIT solicitante para incluir en la solicitud.",
    )
    parser.add_argument(
        "--force-create-ta",
        action="store_true",
        help="Forza la creacion de un TA nuevo en WSAA local.",
    )
    parser.add_argument("--output-file")
    args = parser.parse_args()

    ctgs = parse_ctg_values(args.ctgs, args.ctg_file)
    settings, merged, service = load_wscpe_service(args.env_file, args.fallback_env_file)

    cuit_solicitante = None
    if args.cuit_solicitante:
        if not args.cuit_solicitante.isdigit():
            raise SystemExit("--cuit-solicitante debe ser numerico.")
        cuit_solicitante = int(args.cuit_solicitante)

    rows = []
    estado_totals = {}
    ta_source = None
    ta_expiration = None

    force_ta_next = bool(args.force_create_ta)
    for ctg in ctgs:
        body, ta_source, ta_expiration = service.consultar_cpe_automotor(
            cuit_solicitante=cuit_solicitante,
            nro_ctg=ctg,
            force_ta=force_ta_next,
        )
        force_ta_next = False
        respuesta = body.get("respuesta") or {}
        cabecera = respuesta.get("cabecera") or {}
        origen = respuesta.get("origen") or {}
        destino = respuesta.get("destino") or {}
        err_code, err_desc = extract_first_error(body)

        clean_body = body
        if "respuesta" in body:
            clean_body = dict(body)
            clean_respuesta = dict(respuesta)
            if "pdf" in clean_respuesta:
                clean_respuesta["pdf"] = "<omitted_base64_pdf>"
            clean_body["respuesta"] = clean_respuesta

        estado = (cabecera.get("estado") or "").strip().upper()
        if estado:
            estado_totals[estado] = estado_totals.get(estado, 0) + 1

        rows.append(
            {
                "ctg_query": ctg,
                "http_status": 200,
                "ok": True,
                "error_code": err_code,
                "error_desc": err_desc,
                "nroCTG_respuesta": cabecera.get("nroCTG"),
                "estado": cabecera.get("estado"),
                "tipoCartaPorte": cabecera.get("tipoCartaPorte"),
                "sucursal": cabecera.get("sucursal"),
                "nroOrden": cabecera.get("nroOrden"),
                "fechaEmision": cabecera.get("fechaEmision"),
                "fechaInicioEstado": cabecera.get("fechaInicioEstado"),
                "fechaVencimiento": cabecera.get("fechaVencimiento"),
                "origen_cuit": origen.get("cuit"),
                "origen_planta": origen.get("planta"),
                "destino_cuit": destino.get("cuit"),
                "destino_planta": destino.get("planta"),
                "body": clean_body,
            }
        )

    naming = build_output_naming(
        process_name="prod_consultarCPEAutomotor_porCTG",
        wsid=settings.wsid,
        extension="json",
        output_file=args.output_file,
    )
    output_path = naming.path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    out = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "environment": merged.get("AFIP_ENV") or settings.environment,
        "wsid": settings.wsid,
        "transport": "arca_direct",
        "run_id": naming.run_id,
        "ws_suffix": naming.ws_suffix,
        "output_file_pattern": naming.output_file_pattern,
        "tax_id_auth": str(settings.cuit_auth),
        "cuit_representada": str(settings.cuit_representada),
        "cuit_solicitante": cuit_solicitante,
        "ctgs_query": ctgs,
        "rows_count": len(rows),
        "status_totals": estado_totals,
        "ta_expiration": ta_expiration,
        "ta_source": ta_source,
        "force_create_ta": bool(args.force_create_ta),
        "rows": rows,
        "note": "TA token/sign used in-memory only and persisted only in local cache.",
    }
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OUTPUT_FILE={output_path.as_posix()}")
    for row in rows:
        print(
            f"CTG_QUERY={row['ctg_query']} HTTP={row['http_status']} "
            f"ESTADO={row.get('estado')} TIPO={row.get('tipoCartaPorte')} "
            f"SUC={row.get('sucursal')} NRO={row.get('nroOrden')} "
            f"FOUND_CTG={row.get('nroCTG_respuesta')} ERR={row.get('error_code')}"
        )
    print(f"ROWS={len(rows)} STATUS_TOTALS={estado_totals}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
