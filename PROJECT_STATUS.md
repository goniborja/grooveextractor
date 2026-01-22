# Groove Extractor - Estado del Proyecto

**Ultima actualizacion:** 2026-01-22
**Actualizado por:** Claude Code

---

## Ramas del Repositorio

| Rama | Proposito | Estado | Notas |
|------|-----------|--------|-------|
| `main` | Codigo estable y funcional | Activa | Rama principal |
| `claude/branch-cleanup-8WGB1` | Cambios pendientes de merge a main | PR pendiente | Contiene todos los merges de esta sesion |
| `claude/book-of-drums-guide-8WGB1` | Generador MIDI con humanizacion jamaicana | En desarrollo | NO mergear - tiene bugs en generacion MIDI |

---

## Mergeado a main (esta sesion via PR branch)

| Fuente | Funcionalidad | Fecha |
|--------|---------------|-------|
| `implement-custom-widgets-EYeYT` | Switch OLDIE/NEWIE en UI, docs v0.1 | 2026-01-22 |
| `groove-extractor-data-models-q1GS9` | Conexion style_hint -> BPM analyzer | 2026-01-22 |
| `groove-extractor-data-models-MUlmI` | Filtros OLDIE/NEWIE para hi-hat | 2026-01-22 |
| `groove-extractor-export-format-8WGB1` | DatabaseAggregator, exportacion mejorada | 2026-01-22 |

---

## Ramas pendientes de eliminacion (manual)

| Rama | Razon |
|------|-------|
| `claude/review-groove-extractor-0wIiG` | Obsoleta, contenido ya en main |
| `claude/groove-extractor-tool-AvPbI` | Obsoleta, 35 commits divergentes |
| `claude/implement-custom-widgets-EYeYT` | Ya mergeada via cherry-pick |
| `claude/groove-extractor-data-models-MUlmI` | Ya mergeada via cherry-pick |
| `claude/groove-extractor-data-models-q1GS9` | Ya mergeada |
| `claude/groove-extractor-export-format-8WGB1` | Ya mergeada |

**Comandos para borrar:**
```bash
git push origin --delete claude/review-groove-extractor-0wIiG
git push origin --delete claude/groove-extractor-tool-AvPbI
git push origin --delete claude/implement-custom-widgets-EYeYT
git push origin --delete claude/groove-extractor-data-models-MUlmI
git push origin --delete claude/groove-extractor-data-models-q1GS9
git push origin --delete claude/groove-extractor-export-format-8WGB1
```

---

## Tarea pendiente: Renombrar rama Book of Drums

```bash
git checkout claude/book-of-drums-guide-8WGB1
git checkout -b feature/book-of-drums-midi-generator
git push -u origin feature/book-of-drums-midi-generator
git push origin --delete claude/book-of-drums-guide-8WGB1
```

---

## Funcionalidades principales en main

### Groove Extractor (analisis de audio)
- [x] Separacion de stems (kick, snare, hi-hat)
- [x] Deteccion de BPM con correccion por estilo
- [x] Filtros OLDIE/NEWIE para hi-hat vintage/moderno
- [x] Analisis de swing y timing
- [x] Exportacion a Excel (_groove.xlsx)
- [x] DatabaseAggregator para database.xlsx central
- [x] UI con switch OLDIE/NEWIE
- [x] Funcion detect_bpm_only() para deteccion rapida

### Book of Drums (generacion MIDI) - EN RAMA SEPARADA
- [x] Perfiles de bateristas (Carlton Barrett, Sly Dunbar, Lloyd Knibb, etc.)
- [x] Biblioteca de 26 patrones
- [x] Motor de humanizacion
- [x] Generador MIDI
- [ ] BUG: Generacion MIDI produce notas incorrectas
- [ ] Integracion con UI

---

## Proximos pasos sugeridos

1. **Mergear PR** de `claude/branch-cleanup-8WGB1` a main
2. **Borrar ramas obsoletas** listadas arriba
3. **Renombrar rama** Book of Drums a `feature/book-of-drums-midi-generator`
4. **Arreglar bugs** de Book of Drums en la rama feature
5. **Probar DatabaseAggregator** con analisis reales
6. **Validar filtros OLDIE/NEWIE** con grabaciones vintage

---

## Convencion de ramas

Para futuras ramas, usar estos prefijos:
- `feature/` - Nueva funcionalidad
- `fix/` - Correccion de bugs
- `refactor/` - Reorganizacion de codigo
- `experiment/` - Pruebas que quizas no se mergeen

---

## Historial de sesiones

### Sesion 2026-01-22
**Rama de trabajo:** `claude/branch-cleanup-8WGB1`
**Commits realizados:**
- Cherry-pick de 5 commits de implement-custom-widgets
- Merge de groove-extractor-data-models-q1GS9 (con resolucion de conflictos)
- Merge de groove-extractor-export-format-8WGB1
- Limpieza de _temp_files
- Actualizacion de .gitignore

**Mergeado a main:** No (PR pendiente)
**Pendiente:**
- Usuario debe mergear PR a main
- Usuario debe borrar ramas obsoletas manualmente
- Usuario debe renombrar rama Book of Drums

---
