# Chat Context Local

Directorio operativo para continuidad de chat.

## Archivos
- `legacy_worklog.md`: snapshot congelado desde `docs/work-log.md` en `HEAD`.
- `context_t.md`: contexto actual.
- `context_t-1.md`: contexto inmediatamente anterior.
- `bootstrap_prompt.md`: bloque listo para pegar en un chat nuevo.
- `plan.yaml`: plantilla de entrada jerarquica (`hito -> subhitos -> mini_hitos`).

## Flujo recomendado
1. Inicializar legado una sola vez:
   `py -3 scripts/context_checkpoint.py legacy-init`
2. Guardar checkpoint de trabajo:
   `py -3 scripts/context_checkpoint.py checkpoint --plan-file docs/chat-context/plan.yaml --estado in_progress --proximo "siguiente paso"`
3. Generar prompt de arranque para refrescar chat:
   `py -3 scripts/context_checkpoint.py bootstrap --with-legacy`

Modo retrocompatible (plano):
`py -3 scripts/context_checkpoint.py checkpoint --hito "hito-activo" --estado in_progress --objetivo "objetivo actual" --proximo "siguiente paso"`

## Estructura jerarquica esperada
1. `hito`: `id`, `titulo`, `estado`, `objetivo`
2. `subhitos[]`: `id`, `titulo`, `estado`, `mini_hitos[]`
3. `mini_hitos[]`: `id`, `titulo`, `fecha (YYYY-MM-DD)`, `estado`, `check?`, `evidencia?`
4. Estados permitidos en todos los niveles: `todo`, `in_progress`, `done`, `blocked`

## Regla de cadencia
- Checkpoint al cerrar hito.
- Si el hito sigue abierto, checkpoint intermedio cada 8 interacciones relevantes.
- Al pasar de `context_t-1` a `context_t`, los mini-hitos abiertos (`todo`, `in_progress`, `blocked`) se arrastran automaticamente si no fueron cerrados en el nuevo plan.

## Seguridad
- No incluir secretos (token/sign/password/keys/material criptografico).
- El script aplica sanitizacion basica, pero la responsabilidad final es operativa.
