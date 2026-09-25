"""Genera fixture.html: el fixture de Rift Duel armado con el design system.

Uso, desde la raiz del repo:
    python claude-design-handoff/rift-duel/build_fixture.py
    python claude-design-handoff/rift-duel/build_fixture.py otro.json --out otro.html
    python claude-design-handoff/rift-duel/build_fixture.py --pages ../lolcli-pages

Lee fixture.json y valida los datos: pools, regla Fearless, marcador de la serie
y nombres de campeon contra el catalogo de Data Dragon del repo. Despues genera
una pagina estatica (CSS adentro, sin iframes ni JavaScript). Los retratos son
los splash arts Classic que ya estan en assets/splash_arts/. Con --pages escribe
index.html en la carpeta de la rama gh-pages y copia al lado solo los splash que
usa. Si hay errores, los lista todos, sale con codigo 1 y no toca el HTML anterior.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from build_gallery import DS, FONTS_URL, compile_tokens

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = HERE / "fixture.json"
OUT = HERE / "fixture.html"
CATALOG = REPO / "data" / "ddragon-splash-catalog.json"
SPLASH_DIR = REPO / "assets" / "splash_arts"
# Ruta de las imagenes vista desde la pagina. fixture.html vive dos carpetas abajo de la
# raiz del repo (sirve con file:// y con serve_fixture.py, que mapea /assets/); en la
# rama gh-pages index.html va en la raiz del sitio, con las imagenes copiadas al lado.
IMG_BASE_REPO = "../../assets/splash_arts"
IMG_BASE_PAGES = "assets/splash_arts"
PLACEHOLDER = re.compile(r"^(?:Campeón|Jugador) (\d{1,3})$")
TIME = re.compile(r"^\d{2}:[0-5]\d$")
SIDES = ("blue", "red")
SIDE_TAG = {"blue": "Lado azul", "red": "Lado rojo"}
CONDITIONS = {"first_blood": "First Blood", "cs_100": "100 CS", "first_tower": "Primera torre"}
WINS_NEEDED = 2
MAX_GAMES = 3

# Composicion propia del fixture: grillas, hero compacto, slots pendientes y
# responsive. Solo tokens del design system, sin colores nuevos.
PAGE_CSS = """
.fx-page { max-width: var(--container-2xl); margin: 0 auto; padding: var(--space-6) var(--space-4) var(--space-16); }
.fx-hero { margin-bottom: var(--space-6); }
.fx-rules { justify-content: center; margin-top: var(--space-4); position: relative; }
.fx-rules-note { width: 100%; text-align: center; font-size: var(--font-body-sm); color: var(--text-secondary); }
.fx-nav { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--space-2);
  margin: 0 0 var(--space-8); }
.fx-nav a { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-3);
  background: var(--surface-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm);
  font-size: var(--font-body-sm); color: var(--text-primary); transition: var(--motion-fast); }
.fx-nav a:hover { border-color: var(--border-metal-strong); }
.fx-nav a:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.fx-nav b { font-family: var(--font-display); color: var(--arc-gold-text); font-variant-numeric: tabular-nums; }
.fx-match { background: var(--forge-darker); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
  padding: var(--space-5); margin-bottom: var(--space-8); display: flex; flex-direction: column; gap: var(--space-4);
  scroll-margin-top: var(--space-4); }
.fx-match-head { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); }
.fx-match-title { margin: 0; font-family: var(--font-display); font-size: var(--font-display-sm);
  font-weight: var(--weight-bold); color: var(--arc-gold-bright); letter-spacing: var(--tracking-tight); }
.fx-versus { padding: var(--space-6); margin-bottom: 0; border-radius: var(--radius-md); }
.fx-versus-grid { display: grid; grid-template-columns: 1fr auto 1fr; align-items: start; gap: var(--space-6); }
.fx-player { display: flex; flex-direction: column; gap: var(--space-4); min-width: 0; }
.fx-player.side-red { align-items: flex-end; text-align: right; }
.fx-player-head { display: flex; align-items: center; gap: var(--space-4); }
.fx-player.side-red .fx-player-head { flex-direction: row-reverse; }
.fx-player-id { display: flex; flex-direction: column; gap: var(--space-1); min-width: 0; }
.fx-player.side-red .fx-player-id { align-items: flex-end; }
.fx-tagrow { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2); min-height: 22px; }
.fx-player.side-red .fx-tagrow { flex-direction: row-reverse; }
.fx-name { font-family: var(--font-anton); font-style: italic; font-weight: var(--weight-regular);
  font-size: var(--font-display-xl); line-height: 1; letter-spacing: var(--tracking-hero); text-transform: uppercase;
  overflow-wrap: anywhere; }
.fx-vs { align-self: center; font-family: var(--font-anton); font-style: italic; font-size: var(--font-display-lg);
  text-transform: uppercase; }
.champ-portrait.fx-avatar { width: 72px; height: 72px; flex: none; font-size: var(--font-display-md); }
.fx-player.winner .fx-avatar { border-color: var(--arc-gold); box-shadow: var(--glow-gold); }
.fx-player.loser .fx-name { color: var(--text-secondary); }
.fx-player.loser .fx-avatar { background: var(--surface-raised); }
.fx-pool { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-2); width: 100%;
  max-width: 420px; }
.fx-pool .champ-tile { min-width: 0; }
.fx-portrait { position: relative; overflow: hidden; }
.fx-portrait img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; }
.fx-games { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-3); align-items: start; }
.fx-games .game-result-body { grid-template-columns: 1fr; }
.fx-slot { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3);
  padding: var(--space-4) var(--space-5); border: 1px dashed var(--border-metal); border-radius: var(--radius-md); }
.fx-slot.live { border-style: solid; border-color: var(--border-cyan); background: var(--state-info-dim); }
.fx-slot .game-result-title { color: var(--text-secondary); }
.fx-slot.live .game-result-title { color: var(--text-primary); }
@media (max-width: 1100px) {
  .fx-games { grid-template-columns: 1fr; }
}
@media (max-width: 820px) {
  .fx-versus-grid { grid-template-columns: 1fr; gap: var(--space-4); }
  .fx-vs { justify-self: center; }
  .series-score { grid-template-columns: 1fr 1fr; gap: var(--space-4); padding: var(--space-4); }
  .series-side.side-blue { grid-column: 1; grid-row: 1; }
  .series-side.side-red { grid-column: 2; grid-row: 1; }
  .series-mid { grid-column: 1 / -1; grid-row: 2; }
  .series-side { gap: var(--space-2); }
  .series-score .side-tag { white-space: nowrap; }
  .series-games { width: 100%; }
  .game-pip { flex: 1; min-width: 0; }
}
"""


def norm(name: str) -> str:
    """Clave de comparacion: sin tildes, mayusculas, espacios ni signos."""
    decomposed = unicodedata.normalize("NFKD", name)
    return "".join(ch for ch in decomposed if ch.isalnum() and not unicodedata.combining(ch)).lower()


def load_catalog(path: Path = CATALOG) -> tuple[dict[str, dict], dict[str, str]]:
    """Indice de alias -> campeon y archivo del splash Classic (skinNum 0) por id."""
    catalog = json.loads(path.read_text(encoding="utf-8"))
    index: dict[str, dict] = {}
    for champ in catalog["champions"]:
        for alias in (champ["id"], champ["name"], champ["nameEn"]):
            index[norm(alias)] = champ
    classic = {img["championId"]: img["file"] for img in catalog.get("images", []) if img.get("skinNum") == 0}
    return index, classic


@dataclass
class Champion:
    name: str  # nombre para mostrar
    key: str  # identidad para comparar (id del catalogo o nombre normalizado)
    icon: str | None  # URL del splash vista desde la pagina; None = se muestra la inicial
    splash: str | None = None  # "<id>/<archivo>" dentro de assets/splash_arts


@dataclass
class Match:
    id: str
    players: dict[str, str]
    pools: dict[str, list[Champion]]
    games: list[dict] = field(default_factory=list)
    live: bool = False

    @property
    def wins(self) -> dict[str, int]:
        return {side: sum(1 for g in self.games if g["winner"] == side) for side in SIDES}

    @property
    def winner(self) -> str | None:
        return next((side for side, n in self.wins.items() if n >= WINS_NEEDED), None)

    def used_in(self, side: str) -> dict[str, int]:
        return {g[side].key: n for n, g in enumerate(self.games, 1)}


class Resolver:
    """Convierte nombres de campeon en Champion; junta errores con sugerencias."""

    def __init__(self, index: dict[str, dict], classic: dict[str, str], img_base: str = IMG_BASE_REPO):
        self.index = index
        self.classic = classic
        self.img_base = img_base
        self.missing: set[str] = set()  # campeones sin splash en assets/splash_arts

    def resolve(self, raw: object, where: str, errors: list[str]) -> Champion | None:
        name = str(raw or "").strip()
        if not name:
            errors.append(f"{where}: falta el campeón")
            return None
        if PLACEHOLDER.match(name):
            return Champion(name=name, key=norm(name), icon=None)
        champ = self.index.get(norm(name))
        if champ is None:
            close = difflib.get_close_matches(norm(name), self.index.keys(), n=1, cutoff=0.6)
            hint = f" ¿Quisiste decir {self.index[close[0]]['name']}?" if close else ""
            errors.append(f"{where}: '{name}' no está en el catálogo de campeones.{hint}")
            return None
        splash = f"{champ['id']}/{self.classic.get(champ['id'], champ['id'] + '_Classic.jpg')}"
        if not (SPLASH_DIR / splash).is_file():
            self.missing.add(champ["name"])
            return Champion(name=champ["name"], key=champ["id"], icon=None)
        return Champion(name=champ["name"], key=champ["id"], icon=f"{self.img_base}/{splash}", splash=splash)


def validate(data: dict, resolver: Resolver) -> tuple[list[Match], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    pool_size = data.get("event", {}).get("poolSize", 3)
    raw_matches = data.get("matches")
    if not isinstance(raw_matches, list) or not raw_matches:
        return [], ["fixture.json: 'matches' tiene que ser una lista con al menos un enfrentamiento"], warnings

    matches: list[Match] = []
    seen_ids: set[str] = set()
    appearances: dict[str, list[str]] = {}
    for pos, raw in enumerate(raw_matches, 1):
        mid = str(raw.get("id", "")).strip()
        where = f"Enfrentamiento {mid or '#' + str(pos)}"
        if not mid:
            errors.append(f"{where}: falta el id")
        elif mid in seen_ids:
            errors.append(f"{where}: id repetido")
        seen_ids.add(mid)

        players: dict[str, str] = {}
        pools: dict[str, list[Champion]] = {}
        for side in SIDES:
            slot = raw.get(side) or {}
            player = str(slot.get("player", "")).strip()
            if not player:
                errors.append(f"{where}: falta el jugador del {SIDE_TAG[side].lower()}")
            else:
                appearances.setdefault(player, []).append(mid)
            players[side] = player or SIDE_TAG[side]
            pool_raw = slot.get("pool") or []
            if len(pool_raw) != pool_size:
                errors.append(f"{where}: la pool de {players[side]} tiene {len(pool_raw)} campeones y van {pool_size}")
            champs = [resolver.resolve(c, f"{where}, pool de {players[side]}", errors) for c in pool_raw]
            pools[side] = [c for c in champs if c]
            keys = [c.key for c in pools[side]]
            for dup in sorted({k for k in keys if keys.count(k) > 1}):
                errors.append(f"{where}: la pool de {players[side]} repite {dup}")

        match = Match(id=mid, players=players, pools=pools, live=bool(raw.get("live", False)))
        games_raw = raw.get("games") or []
        if len(games_raw) > MAX_GAMES:
            errors.append(f"{where}: tiene {len(games_raw)} partidas y el máximo es {MAX_GAMES}")
        wins = dict.fromkeys(SIDES, 0)
        used: dict[str, dict[str, int]] = {side: {} for side in SIDES}
        for n, game in enumerate(games_raw[:MAX_GAMES], 1):
            gwhere = f"{where}, P{n}"
            if max(wins.values()) >= WINS_NEEDED:
                errors.append(f"{gwhere}: la serie ya estaba definida y no puede haber otra partida")
            winner = game.get("winner")
            if winner not in SIDES:
                errors.append(f"{gwhere}: 'winner' tiene que ser 'blue' o 'red'")
            else:
                wins[winner] += 1
            picks: dict[str, Champion] = {}
            for side in SIDES:
                champ = resolver.resolve(game.get(side), f"{gwhere}, {SIDE_TAG[side].lower()}", errors)
                if champ is None:
                    continue
                if champ.key not in {c.key for c in pools[side]}:
                    errors.append(f"{gwhere}: {champ.name} no está en la pool de {players[side]}")
                elif champ.key in used[side]:
                    errors.append(f"{gwhere}: {champ.name} ya se usó en P{used[side][champ.key]} (Fearless)")
                else:
                    used[side][champ.key] = n
                picks[side] = champ
            condition = game.get("condition")
            if condition not in CONDITIONS:
                errors.append(f"{gwhere}: 'condition' tiene que ser {', '.join(CONDITIONS)}")
            time = str(game.get("time", ""))
            if not TIME.match(time):
                errors.append(f"{gwhere}: 'time' tiene que ser mm:ss, por ejemplo 06:42 (llegó '{time}')")
            if winner in SIDES and len(picks) == 2 and condition in CONDITIONS:
                match.games.append({"winner": winner, **picks, "condition": condition, "time": time})
        if match.live and max(wins.values()) >= WINS_NEEDED:
            errors.append(f"{where}: 'live' está en true pero la serie ya terminó")
        matches.append(match)

    for player, mids in appearances.items():
        if len(mids) > 1:
            warnings.append(f"{player} aparece en más de un enfrentamiento: {', '.join(mids)}")
    for name in sorted(resolver.missing):
        warnings.append(f"no está el splash de {name} en assets/splash_arts: se muestra la inicial")
    return matches, errors, warnings


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def initials(name: str) -> str:
    placeholder = PLACEHOLDER.match(name)
    if placeholder:
        return placeholder.group(1)
    return next((ch.upper() for ch in name if ch.isalnum()), "?")


def portrait(champ: Champion) -> str:
    img = f'<img src="{esc(champ.icon)}" alt="" loading="lazy">' if champ.icon else ""
    return f'<span class="champ-portrait fx-portrait" aria-hidden="true">{esc(initials(champ.name))}{img}</span>'


def champ_tile(champ: Champion, used_in: int | None) -> str:
    cls = "champ-tile used" if used_in else "champ-tile"
    pill = f'<span class="pill pill-neutral">Usado en P{used_in}</span>' if used_in else ""
    return f'<div class="{cls}">{portrait(champ)}<span class="champ-name">{esc(champ.name)}</span>{pill}</div>'


def status_pill(match: Match) -> str:
    wins = match.wins
    if match.winner:
        score = f"{max(wins.values())}-{min(wins.values())}"
        return f'<span class="pill pill-gold">{esc(match.players[match.winner])} gana {score}</span>'
    if match.live:
        return '<span class="pill pill-cyan">En juego</span>'
    if match.games:
        return '<span class="pill pill-cyan">En curso</span>'
    return '<span class="pill pill-neutral">Pendiente</span>'


def player_block(match: Match, side: str) -> str:
    state = "" if not match.winner else (" winner" if match.winner == side else " loser")
    name = match.players[side]
    trophy = '<span class="pill pill-gold">Ganó la serie</span>' if match.winner == side else ""
    used = match.used_in(side)
    tiles = "".join(champ_tile(c, used.get(c.key)) for c in match.pools[side])
    return (
        f'<div class="fx-player side-{side}{state}">'
        f'<div class="fx-player-head"><span class="champ-portrait fx-avatar" aria-hidden="true">{esc(initials(name))}</span>'
        f'<div class="fx-player-id"><div class="fx-tagrow"><span class="side-tag">{SIDE_TAG[side]}</span>{trophy}</div>'
        f'<span class="versus-name fx-name">{esc(name)}</span></div></div>'
        f'<div class="fx-pool" role="group" aria-label="Pool de {esc(name)}">{tiles}</div></div>'
    )


def series_score(match: Match) -> str:
    wins = match.wins
    pips = []
    for n in range(1, MAX_GAMES + 1):
        if n <= len(match.games):
            side = match.games[n - 1]["winner"]
            pips.append(f'<li class="game-pip won side-{side}"><b>P{n}</b>{esc(match.players[side])}</li>')
        elif match.winner:
            pips.append(f'<li class="game-pip"><b>P{n}</b>No se jugó</li>')
        elif match.live and n == len(match.games) + 1:
            pips.append(f'<li class="game-pip live"><b>P{n}</b>En juego</li>')
        else:
            pips.append(f'<li class="game-pip"><b>P{n}</b>Pendiente</li>')
    label = f"Marcador: {match.players['blue']} {wins['blue']}, {match.players['red']} {wins['red']}"
    blue, red = (
        f'<div class="series-player"><span class="side-tag">{SIDE_TAG[s]}</span>'
        f'<span class="series-name">{esc(match.players[s])}</span></div>'
        for s in SIDES
    )
    return (
        f'<div class="series-score" role="group" aria-label="{esc(label)}">'
        f'<div class="series-side side-blue">{blue}<span class="series-wins">{wins["blue"]}</span></div>'
        f'<div class="series-mid"><span class="series-format">Mejor de 3</span>'
        f'<ol class="series-games">{"".join(pips)}</ol></div>'
        f'<div class="series-side side-red"><span class="series-wins">{wins["red"]}</span>{red}</div></div>'
    )


def game_result(match: Match, n: int) -> str:
    game = match.games[n - 1]
    before = match.games[:n]
    score = f"{sum(g['winner'] == 'blue' for g in before)}-{sum(g['winner'] == 'red' for g in before)}"
    sides = []
    for side in SIDES:
        won = game["winner"] == side
        pill = '<span class="pill pill-gold">Ganó</span>' if won else ""
        sides.append(
            f'<div class="result-side side-{side} {"winner" if won else "loser"}">{portrait(game[side])}'
            f'<div class="result-who"><span class="side-tag">{SIDE_TAG[side]}</span>'
            f'<strong>{esc(match.players[side])}</strong><span class="result-champ">{esc(game[side].name)}</span></div>'
            f"{pill}</div>"
        )
    return (
        f'<article class="game-result"><header class="game-result-head"><h3 class="game-result-title">Partida {n}</h3>'
        f'<span class="win-cond decided">{CONDITIONS[game["condition"]]} · '
        f'<span class="win-cond-time">{esc(game["time"])}</span></span></header>'
        f'<div class="game-result-body">{"".join(sides)}</div>'
        f'<footer class="game-result-foot"><span>Serie</span><b>{score}</b></footer></article>'
    )


def game_slot(match: Match, n: int) -> str:
    if n <= len(match.games):
        return game_result(match, n)
    if match.winner:
        cls, pill = "fx-slot", '<span class="pill pill-neutral">No se jugó</span>'
    elif match.live and n == len(match.games) + 1:
        cls, pill = "fx-slot live", '<span class="pill pill-cyan">En juego</span>'
    else:
        cls, pill = "fx-slot", '<span class="pill pill-neutral">Pendiente</span>'
    return f'<article class="{cls}"><h3 class="game-result-title">Partida {n}</h3>{pill}</article>'


def match_section(match: Match) -> str:
    anchor = f"m{esc(match.id)}"
    return (
        f'<section class="fx-match" id="{anchor}" aria-labelledby="{anchor}-t">'
        f'<header class="fx-match-head"><h2 class="fx-match-title" id="{anchor}-t">Enfrentamiento {esc(match.id)}</h2>'
        f"{status_pill(match)}</header>"
        f'<div class="hero versus-hero fx-versus"><div class="fx-versus-grid">'
        f'{player_block(match, "blue")}<span class="versus-vs fx-vs">vs</span>{player_block(match, "red")}'
        f"</div></div>"
        f"{series_score(match)}"
        f'<div class="fx-games">{"".join(game_slot(match, n) for n in range(1, MAX_GAMES + 1))}</div>'
        f"</section>"
    )


def render(data: dict, matches: list[Match]) -> str:
    event = data.get("event", {})
    title = event.get("title", "Rift Duel")
    tokens = json.loads((DS / "tokens.json").read_text(encoding="utf-8"))
    bundle_css = re.sub(r"^@import[^;]+;\s*", "", (DS / "components" / "bundle.css").read_text(encoding="utf-8"))
    nav = "".join(
        f'<a href="#m{esc(m.id)}"><b>{esc(m.id)}</b>{esc(m.players["blue"])} vs {esc(m.players["red"])}</a>'
        for m in matches
    )
    rules = "".join(f'<span class="win-cond">{label}</span>' for label in CONDITIONS.values())
    return f"""<!doctype html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Fixture</title>
<link rel="stylesheet" href="{FONTS_URL}">
<!-- Generado por build_fixture.py desde fixture.json. No editar a mano. -->
<style>
/* tokens.css (compilado desde design-system/tokens.json) */
{compile_tokens(tokens)}
/* design-system/components/bundle.css */
{bundle_css}
/* fixture */
{PAGE_CSS}
</style>
</head>
<body>
<main class="fx-page">
<header class="hero fx-hero">
<div class="hero-row"><span class="hero-eyebrow">Fixture</span><span class="hero-meta">{esc(event.get("date", ""))}</span></div>
<h1 class="hero-title">{esc(title)}</h1>
<p class="hero-subtitle">{esc(event.get("subtitle", ""))} · {len(matches)} enfrentamientos</p>
<div class="win-conds fx-rules">{rules}
<p class="fx-rules-note">Gana la partida el primero que consigue una. Fearless: cada campeón se usa una sola vez por serie.</p>
</div>
</header>
<nav class="fx-nav" aria-label="Enfrentamientos">{nav}</nav>
{"".join(match_section(m) for m in matches)}
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida fixture.json y genera fixture.html.")
    parser.add_argument("data", nargs="?", type=Path, default=DATA, help="JSON del fixture (default: fixture.json)")
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--out", type=Path, default=OUT, help="HTML a generar (default: fixture.html)")
    target.add_argument("--pages", type=Path, help="carpeta de la rama gh-pages: escribe index.html y copia los splash")
    args = parser.parse_args()

    pages = args.pages.resolve() if args.pages else None
    if pages and (not pages.is_dir() or pages == REPO or REPO in pages.parents):
        print(f"ERROR: --pages tiene que ser la carpeta de la rama gh-pages, fuera del repo ({pages})", file=sys.stderr)
        return 1
    out = pages / "index.html" if pages else args.out

    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: no se pudo leer {args.data}: {exc}", file=sys.stderr)
        return 1
    index, classic = load_catalog()
    resolver = Resolver(index, classic, IMG_BASE_PAGES if pages else IMG_BASE_REPO)
    matches, errors, warnings = validate(data, resolver)
    for warning in warnings:
        print(f"AVISO: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"{len(errors)} error(es): no se generó {out.name}.", file=sys.stderr)
        return 1

    page = render(data, matches)
    out.write_text(page, encoding="utf-8")
    if pages:
        splashes = sorted({c.splash for m in matches for pool in m.pools.values() for c in pool if c.splash})
        for rel in splashes:
            dst = pages / IMG_BASE_PAGES / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SPLASH_DIR / rel, dst)
        (pages / ".nojekyll").touch()
        print(f"gh-pages: {len(splashes)} splash copiados a {pages / IMG_BASE_PAGES}")
    done = sum(1 for m in matches if m.winner)
    live = sum(1 for m in matches if not m.winner and (m.live or m.games))
    print(
        f"{out.name} generado ({len(page) // 1024} KB): {len(matches)} enfrentamientos "
        f"(terminados: {done}, en curso: {live}, pendientes: {len(matches) - done - live})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
