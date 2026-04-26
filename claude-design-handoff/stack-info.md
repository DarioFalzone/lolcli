# Stack Info — riot_lol_cli

> Stack técnico real del proyecto. Información clave para que Claude Design sepa **qué tipo de output puede consumir** este codebase.

## ⚠️ Lo más importante

**Este proyecto NO usa un framework JavaScript moderno (React, Vue, Svelte, etc.).**

El frontend es:
- **HTML + CSS + JavaScript vanilla** (Draft Advisor SPA).
- **Templates Jinja2** que renderizan a HTML estático autocontenido (Match History, Splash Viewer).
- **HTML embebido como strings en Python** (Meta Dashboard — legacy y a migrar).

**Implicación para Claude Design:**
- Si Claude Design genera componentes en React/Vue, hay que **traducirlos a HTML/CSS/JS plain** para integrarlos.
- O bien, el output de Claude Design puede usarse como **specs visuales** (Figma-like) y el equipo los implementa en HTML+CSS.
- Si se quiere que Claude Design genere código consumible directamente, **especificar HTML+CSS plain** o **Web Components**.

---

## 1. Backend

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Lenguaje | Python | `>=3.9` |
| Framework web | FastAPI | `>=0.109.0` |
| Server ASGI | Uvicorn (`[standard]`) | `>=0.27.0` |
| Validación | Pydantic | `>=2.0.0` (V2 estricto) |
| HTTP cliente sync | requests | `>=2.25.0` |
| HTTP cliente async | httpx | `>=0.27.0` |
| ORM / DB | SQLAlchemy | `>=2.0.0` |
| Motor DB | SQLite (local) | — |
| Templates | Jinja2 | `>=3.1.0` |
| CLI | Click | `>=8.0.0` |
| Imágenes | Pillow | `>=10.0.0` |
| Env vars | python-dotenv | `>=1.0.0` |

Fuente: [`pyproject.toml`](../pyproject.toml), [`requirements.txt`](../requirements.txt)

### 1.1 Servidores FastAPI

| Servidor | Puerto | Entry point |
|----------|--------|-------------|
| Draft Advisor | 8001 | `riot-lol-draft-advisor` (script) → `riot_lol_cli.draft_advisor.server:run` |
| Meta Analyzer API | 8000 | `riot-lol-meta-api` (script) → `riot_lol_cli.api_server:run` |

---

## 2. Frontend

### 2.1 Draft Advisor SPA (la "app principal")

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Markup | HTML5 plain | 1 archivo: `index.html` (174 líneas) |
| Estilos | CSS plain | 1 archivo: `styles.css` (954 líneas) |
| Lógica | JavaScript vanilla (ES6+) | 1 archivo: `app.js` |
| State management | Plain object literal | `const state = { … }` global |
| Build tool | **Ninguno** | Servido directamente por FastAPI con `StaticFiles` |
| Bundler | **Ninguno** | Sin webpack/vite/esbuild |
| Package manager | **Ninguno** | No hay `package.json` ni `node_modules` |
| TypeScript | **No** | JS plain |
| CSS preprocessor | **No** | CSS nativo con custom properties |
| CSS framework | **No** (no usa Tailwind, Bootstrap, etc.) | Tokens CSS propios |

**Patrón de servir:**
```python
# server.py
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/assets/splash_arts", StaticFiles(directory=str(assets_dir)))
```

```html
<!-- index.html -->
<link rel="stylesheet" href="/static/styles.css?v=2">
<script src="/static/app.js?v=2"></script>
```

### 2.2 Match History + Splash Viewer (HTML estático)

| Capa | Tecnología |
|------|-----------|
| Markup + estilos | Templates Jinja2 (`.html`) con `<style>` inline |
| Lógica | JavaScript vanilla embebido o externo (`assets/splash-viewer-app.js`) |
| Generación | Comando CLI: `python main.py … --html-template …` |
| Output | Archivo `.html` autocontenido (offline-friendly) |

### 2.3 Meta Dashboard (legacy)

| Capa | Tecnología |
|------|-----------|
| Markup + estilos + JS | **Strings literales en Python** (`dashboard_enhanced.py`) |
| Generación | Función `save_enhanced_dashboard()` |
| Output | Archivo HTML escrito a disco |

**Status**: legacy. Plan implícito de migrar a Jinja2.

---

## 3. Fuentes externas

| Recurso | URL |
|---------|-----|
| Google Fonts (Inter) | `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap` |
| Google Fonts (Outfit) | `https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap` |
| Google Fonts (Spiegel) | `https://fonts.googleapis.com/css2?family=Spiegel:wght@400;700;900&display=swap` |
| Riot Data Dragon CDN (assets) | `https://ddragon.leagueoflegends.com/cdn/<version>/img/champion/...` |
| Riot Data Dragon (datos) | `https://ddragon.leagueoflegends.com/cdn/<version>/data/en_US/...` |

**Observación**: el SPA hace `<link>` a Google Fonts directamente (no auto-host). [A confirmar] si esto es aceptable o si se quiere self-hostear las fuentes para offline-first.

---

## 4. Convenciones de naming

Fuente: `.agent/rules/coding-style.md` y observación del código.

### 4.1 Python (backend)

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Variables | `snake_case` | `match_data`, `draft_state` |
| Funciones | `snake_case` | `get_summoner_by_name()` |
| Clases | `PascalCase` | `RiotClient`, `DatabaseManager`, `SupportProfile` |
| Constantes | `UPPER_SNAKE_CASE` | `BASE_DIR`, `DATA_DRAGON_VERSION` |
| Archivos | `snake_case` | `data_collector.py`, `champion_data.py` |
| Directorios | `snake_case` o `kebab-case` | `meta_analyzer/`, `draft_advisor/` |

### 4.2 CSS

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Custom properties | `--kebab-case` | `--hextech-gold`, `--bg-primary`, `--shape-radius-lg` |
| Class selectors | `kebab-case` (BEM-ish, sin BEM estricto) | `.champion-slot`, `.top-pick-card`, `.card-header` |
| Modifier classes | `kebab-case` separado | `.filled`, `.ally`, `.enemy`, `.active`, `.disabled` |
| ID selectors | `kebab-case` | `id="champion-search"`, `id="recommend-btn"` |

**Convención BEM observada (parcial):**
- Block: `.card`
- Element: `.card-header`, `.card-body`
- Modifier: `.card.disabled` (composición de clases)

No es BEM estricto (no usa `__` ni `--` separadores) pero la idea está.

### 4.3 JavaScript

```js
// State global mutable (anti-pattern moderno pero funcional)
const state = { … };

// Funciones top-level event-driven (no clases, no modules)
function openChampionPicker(team, index) { … }
function closeModal() { … }
function getRecommendation() { … }

// Async-await sin librerías externas
async function init() {
  const res = await fetch('/api/v1/draft/champions');
  state.champions = await res.json();
}
```

**Camelcase** consistente. **Sin `let`/`const` rigurosos** — usa `const` para estado top-level y `let` puntual.

---

## 5. Convenciones de UI / accessibility

### 5.1 Accesibilidad observada

| Práctica | Estado |
|----------|--------|
| `lang="es"` en `<html>` | ✅ presente |
| `<meta charset="UTF-8">` | ✅ |
| `<meta name="viewport">` | ✅ |
| Roles ARIA explícitos | ❌ no se ven |
| `aria-label` en botones icon-only | ❌ no se ven (los botones tienen texto o emoji) |
| `tabindex` explícitos | ❌ |
| Skip-to-content links | ❌ |
| Color contrast WCAG AA/AAA | [A confirmar — dark mode con texto crema sobre navy debería pasar; el gold sobre navy oscuro habría que medirlo] |
| Focus states visibles | ⚠️ parcial (algunos `:focus { border-color }` pero no `:focus-visible` ni outlines accesibles consistentes) |
| Reduced motion | ❌ no hay `@media (prefers-reduced-motion)` |

**Recomendación para Claude Design**: incluir accesibilidad como first-class. El proyecto está delgado en este eje y es deuda conocida.

### 5.2 Internacionalización

- Idioma único: **español argentino**.
- No hay sistema de i18n (no `gettext`, no archivos de locales).
- Strings hardcodeados en HTML / Python.

[A confirmar — si se planea soportar inglés u otros idiomas en el futuro].

---

## 6. Build / Deploy

### 6.1 Build

```bash
# Setup
python -m venv .venv
source .venv/bin/activate    # o .venv\Scripts\activate en Windows
pip install -e .             # instala el paquete con scripts CLI

# o
pip install -r requirements.txt
```

**No hay build step para frontend** — los `.html`/`.css`/`.js` se sirven tal cual.

### 6.2 Run

```bash
# Draft Advisor (puerto 8001)
riot-lol-draft-advisor
# o: python -m riot_lol_cli.draft_advisor.server

# Meta Analyzer API (puerto 8000)
riot-lol-meta-api
# o: python scripts/run_api.py

# CLI (genera HTML estáticos)
python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5
```

### 6.3 Deploy

[A confirmar — actualmente el proyecto corre 100% local. No hay Dockerfile, ni GitHub Actions, ni configuración de hosting].

---

## 7. Testing

| Aspecto | Estado |
|---------|--------|
| Framework | pytest 7.4+ con pytest-asyncio + pytest-cov |
| Tests existentes | Modelos Pydantic, Async API client (parciales) |
| Coverage actual | ~52% según `.agent/rules/testing-guidelines.md` |
| Coverage required en CI | >30% |
| Tests de UI / E2E | **No** (no hay Playwright, Cypress, etc.) |
| Visual regression tests | **No** |

---

## 8. Repository structure (top-level)

```
LOLCLI/
├── pyproject.toml                # build config + dependencies
├── requirements.txt              # runtime deps (mirror)
├── requirements-dev.txt          # dev deps (pytest, ruff)
├── .editorconfig                 # editor config
├── .gitignore
├── README.md
├── AGENTS.md                     # contexto para agentes IA
├── .agent/                       # rules para agentes
│   └── rules/
│       ├── coding-style.md
│       ├── commit-conventions.md
│       └── …
├── KB/                           # ⭐ base de conocimiento texto (Support Advisor)
│   ├── README.md
│   ├── filosofia-de-pickeo.md
│   └── …
├── claude-design-handoff/        # ⭐ ESTA CARPETA
│   ├── design-system.md
│   ├── components-inventory.md
│   ├── screens-flows.md
│   ├── brand-context.md
│   ├── stack-info.md
│   └── README.md
├── src/
│   └── riot_lol_cli/             # paquete Python instalable
│       ├── cli.py                # Click CLI
│       ├── api.py                # RiotClient (sync)
│       ├── api_async.py          # AsyncRiotClient (httpx)
│       ├── api_server.py         # FastAPI Meta Analyzer
│       ├── draft_advisor/        # ⭐ Subsistema principal de UI
│       │   ├── server.py         # FastAPI app
│       │   ├── api.py            # router /api/v1/draft/*
│       │   ├── scoring.py        # motor de scoring
│       │   ├── champion_data.py
│       │   ├── schemas.py        # Pydantic V2 models
│       │   └── static/           # ⭐ FRONT END
│       │       ├── index.html
│       │       ├── styles.css
│       │       └── app.js
│       ├── meta_analyzer/        # detección de meta + tier lists
│       ├── meta_api/             # rutas FastAPI del meta analyzer
│       ├── database/             # SQLAlchemy models
│       ├── paths.py              # BASE_DIR, ASSETS_DIR, etc.
│       ├── settings.py           # ports, env vars
│       └── …
├── templates/                    # Jinja2 templates (root, autoritativo)
│   ├── claude-4-5.html           # Match history export (2329 líneas)
│   ├── splash-viewer.html        # Splash gallery
│   └── naafiri-champion.html
├── data/
│   ├── adc_champions.json
│   ├── junglers_list.json
│   ├── supports_list.json        # ⭐ nuevo (Support Advisor)
│   ├── splash-manifest.json
│   ├── meta_analyzer.db          # SQLite (gitignored)
│   └── draft_advisor/
│       ├── adc_profiles.json
│       ├── support_profiles.json # ⭐ nuevo
│       ├── priority_profiles.json
│       ├── scoring_weights.json
│       └── kb/
│           ├── structured/
│           │   └── support_archetypes.json
│           └── research/
├── assets/
│   ├── splash_arts/              # 2019 JPGs (gitignored, descargables)
│   ├── items/                    # 623 PNGs de íconos de ítems
│   └── splash-viewer-app.js      # JS del splash viewer
├── scripts/
│   ├── run_api.py
│   ├── setup_meta_analyzer.py
│   ├── download_splash_arts.py
│   └── bat/                      # batch scripts Windows
├── outputs/                      # HTML generados (gitignored)
├── docs/                         # documentación
├── tests/                        # pytest tests
└── _archive/                     # proyectos legacy (research, scraping)
```

---

## 9. Resumen para Claude Design

**¿Qué tipo de output del design es consumible directamente?**

| Output | Consumible | Notas |
|--------|-----------|-------|
| Specs visuales (estilo Figma) | ✅ | Ideal — el equipo los traduce a HTML/CSS plain |
| Tokens CSS exportables | ✅ | Reemplazables directos en `:root { … }` |
| Componentes en HTML+CSS plain | ✅ | Pegar directamente |
| Componentes en React/Vue/Svelte | ⚠️ | Requiere traducción manual a HTML+CSS+vanilla JS |
| Web Components nativos | ✅ | El proyecto los soportaría sin friction (vanilla JS) |
| Tailwind classes | ⚠️ | El proyecto NO usa Tailwind. Habría que adoptarlo o portar tokens |

**Recomendación**: Generar **tokens CSS** + **componentes en HTML+CSS plain** + **specs visuales** como output principal. Si Claude Design solo soporta React, traducir manualmente.

---

## 10. Checklist de "data viva" para Claude Design

Esto NO es decisión de design, es **información del estado actual** que ayuda al diseñador a no especular:

- ✅ Hay 24 ADC profiles + 17 Support profiles + 41 Priority profiles
- ✅ Hay 171 campeones con base data (champion_base.json)
- ✅ Hay 2019 splash arts JPG en assets/ (descargables)
- ✅ Hay 623 íconos de ítems PNG en assets/items/
- ✅ Patch base de datos: 16.7
- ✅ Default target_role del Draft Advisor: **support** (recientemente cambiado de adc)
- ⚠️ Ningún botón / link enlaza al cliente de LoL (el draft advisor es paralelo, manual)
