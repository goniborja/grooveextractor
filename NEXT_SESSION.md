# Proxima Sesion - Groove Extractor

**Ultima actualizacion:** 22 enero 2026
**Objetivo:** Implementar detector de patron y extractor de humanizacion

---

## Contexto rapido (1 minuto de lectura)

Groove Extractor analiza audio de bateria jamaicana. Ya tiene:
- Separacion de stems (Demucs)
- Filtros OLDIE/NEWIE para hi-hat (vintage 3500-8000Hz / moderno 4500-10500Hz)
- Deteccion de BPM con correccion por estilo
- DatabaseAggregator para exportar a database.xlsx central
- UI con switch OLDIE/NEWIE

**Falta implementar:** El detector de patrones y extractor de humanizacion real.

---

## Flujo a implementar

```
CARGAR AUDIO + SELECCIONAR ESTILO (ej: "one-drop")
         |
         v
SEPARAR STEMS (ya existe)
         |
         v
DETECTAR PATRON CON KICK+SNARE (los fiables):
   - One-drop: kick+snare juntos en paso 9
   - Steppers: kick en 1,5,9,13 + snare en 9
   - Ska: hi-hat en offbeats (2,4,6,8,10,12,14,16)
   - Rocksteady: kick escaso + snare en 9
   - Early reggae: hi-hat en semicorcheas (todos los 16 pasos)
         |
         v
BUSCAR SEGMENTO VALIDO:
   - Escanear compas por compas
   - Si patron encaja Y calidad suficiente -> PARAR
   - Si no -> seguir buscando
   - Si no encuentra nada -> avisar al usuario
         |
         v
EXTRAER HUMANIZACION (solo del segmento valido):
   - Timing: T1-T16 (desviacion en ms)
   - Velocity: V1-V16 (0-127)
   - Kick y snare: siempre extraer
   - Hi-hat: solo si calidad suficiente
         |
         v
CLASIFICAR SNARE:
   - Cross-stick (nota 37): sustain < 150ms -> patron normal
   - Snare full (nota 38): sustain > 150ms -> fills
         |
         v
EXPORTAR A database.xlsx (DatabaseAggregator ya existe)
```

---

## Prompt para Claude Code (copiar y pegar)

```
CONTEXTO:
Proyecto Groove Extractor (github.com/goniborja/grooveextractor).
Rama: main (actualizada con DatabaseAggregator, OLDIE/NEWIE, etc.)

TAREA:
Implementar detector de patron y extractor de humanizacion.

CREAR:

1. src/analyzers/pattern_detector.py (NUEVO):
   - Clase PatternDetector
   - Plantillas para 5 estilos:
     * ska: hi-hat offbeats (2,4,6,8,10,12,14,16), kick 1,5,9,13
     * rocksteady: kick escaso, snare en 9
     * early_reggae: hi-hat semicorcheas, similar a rocksteady
     * one_drop: kick+snare SOLO en paso 9
     * steppers: kick en 1,5,9,13 + snare en 9
   - Metodo detect_style(kick_onsets, snare_onsets, bpm)
   - Metodo find_valid_segment(stems, style, min_bars=4)
   - Tolerancia: +/-1/8 de beat

2. src/analyzers/humanization_extractor.py (NUEVO):
   - Clase HumanizationExtractor
   - Metodo extract(segment, style) -> HumanizationData
   - Calcular T1-T16 (timing en ms vs grid perfecto)
   - Calcular V1-V16 (velocity 0-127)
   - Umbral de calidad: >80% golpes esperados detectados

3. src/analyzers/snare_classifier.py (NUEVO):
   - Clase SnareClassifier
   - Metodo classify(snare_audio_segment) -> "cross_stick" | "snare_full"
   - Basado en duracion sustain: <150ms = cross_stick

4. Integrar en src/groove_extractor.py:
   - Anadir PatternDetector al pipeline
   - Anadir HumanizationExtractor
   - Conectar con DatabaseAggregator

5. Tests en tests/test_pattern_detector.py

NO TOCAR:
- feature/book-of-drums-midi-generator (tiene bugs)
```

---

## Criterio de "terminado"

- [ ] PatternDetector detecta los 5 estilos
- [ ] find_valid_segment() escanea hasta encontrar segmento bueno
- [ ] HumanizationExtractor genera T1-T16 y V1-V16
- [ ] SnareClassifier distingue cross-stick de snare
- [ ] Integracion con DatabaseAggregator
- [ ] Tests basicos pasan

---

## Archivos de referencia en el proyecto

- `src/exporters/excel_exporter.py` -> DatabaseAggregator
- `src/separators/drum_separator.py` -> OLDIE/NEWIE
- `src/analyzers/jamaican_bpm.py` -> deteccion BPM

---

## Decisiones ya tomadas (ver DECISIONS_LOG.md)

NO rediscutir estos temas, ya estan decididos.
