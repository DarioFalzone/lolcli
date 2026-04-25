# Contexto consolidado - ADC Draft Advisor

- Fecha de actualizacion: 2026-04-12
- Alcance: basado en artefactos del `brain/38fb04ce-8d98-45f4-b9c3-f662aa484fd9`, no en un relevamiento fresco del codigo completo de `LOLCLI`

## 1. Resumen ejecutivo

El proyecto documentado corresponde a un `ADC Draft Advisor` para League of Legends. Su objetivo es asistir la seleccion de ADCs segun composicion aliada, composicion enemiga y contexto de draft, priorizando explicabilidad y credibilidad de los datos presentados al usuario.

Los artefactos leidos reflejan una solucion con:

- backend en `FastAPI`
- UI web tipo SPA servida por el propio backend
- base de conocimiento curada en archivos JSON
- motor de scoring multifactor para recomendaciones
- validadores orientados a coherencia semantica y frescura de datos

El estado general que reflejan los documentos es de una solucion funcional que paso por varias fases: auditoria, implementacion MVP, formalizacion de una capa KB mas robusta y endurecimiento de validaciones sobre versionado.

## 2. Evolucion del trabajo

### Fase inicial: auditoria tecnica e inventario reusable

Los primeros planes documentan una auditoria del proyecto mayor `LOLCLI`, identificando activos reutilizables como:

- cliente Riot / Data Dragon
- patrones de `FastAPI`
- manejo de datos y loaders
- assets visuales de campeones
- listas base de ADCs

En esa etapa tambien se registraron riesgos fuertes:

- ausencia de una base de conocimiento estrategica real
- ausencia de un motor de recomendacion por draft
- falta de parsing de screenshots
- necesidad de una UI especializada para draft

### Fase de implementacion MVP

La documentacion evolutiva muestra que luego se implemento el MVP del asesor, cubriendo:

- knowledge base inicial
- scoring engine
- backend API
- frontend UI

Tambien se registran escenarios de prueba con resultados concretos y una validacion funcional positiva de la experiencia visual.

### Fase posterior: sistema KB mas formal

En una etapa posterior, los planes mutan hacia una arquitectura mas madura de conocimiento, con:

- folder dedicado para KB
- research notes con frontmatter
- manifiestos de fuentes
- retrieval por metadata
- evaluaciones tipo golden drafts
- scripts de validacion e ingesta

Esto muestra una evolucion desde un MVP funcional hacia una base mas mantenible y trazable.

### Fase mas reciente: correccion semantica de versionado

La iteracion mas reciente corrige una confusion entre:

- `live_patch_label`: version visible para el usuario
- `static_data_version`: version tecnica usada para Data Dragon

La documentacion deja claro que ese desacople fue tratado como un tema de credibilidad del producto, no solo como un detalle tecnico.

## 3. Estado funcional consolidado

Segun los artefactos leidos, el estado funcional consolidado es el siguiente:

- base de conocimiento implementada
- motor de scoring implementado
- UI y API funcionando
- endpoint de version desacoplado en `/meta/version-info`
- validadores adicionales construidos para endurecer la consistencia de datos

Los documentos mencionan explicitamente:

- `172` campeones en `champion_base.json`
- `24` perfiles ADC profundos
- `41` perfiles prioritarios no-ADC

Tambien se documenta que:

- el badge/UI de version debia mostrar algo como `Patch 26.7 (Data: 16.7.1)`
- las validaciones estructurales y remotas se ejecutaron con resultado positivo
- la UI del draft advisor llego a un nivel funcional suficiente para pruebas end-to-end

## 4. Arquitectura y decisiones clave

Los documentos dejan asentadas varias decisiones importantes:

- SPA simple servida por `FastAPI`, en lugar de mover el producto a un stack separado tipo React/Vite
- JSON como fuente de verdad curada para conocimiento estrategico, en lugar de SQL para esa capa
- motor de recomendacion basado en scoring multifactor, no en reglas rigidas o un arbol de decision simple
- parsing visual pensado a futuro con enfoque multimodal, evitando depender desde el inicio de OCR o template matching clasico

En terminos de producto, la prioridad visible en los documentos es doble:

- recomendacion util para el usuario
- datos y metadatos presentados de forma semantica correcta

## 5. Evidencia de validacion documentada

La evidencia leida en `walkthrough`, `resolved` y `browser scratchpads` deja los siguientes puntos:

### Caso Nautilus

En una validacion puntual con Nautilus como aliado, se documento:

- top pick observado: `Jinx`
- score observado: `70.6`
- alternativas observadas: `Aphelios`, `Tristana`, `Kai'Sa`

### Caso draft mas completo

En una validacion end-to-end con aliados `Nautilus`, `Maokai`, `Orianna` y enemigos `Zed`, `Lee Sin`, se documento:

- top pick observado: `Tristana`
- score observado: `70.2`
- lectura de composicion: enfoque front-to-back con amenaza critica sobre ADC

### Conclusion visual y UX

La documentacion del browser describe una UI:

- responsiva
- visualmente solida
- con modal de seleccion funcional
- con resultados explicados mediante score breakdown, strengths, risks y alternativas

### Incidencia documentada

Queda explicitamente registrado un problema en portraits / carga de imagenes:

- la app seguia intentando cargar `0.jpg`
- se esperaba una ruta del estilo `${id}_Classic.jpg`

La documentacion plantea como explicacion posible:

- fix no desplegado correctamente
- o problema de cache

## 6. Riesgos, huecos o pendientes visibles

Siguen visibles en la documentacion los siguientes riesgos o pendientes:

- riesgo de deriva semantica entre patch visible al usuario y data version tecnica
- riesgo de contaminacion por fuentes o familias no deseadas, por ejemplo material fuera del producto objetivo
- pendiente documentado sobre portraits / splash loading
- necesidad de no asumir que el estado actual del codigo coincide exactamente con lo narrado por los artefactos sin una inspeccion fresca del repo

Esto ultimo es importante: este documento resume evidencia documental, no reemplaza una verificacion tecnica actual del codigo fuente.

## 7. Fuentes utilizadas

### Artefactos principales

- `task.md`
- `implementation_plan.md`
- `walkthrough.md`

### Artefactos evolutivos / resolved

- `task.md.resolved*`
- `implementation_plan.md.resolved*`
- `walkthrough.md.resolved*`

### Evidencia de ejecucion

- `browser/scratchpad_1y4vxyag.md*`
- `browser/scratchpad_kv1h1uv2.md*`
- `browser/scratchpad_u0k28pde.md*`
- `.system_generated/steps/81/content.md`
- `.system_generated/steps/87/content.md`

### Scripts auxiliares

- `scratch/validate_phase1.py`
- `scratch/validate_phase2.py`

## 8. Nota de alcance

Este documento:

- no modifica `CONTEXTO_DEL_REPO.md`
- no actualiza `INDEX.md` ni `INDICE_MAESTRO.md`
- no mezcla este resumen con un levantamiento general de todo `LOLCLI`
- queda acotado al paquete documental del `brain/38fb04ce-8d98-45f4-b9c3-f662aa484fd9`
