# 06 — Economía asimétrica del soporte

> **Fuente:** `Support_Architecture_Dossier.pdf` p9 + `Nación_Digital_LoL.pdf` p6

## Tesis: el supp opera con el menor presupuesto pero la mayor eficiencia

> *"La fórmula oculta: un soporte opera con el menor presupuesto, pero abusa de objetos con eficiencias superiores al 100%."*
> — Support Architecture Dossier, p9

El soporte gana **2/3 del oro** que un mid-laner. Su poder no viene del oro absoluto, sino de la **eficiencia por objeto comprado**.

## Los 3 ítems pico de eficiencia

### 1. Bloodsong — 264.5% eficiencia ⭐⭐⭐
> Por solo **400g**, otorga una pasiva de **Spellblade** que **amplifica todo el daño recibido por el enemigo**. El mayor pico de poder en oro/efecto del rol.

- **Aplicación:** ADC dual-tirador, scaling lanes, late-game teamfight
- **Champions ideales:** Senna, Pyke, supports tipo "marksman support"

### 2. Locket of the Iron Solari — ~105% eficiencia ⭐⭐
> La mitigación pasiva (Last Stand) + activa (Devotion shield) **anula combinaciones enteras de daño** por una fracción del costo de un ítem de daño equivalente.

- **Aplicación:** vs hard engage, vs assassins, vs wombo combo (Malphite, Yasuo, Orianna)
- **Champions ideales:** Wardens (Braum, Tahm), Engage (Leona, Naut), Catchers (Thresh)

### 3. Mikael's Blessing — Utilidad pura ⭐
> Intercambio directo de oro por **limpieza de CC vital** contra composiciones de enganche continuo.

- **Aplicación:** vs Catch comps (Morgana, Ashe, Naut), vs hard CC chains
- **Champions ideales:** Enchanters con teammate priorizado (Lulu+ADC, Janna+ADC)

## Evolución del oro de soporte (Patch 14+)

> **Fuente complementaria:** `Nación_Digital_LoL.pdf` p6 — "La Misión del Oro"

```
World Atlas (start) → Brújula Rúnica (400g) → [Barrera Evolutiva: 1000g] → Evolución final
                                                                                    ↓
                                                             ┌──────────────────────┴──────────────────────┐
                                                             │                                              │
                                                       Bloodsong       Solstice Sleigh       Celestial Opposition
                                                    (Daño AD desgaste) (Persecución/encierro) (Mitigación pura tanques)
                                                                            │                       │
                                                                      Zaz'Zak's Realmspike       Dream Maker
                                                                       (Daño mágico explosivo)    (Escudos y vitalidad)
```

Las 5 evoluciones finales **dictan el rol post-laning**:

| Evolución | Arquetipo soportado | Champions típicos |
|-----------|---------------------|-------------------|
| **Bloodsong** | Marksman support, AD-poke | Senna, Pyke (build oro) |
| **Solstice Sleigh** | Engage tank con persecución | Leona, Nautilus, Alistar |
| **Celestial Opposition** | Tank puro (Wardens) | Braum, Tahm, Rell |
| **Zaz'Zak's Realmspike** | Mages support | Brand, Zyra, Lux, Vel'Koz |
| **Dream Maker** | Enchanters | Janna, Lulu, Soraka, Milio, Karma, Renata |

## Implicancia para el motor

Esto **alimenta el campo `play_pattern_template`** de cada `SupportProfile`. El motor debe poder generar texto del tipo:

> "Lane: presión nivel 2 con E+Q. **First back: Solstice Sleigh + Boots1** para spike de engage. Mid: roams con jungla, **Locket en compra 2 si hay 2+ assassins enemigos**. Late: front-line tanky, **Mikael's si Pyke o Naut enemigo amenazan al ADC**."

Esta capa de **build awareness** no estaba explícita en los profiles anteriores. Se debe enriquecer cada `play_pattern_template` con:

1. **First back** específico
2. **Core item path** (2-3 items en orden)
3. **Situationals** condicionales (vs X comp → Y item)

## Acción concreta

- ✅ El campo `item_path` está propuesto en el prompt de NotebookLM (`KB/notebooklm/prompt-base.md` si existe) para los 14 soportes fase 2
- ✅ Los profiles fase 1 deberían enriquecerse con `item_path` cuando se actualicen
- ⚠ Fase 2 (no incluida en este sprint): el motor podría sugerir `first_item` en la respuesta de la API

> Nota: este sprint NO toca los profiles individuales. Solo extiende el motor con las nuevas reglas de scoring (triángulo + sinergias medidas).
