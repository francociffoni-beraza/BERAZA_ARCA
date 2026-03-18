#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHAT_CONTEXT_DIR = Path("docs") / "chat-context"
LEGACY_FILE = "legacy_worklog.md"
CONTEXT_T_FILE = "context_t.md"
CONTEXT_T_MINUS_1_FILE = "context_t-1.md"
BOOTSTRAP_FILE = "bootstrap_prompt.md"

REDACTED = "[REDACTED]"
ALLOWED_STATUS = {"todo", "in_progress", "done", "blocked"}
OPEN_STATUS = {"todo", "in_progress", "blocked"}
CHECKBOX_BY_STATUS = {
    "todo": "[ ]",
    "in_progress": "[-]",
    "done": "[x]",
    "blocked": "[!]",
}
INTERNAL_SNAPSHOT_RE = re.compile(
    r"## Internal Snapshot\s*```json\s*([\s\S]*?)\s*```",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class ContextPaths:
    base_dir: Path
    legacy_file: Path
    context_t_file: Path
    context_t_minus_1_file: Path
    bootstrap_file: Path


def resolve_paths(project_root: Path) -> ContextPaths:
    base_dir = project_root / CHAT_CONTEXT_DIR
    return ContextPaths(
        base_dir=base_dir,
        legacy_file=base_dir / LEGACY_FILE,
        context_t_file=base_dir / CONTEXT_T_FILE,
        context_t_minus_1_file=base_dir / CONTEXT_T_MINUS_1_FILE,
        bootstrap_file=base_dir / BOOTSTRAP_FILE,
    )


def run_git(project_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def sanitize_text(value: str) -> str:
    if not value:
        return ""

    text = value

    text = re.sub(
        r"-----BEGIN [A-Z0-9 ]+-----[\s\S]*?-----END [A-Z0-9 ]+-----",
        REDACTED,
        text,
        flags=re.IGNORECASE,
    )

    def redact_json(match: re.Match[str]) -> str:
        key = match.group(1)
        return f"\"{key}\": \"{REDACTED}\""

    text = re.sub(
        r"\"(token|sign|password|secret|api[_-]?key|access[_-]?token)\"\s*:\s*\"[^\"]*\"",
        redact_json,
        text,
        flags=re.IGNORECASE,
    )

    def redact_inline(match: re.Match[str]) -> str:
        key = match.group(1)
        sep = match.group(2)
        return f"{key}{sep}{REDACTED}"

    text = re.sub(
        r"\b([A-Za-z0-9_]*(?:token|sign|password|secret|api[_-]?key|access[_-]?token))\b(\s*[:=]\s*)([^\s,;`]+)",
        redact_inline,
        text,
        flags=re.IGNORECASE,
    )

    return text


def split_items(raw: str, *, separator: str) -> list[str]:
    if not raw:
        return []
    return [sanitize_text(item.strip()) for item in raw.split(separator) if item.strip()]


def merge_unique(*lists: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for items in lists:
        for item in items:
            norm = sanitize_text(str(item).strip())
            if not norm or norm in seen:
                continue
            seen.add(norm)
            out.append(norm)
    return out


def normalize_status(value: str, *, allow_closed_alias: bool) -> str:
    status = sanitize_text(str(value or "")).strip().lower()
    if allow_closed_alias and status == "closed":
        status = "done"
    if status not in ALLOWED_STATUS:
        raise ValueError(
            f"Estado invalido `{status}`. Permitidos: {sorted(ALLOWED_STATUS)}"
        )
    return status


def parse_worklog_entries(worklog_text: str) -> list[dict[str, str]]:
    fields = {
        "- Fecha:": "fecha",
        "- Paso:": "paso",
        "- Cambios:": "cambios",
        "- Evidencia:": "evidencia",
        "- Siguiente accion:": "siguiente_accion",
    }
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    current_field: str | None = None

    for raw_line in worklog_text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("- Fecha:"):
            if current:
                entries.append(current)
            current = {key: "" for key in fields.values()}
            current["fecha"] = line.split(":", 1)[1].strip()
            current_field = "fecha"
            continue

        if not current:
            continue

        matched_field = None
        for prefix, field_key in fields.items():
            if line.startswith(prefix):
                current[field_key] = line.split(":", 1)[1].strip()
                matched_field = field_key
                break

        if matched_field:
            current_field = matched_field
            continue

        stripped = line.strip()
        if stripped and current_field:
            extra = sanitize_text(stripped)
            if current[current_field]:
                current[current_field] = f"{current[current_field]} {extra}".strip()
            else:
                current[current_field] = extra

    if current:
        entries.append(current)

    return entries


def build_legacy_markdown(
    *,
    head_hash: str,
    head_date_iso: str,
    entries: list[dict[str, str]],
) -> str:
    clean_entries = [
        {
            "fecha": sanitize_text(entry.get("fecha", "")),
            "paso": sanitize_text(entry.get("paso", "")),
            "cambios": sanitize_text(entry.get("cambios", "")),
            "evidencia": sanitize_text(entry.get("evidencia", "")),
            "siguiente_accion": sanitize_text(entry.get("siguiente_accion", "")),
        }
        for entry in entries
        if entry.get("fecha", "").strip()
    ]

    first_date = clean_entries[0]["fecha"] if clean_entries else "N/A"
    last_date = clean_entries[-1]["fecha"] if clean_entries else "N/A"
    latest_step = clean_entries[-1]["paso"] if clean_entries else "N/A"

    lines = [
        "# Legacy Worklog Snapshot",
        "",
        "Snapshot congelado para continuidad de chat (fuente canonica: `docs/work-log.md`).",
        "",
        "## Metadata de corte",
        "- cutoff_ref: `HEAD`",
        f"- cutoff_commit: `{head_hash}`",
        f"- cutoff_commit_date: `{head_date_iso}`",
        "",
        "## Resumen consolidado",
        f"- total_entries: `{len(clean_entries)}`",
        f"- date_range: `{first_date}` -> `{last_date}`",
        f"- latest_step: `{latest_step}`",
        "",
        "## Entradas consolidadas",
    ]

    if not clean_entries:
        lines.append("- No se encontraron entradas en `docs/work-log.md` para este corte.")
        lines.append("")
        return "\n".join(lines)

    for index, entry in enumerate(clean_entries, start=1):
        lines.extend(
            [
                f"### {index}. {entry['fecha']} | paso `{entry['paso']}`",
                f"- Cambios: {entry['cambios'] or 'N/A'}",
                f"- Evidencia: {entry['evidencia'] or 'N/A'}",
                f"- Siguiente accion: {entry['siguiente_accion'] or 'N/A'}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def legacy_init(project_root: Path) -> Path:
    paths = resolve_paths(project_root)
    paths.base_dir.mkdir(parents=True, exist_ok=True)

    worklog_at_head = run_git(project_root, "show", "HEAD:docs/work-log.md")
    head_hash = run_git(project_root, "rev-parse", "HEAD").strip()
    head_date_iso = run_git(project_root, "show", "-s", "--format=%cI", "HEAD").strip()
    entries = parse_worklog_entries(worklog_at_head)

    markdown = build_legacy_markdown(
        head_hash=head_hash,
        head_date_iso=head_date_iso,
        entries=entries,
    )
    paths.legacy_file.write_text(markdown, encoding="utf-8")
    return paths.legacy_file


def summarize_repo_state(project_root: Path) -> str:
    try:
        status = run_git(project_root, "status", "--short", "--branch").strip().splitlines()
    except subprocess.CalledProcessError:
        return "Estado de git no disponible."

    if not status:
        return "Sin datos de estado de git."

    branch = sanitize_text(status[0].strip())
    changed = status[1:]
    if not changed:
        return f"{branch}; working_tree=clean"

    sample = ", ".join(sanitize_text(line.strip()) for line in changed[:5])
    suffix = "" if len(changed) <= 5 else f", ... (+{len(changed) - 5} archivos)"
    return f"{branch}; changed_files={len(changed)}; sample={sample}{suffix}"


def parse_snapshot_from_markdown(markdown: str) -> dict[str, Any] | None:
    match = INTERNAL_SNAPSHOT_RE.search(markdown or "")
    if not match:
        return None
    candidate = match.group(1).strip()
    if not candidate:
        return None
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def load_plan_file(plan_file: Path) -> dict[str, Any]:
    if not plan_file.exists():
        raise ValueError(f"No existe --plan-file: {plan_file.as_posix()}")

    content = plan_file.read_text(encoding="utf-8")
    suffix = plan_file.suffix.lower()
    if suffix == ".json":
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON invalido en --plan-file: {exc}") from exc
    else:
        if yaml is None:
            raise ValueError(
                "PyYAML no esta disponible. Instala dependencias con `py -3 -m pip install -r requirements.txt`."
            )
        try:
            payload = yaml.safe_load(content)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"YAML invalido en --plan-file: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("El --plan-file debe contener un objeto raiz.")
    return payload


def _read_required_string(obj: dict[str, Any], key: str, *, context: str) -> str:
    raw = obj.get(key)
    value = sanitize_text(str(raw or "")).strip()
    if not value:
        raise ValueError(f"Falta `{key}` en {context}.")
    return value


def _read_string_list(obj: dict[str, Any], key: str) -> list[str]:
    raw = obj.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(f"`{key}` debe ser una lista.")
    out: list[str] = []
    for idx, item in enumerate(raw, start=1):
        value = sanitize_text(str(item or "")).strip()
        if not value:
            raise ValueError(f"`{key}[{idx}]` no puede ser vacio.")
        out.append(value)
    return out


def normalize_plan_payload(
    payload: dict[str, Any],
    *,
    estado_override: str | None,
    cli_decisiones: list[str],
    cli_pendientes: list[str],
    cli_proximo: str,
    cli_refs: list[str],
    plan_source: str,
) -> dict[str, Any]:
    hito_raw = payload.get("hito")
    if not isinstance(hito_raw, dict):
        raise ValueError("`hito` debe existir y ser un objeto.")

    subhitos_raw = payload.get("subhitos")
    if not isinstance(subhitos_raw, list) or not subhitos_raw:
        raise ValueError("`subhitos` debe existir y tener al menos un elemento.")

    hito_status = normalize_status(
        estado_override if estado_override else _read_required_string(hito_raw, "estado", context="hito"),
        allow_closed_alias=True,
    )
    hito = {
        "id": _read_required_string(hito_raw, "id", context="hito"),
        "titulo": _read_required_string(hito_raw, "titulo", context="hito"),
        "estado": hito_status,
        "objetivo": _read_required_string(hito_raw, "objetivo", context="hito"),
    }

    seen_sub_ids: set[str] = set()
    seen_mini_ids: set[str] = set()
    subhitos: list[dict[str, Any]] = []

    for pos, sub_raw in enumerate(subhitos_raw, start=1):
        if not isinstance(sub_raw, dict):
            raise ValueError(f"`subhitos[{pos}]` debe ser objeto.")

        sub_id = _read_required_string(sub_raw, "id", context=f"subhitos[{pos}]")
        if sub_id in seen_sub_ids:
            raise ValueError(f"ID de subhito duplicado: `{sub_id}`")
        seen_sub_ids.add(sub_id)

        mini_raw = sub_raw.get("mini_hitos")
        if not isinstance(mini_raw, list):
            raise ValueError(f"`mini_hitos` debe ser lista en subhito `{sub_id}`.")

        minis: list[dict[str, Any]] = []
        for mpos, mraw in enumerate(mini_raw, start=1):
            if not isinstance(mraw, dict):
                raise ValueError(f"`mini_hitos[{mpos}]` en `{sub_id}` debe ser objeto.")

            mini_id = _read_required_string(mraw, "id", context=f"mini_hitos[{mpos}]/{sub_id}")
            if mini_id in seen_mini_ids:
                raise ValueError(f"ID de mini-hito duplicado: `{mini_id}`")
            seen_mini_ids.add(mini_id)

            mini_fecha = _read_required_string(mraw, "fecha", context=f"mini_hitos[{mpos}]/{sub_id}")
            try:
                datetime.strptime(mini_fecha, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(
                    f"Fecha invalida `{mini_fecha}` en mini-hito `{mini_id}`. Formato esperado YYYY-MM-DD."
                ) from exc

            check_value = mraw.get("check")
            if isinstance(check_value, bool):
                check_text = "ok" if check_value else "pending"
            elif check_value is None:
                check_text = ""
            else:
                check_text = sanitize_text(str(check_value)).strip()

            minis.append(
                {
                    "id": mini_id,
                    "titulo": _read_required_string(mraw, "titulo", context=f"mini_hitos[{mpos}]/{sub_id}"),
                    "fecha": mini_fecha,
                    "estado": normalize_status(
                        _read_required_string(mraw, "estado", context=f"mini_hitos[{mpos}]/{sub_id}"),
                        allow_closed_alias=False,
                    ),
                    "check": check_text,
                    "evidencia": sanitize_text(str(mraw.get("evidencia", ""))).strip(),
                    "carried_over": False,
                    "subhito_id": sub_id,
                }
            )

        subhitos.append(
            {
                "id": sub_id,
                "titulo": _read_required_string(sub_raw, "titulo", context=f"subhitos[{pos}]"),
                "estado": normalize_status(
                    _read_required_string(sub_raw, "estado", context=f"subhitos[{pos}]"),
                    allow_closed_alias=False,
                ),
                "mini_hitos": minis,
            }
        )

    decisiones = merge_unique(_read_string_list(payload, "decisiones"), cli_decisiones)
    pendientes = merge_unique(_read_string_list(payload, "pendientes"), cli_pendientes)
    refs = merge_unique(_read_string_list(payload, "refs"), cli_refs)
    proximo_from_file = sanitize_text(str(payload.get("proximo", ""))).strip()
    proximo = sanitize_text(cli_proximo).strip() or proximo_from_file or "Revisar mini-hitos abiertos del dia."

    return {
        "hito": hito,
        "subhitos": subhitos,
        "decisiones": decisiones,
        "pendientes": pendientes,
        "proximo": proximo,
        "refs": refs,
        "plan_source": plan_source,
    }


def build_plan_from_legacy_flags(
    *,
    hito: str,
    estado: str,
    objetivo: str,
    decisiones: list[str],
    pendientes: list[str],
    proximo: str,
    refs: list[str],
) -> dict[str, Any]:
    hito_status = normalize_status(estado, allow_closed_alias=True)
    today = date.today().isoformat()

    minis: list[dict[str, Any]] = []
    for idx, pendiente in enumerate(pendientes, start=1):
        lower = pendiente.lower()
        mini_status = "blocked" if "bloque" in lower else "todo"
        minis.append(
            {
                "id": f"legacy-mini-{idx}",
                "titulo": pendiente,
                "fecha": today,
                "estado": mini_status,
                "check": "",
                "evidencia": "",
                "carried_over": False,
                "subhito_id": "legacy-subhito-1",
            }
        )

    if not minis and proximo.strip():
        minis.append(
            {
                "id": "legacy-mini-next",
                "titulo": sanitize_text(proximo.strip()),
                "fecha": today,
                "estado": "in_progress" if hito_status != "done" else "done",
                "check": "",
                "evidencia": "",
                "carried_over": False,
                "subhito_id": "legacy-subhito-1",
            }
        )

    return {
        "hito": {
            "id": sanitize_text(hito.strip()),
            "titulo": sanitize_text(hito.strip()),
            "estado": hito_status,
            "objetivo": sanitize_text(objetivo.strip()),
        },
        "subhitos": [
            {
                "id": "legacy-subhito-1",
                "titulo": "Seguimiento directo",
                "estado": "in_progress" if hito_status != "done" else "done",
                "mini_hitos": minis,
            }
        ],
        "decisiones": decisiones,
        "pendientes": pendientes,
        "proximo": sanitize_text(proximo.strip()) or "Revisar mini-hitos abiertos del dia.",
        "refs": refs,
        "plan_source": "legacy_flags",
    }


def apply_auto_carry(
    *,
    current_plan: dict[str, Any],
    previous_snapshot: dict[str, Any] | None,
) -> list[dict[str, str]]:
    if not previous_snapshot:
        return []

    previous_plan = previous_snapshot.get("plan")
    if not isinstance(previous_plan, dict):
        return []

    previous_subhitos = previous_plan.get("subhitos")
    if not isinstance(previous_subhitos, list):
        return []

    current_subhitos = current_plan.get("subhitos")
    if not isinstance(current_subhitos, list):
        return []

    current_status_by_mini: dict[str, str] = {}
    sub_map: dict[str, dict[str, Any]] = {}
    for sub in current_subhitos:
        if not isinstance(sub, dict):
            continue
        sub_id = sanitize_text(str(sub.get("id", ""))).strip()
        if not sub_id:
            continue
        sub_map[sub_id] = sub
        minis = sub.get("mini_hitos")
        if not isinstance(minis, list):
            continue
        for mini in minis:
            if not isinstance(mini, dict):
                continue
            mini_id = sanitize_text(str(mini.get("id", ""))).strip()
            mini_status = sanitize_text(str(mini.get("estado", ""))).strip().lower()
            if mini_id:
                current_status_by_mini[mini_id] = mini_status

    carried: list[dict[str, str]] = []
    for prev_sub in previous_subhitos:
        if not isinstance(prev_sub, dict):
            continue
        prev_sub_id = sanitize_text(str(prev_sub.get("id", ""))).strip()
        prev_sub_title = sanitize_text(str(prev_sub.get("titulo", ""))).strip() or "Carry-over"

        prev_minis = prev_sub.get("mini_hitos")
        if not isinstance(prev_minis, list):
            continue

        for prev_mini in prev_minis:
            if not isinstance(prev_mini, dict):
                continue
            mini_id = sanitize_text(str(prev_mini.get("id", ""))).strip()
            if not mini_id:
                continue
            mini_status = sanitize_text(str(prev_mini.get("estado", ""))).strip().lower()
            if mini_status not in OPEN_STATUS:
                continue
            if mini_id in current_status_by_mini:
                continue

            target_sub_id = prev_sub_id or "carry-over-subhito"
            target_sub = sub_map.get(target_sub_id)
            if target_sub is None:
                target_sub = {
                    "id": target_sub_id,
                    "titulo": prev_sub_title,
                    "estado": "in_progress",
                    "mini_hitos": [],
                }
                current_subhitos.append(target_sub)
                sub_map[target_sub_id] = target_sub

            copied = {
                "id": mini_id,
                "titulo": sanitize_text(str(prev_mini.get("titulo", ""))).strip() or mini_id,
                "fecha": sanitize_text(str(prev_mini.get("fecha", ""))).strip() or date.today().isoformat(),
                "estado": mini_status,
                "check": sanitize_text(str(prev_mini.get("check", ""))).strip(),
                "evidencia": sanitize_text(str(prev_mini.get("evidencia", ""))).strip(),
                "carried_over": True,
                "subhito_id": target_sub_id,
            }
            target_sub["mini_hitos"].append(copied)
            current_status_by_mini[mini_id] = mini_status
            carried.append(
                {
                    "mini_hito_id": mini_id,
                    "subhito_id": target_sub_id,
                    "estado": mini_status,
                }
            )

    return carried


def _collect_all_mini(plan: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    subhitos = plan.get("subhitos")
    if not isinstance(subhitos, list):
        return out
    for sub in subhitos:
        if not isinstance(sub, dict):
            continue
        sub_id = sanitize_text(str(sub.get("id", ""))).strip()
        minis = sub.get("mini_hitos")
        if not isinstance(minis, list):
            continue
        for mini in minis:
            if not isinstance(mini, dict):
                continue
            copied = dict(mini)
            copied["subhito_id"] = sub_id
            copied["subhito_titulo"] = sanitize_text(str(sub.get("titulo", ""))).strip()
            out.append(copied)
    return out


def _build_daily_index(plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for mini in _collect_all_mini(plan):
        key = sanitize_text(str(mini.get("fecha", ""))).strip() or "sin-fecha"
        index.setdefault(key, []).append(mini)

    for key in index:
        index[key].sort(key=lambda item: str(item.get("id", "")))
    return dict(sorted(index.items(), key=lambda kv: kv[0]))


def build_context_markdown(
    *,
    plan: dict[str, Any],
    repo_state: str,
    carried_over: list[dict[str, str]],
) -> str:
    generated_at = datetime.now(tz=timezone.utc).isoformat()
    today_iso = date.today().isoformat()
    hito = plan["hito"]
    daily_index = _build_daily_index(plan)

    lines = [
        "# Contexto T",
        "",
        "## 1) Objetivo activo",
        f"- Hito ID: `{hito['id']}`",
        f"- Titulo: {hito['titulo']}",
        f"- Estado: `{hito['estado']}`",
        f"- Objetivo: {hito['objetivo']}",
        f"- Estado repo: {sanitize_text(repo_state)}",
        "",
        "## 2) Arbol de ejecucion (Hito -> Subhitos -> Minihitos)",
    ]

    subhitos = plan.get("subhitos", [])
    for sub in subhitos:
        lines.append(f"### Subhito `{sub['id']}` - {sub['titulo']} (`{sub['estado']}`)")
        mini_hitos = sub.get("mini_hitos", [])
        if not mini_hitos:
            lines.append("- Sin mini-hitos.")
            lines.append("")
            continue

        for mini in mini_hitos:
            marker = CHECKBOX_BY_STATUS.get(mini["estado"], "[ ]")
            carry = " [carry-over]" if mini.get("carried_over") else ""
            extra = []
            if mini.get("check"):
                extra.append(f"check={mini['check']}")
            if mini.get("evidencia"):
                extra.append(f"evidencia={mini['evidencia']}")
            suffix = f" | {'; '.join(extra)}" if extra else ""
            lines.append(
                f"- {marker} `{mini['id']}` ({mini['fecha']}) {mini['titulo']}{carry} | estado=`{mini['estado']}`{suffix}"
            )
        lines.append("")

    lines.append("## 3) Checklist diario")
    if not daily_index:
        lines.append("- Sin mini-hitos diarios cargados.")
    else:
        for day, minis in daily_index.items():
            lines.append(f"### {day}")
            for mini in minis:
                marker = CHECKBOX_BY_STATUS.get(str(mini.get("estado", "")), "[ ]")
                lines.append(
                    f"- {marker} `{mini.get('id', '')}` {mini.get('titulo', '')} (subhito `{mini.get('subhito_id', '')}`)"
                )
            lines.append("")

    blocked = [
        mini
        for mini in _collect_all_mini(plan)
        if str(mini.get("estado", "")).strip().lower() == "blocked"
    ]
    lines.append("## 4) Bloqueos y pendientes")
    if blocked or plan.get("pendientes"):
        for mini in blocked:
            lines.append(
                f"- Bloqueado `{mini.get('id', '')}` ({mini.get('subhito_id', '')}): {mini.get('titulo', '')}"
            )
        for pending in plan.get("pendientes", []):
            lines.append(f"- Pendiente adicional: {pending}")
    else:
        lines.append("- N/A")

    lines.extend(
        [
            "",
            "## 5) Proximos pasos inmediatos",
            f"1. {plan.get('proximo', 'Revisar mini-hitos abiertos del dia.')}",
        ]
    )

    today_open = [
        mini
        for mini in daily_index.get(today_iso, [])
        if str(mini.get("estado", "")).strip().lower() in OPEN_STATUS
    ]
    if today_open:
        lines.append("2. Priorizar checks abiertos de hoy:")
        for mini in today_open:
            lines.append(f"- `{mini.get('id', '')}` ({mini.get('subhito_id', '')}) {mini.get('titulo', '')}")

    refs = plan.get("refs", [])
    carried_ids = [entry["mini_hito_id"] for entry in carried_over]
    lines.extend(
        [
            "",
            "## Metadata",
            f"- generated_at_utc: `{generated_at}`",
            f"- plan_source: `{plan.get('plan_source', 'unknown')}`",
            f"- refs: {', '.join(refs) if refs else 'N/A'}",
            f"- carried_over_count: `{len(carried_ids)}`",
            f"- carried_over_ids: {', '.join(carried_ids) if carried_ids else 'N/A'}",
            "- cadence_policy: `checkpoint al cierre de hito + cada 8 interacciones relevantes si el hito sigue abierto`",
            "",
            "## Internal Snapshot",
            "```json",
            json.dumps(
                {
                    "schema_version": 2,
                    "generated_at_utc": generated_at,
                    "plan": plan,
                    "carried_over": carried_over,
                },
                ensure_ascii=False,
                indent=2,
            ),
            "```",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def checkpoint(
    *,
    project_root: Path,
    plan_file: str | None,
    hito: str | None,
    estado: str | None,
    objetivo: str | None,
    estado_repo: str | None,
    decisiones: list[str],
    pendientes: list[str],
    proximo: str | None,
    refs: list[str],
) -> Path:
    paths = resolve_paths(project_root)
    paths.base_dir.mkdir(parents=True, exist_ok=True)

    if paths.context_t_file.exists():
        previous = paths.context_t_file.read_text(encoding="utf-8")
        paths.context_t_minus_1_file.write_text(previous, encoding="utf-8")

    previous_snapshot: dict[str, Any] | None = None
    if paths.context_t_minus_1_file.exists():
        previous_snapshot = parse_snapshot_from_markdown(
            paths.context_t_minus_1_file.read_text(encoding="utf-8")
        )

    plan_data: dict[str, Any]
    if plan_file:
        payload = load_plan_file(Path(plan_file))
        plan_data = normalize_plan_payload(
            payload,
            estado_override=estado if estado else None,
            cli_decisiones=decisiones,
            cli_pendientes=pendientes,
            cli_proximo=proximo or "",
            cli_refs=refs,
            plan_source=f"plan_file:{Path(plan_file).as_posix()}",
        )
    else:
        if not hito or not objetivo or not proximo:
            raise ValueError(
                "Modo legacy requiere --hito, --objetivo y --proximo cuando no se usa --plan-file."
            )
        plan_data = build_plan_from_legacy_flags(
            hito=hito,
            estado=estado or "in_progress",
            objetivo=objetivo,
            decisiones=decisiones,
            pendientes=pendientes,
            proximo=proximo,
            refs=refs,
        )

    carried_over = apply_auto_carry(current_plan=plan_data, previous_snapshot=previous_snapshot)

    repo_state = estado_repo.strip() if estado_repo else summarize_repo_state(project_root)
    markdown = build_context_markdown(
        plan=plan_data,
        repo_state=repo_state,
        carried_over=carried_over,
    )
    paths.context_t_file.write_text(markdown, encoding="utf-8")
    return paths.context_t_file


def summarize_open_by_subhito(snapshot: dict[str, Any]) -> list[str]:
    out: list[str] = []
    plan = snapshot.get("plan")
    if not isinstance(plan, dict):
        return out
    subhitos = plan.get("subhitos")
    if not isinstance(subhitos, list):
        return out

    for sub in subhitos:
        if not isinstance(sub, dict):
            continue
        minis = sub.get("mini_hitos")
        if not isinstance(minis, list):
            continue
        counts = {"todo": 0, "in_progress": 0, "blocked": 0}
        for mini in minis:
            if not isinstance(mini, dict):
                continue
            st = str(mini.get("estado", "")).strip().lower()
            if st in counts:
                counts[st] += 1
        total_open = counts["todo"] + counts["in_progress"] + counts["blocked"]
        if total_open == 0:
            continue
        sub_id = sanitize_text(str(sub.get("id", ""))).strip()
        sub_title = sanitize_text(str(sub.get("titulo", ""))).strip()
        out.append(
            f"- `{sub_id}` {sub_title}: open={total_open} (todo={counts['todo']}, in_progress={counts['in_progress']}, blocked={counts['blocked']})"
        )
    return out


def summarize_today_open(snapshot: dict[str, Any], today_iso: str) -> list[str]:
    out: list[str] = []
    plan = snapshot.get("plan")
    if not isinstance(plan, dict):
        return out
    for mini in _collect_all_mini(plan):
        mini_date = str(mini.get("fecha", "")).strip()
        mini_status = str(mini.get("estado", "")).strip().lower()
        if mini_date == today_iso and mini_status in OPEN_STATUS:
            out.append(
                f"- `{mini.get('id', '')}` ({mini.get('subhito_id', '')}) {mini.get('titulo', '')} | estado={mini_status}"
            )
    return out


def build_bootstrap_markdown(
    *,
    context_t_text: str,
    context_t_minus_1_text: str,
    summary_open_by_subhito: list[str],
    focus_today: list[str],
    legacy_text: str | None,
) -> str:
    lines = [
        "# Bootstrap Prompt",
        "",
        "Usar este bloque para refrescar chat sin perder continuidad operativa.",
        "",
        "## Instruccion de arranque",
        "Continuemos desde este contexto. Prioriza checks abiertos de hoy y mini-hitos bloqueados.",
        "",
        "## Resumen operativo (t)",
    ]

    if summary_open_by_subhito:
        lines.extend(summary_open_by_subhito)
    else:
        lines.append("- Sin mini-hitos abiertos por subhito en el snapshot actual.")

    lines.extend(["", "## Foco del dia (checks abiertos)"])
    if focus_today:
        lines.extend(focus_today)
    else:
        lines.append("- No hay checks abiertos para hoy.")

    lines.extend(
        [
            "",
            "## Contexto (t)",
            "```md",
            context_t_text.strip() if context_t_text.strip() else "[context_t.md no disponible]",
            "```",
            "",
            "## Contexto (t-1)",
            "```md",
            context_t_minus_1_text.strip() if context_t_minus_1_text.strip() else "[context_t-1.md no disponible]",
            "```",
        ]
    )

    if legacy_text is not None:
        lines.extend(
            [
                "",
                "## Legacy congelado",
                "```md",
                legacy_text.strip() if legacy_text.strip() else "[legacy_worklog.md vacio]",
                "```",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def compress_legacy_for_bootstrap(legacy_text: str, *, max_entries: int = 5) -> str:
    if not legacy_text.strip():
        return legacy_text

    lines = legacy_text.splitlines()
    if "## Entradas consolidadas" not in lines:
        return legacy_text

    entries_header_index = lines.index("## Entradas consolidadas")
    preamble = lines[: entries_header_index + 1]
    tail = lines[entries_header_index + 1 :]

    entry_lines: list[str] = []
    entry_count = 0
    capture = False

    for line in tail:
        if line.startswith("### "):
            entry_count += 1
            if entry_count > max_entries:
                break
            capture = True
        if capture:
            entry_lines.append(line)

    compact = preamble + entry_lines
    compact.extend(
        [
            "",
            f"_Legacy truncado para bootstrap (entries_shown={min(entry_count, max_entries)}; max_entries={max_entries})._",
            "_Abrir `docs/chat-context/legacy_worklog.md` para detalle completo._",
        ]
    )
    return "\n".join(compact).rstrip() + "\n"


def bootstrap(project_root: Path, *, with_legacy: bool) -> Path:
    paths = resolve_paths(project_root)
    paths.base_dir.mkdir(parents=True, exist_ok=True)

    raw_t = paths.context_t_file.read_text(encoding="utf-8") if paths.context_t_file.exists() else ""
    raw_t_minus_1 = (
        paths.context_t_minus_1_file.read_text(encoding="utf-8")
        if paths.context_t_minus_1_file.exists()
        else ""
    )

    context_t_text = sanitize_text(raw_t)
    context_t_minus_1_text = sanitize_text(raw_t_minus_1)

    snapshot_t = parse_snapshot_from_markdown(raw_t) or {}
    summary_open = summarize_open_by_subhito(snapshot_t)
    focus_today = summarize_today_open(snapshot_t, today_iso=date.today().isoformat())

    legacy_text = None
    if with_legacy and paths.legacy_file.exists():
        full_legacy_text = sanitize_text(paths.legacy_file.read_text(encoding="utf-8"))
        legacy_text = compress_legacy_for_bootstrap(full_legacy_text)

    markdown = build_bootstrap_markdown(
        context_t_text=context_t_text,
        context_t_minus_1_text=context_t_minus_1_text,
        summary_open_by_subhito=summary_open,
        focus_today=focus_today,
        legacy_text=legacy_text,
    )
    paths.bootstrap_file.write_text(markdown, encoding="utf-8")
    return paths.bootstrap_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gestion de memoria de chat local (legacy congelado + contexto t/t-1)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "legacy-init",
        help="Genera docs/chat-context/legacy_worklog.md desde docs/work-log.md en HEAD.",
    )

    checkpoint_parser = subparsers.add_parser(
        "checkpoint",
        help="Rota contexto(t)->contexto(t-1) y guarda nuevo contexto(t).",
    )
    checkpoint_parser.add_argument("--plan-file", help="Ruta a YAML/JSON con estructura hito->subhitos->mini_hitos.")
    checkpoint_parser.add_argument("--hito")
    checkpoint_parser.add_argument(
        "--estado",
        choices=["todo", "in_progress", "done", "blocked", "closed"],
        default=None,
    )
    checkpoint_parser.add_argument("--objetivo")
    checkpoint_parser.add_argument("--estado-repo")
    checkpoint_parser.add_argument(
        "--decisiones",
        default="",
        help="Lista separada por ';'.",
    )
    checkpoint_parser.add_argument(
        "--pendientes",
        default="",
        help="Lista separada por ';'.",
    )
    checkpoint_parser.add_argument("--proximo")
    checkpoint_parser.add_argument(
        "--refs",
        default="",
        help="Lista separada por ',' con rutas/referencias utiles.",
    )

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="Genera docs/chat-context/bootstrap_prompt.md con contexto(t) + contexto(t-1).",
    )
    bootstrap_parser.add_argument("--with-legacy", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "legacy-init":
        path = legacy_init(PROJECT_ROOT)
        print(f"LEGACY_FILE={path.as_posix()}")
        return 0

    if args.command == "checkpoint":
        try:
            path = checkpoint(
                project_root=PROJECT_ROOT,
                plan_file=args.plan_file,
                hito=args.hito,
                estado=args.estado,
                objetivo=args.objetivo,
                estado_repo=args.estado_repo,
                decisiones=split_items(args.decisiones, separator=";"),
                pendientes=split_items(args.pendientes, separator=";"),
                proximo=args.proximo,
                refs=split_items(args.refs, separator=","),
            )
        except ValueError as exc:
            parser.error(str(exc))
            return 2

        paths = resolve_paths(PROJECT_ROOT)
        print(f"CONTEXT_T_FILE={path.as_posix()}")
        print(f"CONTEXT_T_MINUS_1_FILE={paths.context_t_minus_1_file.as_posix()}")
        return 0

    if args.command == "bootstrap":
        path = bootstrap(PROJECT_ROOT, with_legacy=args.with_legacy)
        print(f"BOOTSTRAP_FILE={path.as_posix()}")
        return 0

    parser.error("Comando no soportado.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
