# Bitacora CTG Recibidas

Bitacora operativa para control de Cartas de Porte recibidas, actualizada en cada corrida automatica.

- Ultima actualizacion: `2026-03-12T21:14:02.194812+00:00`
- Ventana consultada: `2026-03-10..2026-03-12`
- Plantas consultadas: `20217,20218,20219,519447,700011`
- Tipo Carta de Porte: `74`

## Resumen ultima corrida

- CTG detectadas en la corrida: `3`
- CTG nuevas en catalogo: `3`
- Estados detectados: `{'AC': 3}`

## Catalogo vigente (9 CTG)

| CTG | Estado | Fecha emision | Inicio estado | Planta destino | CUIT origen | Primera vez | Ultima vez | Fuentes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10130106787 | AC | 2026-03-12T17:42:59.000Z | 2026-03-12T17:42:59.000Z | 20219 | 30659699318 | 2026-03-12T21:14:02.194812+00:00 | 2026-03-12T21:14:02.194812+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |
| 10130105171 | AC | 2026-03-12T17:18:58.000Z | 2026-03-12T17:18:59.000Z | 20219 | 30659699318 | 2026-03-12T21:14:02.194812+00:00 | 2026-03-12T21:14:02.194812+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |
| 10130094563 | AC | 2026-03-12T15:00:53.000Z | 2026-03-12T15:00:54.000Z | 20219 | 30659699318 | 2026-03-12T21:14:02.194812+00:00 | 2026-03-12T21:14:02.194812+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |
| 10129907121 | CN | 2026-03-05T10:48:52.000Z | 2026-03-05T17:21:47.000Z | 20219 | 30659699318 | 2026-03-05T20:39:46.154786+00:00 | 2026-03-05T20:41:32.644282+00:00 | consultarCPEAutomotor(nroCTG),seed_manual |
| 10129920861 | CN | 2026-03-05T16:59:18.000Z | 2026-03-05T17:06:42.000Z | 20219 | 20081033413 | 2026-03-05T20:39:46.154786+00:00 | 2026-03-05T20:41:32.644282+00:00 | consultarCPEAutomotor(nroCTG),seed_manual |
| 10129916478 | AC | 2026-03-05T15:30:21.000Z | 2026-03-05T15:30:21.000Z | 20219 | 20214448700 | 2026-03-05T20:37:25.442577+00:00 | 2026-03-05T20:41:32.644282+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |
| 10129913996 | AC | 2026-03-05T14:41:32.000Z | 2026-03-05T14:41:32.000Z | 20219 | 20214448700 | 2026-03-05T20:37:25.442577+00:00 | 2026-03-05T20:41:32.644282+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |
| 10129907277 | AC | 2026-03-05T10:53:31.000Z | 2026-03-05T10:53:32.000Z | 20219 | 30659699318 | 2026-03-05T20:37:25.442577+00:00 | 2026-03-05T20:41:32.644282+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |
| 10129906706 | AC | 2026-03-05T10:37:07.000Z | 2026-03-05T10:37:08.000Z | 20219 | 30659699318 | 2026-03-05T20:37:25.442577+00:00 | 2026-03-05T20:41:32.644282+00:00 | consultarCPEAutomotor(nroCTG),consultarCPEPorDestino |

## Historial corridas (ultimas 20)

- `2026-03-12T21:14:02.194812+00:00` ventana `2026-03-10..2026-03-12` detectadas=3 nuevas=3 estados={'AC': 3}
- `2026-03-05T20:41:32.644282+00:00` ventana `2026-03-03..2026-03-05` detectadas=6 nuevas=0 estados={'AC': 4, 'CN': 2}
- `2026-03-05T20:40:35.104093+00:00` ventana `2026-03-03..2026-03-05` detectadas=6 nuevas=0 estados={'AC': 4, 'CN': 2}
- `2026-03-05T20:39:46.154786+00:00` ventana `2026-03-03..2026-03-05` detectadas=6 nuevas=2 estados={'AC': 4, 'CN': 2}
- `2026-03-05T20:38:31.800234+00:00` ventana `2026-03-03..2026-03-05` detectadas=4 nuevas=0 estados={'AC': 4}
- `2026-03-05T20:37:25.442577+00:00` ventana `2026-03-03..2026-03-05` detectadas=4 nuevas=4 estados={'AC': 4}

## Nota

- Esta bitacora depende de `consultarCPEPorDestino` para detectar CTG y de `consultarCPEAutomotor` por `nroCTG` para enriquecer detalle.
- Si ARCA no expone alguna CTG en `consultarCPEPorDestino`, no podra incorporarse automaticamente hasta que aparezca en ese metodo o se consulte manualmente por `nroCTG`.
