# Onboarding Rápido y Mapa Atómico ( riot_lol_cli )

¡Bienvenido al repositorio `riot_lol_cli`! Esta guía está diseñada para que cualquier desarrollador o agente de IA adquiera contexto experto y comience a operar en **3 minutos** sin necesidad de leer todo el código base de golpe.

---

## 1. El Ecosistema de un Vistazo
`riot_lol_cli` es un único proyecto de Python (no un monorepo) que consolida un CLI Click y **7 servidores FastAPI independientes** que interactúan localmente.

El punto de entrada principal para el usuario es el **Home Hub (puerto 8080)**, que sirve de puente hacia el resto de las interfaces (estilo Hextech oscuro con tokens CSS vainilla).

### Tabla Maestra de Servicios

| Servicio | Puerto | Comando de Arranque | Archivo Core de Lógica | Propósito Principal |
| :--- | :--- | :--- | :--- | :--- |
| **Home Hub** | `8080` | `python -m riot_lol_cli.home.server` | `src/riot_lol_cli/home/` | Panel central y launcher de todos los servicios |
| **Meta API** | `8000` | `python scripts/run_api.py` | `src/riot_lol_cli/meta_api/` | Consenso, anomalías y cockpit de Esports/Jungle |
| **Draft Advisor** | `8001` | `python -m riot_lol_cli.draft_advisor.server` | `src/riot_lol_cli/draft_advisor/` | Recomendador ADC/Supp/Jungle con motor heurístico |
| **Meta Scraper** | `8002` | `python -m riot_lol_cli.meta_scraper.server` | `src/riot_lol_cli/meta_scraper/` | Scraper Playwright de OP.GG, LoLalytics y U.GG |
| **Jungle Meta** | `8003` | `python -m riot_lol_cli.jungle_meta.server` | `src/riot_lol_cli/jungle_meta/` | Tier list curada por parche (fuente para el Advisor) |
| **Items Browser** | `8004` | `python -m riot_lol_cli.items_browser.server` | `src/riot_lol_cli/items_browser/` | Catálogo interactivo de ítems de LoL (EN/ES) |
| **Patch Notes** | `8005` | `python -m riot_lol_cli.patch_notes.server` | `src/riot_lol_cli/patch_notes/` | Comparador, diff de versiones y buscador FTS |

---

## 2. Mapa Conceptual de Paths

*   `src/riot_lol_cli/` ➔ Paquete de código fuente activo.
*   `data/` ➔ Base de datos SQLite (`meta_analyzer.db`), JSONs curados, KB estructurada y caches.
*   `assets/` ➔ Imágenes locales de ítems y splash arts indexados (~3000 skins).
*   `templates/` ➔ Plantillas HTML Jinja2 (como `claude-4-5.html` para la exportación de partidas).
*   `scripts/` ➔ Scripts de mantenimiento y lanzadores rápidos de Windows (`scripts/bat/`).
*   `projects/active/` ➔ Manifiestos navegables por proyecto (documentación y deudas). No duplicar código aquí.

---

## 3. Las Tres Reglas de Oro Transversales

### Regla I: El Principio de Atomización
Para garantizar un control humano riguroso y facilitar la auditoría, **escribe código minimalista y archivos altamente cohesionados**:
*   Evita duplicación de código e imports redundantes.
*   Mantén los archivos en la menor cantidad de líneas posibles.
*   Si una funcionalidad excede el alcance del módulo, extraela a una función pura o a un helper de utilidad.

### Regla II: Cero Mojibake (UTF-8 sin BOM)
> [!IMPORTANT]
> Todos los archivos del repositorio (JSON, Python, Markdown, HTML, CSS) se leen y escriben **estrictamente como UTF-8 sin BOM**.
> *   **NUNCA** uses redirecciones de PowerShell nativas como `Set-Content` o `Out-File` con `-Encoding UTF8` (introducen el BOM `EF BB BF`).
> *   Para interactuar con archivos en PowerShell, delega la escritura a Python o usa métodos .NET seguros como `[System.IO.File]::WriteAllText()`.
> *   FastAPI debe configurarse obligatoriamente con la clase de respuesta `UTF8JSONResponse` para inyectar la cabecera `charset=utf-8`.

### Regla III: Verificación Visual Obligatoria
Después de cualquier modificación visual (HTML/CSS/JS) y antes de cerrar la tarea, ejecuta:
```bash
python scripts/visual_smoke.py http://localhost:<puerto>/<ruta>
```
Audita la captura generada en `outputs/visual-smoke/` para certificar que el diseño no contiene cascadas rotas, mojibake en el texto o modales fantasma.

---

## 4. Primeros Pasos Operativos

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```
2.  **Lanzar todos los servicios a la vez (idempotente):**
    ```bash
    scripts\bat\levantar_todo.bat
    ```
3.  **Ejecutar pruebas preventivas antes de commitear:**
    ```bash
    .venv\Scripts\python.exe -m pytest -q
    .venv\Scripts\python.exe -m ruff check src tests scripts
    ```
