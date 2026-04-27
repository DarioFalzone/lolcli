# 08 — Ecosistema Crash & Move (Control de Oleadas)

> **Fuente:** `Support_Architecture_Dossier.pdf` p11 + `imagen guia.png` (sector "Ventana de Roaming Crash-and-Move")

## Las 3 fases del ciclo

El ecosistema **Crash & Move** es la herramienta más subestimada del soporte. Define ventanas de **30-45 segundos de inmunidad** después de cada crash.

### Fase 1 — El Crash (Minuto X:00)
```
Tu oleada bot ──────────────────► |TORRE ENEMIGA|
                                    súbditos mueren
                                    enemy ADC + supp obligados a recolectar
```

Empujás violentamente la oleada bajo la torre rival. **El enemigo está obligado a quedarse** allí 30-45s para no perder XP/oro.

### Fase 2 — La Ventana de Tempo (X:05 — X:35)
```
Tu oleada ya en torre              |TORRE ENEMIGA|
        │                                  │
        │ Vos rotás ◄────────── Inmunidad ──┘
        ▼
   ┌─ A. Visión profunda en river/jungle enemiga (control wards en tribush, baron pit)
   ├─ B. Gank a carril central (mid empujado)
   └─ C. Acompañar jungla a smite contestado (scuttle, grubs)
```

**30 a 45 segundos de inmunidad a castigo.** Es la ventana donde el supp puede:
- Profundizar visión en jungla enemiga
- Gankear mid si está empujado
- Acompañar al jungla en objetivos contestados

### Fase 3 — El Rebote (X:45)
```
Oleada enemiga ◄──────────────────|TU TORRE|
       (rebota tras crash)            tu ADC protegido
```

La oleada enemiga **rebota** y choca contra tu torre. **Volvés exactamente cuando** ese rebote ocurre, protegiendo a tu ADC de un dive del enemigo.

## La línea de tiempo completa

```
X:00 ┊ Crash (bot push to enemy tower)
X:05 ┊ Inmunidad activada — empieza ventana
X:15 ┊ Pico de profundidad útil (river/jungle scan, mid gank)
X:25 ┊ Empezás a regresar
X:35 ┊ Llegás a tu lado del mapa
X:45 ┊ Rebote: oleada enemiga choca contra tu torre, vos ya estás peeling
```

## Por qué funciona (el "tempo asimétrico")

> *"El soporte regresa exactamente cuando la oleada enemiga choca contra tu torre, protegiendo al tirador de un Dive."*
> — Support Architecture Dossier, p11

Es **timing perfecto**: la oleada actúa como **timer natural** de tu rotación. No necesitás reloj — la oleada te dice cuándo volver.

## Implicancia para el motor

El motor del Draft Advisor podría sugerir, en `enabled_play_pattern`, **menciones explícitas a la ventana Crash & Move** para los soportes con buena rotación:

### Champions que abusan Crash & Move (alta J Prox)
- **Pyke** — invisibilidad en river, retorno por estado del rebote
- **Bard** — meeps + tunnel para retornos
- **Thresh** — flay+lantern setup en mid después de crash bot
- **Rakan** — alta movilidad para roams cortos
- **Senna** — souls en river durante rotación

### Champions que NO abusan Crash & Move (baja S Prox)
- **Soraka** — sin movilidad, debería B-Prox alta
- **Yuumi** — anclado al ADC
- **Milio** — kit centrado en peeling, no en roaming
- **Janna** — con shields para enable, pero sin gap close

## Aplicación en `play_pattern_template`

Para soportes con high-rotation potential:

> "Mid (50-70 pal): **después del crash bot a X:00**, tenés ~30s de ventana. Rotá a mid si está pusheado, o agarrá control ward en tribush enemy. **Volvés a X:45** cuando rebota la oleada."

Para soportes anchored (Soraka, Yuumi):

> "Mid (50-70 pal): tu rol es **B Prox alta** — quedate cerca del ADC. Solo abandonás carril si hay teamfight directo o objetivo claro. Crash & Move no aplica."

## Material para coaching/04-laning-fundamentals.md

Crash & Move es **uno de los 5 lane principles fundamentales** que respetan los pros (Dossier p11 implícito):

1. ✅ Matchup-aware lvl 2 race
2. ✅ Wave management según matchup
3. ✅ **Crash & Move tempo windows** (este doc)
4. ✅ Recall timing junto al ADC (sincronizar back)
5. ✅ Side dependency (jugar lado seguro vs lado peligroso)

Esto va al doc `KB/coaching/04-laning-fundamentals.md` cuando se genere.
