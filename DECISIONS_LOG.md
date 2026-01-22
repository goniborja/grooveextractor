# Registro de Decisiones Tecnicas - Groove Extractor

Este archivo documenta las decisiones tecnicas tomadas para evitar rediscutirlas.

---

## Sesion 22 enero 2026

### 1. Estilos a soportar

**Decision:** 5 estilos jamaicanos
- ska (110-145 BPM, hi-hat offbeats)
- rocksteady (80-100 BPM, laid-back)
- early_reggae / skinhead (100-120 BPM)
- one_drop / roots (70-90 BPM)
- steppers (110-140 BPM, four-on-the-floor)

**Razon:** Son los fundamentales segun documentacion de patrones jamaicanos. Rockers y nyabinghi quedan fuera por ahora.

---

### 2. Instrumento de referencia para deteccion

**Decision:** Usar kick + snare como referencia principal. Hi-hat es opcional.

**Razon:** Demucs separa bien kick y snare, pero mal hi-hat. No podemos confiar en hi-hat para detectar patron.

---

### 3. Estrategia de busqueda de segmento

**Decision:** Escanear la cancion compas por compas hasta encontrar segmento valido. NO analizar toda la cancion.

**Razon:** En reggae no cambian el groove. Un buen segmento de 4-8 compases es suficiente. Intros y breaks confunden.

---

### 4. Categorias de compas

**Decision:** 3 categorias
- RHYTHM: sigue el patron
- VARIATION: 1-2 golpes extra (ej: anacrusa antes de estribillo)
- FILL/BREAK: >50% del compas diferente

**Razon:** Las variaciones son utiles porque marcan estructura de cancion.

---

### 5. Notas MIDI para snare

**Decision:**
- Cross-stick = nota MIDI 37 (para patron normal)
- Snare full = nota MIDI 38 (para fills y breaks)

**Razon:** En reggae tradicional se usa cross-stick/rimshot para el ritmo. Snare completo solo en fills.

---

### 6. Clasificacion de snare por sustain

**Decision:**
- < 150ms sustain = cross-stick
- > 150ms sustain = snare full

**Razon:** Diferencia mas audible y medible. Cross-stick tiene "toc" seco, snare tiene resonancia.

---

### 7. Filtros OLDIE/NEWIE para hi-hat

**Decision:**
- OLDIE (grabaciones vintage): 3500-8000 Hz
- NEWIE (grabaciones modernas): 4500-10500 Hz

**Razon:** Hi-hat vintage tiene menos brillo. Ajustar filtro mejora deteccion en grabaciones antiguas.

---

### 8. Gestion de ramas Git

**Decision:**
- Prefijo `feature/` para funcionalidad nueva
- Prefijo `fix/` para bugs
- Prefijo `refactor/` para reorganizacion
- NO usar sufijos aleatorios tipo `-8WGB1`

**Razon:** Ramas con nombres cripticos son imposibles de gestionar.

---

### 9. Book of Drums

**Decision:** NO mergear rama `feature/book-of-drums-midi-generator` a main hasta arreglar bugs.

**Razon:** Genera notas MIDI incorrectas (nota 37 en vez de 38) y patrones caoticos. Primero extraer datos reales con Groove Extractor.

---

### 10. Flujo del ecosistema

**Decision:**
```
Groove Extractor (extrae datos) -> database.xlsx -> Book of Drums (genera MIDI)
```

**Razon:** No tiene sentido generar MIDI humanizado sin datos reales de humanizacion de bateristas.

---

### 11. Estructura de database.xlsx

**Decision:** 5 hojas
- ESTILOS: catalogo de estilos
- PATRONES: metadatos de cada analisis
- REJILLAS: patrones en grid 16-pasos
- HUMANIZACION: V1-V16, T1-T16
- INSTRUMENTOS: catalogo MIDI (kick=36, snare=38, etc.)

**Razon:** Compatible con el database.xlsx de referencia que ya teniamos definido.

---

## Plantilla para nuevas decisiones

### [Numero]. [Titulo]

**Decision:** [Que se decidio]

**Razon:** [Por que]

**Fecha:** [Cuando]
