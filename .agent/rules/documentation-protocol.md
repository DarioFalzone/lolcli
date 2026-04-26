# Protocolo Antidraft Documentacional

**Regla central:** La documentación se actualiza en el mismo commit que el código que la origina. No existe "documentaré después". Si el código cambió y la documentación no, el commit no está completo.

---

## Qué cuenta como "iteración significativa"

| Tipo | Ejemplos |
|------|---------|
| Feature nuevo | Nuevo endpoint, nueva página, nueva funcionalidad |
| Extensión de feature | Agregar un parámetro, una variante, un modo |
| Refactor que cambia contratos | Renombrar schemas, cambiar payloads, cambiar rutas |
| Cambio en cómo se levanta el proyecto | Nuevo puerto, nuevo comando, nuevo script |
| Migración de datos o tokens | Renombrar tokens CSS, cambiar estructura de JSON |
| Bug fix con impacto visible | Si el fix cambia comportamiento que el usuario conocía |

**No requiere documentación:** fixes de typo, cambios de linting puro, ajustes internos sin impacto en la API ni en cómo se usa el sistema.

---

## Mapa de responsabilidades

### `bitacora_de_cambios.md` (raíz)
**Siempre.** Para toda iteración significativa.

```markdown
## [YYYY-MM-DD] Título breve

### Qué se hizo
- Descripción concisa de cada cambio principal

### Archivos clave
- `ruta/archivo.py` — qué cambió y por qué (la decisión, no el cómo)
```

---

### `AGENTS.md` (raíz)
Actualizar cuando cambie:
- La **arquitectura**: un subsistema nuevo, un servidor nuevo, un cambio de puerto
- El **mapa de subsistemas** (tabla de módulos)
- Los **paths críticos** (si se mueven archivos importantes)
- La **versión** del proyecto

---

### `docs/getting-started.md`
Actualizar cuando cambie:
- Un comando de instalación, ejecución o generación
- Un puerto o ruta de acceso
- Un prerequisito nuevo
- Un script nuevo en `scripts/`

---

### `docs/draft_advisor/README.md`
Actualizar cuando cambie:
- Un endpoint (ruta, método, payload, respuesta)
- El schema `DraftState` o `RecommendationOutput`
- Los archivos de datos cargados al inicio (`support_profiles.json`, etc.)
- El motor de scoring (nuevos factores, pesos cambiados)
- El flujo frontend (nuevas interacciones, nuevos estados)
- Upgrades activados o comentados

---

### `docs/design-system.md`
Actualizar cuando cambie:
- Un token CSS canónico (nuevo, renombrado, eliminado)
- El estado de migración de una surface
- Una clase de componente nueva en `components.css`
- El orden de carga de hojas de estilo en `index.html`

---

### Docs de subsistema (`docs/<subsistema>/README.md`)
Si el subsistema no tiene docs, **crearlo** cuando el subsistema sea significativo.
Mínimo que debe tener:
1. Cómo levantarlo
2. Sus endpoints / comandos principales
3. Su estructura de archivos

---

## Checklist antes de hacer el commit final

```
[ ] bitacora_de_cambios.md actualizada con fecha de hoy
[ ] AGENTS.md actualizado si cambió arquitectura o puertos
[ ] docs/getting-started.md actualizado si cambió algún comando
[ ] docs/draft_advisor/README.md actualizado si cambió API o datos
[ ] docs/design-system.md actualizado si cambió algún token o componente
[ ] Upgrades pendientes documentados en CLAUDE.md (sección "Upgrades conocidos")
[ ] Si un feature quedó comentado/incompleto → hay un TODO comment en el código
     con instrucciones claras de cómo activarlo
```

---

## Cómo documentar upgrades comentados en código

Cuando se comenta código como "upgrade futuro", el bloque debe incluir:

```html
<!--
UPGRADE FUTURO: Nombre del Feature
===================================
Descripción de qué hace este bloque.
Estado del backend: [ya implementado / pendiente]
Para activar:
  1. Paso concreto 1
  2. Paso concreto 2
  3. Verificar que X funciona
-->
```

Y registrar en `CLAUDE.md` sección "Upgrades conocidos".

---

## Anti-patrones a evitar

- ❌ Hacer un commit de código sin actualizar la bitácora
- ❌ Dejar un TODO en el código sin documentar en `CLAUDE.md`
- ❌ Cambiar un endpoint y no actualizar el README del subsistema
- ❌ Agregar un comando nuevo y no actualizar `getting-started.md`
- ❌ "Documentaré en el próximo commit" — si el código ya está, la doc va en el mismo commit
- ❌ Describir QUÉ hace el código en lugar de POR QUÉ se tomó esa decisión
