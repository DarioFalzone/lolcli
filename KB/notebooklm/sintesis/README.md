# Sintesis NotebookLM

Sintesis consolidada de las fuentes NotebookLM del Draft Advisor. Reemplaza los nueve documentos numerados y el indice fragmentado para dejar un unico punto navegable.

## Fuentes procesadas

- `KB/notebooklm/Support_Architecture_Dossier.pdf`: arquitectura del rol de soporte, pick order, composiciones, triangulo estrategico, sinergias, economia, roaming y meta regional.
- `KB/notebooklm/Nacion_Digital_LoL.pdf`: analisis sistemico y sociocultural de LoL.
- `KB/notebooklm/imagen guia de estrategia de seleccion y macrogame.png`: infografia maestra.
- `KB/notebooklm/guia de estudio estrategia de soporte`: guia de estudio y glosario.

## Ejes procesables

| Eje | Idea util | Aplicacion |
|-----|-----------|------------|
| Paradigma del arquitecto | El soporte dicta condiciones de juego mediante draft, economia y macro | Justifica pesos altos de `ally_synergy` y `comp_gap_fill` |
| Pick order | Top tiene mayor riesgo de counter; ADC/Jungla son mas seguros para blind | Ajustar `pick_position`, especialmente late/counter |
| Cinco composiciones | Attack, Catch, Protect, Siege/Poke y Split tienen predominancias | Alimenta `comp_predominance.json` |
| Triangulo moderno | Engage > Poke, Poke > Sustain, Sustain/Disengage > Engage | Alimenta `strategic_triangle.json` |
| Sinergias medidas | Parejas ADC+Support con WR > 53% son data, no opinion | Alimenta `measured_synergies.json` |
| Economia asimetrica | El soporte multiplica valor con evoluciones e items baratos | Enriquecer `item_path` y `play_pattern_template` |
| Regla de 3 chequeos | Roam solo si ADC esta seguro, oleada permite salir y hay objetivo real | Coaching y templates de roaming |
| Crash & Move | Crash bot crea ventana de 30-45s para vision, invade o mid gank | Coaching y templates por soporte roamer |
| Meta regional | LCK prioriza control; LPL prioriza engage/skirmish | Modula preferencias por `queue_type`/estilo |

## Resumen ejecutivo

1. El soporte moderno es arquitecto, no acompanante. Su impacto principal viene de habilitar win conditions, multiplicar recursos baratos y controlar tempo/vision.
2. El triangulo estrategico es una regla central del motor: Engage castiga Poke; Poke castiga Sustain; Sustain y, sobre todo, Disengage castigan Engage.
3. Las sinergias medidas deben valer mas que heuristicas blandas. Ejemplos integrados: Samira+Nautilus, Lucian+Nami, Ashe+Seraphine y Jinx+Thresh.
4. El ultimo pick rojo es el recurso mas valioso del draft, pero el soporte suele operar en riesgo moderado; cuando el contexto es late/counter, `enemy_matchup` debe pesar mas.
5. El draft debe leerse como ingenieria de composiciones, no como suma de campeones individuales.

## Reglas integradas al motor

- `data/draft_advisor/kb/structured/measured_synergies.json`: parejas ADC+Support con winrate medido y heuristicas pro-scene.
- `data/draft_advisor/kb/structured/strategic_triangle.json`: triangulo fine-grained y eje Disengage > Engage.
- `data/draft_advisor/kb/structured/comp_predominance.json`: predominancia entre composiciones.
- `data/draft_advisor/kb/structured/jungler_archetypes.json`: arquetipos de jungla y modificadores para bot lane.
- `data/draft_advisor/kb/structured/queue_style_hints.json`: sesgos por tipo de cola.

## Pendientes utiles

- Enriquecer `play_pattern_template` con first back, item path y condiciones situacionales.
- Agregar coaching de roaming basado en 3 chequeos y Crash & Move.
- Refinar boosts de J Prox y B Prox cuando el jungla aliado o el ADC requieran cobertura especifica.
- Mantener el material original en PDF/imagen como fuente; esta sintesis es el indice operativo para agentes.
