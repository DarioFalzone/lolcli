# Claude Design Handoff — riot_lol_cli

> Material de contexto para importar este proyecto a [claude.ai/design](https://claude.ai/design) y configurar el design system de la organización.

**Generado**: 2026-04-25
**Proyecto**: riot_lol_cli (CLI + servicios de análisis para League of Legends)
**Identidad visual**: Hextech Dark / Premium Gaming

---

## ⚡ TL;DR — qué subir y en qué orden

Subí los archivos a Claude Design en este orden. Cada uno tiene un objetivo distinto y construye sobre el anterior:

| Orden | Archivo | Para qué sirve en Claude Design |
|-------|---------|--------------------------------|
| 1️⃣ | [`brand-context.md`](brand-context.md) | Setear voz, tono, identidad visual y principios de diseño antes de cualquier decisión técnica. |
| 2️⃣ | [`stack-info.md`](stack-info.md) | Que Claude Design sepa qué tipo de output puede generar (HTML+CSS plain vs React) — evita salidas inutilizables. |
| 3️⃣ | [`design-system.md`](design-system.md) | Tokens reales (colores, tipografía, espaciado, radius, shadows, breakpoints) listos para importar como design tokens. |
| 4️⃣ | [`components-inventory.md`](components-inventory.md) | Lista de componentes existentes con sus variantes y estados — base para definir el sistema de componentes. |
| 5️⃣ | [`screens-flows.md`](screens-flows.md) | Mapa de pantallas y flujos — para entender contexto de uso al diseñar componentes nuevos. |

**Tiempo estimado de setup**: 30-45 minutos si los subís uno por uno y revisás el output de Claude Design entre cada upload.

---

## 📂 Contenido de esta carpeta

```
claude-design-handoff/
├── README.md                    ← Este archivo
├── brand-context.md             ← Voz, tono, identidad, principios
├── stack-info.md                ← Stack técnico + convenciones
├── design-system.md             ← Tokens (colors, fonts, spacing, etc.)
├── components-inventory.md      ← Componentes reutilizables
└── screens-flows.md             ← Pantallas y flujos
```

---

## 🎯 Objetivos del handoff

1. **Centralizar el design system** que hoy está disperso en 3 paletas distintas (Draft Advisor SPA, claude-4-5 template, dashboard_enhanced).
2. **Documentar componentes** que existen pero no están formalizados (son clases CSS sueltas, no componentes con props).
3. **Establecer una identidad visual coherente** que pueda escalarse a nuevas features sin romper la estética Hextech.
4. **Tener una fuente única de verdad** para colores, tipografía, espaciado, etc. que reemplace los 3 sistemas duplicados.

---

## 🔑 Hallazgos críticos (leer antes de subir)

### 1. Hay **3 paletas de tokens** en uso

El proyecto tiene la misma identidad visual pero implementada con tokens distintos en 3 surfaces:

- `--hextech-*` / `--piltover-*` (canónica, Match History + Splash Viewer)
- `--gold` / `--blue` / `--bg-primary` (Draft Advisor SPA, simplificada)
- `--primary` / `--secondary` / `--accent` (Dashboard legacy en Python)

**Acción para Claude Design**: definir **una única paleta canónica** y proponer plan de migración. Recomendación: usar `--hextech-*` como base.

### 2. **No es un proyecto React/Vue**

El frontend es **HTML + CSS + JavaScript vanilla** servido directamente por FastAPI. No hay package.json, no hay bundler, no hay framework JS.

**Acción para Claude Design**: si genera componentes en React, hay que traducirlos manualmente. Preferir output como HTML+CSS plain o specs visuales.

### 3. Identidad visual = **Hextech de League of Legends**

No es una marca neutral. El proyecto está alineado con la estética oficial de Riot Games. Esto significa:
- Dark mode obligatorio.
- Gold + cyan como acentos firmados.
- Glow effects, gradientes, fondo navy con orbes radiales — son **firma visual**, no decoración opcional.
- Tipografías Spiegel (oficial Riot) o Inter+Outfit (alternativa moderna).

### 4. Audiencia y voz: **gamer experto en español argentino**

- No tutorial-friendly.
- Mezcla español + jerga gamer en inglés (engage, peel, dive, scaling).
- Voseo argentino implícito en algunos textos.
- Tono técnico-conciso.

---

## 🚀 Cómo usar Claude Design con este handoff

### Paso 1: Subir contexto de marca y técnico (5 min)

En Claude Design, crear un nuevo proyecto y subir:
1. `brand-context.md`
2. `stack-info.md`

Pedirle a Claude Design: _"Confirmá que entendiste la identidad visual y el stack. Resumime en 3 párrafos lo que vas a tener en cuenta."_

### Paso 2: Importar el design system (10 min)

Subir `design-system.md`. Pedirle:
- _"Generá los design tokens en formato exportable a CSS custom properties."_
- _"Identificá inconsistencias entre las 3 paletas y propone una unificada."_
- _"Validá que la paleta cumple WCAG AA en contraste de texto."_

### Paso 3: Generar componentes formales (15 min)

Subir `components-inventory.md`. Pedirle:
- _"Por cada componente listado, definí props/variants/states formalmente y generá ejemplos visuales."_
- _"Priorizá los 'Alta prioridad' del resumen al final del documento."_
- _"Output como HTML+CSS plain (no React) para que sea consumible en este proyecto."_

### Paso 4: Diseñar pantallas faltantes o refactor (10 min)

Subir `screens-flows.md`. Pedirle:
- _"De las pantallas listadas, ¿cuáles tienen problemas de UX evidentes?"_
- _"Sugerí 3 mejoras al Draft Advisor que mantengan la identidad visual."_
- _"Diseñá el modal de detalle del campeón que está [A confirmar] en el dashboard mejorado."_

---

## ✅ Checklist de validación post-import

Después de subir todo, validá que Claude Design tiene contexto correcto:

- [ ] ¿Sabe que es dark mode obligatorio?
- [ ] ¿Sabe que la audiencia es gamer experto?
- [ ] ¿Sabe que NO usa React, es HTML/CSS/JS plain?
- [ ] ¿Tiene los 3 tokens canónicos (`--hextech-gold`, `--hextech-blue`, `--piltover-black`)?
- [ ] ¿Distingue las 3 paletas en uso y propone unificación?
- [ ] ¿Conoce los 14+ componentes del inventario?
- [ ] ¿Sabe que las pantallas principales son Draft Advisor, Meta Dashboard, Match History, Splash Viewer?
- [ ] ¿Mantiene el principio de "movimiento sutil" (animaciones lentas) y "glow as signature"?

Si responde "no" a alguna, complementá con un mensaje aclaratorio antes de pedir output.

---

## 🔄 Mantenimiento de este handoff

Estos archivos son **una foto del estado del proyecto a fecha 2026-04-25**. Para mantenerlos vivos:

1. Cada vez que se agregue un componente nuevo o se cambien tokens, actualizar `components-inventory.md` y/o `design-system.md`.
2. Cuando se unifiquen las 3 paletas (deuda conocida), actualizar `design-system.md` para reflejar la paleta canónica única.
3. Si se migra el Draft Advisor a React/Vue, actualizar `stack-info.md` ASAP — cambiaría qué output puede consumir Claude Design.
4. Re-importar a Claude Design después de cambios mayores para refrescar el contexto.

---

## 📚 Documentos relacionados (fuera de este handoff)

| Documento | Path | Uso |
|-----------|------|-----|
| AGENTS.md root | [`../AGENTS.md`](../AGENTS.md) | Contexto general del proyecto para agentes IA |
| Coding style | [`../.agent/rules/coding-style.md`](../.agent/rules/coding-style.md) | Convenciones de código |
| KB de Support Advisor | [`../KB/`](../KB/) | Base de conocimiento del sistema de recomendación de soportes |
| Reorg report | [`../REORGANIZATION_REPORT.md`](../REORGANIZATION_REPORT.md) | Historia de la última reorganización del repo |

---

## 🤝 Quién mantiene esto

**Owner del proyecto**: Dario Falzone (QA profesional, jugador de LoL).

Para sugerencias o correcciones: editar los archivos de esta carpeta y/o re-generar con un agente IA pasándole los archivos fuente del proyecto.
