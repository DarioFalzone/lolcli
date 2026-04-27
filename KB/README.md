# KB — Knowledge Base de Support Advisor

Carpeta de **estudio y razonamiento** que respalda las recomendaciones del Support Advisor.

> Estos documentos están en formato texto humano (Markdown) para que sean fáciles de leer, editar y discutir. Son la **fuente de verdad conceptual** que después se traduce a JSON estructurado en `data/draft_advisor/support_profiles.json` y al motor de scoring en `scoring.py`.

## Cómo usar este KB

- **Para Dario (jugador):** leé `filosofia-de-pickeo.md` para entender qué prioriza el sistema. Si no estás de acuerdo con un pick recomendado, revisá `arquetipos-de-soporte.md` y `sinergia-supp-adc.md` para ver el razonamiento.
- **Para implementar/extender:** estos docs son el **input** para los JSON. Si querés cambiar cómo razona el sistema, primero edita acá, después ajustá `scoring.py` y los JSON.
- **Para agentes de IA:** leé este README, después `filosofia-de-pickeo.md`, y consultá los archivos específicos según el contexto del cambio.

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
| [notebooklm/sintesis/](notebooklm/sintesis/) | 10 .md | **Síntesis procesable** de las fuentes. Cada doc cubre un eje aplicable al motor. |

### Hallazgos integrados al motor (2026-04-27)

3 nuevos JSON estructurados consumidos por `scoring.py`:

- **`data/draft_advisor/kb/structured/measured_synergies.json`** — Parejas ADC+supp con winrate medido (4 medidas: Samira+Naut 53.7%, Lucian+Nami 54.0%, Ashe+Sera 54.7%, Jinx+Thresh 54.3%) + 10 heurísticas pro-scene.
- **`data/draft_advisor/kb/structured/strategic_triangle.json`** — Triángulo Engage > Poke > Sustain + eje invertido Disengage > Engage. Subdivide enchanters en `enchanter_disengage` (Janna, Lulu, Milio, Renata, Karma) vs `enchanter_pure` (Soraka, Yuumi, Nami).
- **`data/draft_advisor/kb/structured/comp_predominance.json`** — Ciclo piedra-papel-tijera entre las 5 composiciones (Attack > Siege > Protect > Catch > Attack).

Ver [`notebooklm/sintesis/INDEX.md`](notebooklm/sintesis/INDEX.md) para el índice completo y `bitacora_de_cambios.md` para el detalle del commit.

## Cobertura actual (Phase 2 — Expandida)

17 soportes cubiertos en detalle:

**Engage (4):** Leona, Nautilus, Alistar, Rell
**Enchanter (5):** Lulu, Janna, Soraka, Milio, Nami
**Poke / Mage (2):** Lux, Karma
**Warden (2):** Braum, Taric
**Catcher (4):** Thresh, Pyke, Rakan, Blitzcrank

**Próxima fase:** sumar Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard.

## Versión

- **Phase:** 2 (Expandida)
- **Patch base:** 16.7
- **Última actualización:** 2026-04-25
- **Soportes:** 17 perfiles detallados
