# 07 — La Regla de los 3 Chequeos (Algoritmo de Roaming Temprano)

> **Fuente:** `Support_Architecture_Dossier.pdf` p10 + `guia de estudio` p1-2

## El árbol de decisión

```
                ¿ROAMEAR DESDE BOT?
                        │
        ┌───────────────┴───────────────┐
        │                               │
   Check 1: ¿Mi ADC está a salvo (20-30s)?
   ├─ NO freeze enemigo, ├─ NO es diveable, ├─ ¿Tiene Hechizos disponibles?
        │                               │
       NO ────────► FALLO: ROAM = DONACIÓN DE RECURSOS (rompe tu carril por 5 min)
        │
       SÍ
        ▼
   Check 2: ¿La oleada permite salir?
   ├─ NO salir si la oleada empuja LENTO HACIA TUS ALIADOS
   ├─ Esperar Crash o Bounce
        │
       NO ────────► FALLO
        │
       SÍ
        ▼
   Check 3: ¿Hay un objetivo REAL?
   ├─ Mid empujado contra torre
   ├─ Invasión jungla planeada
   ├─ Pelea inminente en obj (Dragón, Grub)
        │
       NO ────────► FALLO
        │
       SÍ
        ▼
   ✅ EJECUTAR ROAMING
```

## Por qué es un algoritmo (y no una intuición)

> *"Si una condición falla y rotás, no es un roaming, es una donación de recursos que rompe tu propio carril por los próximos 5 minutos."*
> — Support Architecture Dossier, p10

Cada check es un **filtro estricto**. No hay "casi" — o cumple los 3 o no roam. La asimetría del costo (5 min de carril roto) vs beneficio (~1 kill mid o visión) hace que el threshold deba ser alto.

## Los 3 estados implícitos

| Variable | Cómo medirla |
|----------|--------------|
| **ADC safety window** | ¿Puede sobrevivir 30s sin mí? Influye: HP, Hechizos, jungler enemy proximity, freeze state |
| **Wave state** | Crash (tuyo) ✅ / Bounce (tuyo) ✅ / Push lento aliado ❌ / Push lento enemigo ⚠ |
| **Objetivo concreto** | Mid push, jungle invade, scuttle fight, Drag/Grub spawn imminente |

## Implicancia para el motor (futuro)

El motor actual del Draft Advisor **no modela el roaming** porque opera en champ select, no en partida. Pero esta lógica respalda dos features futuros:

### 1. Score de "roam-friendly setup"
Algunas combinaciones ADC+supp permiten más roams (ADC con waveclear seguro: Caitlyn+supp → ADC puede freeze/bouncer solo). Otras lo prohíben (ADC inmóvil + dive enemy: Jinx+supp vs Zed+Naut → supp NO puede roam).

Este score se podría incorporar como sub-factor de `ally_synergy` o como parte de `play_pattern_template`.

### 2. Texto de coaching en `enabled_play_pattern`
La explicación generada por el motor debería mencionar las **ventanas de roam** explícitas:

> "Mid (50-70 pal): después de **crash bot a torre minuto X:00**, tenés 30-45s para roamear a mid si está empujado, o tradear visión en river."

Esto enriquece el output sin necesidad de cambios en el motor — solo template engineering en `_generate_play_pattern_supp()`.

## Material para coaching/03-roaming-mastery.md

Este doc es **directo input** para el archivo de coaching `coaching/03-roaming-mastery.md` planteado en el prompt para NotebookLM. La regla de los 3 chequeos es el corazón del documento.

> **Pendiente:** crear `KB/coaching/03-roaming-mastery.md` con esta regla + la regla 4 ("Roam timer") + la regla 5 ("Recall tras roam exitoso para no perder oleada").

## Glosario relevante (de `guia de estudio` p4)

- **Roaming**: acción del soporte de abandonar temporalmente el carril inferior para generar presión o visión en otras áreas del mapa.
- **Freeze**: mantener la oleada cerca de tu torre sin empujarla para forzar overextend del enemigo.
- **Crash**: empujar la oleada hasta que muera bajo torre enemiga (genera ventana de tempo).
- **Bounce**: usar el rebote natural de la oleada después de un crash.
