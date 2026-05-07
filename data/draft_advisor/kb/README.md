# Draft Advisor Knowledge Base

## Propósito

Esta base de conocimiento sostiene el asistente de recomendaciones ADC con investigación curada, análisis de parches, inteligencia de matchups y heurísticas de draft. El objetivo es mejorar el sistema con adquisición de conocimiento **controlada y revisable**, no acumular archivos sueltos.

## Arquitectura

```
kb/
├── taxonomy.json       # Vocabulario controlado: tipos de nota, confianza, temas, etc.
├── manifest.json       # Registro de procedencia de fuentes
├── sources/            # Materiales fuente crudos, sin modificar
│   ├── patch_notes/    # JSONs scrapeados de notas de parche
│   ├── pdf/            # PDFs originales
│   ├── web/            # Exportaciones web guardadas
│   └── notes/          # Notas personales crudas
├── research/           # Notas Markdown normalizadas
│   ├── adcs/           # Investigación estratégica por ADC
│   ├── supports/       # Análisis de sinergias de support
│   ├── threats/        # Análisis de amenazas enemigas
│   ├── archetypes/     # Investigación de arquetipos de composición
│   ├── matchups/       # Notas de matchup de línea/partida
│   ├── patches/        # Impacto de parches
│   ├── heuristics/     # Reglas de decisión de draft
│   └── meta/           # Resúmenes puntuales de meta
├── structured/         # Datos estructurados derivados
│   ├── patch_overrides.json
│   ├── comp_archetypes.json
│   └── matchup_rules.json
├── evals/              # Casos golden de draft + resultados
│   ├── golden_drafts.json
│   └── eval_results/
└── scripts/            # Herramientas de KB
    ├── validate_kb.py
    └── ingest_scaffold.py
```

## Principios

1. **Las fuentes crudas no se editan.** Guardar originales en `sources/`.
2. **Las notas de investigación son Markdown revisado por humanos.** Viven en `research/`.
3. **Los datos estructurados son la fuente de verdad del scoring.** La investigación los informa, pero no los reemplaza de forma silenciosa.
4. **Toda fuente tiene procedencia** registrada en `manifest.json`.
5. **Los cambios deben pasar evaluación golden** antes de entrar a datos estructurados.
6. **Idioma:** notas activas, razones y plantillas deben quedar en español. Se permiten tecnicismos gamer claros como `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `frontline`, `wave`, `burst` y `scaling`.

## Reglas ADC de Línea

`structured/matchup_rules.json` contiene `adc_lane_veto_rules` para casos donde el meta global no alcanza para recomendar un pick. La regla activa principal es `Nilah + Soraka vs Caitlyn + Nautilus`: aunque Nilah sea maestría alta, la línea pierde prioridad, rango seguro y control de crash, por lo que queda como `fallback_lane_veto`.

Tambien contiene `adc_matchup_bonus_rules` para aprendizajes positivos de draft que suman fit tactico sin saltarse el gate de meta/maestria. Caso activo: `Xayah` contra `Malphite` y `TahmKench`, donde la R y las plumas castigan engage frontal predecible y frontlines melee.

## Cómo Agregar Conocimiento

### Agregar una nota de investigación

1. Crear un `.md` en el subfolder correcto dentro de `research/`.
2. Usar el schema de frontmatter (mirar una nota existente como plantilla).
3. Empezar con `review_status: "draft"`.
4. Ejecutar `python -m data.draft_advisor.kb.scripts.validate_kb`.
5. Cambiar a `review_status: "reviewed"` después de revisar.

### Agregar una fuente cruda

1. Colocar el archivo en el subfolder correcto de `sources/`.
2. Agregar una entrada en `manifest.json` con metadata de la fuente.
3. Normalizar en una o más notas de investigación.
4. Linkear esas notas en `linked_research_notes` de la entrada del manifest.

### Proponer un cambio estructurado

1. Escribir la nota de investigación que justifica el cambio.
2. Agregar el override/regla al archivo correspondiente en `structured/`.
3. Ejecutar `python -m riot_lol_cli.draft_advisor.eval_runner` para verificar que los casos golden siguen pasando.
4. Si falla algún caso, revisar o rechazar el cambio.

## Formato de Parche

Toda referencia de parche debe cumplir `^\d+\.\d+$`, por ejemplo `16.7`.
Usar `*` para notas agnósticas de parche.
