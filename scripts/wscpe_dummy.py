#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from _arca_runtime import build_output_naming, load_wscpe_service



def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test WSCPE dummy via ARCA directo.")
    parser.add_argument("--env-file", default=".env.prod")
    parser.add_argument("--fallback-env-file", default=".env")
    parser.add_argument("--output-file")
    args = parser.parse_args()

    settings, _, service = load_wscpe_service(args.env_file, args.fallback_env_file)
    body = service.dummy()

    naming = build_output_naming(
        process_name="wscpe_dummy",
        wsid=settings.wsid,
        extension="json",
        output_file=args.output_file,
    )
    output_path = naming.path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    out = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "environment": settings.environment,
        "method": "dummy",
        "transport": "arca_direct",
        "run_id": naming.run_id,
        "ws_suffix": naming.ws_suffix,
        "output_file_pattern": naming.output_file_pattern,
        "http_status": 200,
        "ok": True,
        "body": body,
    }
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    respuesta = body.get("respuesta") if isinstance(body, dict) else None
    print(f"OUTPUT_FILE={output_path.as_posix()}")
    print(
        "APP={0} AUTH={1} DB={2}".format(
            (respuesta or {}).get("appserver"),
            (respuesta or {}).get("authserver"),
            (respuesta or {}).get("dbserver"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
