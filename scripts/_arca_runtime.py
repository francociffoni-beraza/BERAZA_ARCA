from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from arca.config import load_settings_from_files  # noqa: E402
from arca.services.wscpe import WSCpeService  # noqa: E402


WS_SUFFIX_BY_WSID = {
    "wscpe": "cpe",
    "mis-comprobantes": "misComp",
    "wsfe": "facturas",
}


@dataclass(frozen=True)
class OutputNaming:
    path: Path
    run_id: str
    ws_suffix: str
    output_file_pattern: str



def build_run_id(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime("%Y%m%d_%H%M%S")



def resolve_ws_suffix(wsid: str) -> str:
    key = (wsid or "").strip().lower()
    if key in WS_SUFFIX_BY_WSID:
        return WS_SUFFIX_BY_WSID[key]
    sanitized = "".join(ch for ch in key if ch.isalnum())
    return sanitized or "ws"



def build_output_naming(
    *,
    process_name: str,
    wsid: str,
    extension: str = "json",
    output_file: str | None = None,
    base_output_dir: str = "output",
    run_id: str | None = None,
) -> OutputNaming:
    rid = run_id or build_run_id()
    ws_suffix = resolve_ws_suffix(wsid)
    ext = extension.lstrip(".")
    pattern = f"{process_name}_{rid}_{ws_suffix}.{ext}"

    if output_file:
        return OutputNaming(
            path=Path(output_file),
            run_id=rid,
            ws_suffix=ws_suffix,
            output_file_pattern=pattern,
        )

    year = rid[0:4]
    month = rid[4:6]
    day = rid[6:8]
    run_dir = Path(base_output_dir) / "runs" / year / month / day / f"run_{rid}"
    return OutputNaming(
        path=run_dir / pattern,
        run_id=rid,
        ws_suffix=ws_suffix,
        output_file_pattern=pattern,
    )



def load_wscpe_service(env_file: str, fallback_env_file: str | None = None):
    settings, merged = load_settings_from_files(
        env_file=Path(env_file),
        fallback_file=Path(fallback_env_file) if fallback_env_file else None,
    )
    return settings, merged, WSCpeService(settings)



def normalize_cartas(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []



def extract_first_error(body: dict):
    respuesta = (body or {}).get("respuesta") or {}
    errores = respuesta.get("errores") or {}
    err = errores.get("error")
    if isinstance(err, list) and err:
        item = err[0] if isinstance(err[0], dict) else {}
        return item.get("codigo"), item.get("descripcion")
    if isinstance(err, dict):
        return err.get("codigo"), err.get("descripcion")
    return None, None
