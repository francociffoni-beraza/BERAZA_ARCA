#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone

from _arca_runtime import build_output_naming, load_wscpe_service, normalize_cartas



def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consulta WSCPE PROD: consultarCPEPorDestino por planta."
    )
    parser.add_argument("--env-file", default=".env.prod")
    parser.add_argument("--fallback-env-file", default=".env")
    parser.add_argument("--plants", default="20217,20218,20219,519447,700011")
    parser.add_argument("--tipo", type=int, default=74)
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--output-file")
    parser.add_argument(
        "--include-statuses",
        default="",
        help="Filtra estados de cartaPorte (ej: AC,CF,CO,CN).",
    )
    parser.add_argument(
        "--force-create-ta",
        action="store_true",
        help="Forza la creacion de un TA nuevo en WSAA local.",
    )
    args = parser.parse_args()

    settings, merged, service = load_wscpe_service(args.env_file, args.fallback_env_file)

    plants = [int(p.strip()) for p in args.plants.split(",") if p.strip()]
    if not plants:
        raise SystemExit("No plants provided.")

    status_filter = {s.strip().upper() for s in args.include_statuses.split(",") if s.strip()}

    today = date.today()
    to_date = parse_date(args.to_date) if args.to_date else today
    from_date = parse_date(args.from_date) if args.from_date else to_date - timedelta(days=2)
    if (to_date - from_date).days > 2:
        raise SystemExit("Date range cannot exceed 3 days for consultarCPEPorDestino.")

    results = []
    total_raw_count = 0
    total_filtered_count = 0
    status_totals_raw = {}
    status_totals_filtered = {}
    ta_source = None
    ta_expiration = None

    force_ta_next = bool(args.force_create_ta)
    for plant in plants:
        body, ta_source, ta_expiration = service.consultar_cpe_por_destino(
            planta=plant,
            fecha_partida_desde=from_date.isoformat(),
            fecha_partida_hasta=to_date.isoformat(),
            tipo_carta_porte=args.tipo,
            force_ta=force_ta_next,
        )
        force_ta_next = False

        respuesta = (body or {}).get("respuesta") or {}
        cartas_raw = normalize_cartas(respuesta.get("cartaPorte"))
        cartas_filtered = cartas_raw
        if status_filter:
            cartas_filtered = [
                c
                for c in cartas_raw
                if (c.get("estado") or "").strip().upper() in status_filter
            ]

        raw_counts = {}
        for c in cartas_raw:
            st = (c.get("estado") or "").strip().upper()
            if not st:
                continue
            raw_counts[st] = raw_counts.get(st, 0) + 1
            status_totals_raw[st] = status_totals_raw.get(st, 0) + 1

        filtered_counts = {}
        for c in cartas_filtered:
            st = (c.get("estado") or "").strip().upper()
            if not st:
                continue
            filtered_counts[st] = filtered_counts.get(st, 0) + 1
            status_totals_filtered[st] = status_totals_filtered.get(st, 0) + 1

        total_raw_count += len(cartas_raw)
        total_filtered_count += len(cartas_filtered)

        body_out = body
        if status_filter and "respuesta" in body:
            body_out = dict(body)
            respuesta_out = dict(respuesta)
            respuesta_out["cartaPorte"] = cartas_filtered
            body_out["respuesta"] = respuesta_out

        resumen = {
            "planta": plant,
            "http_status": 200,
            "ok": True,
            "cartas_raw_count": len(cartas_raw),
            "cartas_filtered_count": len(cartas_filtered),
            "status_counts_raw": raw_counts,
            "status_counts_filtered": filtered_counts,
            "body": body_out,
        }
        results.append(resumen)

    naming = build_output_naming(
        process_name="prod_consultarCPEPorDestino",
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
        "fechaPartidaDesde": from_date.isoformat(),
        "fechaPartidaHasta": to_date.isoformat(),
        "plants": plants,
        "include_statuses": sorted(status_filter) if status_filter else None,
        "total_cartas_raw": total_raw_count,
        "total_cartas_filtered": total_filtered_count,
        "status_totals_raw": status_totals_raw,
        "status_totals_filtered": status_totals_filtered,
        "ta_expiration": ta_expiration,
        "ta_source": ta_source,
        "force_create_ta": bool(args.force_create_ta),
        "results": results,
        "note": "TA token/sign used in-memory only and persisted only in local cache.",
    }
    output_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"OUTPUT_FILE={output_path.as_posix()}")
    for row in results:
        err_code = None
        errores = (row.get("body", {}).get("respuesta") or {}).get("errores") or {}
        err = errores.get("error")
        if isinstance(err, list) and err:
            err_code = err[0].get("codigo")
        elif isinstance(err, dict):
            err_code = err.get("codigo")
        print(
            f"PLANTA={row['planta']} HTTP={row['http_status']} "
            f"CARTAS={row['cartas_filtered_count']} ERR={err_code}"
        )
    print(
        f"TOTAL_CARTAS_RAW={total_raw_count} "
        f"TOTAL_CARTAS_FILTERED={total_filtered_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
