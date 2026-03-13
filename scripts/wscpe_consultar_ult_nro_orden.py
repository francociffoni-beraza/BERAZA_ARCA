#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from _arca_runtime import build_output_naming, load_wscpe_service



def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta WSCPE consultarUltNroOrden via ARCA directo.")
    parser.add_argument("--env-file", default=".env.prod")
    parser.add_argument("--fallback-env-file", default=".env")
    parser.add_argument("--tipo", type=int, default=74)
    parser.add_argument("--sucursal", type=int, default=2)
    parser.add_argument("--force-create-ta", action="store_true")
    parser.add_argument("--output-file")
    args = parser.parse_args()

    settings, _, service = load_wscpe_service(args.env_file, args.fallback_env_file)
    body, ta_source, ta_expiration = service.consultar_ult_nro_orden(
        sucursal=args.sucursal,
        tipo_cpe=args.tipo,
        force_ta=bool(args.force_create_ta),
    )

    naming = build_output_naming(
        process_name="wscpe_consultarUltNroOrden",
        wsid=settings.wsid,
        extension="json",
        output_file=args.output_file,
    )
    output_path = naming.path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    out = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "environment": settings.environment,
        "method": "consultarUltNroOrden",
        "transport": "arca_direct",
        "run_id": naming.run_id,
        "ws_suffix": naming.ws_suffix,
        "output_file_pattern": naming.output_file_pattern,
        "tax_id_auth": str(settings.cuit_auth),
        "cuit_representada": str(settings.cuit_representada),
        "request_solicitud": {
            "sucursal": args.sucursal,
            "tipoCPE": args.tipo,
        },
        "http_status": 200,
        "ok": True,
        "body": body,
        "ta_source": ta_source,
        "ta_expiration": ta_expiration,
        "force_create_ta": bool(args.force_create_ta),
    }

    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    nro = ((body.get("respuesta") or {}).get("nroOrden") if isinstance(body, dict) else None)
    print(f"OUTPUT_FILE={output_path.as_posix()}")
    print(f"NRO_ORDEN={nro} TA_SOURCE={ta_source} FORCE={bool(args.force_create_ta)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
