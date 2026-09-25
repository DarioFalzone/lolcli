"""Genera gallery.html: vista local del design system Rift Duel.

Uso, desde la raiz del repo:
    python claude-design-handoff/rift-duel/build_gallery.py

Compila tokens.css desde design-system/tokens.json con el mismo formato que usa
el tipo Design System y arma una sola pagina con la portada, los colores, la
tipografia y todos los componentes.

La pagina es autocontenida: tokens y bundle.css van adentro, los componentes se
dibujan directo en la pagina (sin iframes) y no usa JavaScript. Se ve igual si
se abre con doble clic, copiada a otra carpeta o desde un visor que bloquea
scripts. Solo necesita internet para las fuentes de Google Fonts.
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
GROUP_ORDER = ["Serie", "Jugadores", "Acciones", "Estado", "Contenedores", "Datos"]
LENGTH_FAMILIES = ["spacing", "radius", "fontSize", "fontWeight", "lineHeight", "letterSpacing", "layout"]
COVER_SCOPE = ".rd-cover-inline"

# Estilos propios de la galeria. Solo apuntan a hijos directos (>) para no pisar
# los estilos de los componentes, que se dibujan dentro de .rd-demo.
PAGE_CSS = """
.rd-page { max-width: 1520px; margin: 0 auto; padding: var(--space-8) var(--space-6) var(--space-16); }
.rd-intro { color: var(--text-secondary); max-width: 760px; }
.rd-intro a, .rd-nav a { color: var(--arc-gold-text); }
.rd-nav { font-size: var(--font-body-sm); color: var(--text-tertiary); line-height: 2; margin: var(--space-4) 0 var(--space-8); }
.rd-section { margin-top: var(--space-12); }
.rd-section > h2 { font-family: var(--font-anton); font-style: italic; font-weight: 400; font-size: var(--font-display-xl);
  text-transform: uppercase; color: var(--arc-gold); margin: 0 0 var(--space-4); letter-spacing: var(--tracking-hero); }
.rd-comp { margin-bottom: var(--space-8); }
.rd-comp > h3 { font-family: var(--font-display); font-size: var(--font-display-sm); margin: 0 0 var(--space-1); }
.rd-comp > p { color: var(--text-secondary); margin: 0 0 var(--space-3); max-width: 860px; }
.rd-comp > p code, .rd-swatch code { color: var(--arc-cyan); font-family: var(--font-mono); font-size: var(--font-caption-sm); }
.rd-demo { overflow-x: auto; background: var(--forge-black); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md); }
.rd-cover-inline { width: 960px; max-width: 100%; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); }
.rd-swatches { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--space-3); }
.rd-swatch { margin: 0; background: var(--surface-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md);
  overflow: hidden; }
.rd-chip { display: block; height: 56px; border-bottom: 1px solid var(--border-divider); }
.rd-swatch > figcaption { padding: var(--space-2) var(--space-3); display: flex; flex-direction: column; gap: 2px;
  font-size: var(--font-caption); }
.rd-swatch > figcaption > span { color: var(--text-secondary); }
.rd-type-row { display: grid; grid-template-columns: 260px 1fr; gap: var(--space-4); align-items: baseline;
  padding: var(--space-3) 0; border-bottom: 1px solid var(--border-divider); overflow: hidden; }
.rd-type-meta { font-family: var(--font-mono); font-size: var(--font-caption-sm); color: var(--text-secondary); }
"""


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


def read_group(preview: str) -> str:
    group = re.search(r'group="([^"]+)"', preview.splitlines()[0])
    return group.group(1) if group else ""


def body_inner(preview: str) -> str:
    match = re.search(r"<body>(.*)</body>", preview, re.S)
    if not match:
        raise ValueError("preview sin <body>")
    return match.group(1).strip()


def scope_cover_css(css: str) -> str:
    """Encierra el CSS de la portada en COVER_SCOPE para que no choque con el resto."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []
    for selectors, decls in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        selectors = selectors.strip()
        if "html" in selectors:
            continue
        if selectors == "body":
            rules.append(f"{COVER_SCOPE} {{{decls}}}")
            continue
        scoped = ", ".join(f"{COVER_SCOPE} {sel.strip()}" for sel in selectors.split(","))
        rules.append(f"{scoped} {{{decls}}}")
    return "\n".join(rules)


def summary(readme: Path) -> str:
    """Primer parrafo despues del titulo: es el resumen que muestra el tipo."""
    paragraphs = [p.strip() for p in readme.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    text = next((p for p in paragraphs if not p.startswith("#")), "")
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text, quote=False))


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
    # El @import de Google Fonts se reemplaza por el <link> del <head>.
    bundle_css = re.sub(r"^@import[^;]+;\s*", "", (DS / "components" / "bundle.css").read_text(encoding="utf-8"))

    cover = (DS / "components" / "Cover" / "preview.html").read_text(encoding="utf-8")
    cover_style = re.search(r"<style>(.*?)</style>", cover, re.S)
    cover_css = scope_cover_css(cover_style.group(1)) if cover_style else ""

    groups: dict[str, list[str]] = {g: [] for g in GROUP_ORDER}
    for comp_dir in sorted((DS / "components").iterdir()):
        preview_file = comp_dir / "preview.html"
        if comp_dir.name == "Cover" or not preview_file.exists():
            continue
        preview = preview_file.read_text(encoding="utf-8")
        groups.setdefault(read_group(preview), []).append(
            f'<article class="rd-comp" id="{comp_dir.name}"><h3>{comp_dir.name}</h3>'
            f"<p>{summary(comp_dir / 'README.md')}</p>"
            f'<div class="rd-demo">{body_inner(preview)}</div></article>'
        )

    sections = "\n".join(
        f'<section class="rd-section"><h2>{group}</h2>{"".join(items)}</section>'
        for group, items in groups.items()
        if items
    )
    nav = " · ".join(
        f'<a href="#{name}">{name}</a>'
        for items in groups.values()
        for name in re.findall(r'<article class="rd-comp" id="(\w+)"', "".join(items))
    )
    page = f"""<!doctype html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rift Duel — galería local</title>
<link rel="stylesheet" href="{FONTS_URL}">
<!-- Generado por build_gallery.py desde design-system/. No editar a mano. -->
<style>
/* tokens.css (compilado desde design-system/tokens.json) */
{tokens_css}
/* design-system/components/bundle.css */
{bundle_css}
/* portada (components/Cover/preview.html), encerrada en {COVER_SCOPE} */
{cover_css}
/* galería */
{PAGE_CSS}
</style>
</head>
<body>
<main class="rd-page">
<div class="{COVER_SCOPE[1:]}">{body_inner(cover)}</div>
<p class="rd-intro">Galería local del design system. La versión oficial está en
<a href="{ARTIFACT_URL}">el artifact Rift Duel</a> (privado: se abre con tu cuenta de claude.ai).
Las previews son versiones estáticas en HTML + CSS.</p>
<nav class="rd-nav">{nav}</nav>
<section class="rd-section"><h2>Colores</h2><div class="rd-swatches">{swatches(tokens)}</div></section>
<section class="rd-section"><h2>Tipografía</h2>{type_samples(tokens)}</section>
{sections}
</main>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"gallery.html generado: {OUT} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
