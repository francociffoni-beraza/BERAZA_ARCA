#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone

from _arca_runtime import build_output_naming, extract_first_error, load_wscpe_service



def parse_ws_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Barrido WSCPE PROD por consultarCPEAutomotor en los ultimos N dias."
    )
    parser.add_argument("--env-file", default=".env.prod")
    parser.add_argument("--fallback-env-file", default=".env")
    parser.add_argument("--tipo", type=int, default=74)
    parser.add_argument("--sucursal", type=int, default=2)
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--scan-limit", type=int, default=300)
    parser.add_argument(
        "--stop-after-older-streak",
        type=int,
        default=20,
        help="Corta el barrido tras N cartas consecutivas mas viejas que la ventana.",
    )
    parser.add_argument(
        "--force-create-ta",
        action="store_true",
        help="Forza creacion de TA nuevo en WSAA local.",
    )
    parser.add_argument("--output-file")
    args = parser.parse_args()

    if args.days < 1:
        raise SystemExit("--days debe ser >= 1")
    if args.scan_limit < 1:
        raise SystemExit("--scan-limit debe ser >= 1")

    settings, merged, service = load_wscpe_service(args.env_file, args.fallback_env_file)

    ult_body, ta_source, ta_expiration = service.consultar_ult_nro_orden(
        sucursal=args.sucursal,
        tipo_cpe=args.tipo,
        force_ta=bool(args.force_create_ta),
    )

    ult_nro = int((ult_body.get("respuesta") or {}).get("nroOrden") or 0)
    if ult_nro <= 0:
        raise SystemExit(
            f"consultarUltNroOrden devolvio nroOrden={ult_nro} para sucursal={args.sucursal}, tipo={args.tipo}"
        )

    to_date = date.today()
    from_date = to_date - timedelta(days=args.days - 1)

    start_nro = max(1, ult_nro - args.scan_limit + 1)
    matches = []
    attempts = []
    older_streak = 0
    stopped_early = False

    for nro in range(ult_nro, start_nro - 1, -1):
        body, _, _ = service.consultar_cpe_automotor(
            cuit_solicitante=settings.cuit_representada,
            carta_porte={
                "tipoCPE": args.tipo,
                "sucursal": args.sucursal,
                "nroOrden": nro,
            },
            force_ta=False,
        )
        respuesta = body.get("respuesta") or {}
        cabecera = respuesta.get("cabecera") or {}

        err_code, err_desc = extract_first_error(body)
        row = {
            "nroOrden": nro,
            "http_status": 200,
            "ok": True,
            "error_code": err_code,
            "error_desc": err_desc,
        }

        fecha_emision_raw = cabecera.get("fechaEmision")
        if fecha_emision_raw:
            emision_dt = parse_ws_datetime(fecha_emision_raw)
            emision_date = emision_dt.date()
            row["fechaEmision"] = fecha_emision_raw
            row["estado"] = cabecera.get("estado")
            row["nroCTG"] = cabecera.get("nroCTG")
            row["origen_planta"] = (respuesta.get("origen") or {}).get("planta")
            row["destino_planta"] = (respuesta.get("destino") or {}).get("planta")
            row["cuit_origen"] = (respuesta.get("origen") or {}).get("cuit")

            if from_date <= emision_date <= to_date:
                clean_respuesta = dict(respuesta)
                if "pdf" in clean_respuesta:
                    clean_respuesta["pdf"] = "<omitted_base64_pdf>"
                matches.append(
                    {
                        "nroOrden": nro,
                        "fechaEmision": fecha_emision_raw,
                        "estado": cabecera.get("estado"),
                        "nroCTG": cabecera.get("nroCTG"),
                        "origen_planta": (respuesta.get("origen") or {}).get("planta"),
                        "destino_planta": (respuesta.get("destino") or {}).get("planta"),
                        "cuit_origen": (respuesta.get("origen") or {}).get("cuit"),
                        "cuit_destino": (respuesta.get("destino") or {}).get("cuit"),
                        "response": clean_respuesta,
                    }
                )
                older_streak = 0
            elif emision_date < from_date:
                older_streak += 1
            else:
                older_streak = 0
        attempts.append(row)

        if older_streak >= args.stop_after_older_streak:
            stopped_early = True
            break

    naming = build_output_naming(
        process_name=f"prod_consultarCPEAutomotor_ultimos{args.days}dias",
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
        "tipoCartaPorte": args.tipo,
        "sucursal": args.sucursal,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "days": args.days,
        "scan_limit": args.scan_limit,
        "stop_after_older_streak": args.stop_after_older_streak,
        "stopped_early": stopped_early,
        "force_create_ta": bool(args.force_create_ta),
        "ta_source": ta_source,
        "ta_expiration": ta_expiration,
        "ult_nro_orden": ult_nro,
        "scanned_from_nro": ult_nro,
        "scanned_to_nro": attempts[-1]["nroOrden"] if attempts else None,
        "attempts_count": len(attempts),
        "matches_count": len(matches),
        "matches": matches,
        "attempts": attempts,
        "note": "TA token/sign used in-memory only and persisted only in local cache.",
    }
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OUTPUT_FILE={output_path.as_posix()}")
    print(
        f"RANGE={from_date.isoformat()}..{to_date.isoformat()} "
        f"ULT_NRO={ult_nro} SCANNED={len(attempts)} MATCHES={len(matches)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
