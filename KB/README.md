# KB — Knowledge Base de Support Advisor

Carpeta de **estudio y razonamiento** que respalda las recomendaciones del Support Advisor.

> Estos documentos están en formato texto humano (Markdown) para que sean fáciles de leer, editar y discutir. Son la **fuente de verdad conceptual** que después se traduce a JSON estructurado en `data/draft_advisor/support_profiles.json` y al motor de scoring en `scoring.py`.

## Cómo usar este KB

- **Para Dario (jugador):** leé `filosofia-de-pickeo.md` para entender qué prioriza el sistema. Si no estás de acuerdo con un pick recomendado, revisá `arquetipos-de-soporte.md` y `sinergia-supp-adc.md` para ver el razonamiento.
- **Para implementar/extender:** estos docs son el **input** para los JSON. Si querés cambiar cómo razona el sistema, primero edita acá, después ajustá `scoring.py` y los JSON.
- **Para agentes de IA:** leé este README, después `filosofia-de-pickeo.md`, y consultá los archivos específicos según el contexto del cambio.

## Maestria ADC personal

La captura [`tier list adc 04 05 2026.png`](tier%20list%20adc%2004%2005%202026.png) es evidencia visual de la maestria ADC del usuario.

La fuente editable que consume el Draft Advisor vive en `data/draft_advisor/personal_adc_mastery.json`. No leer la imagen directamente desde el motor: si cambia la tier list, actualizar primero ese JSON y dejar entradas dudosas en `needs_review`.

Esta maestria no reemplaza la KB estrategica: funciona como gate de recomendacion ADC junto con el snapshot de meta en `data/meta_scraper/normalized/latest_adc_tier.json`.

## Índice

| Documento | Propósito |
|-----------|-----------|
| [filosofia-de-pickeo.md](filosofia-de-pickeo.md) | Cómo razona el sistema. Pesos. Prioridades. Reglas heurísticas. |
| [arquetipos-de-soporte.md](arquetipos-de-soporte.md) | Las 4 categorías de soporte: engage, enchanter, poke mage, catcher/pick. |
| [sinergia-supp-adc.md](sinergia-supp-adc.md) | Tabla detallada de qué soporte va con qué ADC. |
| [matchups-supp-vs-supp.md](matchups-supp-vs-supp.md) | Quién gana lane phase contra quién. Bullies vs scaling. |
| [plan-de-juego-por-arquetipo.md](plan-de-juego-por-arquetipo.md) | Templates de "lane → mid → late" por arquetipo. Output del campo `enabled_play_pattern`. |
| [amenazas-y-respuestas.md](amenazas-y-respuestas.md) | Qué soporte responde a cada tipo de comp enemiga: dive, poke, pick, scaling. |
| [SUPPORT_THEORY.md](SUPPORT_THEORY.md) | Teoría avanzada del rol de soporte (resumen integrador). |

## Material extendido (NotebookLM 2026-04-27)

`KB/notebooklm/` contiene fuentes pesadas (PDFs, infografías) procesadas para ampliar la KB:

| Carpeta / archivo | Tipo | Contenido |
|-------------------|------|-----------|
| [notebooklm/Support_Architecture_Dossier.pdf](notebooklm/Support_Architecture_Dossier.pdf) | PDF (13 pp) | Arquitectura del rol de soporte: paradigma del arquitecto, métricas J/B Prox, jerarquía de pick order, triángulo Engage/Poke/Sustain, sinergias 2v2 medidas, economía asimétrica, regla de los 3 chequeos, Crash & Move, LCK vs LPL. |
| [notebooklm/Nación_Digital_LoL.pdf](notebooklm/Nación_Digital_LoL.pdf) | PDF (12 pp) | Análisis sociocultural y sistémico de LoL: roles como especialización, ecosistema piedra-papel-tijera, evolución del oro, individualismo vs colectivismo regional. |
| [notebooklm/imagen guia de estrategia de seleccion y macrogame.png](notebooklm/imagen%20guia%20de%20estrategia%20de%20seleccion%20y%20macrogame.png) | Infografía | Guía maestra del soporte (visual). |
| [notebooklm/guia de estudio estrategia de soporte](notebooklm/guia%20de%20estudio%20estrategia%20de%20soporte) | Texto plano | Guía de estudio: quiz, respuestas, glosario técnico. |
| [notebooklm/sintesis/README.md](notebooklm/sintesis/README.md) | Markdown consolidado | **Sintesis procesable** de las fuentes. Resume los ejes aplicables al motor. |

### Hallazgos integrados al motor (2026-04-27)

3 nuevos JSON estructurados consumidos por `scoring.py`:

- **`data/draft_advisor/kb/structured/measured_synergies.json`** — Parejas ADC+supp con winrate medido (4 medidas: Samira+Naut 53.7%, Lucian+Nami 54.0%, Ashe+Sera 54.7%, Jinx+Thresh 54.3%) + 10 heurísticas pro-scene.
- **`data/draft_advisor/kb/structured/strategic_triangle.json`** — Triángulo Engage > Poke > Sustain + eje invertido Disengage > Engage. Subdivide enchanters en `enchanter_disengage` (Janna, Lulu, Milio, Renata, Karma) vs `enchanter_pure` (Soraka, Yuumi, Nami).
- **`data/draft_advisor/kb/structured/comp_predominance.json`** — Ciclo piedra-papel-tijera entre las 5 composiciones (Attack > Siege > Protect > Catch > Attack).

Ver [`notebooklm/sintesis/README.md`](notebooklm/sintesis/README.md) para el indice consolidado y `bitacora_de_cambios.md` para el detalle historico.

## Cobertura actual (Phase 2 — Expandida + Audit 2026-04-27)

17 soportes cubiertos en detalle (support_profiles.json):

**Engage (4):** Leona, Nautilus, Alistar, Rell
**Enchanter (5):** Lulu, Janna, Soraka, Milio, Nami
**Poke / Mage (2):** Lux, Karma
**Warden (2):** Braum, Taric
**Catcher (4):** Thresh, Pyke, Rakan, Blitzcrank

**Triángulo estratégico (strategic_triangle.json v1.1):** 6 archetypes fine-grained:
- `engage`, `poke`, `enchanter_disengage`, `enchanter_pure`, `catcher`, `warden`
- Warden (Braum, Taric, TahmKench) beats engage+catcher, loses to poke
- Rakan clasificado como `catcher`

**Próxima fase:** sumar Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard.

## Versión

- **Phase:** 2 (Expandida + Audit)
- **Patch base:** 16.7
- **Última actualización:** 2026-04-27
- **Soportes:** 17 perfiles detallados
- **strategic_triangle.json:** v1.1 (6 archetypes)
- **comp_predominance.json:** v1.0 (consumido en scoring)

## Fuentes de scraping y jungla

Esta seccion absorbe las notas sueltas `fuentes-de-datos-scraping.md` y `jungla-draft-notes.md`.

### Fuentes de datos para scraping

Fuentes base para Meta Scraper y analisis de datos:

- U.GG: SoloQ, Pro Play, winrate, runas, builds core y situacionales.
- OP.GG: tendencias populares, elo alto y contexto asiatico.
- LoLalytics: estadisticas detalladas por parche, elo, region y sinergias.
- Blitz.gg: metricas rapidas de matchups y builds desde ecosistema cliente.
- Mobalytics: explicaciones textuales de matchups, picos de poder y consejos.
- Probuilds.net: builds de jugadores profesionales en SoloQ.
- METAsrc: tier lists y winrates consolidados.

Fuentes avanzadas a evaluar por adapter:

- Onetricks.gg: adaptaciones de OTPs, runas, maxeo y matchups escondidos por promedios.
- LeagueOfGraphs: macroestadisticas, popularidad, duracion de partidas y evolucion temporal.
- Gol.gg: fuente fuerte para Pro Play, composiciones, presencia y torneos.
- DeepLoL.gg: datos coreanos de elo alto, impacto temprano y lane dominance.

No asumir que una fuente externa es verdad absoluta: cada adapter debe documentar origen, fecha, rol, patch y limitaciones.

### Criterio para jungla y Draft Advisor

La investigacion completa de jugadores profesionales vive en `projects/active/junglas-pro/`. A `KB/` solo entra lo que pueda convertirse en regla de draft o scoring:

- arquetipos de jungla y su impacto en bot lane;
- ventanas de presion temprana, pathing y cobertura de dive;
- sinergias ADC/Support/Jungla;
- respuestas ante composiciones de pick, dive, poke o scaling;
- heuristicas verificables que puedan terminar en JSON estructurado.

No entra a `KB/`:

- perfiles completos de jugadores profesionales;
- rankings historicos sin uso directo en draft;
- imagenes, portal HTML o material visual;
- metodologia interna de `junglas-pro` que no afecte al motor.

Si una nota de jungla se usa para scoring, documentar primero el razonamiento en esta KB y luego sincronizar el JSON correspondiente en `data/draft_advisor/kb/structured/`.
