from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "context_checkpoint.py"
MODULE_NAME = "context_checkpoint"

spec = importlib.util.spec_from_file_location(MODULE_NAME, SCRIPT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("No se pudo cargar scripts/context_checkpoint.py")
context_checkpoint = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = context_checkpoint
spec.loader.exec_module(context_checkpoint)


def run_git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class ContextCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        (self.repo / "docs").mkdir(parents=True, exist_ok=True)

        sample_worklog = """# Work log

- Fecha: 2026-03-01
- Paso: general
- Cambios: Primer cambio de ejemplo.
- Evidencia: Archivo base.
- Siguiente accion: Continuar.

- Fecha: 2026-03-02
- Paso: 2
- Cambios: Actualizacion con token=abc y sign=def.
- Evidencia: LEGACY_ACCESS_TOKEN=foo
- Siguiente accion: Cerrar.
"""
        (self.repo / "docs" / "work-log.md").write_text(sample_worklog, encoding="utf-8")

        run_git(self.repo, "init")
        run_git(self.repo, "config", "user.email", "test@example.com")
        run_git(self.repo, "config", "user.name", "Test User")
        run_git(self.repo, "add", "docs/work-log.md")
        run_git(self.repo, "commit", "-m", "init")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_legacy_init_uses_head_and_is_idempotent(self) -> None:
        out_path = context_checkpoint.legacy_init(self.repo)
        self.assertTrue(out_path.exists())
        first_text = out_path.read_text(encoding="utf-8")

        head_hash = run_git(self.repo, "rev-parse", "HEAD")
        self.assertIn("- cutoff_ref: `HEAD`", first_text)
        self.assertIn(f"- cutoff_commit: `{head_hash}`", first_text)
        self.assertIn("[REDACTED]", first_text)
        self.assertNotIn("token=abc", first_text)
        self.assertNotIn("LEGACY_ACCESS_TOKEN=foo", first_text)

        out_path_2 = context_checkpoint.legacy_init(self.repo)
        second_text = out_path_2.read_text(encoding="utf-8")
        self.assertEqual(first_text, second_text)

    def test_checkpoint_legacy_mode_still_works(self) -> None:
        context_checkpoint.checkpoint(
            project_root=self.repo,
            plan_file=None,
            hito="hito-legacy",
            estado="in_progress",
            objetivo="Objetivo legacy",
            estado_repo="repo limpio",
            decisiones=["decision 1"],
            pendientes=["pendiente 1"],
            proximo="Paso 1",
            refs=["docs/work-log.md"],
        )
        paths = context_checkpoint.resolve_paths(self.repo)
        self.assertTrue(paths.context_t_file.exists())
        text = paths.context_t_file.read_text(encoding="utf-8")
        self.assertIn("## 2) Arbol de ejecucion", text)
        self.assertIn("legacy-subhito-1", text)
        self.assertIn("hito-legacy", text)

    def test_checkpoint_plan_file_yaml_renders_hierarchy(self) -> None:
        today = date.today().isoformat()
        plan_file = self.repo / "plan.yaml"
        plan_file.write_text(
            f"""
hito:
  id: H1
  titulo: Integracion WSCPE
  estado: in_progress
  objetivo: Cerrar flujo diario por mini-hitos
subhitos:
  - id: S1
    titulo: Emitidas
    estado: in_progress
    mini_hitos:
      - id: M1
        titulo: Revisar ultimos comprobantes
        fecha: {today}
        estado: todo
        check: pendiente
        evidencia: output/a.json
decisiones:
  - Mantener foco en cpe
pendientes:
  - validar corrida
proximo: ejecutar consulta emitidas
refs:
  - docs/work-log.md
""".strip(),
            encoding="utf-8",
        )

        context_checkpoint.checkpoint(
            project_root=self.repo,
            plan_file=plan_file.as_posix(),
            hito=None,
            estado="in_progress",
            objetivo=None,
            estado_repo="status test",
            decisiones=[],
            pendientes=[],
            proximo=None,
            refs=[],
        )
        text = context_checkpoint.resolve_paths(self.repo).context_t_file.read_text(encoding="utf-8")
        self.assertIn("Hito ID: `H1`", text)
        self.assertIn("Subhito `S1`", text)
        self.assertIn("`M1`", text)
        self.assertIn("## 3) Checklist diario", text)
        self.assertIn("## Internal Snapshot", text)

    def test_checkpoint_plan_file_invalid_schema_raises(self) -> None:
        plan_file = self.repo / "plan_bad.yaml"
        plan_file.write_text(
            """
hito:
  id: H1
  titulo: Invalido
  estado: in_progress
  objetivo: test
subhitos:
  - id: S1
    titulo: x
    estado: in_progress
    mini_hitos:
      - id: M1
        titulo: y
        fecha: 2026-03-17
        estado: wrong_state
""".strip(),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            context_checkpoint.checkpoint(
                project_root=self.repo,
                plan_file=plan_file.as_posix(),
                hito=None,
                estado="in_progress",
                objetivo=None,
                estado_repo=None,
                decisiones=[],
                pendientes=[],
                proximo=None,
                refs=[],
            )

    def test_auto_carry_from_t_minus_1(self) -> None:
        today = date.today().isoformat()
        plan_v1 = self.repo / "plan_v1.yaml"
        plan_v1.write_text(
            f"""
hito:
  id: H1
  titulo: Flujo carry
  estado: in_progress
  objetivo: test
subhitos:
  - id: S1
    titulo: Stream principal
    estado: in_progress
    mini_hitos:
      - id: M_OPEN
        titulo: Pendiente que debe arrastrar
        fecha: {today}
        estado: todo
""".strip(),
            encoding="utf-8",
        )

        plan_v2 = self.repo / "plan_v2.yaml"
        plan_v2.write_text(
            f"""
hito:
  id: H1
  titulo: Flujo carry
  estado: in_progress
  objetivo: test
subhitos:
  - id: S1
    titulo: Stream principal
    estado: in_progress
    mini_hitos:
      - id: M_NEW
        titulo: Mini nuevo
        fecha: {today}
        estado: in_progress
""".strip(),
            encoding="utf-8",
        )

        context_checkpoint.checkpoint(
            project_root=self.repo,
            plan_file=plan_v1.as_posix(),
            hito=None,
            estado="in_progress",
            objetivo=None,
            estado_repo=None,
            decisiones=[],
            pendientes=[],
            proximo=None,
            refs=[],
        )
        context_checkpoint.checkpoint(
            project_root=self.repo,
            plan_file=plan_v2.as_posix(),
            hito=None,
            estado="in_progress",
            objetivo=None,
            estado_repo=None,
            decisiones=[],
            pendientes=[],
            proximo=None,
            refs=[],
        )

        paths = context_checkpoint.resolve_paths(self.repo)
        text = paths.context_t_file.read_text(encoding="utf-8")
        self.assertIn("M_OPEN", text)
        self.assertIn("[carry-over]", text)
        self.assertIn("carried_over_count: `1`", text)

        snapshot = context_checkpoint.parse_snapshot_from_markdown(text)
        self.assertIsNotNone(snapshot)
        assert snapshot is not None
        carried = snapshot.get("carried_over") or []
        self.assertEqual(len(carried), 1)
        self.assertEqual(carried[0].get("mini_hito_id"), "M_OPEN")

    def test_bootstrap_prioritizes_daily_focus(self) -> None:
        today = date.today().isoformat()
        plan_file = self.repo / "plan_bootstrap.yaml"
        plan_file.write_text(
            f"""
hito:
  id: H1
  titulo: Bootstrap focus
  estado: in_progress
  objetivo: foco diario
subhitos:
  - id: S1
    titulo: Diario
    estado: in_progress
    mini_hitos:
      - id: M1
        titulo: Check del dia
        fecha: {today}
        estado: in_progress
""".strip(),
            encoding="utf-8",
        )

        context_checkpoint.legacy_init(self.repo)
        context_checkpoint.checkpoint(
            project_root=self.repo,
            plan_file=plan_file.as_posix(),
            hito=None,
            estado="in_progress",
            objetivo=None,
            estado_repo=None,
            decisiones=[],
            pendientes=[],
            proximo=None,
            refs=[],
        )
        out_path = context_checkpoint.bootstrap(self.repo, with_legacy=True)
        text = out_path.read_text(encoding="utf-8")

        self.assertIn("## Resumen operativo (t)", text)
        self.assertIn("## Foco del dia (checks abiertos)", text)
        self.assertIn("M1", text)
        self.assertIn("Legacy truncado para bootstrap", text)

    def test_sanitize_text_redacts_sensitive_values(self) -> None:
        raw = """
token=abc123 sign:xyz987
LEGACY_ACCESS_TOKEN=supersecret
{"token":"tok","sign":"sig","password":"pw"}
-----BEGIN PRIVATE KEY-----
abcd
-----END PRIVATE KEY-----
"""
        clean = context_checkpoint.sanitize_text(raw)
        self.assertNotIn("abc123", clean)
        self.assertNotIn("xyz987", clean)
        self.assertNotIn("supersecret", clean)
        self.assertNotIn("-----BEGIN PRIVATE KEY-----", clean)
        self.assertIn("[REDACTED]", clean)


if __name__ == "__main__":
    unittest.main()
