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
