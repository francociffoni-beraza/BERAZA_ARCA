from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigError


TESTING_ALIASES = {"dev", "testing", "test", "homo", "homologacion", "homologación", "qa"}
PROD_ALIASES = {"prod", "production", "prd"}

DEFAULT_WSAA_URL = {
    "testing": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms",
    "production": "https://wsaa.afip.gov.ar/ws/services/LoginCms",
}

DEFAULT_WSCPE_URL = {
    "testing": "https://cpea-ws-qaext.afip.gob.ar/wscpe/services/soap",
    "production": "https://cpea-ws.afip.gob.ar/wscpe/services/soap",
}


@dataclass(frozen=True)
class ArcaSettings:
    environment: str
    wsid: str
    cuit_auth: int
    cuit_representada: int
    cert_path: Path
    key_path: Path
    wsaa_url: str
    wscpe_url: str
    timeout_seconds: int
    verify_tls: bool
    ta_cache_dir: Path



def read_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip().lstrip("\ufeff")] = value.strip()
    return data



def merge_env(primary: dict[str, str], fallback: dict[str, str] | None = None) -> dict[str, str]:
    out = dict(fallback or {})
    out.update(primary)
    return out



def parse_bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise ConfigError(f"Boolean value not valid: {value}")



def normalize_environment(raw_value: str) -> str:
    v = (raw_value or "").strip().lower()
    if v in TESTING_ALIASES:
        return "testing"
    if v in PROD_ALIASES:
        return "production"
    raise ConfigError(f"AFIP_ENV/ARCA_ENV not valid: {raw_value}")



def _require_int(data: dict[str, str], key: str) -> int:
    value = (data.get(key) or "").strip()
    if not value:
        raise ConfigError(f"Missing required variable: {key}")
    if not value.isdigit():
        raise ConfigError(f"{key} must be numeric")
    return int(value)



def _require_path(data: dict[str, str], key: str) -> Path:
    value = (data.get(key) or "").strip()
    if not value:
        raise ConfigError(f"Missing required variable: {key}")
    path = Path(value)
    if not path.exists():
        raise ConfigError(f"{key} does not exist: {value}")
    return path



def load_settings(env: dict[str, str]) -> ArcaSettings:
    raw_env = env.get("ARCA_ENV") or env.get("AFIP_ENV") or "prod"
    environment = normalize_environment(raw_env)

    wsid = (env.get("AFIP_WSID") or "wscpe").strip() or "wscpe"
    cuit_auth = _require_int(env, "AFIP_CUIT")
    cuit_representada_raw = (env.get("AFIP_CUIT_REPRESENTADA") or "").strip()
    if not cuit_representada_raw:
        cuit_representada = cuit_auth
    elif not cuit_representada_raw.isdigit():
        raise ConfigError("AFIP_CUIT_REPRESENTADA must be numeric")
    else:
        cuit_representada = int(cuit_representada_raw)
    cert_path = _require_path(env, "AFIP_CERT_PATH")
    key_path = _require_path(env, "AFIP_KEY_PATH")

    wsaa_url = (env.get("ARCA_WSAA_URL") or "").strip() or DEFAULT_WSAA_URL[environment]
    wscpe_url = (env.get("ARCA_WSCPE_URL") or "").strip() or DEFAULT_WSCPE_URL[environment]

    timeout_raw = (env.get("ARCA_TIMEOUT_SECONDS") or "90").strip()
    if not timeout_raw.isdigit() or int(timeout_raw) <= 0:
        raise ConfigError("ARCA_TIMEOUT_SECONDS must be a positive integer")

    verify_tls = parse_bool(env.get("ARCA_VERIFY_TLS"), True)
    ta_cache_dir = Path((env.get("ARCA_TA_CACHE_DIR") or ".arca-ta-cache").strip() or ".arca-ta-cache")

    return ArcaSettings(
        environment=environment,
        wsid=wsid,
        cuit_auth=cuit_auth,
        cuit_representada=cuit_representada,
        cert_path=cert_path,
        key_path=key_path,
        wsaa_url=wsaa_url,
        wscpe_url=wscpe_url,
        timeout_seconds=int(timeout_raw),
        verify_tls=verify_tls,
        ta_cache_dir=ta_cache_dir,
    )



def load_settings_from_files(env_file: Path, fallback_file: Path | None = None) -> tuple[ArcaSettings, dict[str, str]]:
    if not env_file.exists():
        raise ConfigError(f"Missing env file: {env_file}")
    primary = read_env_file(env_file)
    fallback = read_env_file(fallback_file) if fallback_file and fallback_file.exists() else {}
    merged = merge_env(primary, fallback)
    return load_settings(merged), merged
