"""Genera gallery.html: vista local del design system Rift Duel.

Uso, desde la raiz del repo:
    python claude-design-handoff/rift-duel/build_gallery.py

Compila tokens.css desde design-system/tokens.json con el mismo formato que usa
el tipo Design System, enlaza components/bundle.css y arma una sola pagina con
la portada, los colores, la tipografia y cada componente en su propio iframe.
El resultado se abre con doble clic desde esta carpeta (usa design-system/, que
esta al lado); solo necesita internet para Google Fonts.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE / "design-system"
OUT = HERE / "gallery.html"
ARTIFACT_URL = "https://claude.ai/artifact/2pYJqbC4tHCaMhQ5Umiu2N"
FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700"
    "&family=Outfit:wght@500;600;700;800;900&display=swap"
)
# Relativo a gallery.html: la pagina y todos los iframes comparten el mismo archivo.
BUNDLE_HREF = "design-system/components/bundle.css"
GROUP_ORDER = ["Serie", "Jugadores", "Acciones", "Estado", "Contenedores", "Datos"]
LENGTH_FAMILIES = ["spacing", "radius", "fontSize", "fontWeight", "lineHeight", "letterSpacing", "layout"]

# Cada iframe le avisa su alto real a la pagina (postMessage funciona con file://).
RESIZE_SCRIPT = (
    "<script>function rdSend(){parent.postMessage({rdGallery:%s,h:document.documentElement.scrollHeight},'*');}"
    "addEventListener('load',rdSend);if(document.fonts){document.fonts.ready.then(rdSend);}</script>"
)


def theme_value(value: str | dict, theme: str) -> str:
    return value if isinstance(value, str) else value[theme]


def color_value(value: str) -> str:
    """Un alias "{token}" se compila como var(--token), igual que en el tipo."""
    return f"var(--{value[1:-1]})" if value.startswith("{") else value


def compile_tokens(tokens: dict) -> str:
    theme = tokens["color"]["themes"][0]["id"]
    lines = [f':root, [data-theme="{theme}"] {{']
    for tok in tokens["color"]["tokens"]:
        lines.append(f"  --{tok['name']}: {color_value(theme_value(tok['value'], theme))};")
    for tok in tokens.get("shadow", {}).get("tokens", []):
        lines.append(f"  --{tok['name']}: {theme_value(tok['value'], theme)};")
    lines += ["}", ":root {"]
    for family in LENGTH_FAMILIES:
        for tok in tokens.get(family, {}).get("tokens", []):
            lines.append(f"  --{tok['name']}: {tok['value']};")
    for key, stack in tokens["type"]["families"].items():
        lines.append(f"  --font-{key}: {stack};")
    lines.append("}")
    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            decls = [
                f"font-family: var(--font-{style.get('family', group['family'])})",
                f"font-size: {style['fontSize']}",
                f"line-height: {style['lineHeight']}",
                f"font-weight: {style['fontWeight']}",
            ]
            if "letterSpacing" in style:
                decls.append(f"letter-spacing: {style['letterSpacing']}")
            if "fontStyle" in style:
                decls.append(f"font-style: {style['fontStyle']}")
            lines.append(f".{style['name']} {{ {'; '.join(decls)}; }}")
    return "\n".join(lines)


def read_marker(preview: str) -> dict:
    marker = preview.splitlines()[0]
    group = re.search(r'group="([^"]+)"', marker)
    height = re.search(r"height=(\d+)", marker)
    width = re.search(r"width=(\d+)", marker)
    return {
        "group": group.group(1) if group else "",
        "height": int(height.group(1)) if height else 120,
        "width": int(width.group(1)) if width else None,
    }


def summary(readme: Path) -> str:
    """Primer parrafo despues del titulo: es el resumen que muestra el tipo."""
    paragraphs = [p.strip() for p in readme.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    text = next((p for p in paragraphs if not p.startswith("#")), "")
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text, quote=False))


def frame(name: str, preview: str, tokens_css: str, marker: dict) -> str:
    doc = preview.split("\n", 1)[1]  # sin el marcador @dsCard
    doc = doc.replace('<html lang="es">', '<html lang="es" data-theme="dark">', 1)
    doc = doc.replace("<head>", f'<head>\n<style>{tokens_css}</style>\n<link rel="stylesheet" href="{BUNDLE_HREF}">', 1)
    doc = doc.replace("</body>", RESIZE_SCRIPT % json.dumps(name) + "\n</body>", 1)
    width = f"width:{marker['width']}px;" if marker["width"] else ""
    return (
        f'<div class="rd-frame-wrap"><iframe data-comp="{name}" title="{name}" loading="lazy" '
        f'style="{width}height:{marker["height"]}px" srcdoc="{html.escape(doc, quote=True)}"></iframe></div>'
    )


def swatches(tokens: dict) -> str:
    theme = tokens["color"]["themes"][0]["id"]
    cells = []
    for tok in tokens["color"]["tokens"]:
        value = theme_value(tok["value"], theme)
        cells.append(
            f'<figure class="rd-swatch"><span class="rd-chip" style="background:var(--{tok["name"]})"></span>'
            f"<figcaption><b>{tok['name']}</b><code>{html.escape(value)}</code>"
            f"<span>{html.escape(tok['usage'])}</span></figcaption></figure>"
        )
    return "\n".join(cells)


def type_samples(tokens: dict) -> str:
    rows = []
    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            meta = f"{style['name']} · {style['fontSize']} · {style['fontWeight']}"
            rows.append(
                f'<div class="rd-type-row"><span class="rd-type-meta">{meta}</span>'
                f'<span class="{style["name"]}">{html.escape(style["sample"])}</span></div>'
            )
    return "\n".join(rows)


def main() -> None:
    tokens = json.loads((DS / "tokens.json").read_text(encoding="utf-8"))
    tokens_css = compile_tokens(tokens)

    cover = (DS / "components" / "Cover" / "preview.html").read_text(encoding="utf-8")
    groups: dict[str, list[str]] = {g: [] for g in GROUP_ORDER}
    for comp_dir in sorted((DS / "components").iterdir()):
        preview_file = comp_dir / "preview.html"
        if comp_dir.name == "Cover" or not preview_file.exists():
            continue
        preview = preview_file.read_text(encoding="utf-8")
        marker = read_marker(preview)
        groups.setdefault(marker["group"], []).append(
            f'<article class="rd-comp" id="{comp_dir.name}"><h3>{comp_dir.name}</h3>'
            f"<p>{summary(comp_dir / 'README.md')}</p>{frame(comp_dir.name, preview, tokens_css, marker)}</article>"
        )

    sections = "\n".join(
        f'<section class="rd-section"><h2>{group}</h2>{"".join(items)}</section>'
        for group, items in groups.items()
        if items
    )
    nav = " · ".join(
        f'<a href="#{name}">{name}</a>'
        for items in groups.values()
        for name in re.findall(r'id="(\w+)"', "".join(items))
    )
    page = f"""<!doctype html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rift Duel — galería local</title>
<link rel="stylesheet" href="{FONTS_URL}">
<link rel="stylesheet" href="{BUNDLE_HREF}">
<!-- Generado por build_gallery.py desde design-system/. No editar a mano. -->
<style>
{tokens_css}
.rd-page {{ max-width: 1520px; margin: 0 auto; padding: var(--space-8) var(--space-6) var(--space-16); }}
.rd-intro {{ color: var(--text-secondary); max-width: 760px; }}
.rd-intro a, .rd-nav a {{ color: var(--arc-gold-text); }}
.rd-nav {{ font-size: var(--font-body-sm); color: var(--text-tertiary); line-height: 2; margin: var(--space-4) 0 var(--space-8); }}
.rd-section {{ margin-top: var(--space-12); }}
.rd-section > h2 {{ font-family: var(--font-anton); font-style: italic; font-weight: 400; font-size: var(--font-display-xl);
  text-transform: uppercase; color: var(--arc-gold); margin: 0 0 var(--space-4); letter-spacing: var(--tracking-hero); }}
.rd-comp {{ margin-bottom: var(--space-8); }}
.rd-comp h3 {{ font-family: var(--font-display); font-size: var(--font-display-sm); margin: 0 0 var(--space-1); }}
.rd-comp p {{ color: var(--text-secondary); margin: 0 0 var(--space-3); max-width: 860px; }}
.rd-frame-wrap {{ overflow-x: auto; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); }}
.rd-frame-wrap iframe {{ display: block; width: 100%; min-width: 100%; border: 0; background: var(--forge-black); }}
.rd-cover {{ width: fit-content; max-width: 100%; }}
.rd-cover iframe {{ width: 960px; min-width: 0; height: 320px; }}
.rd-swatches {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--space-3); }}
.rd-swatch {{ margin: 0; background: var(--surface-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md);
  overflow: hidden; }}
.rd-chip {{ display: block; height: 56px; border-bottom: 1px solid var(--border-divider); }}
.rd-swatch figcaption {{ padding: var(--space-2) var(--space-3); display: flex; flex-direction: column; gap: 2px;
  font-size: var(--font-caption); }}
.rd-swatch code, .rd-comp code {{ color: var(--arc-cyan); font-family: var(--font-mono); font-size: var(--font-caption-sm); }}
.rd-swatch span {{ color: var(--text-secondary); }}
.rd-type-row {{ display: grid; grid-template-columns: 260px 1fr; gap: var(--space-4); align-items: baseline;
  padding: var(--space-3) 0; border-bottom: 1px solid var(--border-divider); overflow: hidden; }}
.rd-type-meta {{ font-family: var(--font-mono); font-size: var(--font-caption-sm); color: var(--text-secondary); }}
</style>
</head>
<body>
<main class="rd-page">
<div class="rd-frame-wrap rd-cover">{frame("Cover", cover, tokens_css, {"height": 320, "width": 960})}</div>
<p class="rd-intro">Galería local del design system. La versión oficial está en
<a href="{ARTIFACT_URL}">el artifact Rift Duel</a> (privado: se abre con tu cuenta de claude.ai).
Las previews son versiones estáticas en HTML + CSS.</p>
<nav class="rd-nav">{nav}</nav>
<section class="rd-section"><h2>Colores</h2><div class="rd-swatches">{swatches(tokens)}</div></section>
<section class="rd-section"><h2>Tipografía</h2>{type_samples(tokens)}</section>
{sections}
</main>
<script>
addEventListener("message", (e) => {{
  const d = e.data || {{}};
  if (!d.rdGallery) return;
  const f = document.querySelector('iframe[data-comp="' + d.rdGallery + '"]');
  if (f && d.rdGallery !== "Cover") f.style.height = d.h + "px";
}});
</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"gallery.html generado: {OUT} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
