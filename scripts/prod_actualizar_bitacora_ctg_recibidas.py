#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from _arca_runtime import (
    build_output_naming,
    build_run_id,
    extract_first_error,
    load_wscpe_service,
    normalize_cartas,
    resolve_ws_suffix,
)



def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()



def split_windows(from_date: date, to_date: date):
    windows = []
    cursor = from_date
    while cursor <= to_date:
        end = min(cursor + timedelta(days=2), to_date)
        windows.append((cursor, end))
        cursor = end + timedelta(days=1)
    return windows



def to_iso_now():
    return datetime.now(timezone.utc).isoformat()



def parse_ctg_seed_values(values_arg: str, file_arg: str):
    values = []
    if values_arg:
        values.extend([x.strip() for x in values_arg.split(",") if x.strip()])
    if file_arg:
        path = Path(file_arg)
        if not path.exists():
            raise SystemExit(f"Seed CTG file does not exist: {path}")
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            values.append(line)

    out = []
    seen = set()
    for value in values:
        if not value.isdigit():
            raise SystemExit(f"Seed CTG invalido (no numerico): {value}")
        ctg = int(value)
        if ctg <= 0:
            raise SystemExit(f"Seed CTG invalido (<=0): {value}")
        if ctg in seen:
            continue
        seen.add(ctg)
        out.append(ctg)
    return out



def fmt_md(value):
    if value is None:
        return "-"
    text = str(value).strip()
    return text if text else "-"



def choose_latest_timestamp(record: dict):
    candidates = [
        record.get("fechaInicioEstado"),
        record.get("fechaUltimaModificacion"),
        record.get("fechaPartida"),
        record.get("fechaEmision"),
    ]
    for value in candidates:
        if value:
            return value
    return None



def load_catalog(path: Path):
    if not path.exists():
        return {
            "created_at": to_iso_now(),
            "updated_at": None,
            "cuit_representada": None,
            "records": {},
            "runs": [],
        }
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "created_at": to_iso_now(),
            "updated_at": None,
            "cuit_representada": None,
            "records": {},
            "runs": [],
        }

    if "records" not in obj or not isinstance(obj.get("records"), dict):
        obj["records"] = {}
    if "runs" not in obj or not isinstance(obj.get("runs"), list):
        obj["runs"] = []
    if "created_at" not in obj:
        obj["created_at"] = to_iso_now()
    return obj



def render_markdown(
    *,
    run_at: str,
    from_date: date,
    to_date: date,
    plants: list[int],
    tipo: int,
    records_sorted: list[dict],
    run_summary: dict,
    runs: list[dict],
):
    lines = []
    lines.append("# Bitacora CTG Recibidas")
    lines.append("")
    lines.append(
        "Bitacora operativa para control de Cartas de Porte recibidas, actualizada en cada corrida automatica."
    )
    lines.append("")
    lines.append(f"- Ultima actualizacion: `{run_at}`")
    lines.append(f"- Ventana consultada: `{from_date.isoformat()}..{to_date.isoformat()}`")
    lines.append(f"- Plantas consultadas: `{','.join(str(x) for x in plants)}`")
    lines.append(f"- Tipo Carta de Porte: `{tipo}`")
    lines.append("")

    lines.append("## Resumen ultima corrida")
    lines.append("")
    lines.append(f"- CTG detectadas en la corrida: `{run_summary.get('detected_count', 0)}`")
    lines.append(f"- CTG nuevas en catalogo: `{run_summary.get('new_count', 0)}`")
    lines.append(f"- Estados detectados: `{run_summary.get('status_counts', {})}`")
    seed_ctgs = run_summary.get("seed_ctgs") or []
    if seed_ctgs:
        lines.append(f"- Seed manual aplicada: `{','.join(str(x) for x in seed_ctgs)}`")
    lines.append("")

    lines.append(f"## Catalogo vigente ({len(records_sorted)} CTG)")
    lines.append("")
    lines.append(
        "| CTG | Estado | Fecha emision | Inicio estado | Planta destino | CUIT origen | Primera vez | Ultima vez | Fuentes |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for rec in records_sorted:
        lines.append(
            "| "
            + " | ".join(
                [
                    fmt_md(rec.get("nroCTG")),
                    fmt_md(rec.get("estado")),
                    fmt_md(rec.get("fechaEmision")),
                    fmt_md(rec.get("fechaInicioEstado")),
                    fmt_md(rec.get("destino_planta")),
                    fmt_md(rec.get("origen_cuit")),
                    fmt_md(rec.get("first_seen_at")),
                    fmt_md(rec.get("last_seen_at")),
                    fmt_md(",".join(rec.get("sources", []))),
                ]
            )
            + " |"
        )
    if not records_sorted:
        lines.append("| - | - | - | - | - | - | - | - | - |")
    lines.append("")

    lines.append("## Historial corridas (ultimas 20)")
    lines.append("")
    for run in runs[-20:][::-1]:
        lines.append(
            "- "
            f"`{run.get('run_at')}` "
            f"ventana `{run.get('from_date')}..{run.get('to_date')}` "
            f"detectadas={run.get('detected_count', 0)} "
            f"nuevas={run.get('new_count', 0)} "
            f"estados={run.get('status_counts', {})}"
        )
    if not runs:
        lines.append("- Sin corridas registradas.")
    lines.append("")

    lines.append("## Nota")
    lines.append("")
    lines.append(
        "- Esta bitacora depende de `consultarCPEPorDestino` para detectar CTG y de `consultarCPEAutomotor` por `nroCTG` para enriquecer detalle."
    )
    lines.append(
        "- Si ARCA no expone alguna CTG en `consultarCPEPorDestino`, no podra incorporarse automaticamente hasta que aparezca en ese metodo o se consulte manualmente por `nroCTG`."
    )
    lines.append("")

    return "\n".join(lines)



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Actualiza bitacora de CTG recibidas en PROD (catalogo + markdown)."
    )
    parser.add_argument("--env-file", default=".env.prod")
    parser.add_argument("--fallback-env-file", default=".env")
    parser.add_argument("--plants", default="20217,20218,20219,519447,700011")
    parser.add_argument("--tipo", type=int, default=74)
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument(
        "--seed-ctgs",
        default="",
        help="CTG adicionales separadas por coma para enriquecer catalogo.",
    )
    parser.add_argument(
        "--seed-ctg-file",
        default="",
        help="Archivo con CTG adicionales (una por linea).",
    )
    parser.add_argument(
        "--force-create-ta",
        action="store_true",
        help="Forza la creacion de un TA nuevo en WSAA local.",
    )
    parser.add_argument(
        "--catalog-file",
        default="output/ctg_recibidas_catalogo.json",
    )
    parser.add_argument(
        "--bitacora-file",
        default="docs/bitacora-ctg-recibidas.md",
    )
    parser.add_argument(
        "--versioned-dir",
        default="docs/bitacora-ctg-recibidas-versiones",
        help="Directorio donde guardar copias versionadas de la bitacora markdown.",
    )
    parser.add_argument(
        "--skip-versioned-bitacora",
        action="store_true",
        help="No genera copia versionada de la bitacora markdown.",
    )
    parser.add_argument("--output-file")
    args = parser.parse_args()

    if args.days < 1:
        raise SystemExit("--days debe ser >= 1")

    settings, merged, service = load_wscpe_service(args.env_file, args.fallback_env_file)
    run_id = build_run_id()
    ws_suffix = resolve_ws_suffix(settings.wsid)

    plants = [int(p.strip()) for p in args.plants.split(",") if p.strip()]
    if not plants:
        raise SystemExit("No plants provided.")

    today = date.today()
    to_date = parse_date(args.to_date) if args.to_date else today
    from_date = (
        parse_date(args.from_date)
        if args.from_date
        else to_date - timedelta(days=args.days - 1)
    )
    if from_date > to_date:
        raise SystemExit("--from-date no puede ser mayor a --to-date")

    seed_ctgs = parse_ctg_seed_values(args.seed_ctgs, args.seed_ctg_file)

    windows = split_windows(from_date, to_date)
    por_destino_raw = []
    discovered = {}

    force_ta_next = bool(args.force_create_ta)
    ta_source = None
    ta_expiration = None

    for w_from, w_to in windows:
        for plant in plants:
            body, ta_source, ta_expiration = service.consultar_cpe_por_destino(
                planta=plant,
                fecha_partida_desde=w_from.isoformat(),
                fecha_partida_hasta=w_to.isoformat(),
                tipo_carta_porte=args.tipo,
                force_ta=force_ta_next,
            )
            force_ta_next = False

            err_code, err_desc = extract_first_error(body)
            cartas = normalize_cartas((body.get("respuesta") or {}).get("cartaPorte"))
            row = {
                "window_from": w_from.isoformat(),
                "window_to": w_to.isoformat(),
                "planta": plant,
                "http_status": 200,
                "ok": True,
                "error_code": err_code,
                "error_desc": err_desc,
                "cartas_count": len(cartas),
                "cartas": cartas,
            }
            por_destino_raw.append(row)

            for carta in cartas:
                nro = carta.get("nroCTG")
                if not nro:
                    continue
                ctg = int(nro)
                existing = discovered.get(ctg) or {}
                existing.update(
                    {
                        "nroCTG": ctg,
                        "estado_por_destino": carta.get("estado"),
                        "fechaPartida": carta.get("fechaPartida"),
                        "fechaUltimaModificacion": carta.get("fechaUltimaModificacion"),
                        "destino_planta": plant,
                        "source": "consultarCPEPorDestino",
                    }
                )
                discovered[ctg] = existing

    for seed_ctg in seed_ctgs:
        discovered.setdefault(
            seed_ctg,
            {
                "nroCTG": seed_ctg,
                "source": "seed_manual",
            },
        )

    ctgs = sorted(discovered.keys())
    detected_by_por_destino = {
        ctg
        for ctg, info in discovered.items()
        if (info or {}).get("source") == "consultarCPEPorDestino"
    }

    detailed_rows = []
    status_counts_run = {}
    for ctg in ctgs:
        source_hint = (discovered.get(ctg) or {}).get("source")
        source_methods = ["consultarCPEAutomotor(nroCTG)"]
        if source_hint == "consultarCPEPorDestino":
            source_methods.append("consultarCPEPorDestino")
        elif source_hint == "seed_manual":
            source_methods.append("seed_manual")

        body, ta_source, ta_expiration = service.consultar_cpe_automotor(
            nro_ctg=ctg,
            force_ta=force_ta_next,
        )
        force_ta_next = False

        respuesta = body.get("respuesta") or {}
        cabecera = respuesta.get("cabecera") or {}
        origen = respuesta.get("origen") or {}
        destino = respuesta.get("destino") or {}
        err_code, err_desc = extract_first_error(body)

        estado = (cabecera.get("estado") or "").strip().upper()
        if estado:
            status_counts_run[estado] = status_counts_run.get(estado, 0) + 1

        detailed = {
            "nroCTG": ctg,
            "http_status": 200,
            "ok": True,
            "error_code": err_code,
            "error_desc": err_desc,
            "tipoCartaPorte": cabecera.get("tipoCartaPorte"),
            "sucursal": cabecera.get("sucursal"),
            "nroOrden": cabecera.get("nroOrden"),
            "estado": cabecera.get("estado"),
            "fechaEmision": cabecera.get("fechaEmision"),
            "fechaInicioEstado": cabecera.get("fechaInicioEstado"),
            "fechaVencimiento": cabecera.get("fechaVencimiento"),
            "fechaPartida": discovered.get(ctg, {}).get("fechaPartida"),
            "fechaUltimaModificacion": discovered.get(ctg, {}).get("fechaUltimaModificacion"),
            "origen_cuit": origen.get("cuit"),
            "origen_planta": origen.get("planta"),
            "destino_cuit": destino.get("cuit"),
            "destino_planta": destino.get("planta") or discovered.get(ctg, {}).get("destino_planta"),
            "source_methods": source_methods,
        }
        detailed_rows.append(detailed)

    catalog_path = Path(args.catalog_file)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog(catalog_path)
    run_at = to_iso_now()

    records = catalog.get("records", {})
    new_count = 0
    for row in detailed_rows:
        key = str(row["nroCTG"])
        current = records.get(key)
        if current is None:
            new_count += 1
            current = {
                "nroCTG": row["nroCTG"],
                "first_seen_at": run_at,
                "last_seen_at": run_at,
                "seen_count": 0,
                "observed_statuses": {},
                "sources": [],
            }

        current["last_seen_at"] = run_at
        current["seen_count"] = int(current.get("seen_count") or 0) + 1

        estado = (row.get("estado") or "").strip().upper()
        observed_statuses = current.get("observed_statuses") or {}
        if estado:
            observed_statuses[estado] = int(observed_statuses.get(estado) or 0) + 1
        current["observed_statuses"] = observed_statuses

        sources = set(current.get("sources") or [])
        if row["nroCTG"] not in detected_by_por_destino and "seed_manual" in row.get("source_methods", []):
            sources.discard("consultarCPEPorDestino")
        for source in row.get("source_methods") or []:
            sources.add(source)
        current["sources"] = sorted(sources)

        for field in [
            "estado",
            "tipoCartaPorte",
            "sucursal",
            "nroOrden",
            "fechaEmision",
            "fechaInicioEstado",
            "fechaVencimiento",
            "fechaPartida",
            "fechaUltimaModificacion",
            "origen_cuit",
            "origen_planta",
            "destino_cuit",
            "destino_planta",
        ]:
            value = row.get(field)
            if value is not None:
                current[field] = value

        current["latest_reference_ts"] = choose_latest_timestamp(current)
        records[key] = current

    run_summary = {
        "run_at": run_at,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "plants": plants,
        "seed_ctgs": seed_ctgs,
        "detected_count": len(detailed_rows),
        "new_count": new_count,
        "status_counts": status_counts_run,
        "ctgs_detected": [row["nroCTG"] for row in detailed_rows],
    }
    runs = catalog.get("runs") or []
    runs.append(run_summary)
    runs = runs[-100:]

    catalog["updated_at"] = run_at
    catalog["cuit_representada"] = str(settings.cuit_representada)
    catalog["records"] = records
    catalog["runs"] = runs
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    records_sorted = sorted(
        records.values(),
        key=lambda x: (
            x.get("last_seen_at") or "",
            x.get("latest_reference_ts") or "",
            str(x.get("nroCTG") or ""),
        ),
        reverse=True,
    )

    bitacora_path = Path(args.bitacora_file)
    bitacora_path.parent.mkdir(parents=True, exist_ok=True)
    md = render_markdown(
        run_at=run_at,
        from_date=from_date,
        to_date=to_date,
        plants=plants,
        tipo=args.tipo,
        records_sorted=records_sorted,
        run_summary=run_summary,
        runs=runs,
    )
    bitacora_path.write_text(md, encoding="utf-8")

    versioned_bitacora_path = None
    if not args.skip_versioned_bitacora:
        versioned_dir = Path(args.versioned_dir)
        versioned_dir.mkdir(parents=True, exist_ok=True)
        versioned_bitacora_path = versioned_dir / f"bitacora-ctg-recibidas_{run_id}_{ws_suffix}.md"
        versioned_bitacora_path.write_text(md, encoding="utf-8")

    catalog_snapshot_naming = build_output_naming(
        process_name="ctg_recibidas_catalogo",
        wsid=settings.wsid,
        extension="json",
        run_id=run_id,
    )
    catalog_snapshot_path = catalog_snapshot_naming.path
    catalog_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_snapshot_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    snapshot = {
        "generated_at": run_at,
        "environment": merged.get("AFIP_ENV") or settings.environment,
        "wsid": settings.wsid,
        "transport": "arca_direct",
        "run_id": run_id,
        "ws_suffix": ws_suffix,
        "output_file_pattern": None,
        "tax_id_auth": str(settings.cuit_auth),
        "cuit_representada": str(settings.cuit_representada),
        "tipoCartaPorte": args.tipo,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "plants": plants,
        "windows": [{"from": a.isoformat(), "to": b.isoformat()} for a, b in windows],
        "ta_expiration": ta_expiration,
        "ta_source": ta_source,
        "force_create_ta": bool(args.force_create_ta),
        "por_destino_requests": por_destino_raw,
        "ctg_details": detailed_rows,
        "run_summary": run_summary,
        "catalog_file": catalog_path.as_posix(),
        "catalog_snapshot_file": catalog_snapshot_path.as_posix(),
        "bitacora_file": bitacora_path.as_posix(),
        "bitacora_versioned_file": (
            versioned_bitacora_path.as_posix() if versioned_bitacora_path else None
        ),
        "seed_ctgs": seed_ctgs,
    }
    output_naming = build_output_naming(
        process_name="prod_bitacora_ctg_recibidas_run",
        wsid=settings.wsid,
        extension="json",
        output_file=args.output_file,
        run_id=run_id,
    )
    snapshot["output_file_pattern"] = output_naming.output_file_pattern
    output_path = output_naming.path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OUTPUT_FILE={output_path.as_posix()}")
    print(f"CATALOG_FILE={catalog_path.as_posix()}")
    print(f"BITACORA_FILE={bitacora_path.as_posix()}")
    if versioned_bitacora_path:
        print(f"BITACORA_VERSIONED_FILE={versioned_bitacora_path.as_posix()}")
    print(
        f"RANGE={from_date.isoformat()}..{to_date.isoformat()} "
        f"CTG_DETECTED={len(detailed_rows)} NEW={new_count} STATUS={status_counts_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
