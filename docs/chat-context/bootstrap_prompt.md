# Bootstrap Prompt

Usar este bloque para refrescar chat sin perder continuidad operativa.

## Instruccion de arranque
Continuemos desde este contexto. Prioriza checks abiertos de hoy y mini-hitos bloqueados.

## Resumen operativo (t)
- `S1` Subhito 1: open=2 (todo=1, in_progress=1, blocked=0)

## Foco del dia (checks abiertos)
- `M1` (S1) Mini-hito diario 1 | estado=todo
- `M2` (S1) Mini-hito diario 2 | estado=in_progress

## Contexto (t)
```md
# Contexto T

## 1) Objetivo activo
- Hito ID: `H1`
- Titulo: Hito principal del dia
- Estado: `in_progress`
- Objetivo: Resultado de negocio o tecnico esperado
- Estado repo: ## main...origin/main [ahead 1]; changed_files=7; sample=M AGENTS.md, M README.md, M docs/work-log.md, ?? docs/chat-context/, ?? requirements.txt, ... (+2 archivos)

## 2) Arbol de ejecucion (Hito -> Subhitos -> Minihitos)
### Subhito `S1` - Subhito 1 (`in_progress`)
- [ ] `M1` (2026-03-17) Mini-hito diario 1 | estado=`todo` | check=pendiente; evidencia=output/archivo.json
- [-] `M2` (2026-03-17) Mini-hito diario 2 | estado=`in_progress`

## 3) Checklist diario
### 2026-03-17
- [ ] `M1` Mini-hito diario 1 (subhito `S1`)
- [-] `M2` Mini-hito diario 2 (subhito `S1`)

## 4) Bloqueos y pendientes
- Pendiente adicional: Bloqueo o pendiente transversal

## 5) Proximos pasos inmediatos
1. Continuar mini-hitos de hoy
2. Priorizar checks abiertos de hoy:
- `M1` (S1) Mini-hito diario 1
- `M2` (S1) Mini-hito diario 2

## Metadata
- generated_at_utc: `2026-03-17T20:55:25.150473+00:00`
- plan_source: `plan_file:docs/chat-context/plan.yaml`
- refs: docs/work-log.md, docs/chat-context/plan.yaml
- carried_over_count: `0`
- carried_over_ids: N/A
- cadence_policy: `checkpoint al cierre de hito + cada 8 interacciones relevantes si el hito sigue abierto`

## Internal Snapshot
```json
{
  "schema_version": 2,
  "generated_at_utc": "2026-03-17T20:55:25.150473+00:00",
  "plan": {
    "hito": {
      "id": "H1",
      "titulo": "Hito principal del dia",
      "estado": "in_progress",
      "objetivo": "Resultado de negocio o tecnico esperado"
    },
    "subhitos": [
      {
        "id": "S1",
        "titulo": "Subhito 1",
        "estado": "in_progress",
        "mini_hitos": [
          {
            "id": "M1",
            "titulo": "Mini-hito diario 1",
            "fecha": "2026-03-17",
            "estado": "todo",
            "check": "pendiente",
            "evidencia": "output/archivo.json",
            "carried_over": false,
            "subhito_id": "S1"
          },
          {
            "id": "M2",
            "titulo": "Mini-hito diario 2",
            "fecha": "2026-03-17",
            "estado": "in_progress",
            "check": "",
            "evidencia": "",
            "carried_over": false,
            "subhito_id": "S1"
          }
        ]
      }
    ],
    "decisiones": [
      "Decision tecnica relevante"
    ],
    "pendientes": [
      "Bloqueo o pendiente transversal"
    ],
    "proximo": "Continuar mini-hitos de hoy",
    "refs": [
      "docs/work-log.md",
      "docs/chat-context/plan.yaml"
    ],
    "plan_source": "plan_file:docs/chat-context/plan.yaml"
  },
  "carried_over": []
}
```
```

## Contexto (t-1)
```md
# Contexto T

## 1) Objetivo activo
- Hito ID: `H1`
- Titulo: Hito principal del dia
- Estado: `in_progress`
- Objetivo: Resultado de negocio o tecnico esperado
- Estado repo: ## main...origin/main [ahead 1]; changed_files=7; sample=M AGENTS.md, M README.md, M docs/work-log.md, ?? docs/chat-context/, ?? requirements.txt, ... (+2 archivos)

## 2) Arbol de ejecucion (Hito -> Subhitos -> Minihitos)
### Subhito `S1` - Subhito 1 (`in_progress`)
- [ ] `M1` (2026-03-17) Mini-hito diario 1 | estado=`todo` | check=pendiente; evidencia=output/archivo.json
- [-] `M2` (2026-03-17) Mini-hito diario 2 | estado=`in_progress`

## 3) Checklist diario
### 2026-03-17
- [ ] `M1` Mini-hito diario 1 (subhito `S1`)
- [-] `M2` Mini-hito diario 2 (subhito `S1`)

## 4) Bloqueos y pendientes
- Pendiente adicional: Bloqueo o pendiente transversal

## 5) Proximos pasos inmediatos
1. Ejecutar mini-hitos pendientes de hoy
2. Priorizar checks abiertos de hoy:
- `M1` (S1) Mini-hito diario 1
- `M2` (S1) Mini-hito diario 2

## Metadata
- generated_at_utc: `2026-03-17T20:52:58.639457+00:00`
- plan_source: `plan_file:docs/chat-context/plan.yaml`
- refs: docs/work-log.md, docs/chat-context/plan.yaml
- carried_over_count: `0`
- carried_over_ids: N/A
- cadence_policy: `checkpoint al cierre de hito + cada 8 interacciones relevantes si el hito sigue abierto`

## Internal Snapshot
```json
{
  "schema_version": 2,
  "generated_at_utc": "2026-03-17T20:52:58.639457+00:00",
  "plan": {
    "hito": {
      "id": "H1",
      "titulo": "Hito principal del dia",
      "estado": "in_progress",
      "objetivo": "Resultado de negocio o tecnico esperado"
    },
    "subhitos": [
      {
        "id": "S1",
        "titulo": "Subhito 1",
        "estado": "in_progress",
        "mini_hitos": [
          {
            "id": "M1",
            "titulo": "Mini-hito diario 1",
            "fecha": "2026-03-17",
            "estado": "todo",
            "check": "pendiente",
            "evidencia": "output/archivo.json",
            "carried_over": false,
            "subhito_id": "S1"
          },
          {
            "id": "M2",
            "titulo": "Mini-hito diario 2",
            "fecha": "2026-03-17",
            "estado": "in_progress",
            "check": "",
            "evidencia": "",
            "carried_over": false,
            "subhito_id": "S1"
          }
        ]
      }
    ],
    "decisiones": [
      "Decision tecnica relevante"
    ],
    "pendientes": [
      "Bloqueo o pendiente transversal"
    ],
    "proximo": "Ejecutar mini-hitos pendientes de hoy",
    "refs": [
      "docs/work-log.md",
      "docs/chat-context/plan.yaml"
    ],
    "plan_source": "plan_file:docs/chat-context/plan.yaml"
  },
  "carried_over": []
}
```
```

