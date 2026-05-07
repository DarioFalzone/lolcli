from pathlib import Path
from typing import Optional

import click

from riot_lol_cli import paths
from riot_lol_cli.rendering import generate_match_history_html, load_matches_data, load_template
from riot_lol_cli.splash import build_splash_manifest, generate_splash_viewer_html, load_splash_manifest
from riot_lol_cli.versioning import bump_version, get_version

paths.ensure_runtime_directories()


def _default_match_output(matches_data: dict, html_template: str) -> Path:
    output_dir = paths.OUTPUT_DIR / html_template
    output_dir.mkdir(parents=True, exist_ok=True)
    summoner_name = matches_data.get("summoner_name", "output")
    return output_dir / f"{summoner_name}-{html_template}.html"


@click.group()
@click.version_option(version=get_version())
def cli() -> None:
    """CLI principal para la generación de estadísticas de League of Legends."""


@cli.command()
@click.option(
    "--read-json", type=click.Path(exists=True), required=True, help="Ruta al archivo JSON con datos de partidas"
)
@click.option("--html-template", default="default", show_default=True, help="Nombre de la plantilla HTML a utilizar")
@click.option("--output", "-o", help="Ruta de salida para el archivo HTML")
def generate(read_json: str, html_template: str, output: Optional[str]) -> None:
    """Genera un archivo HTML con estadísticas de partidas."""
    try:
        template = load_template(html_template)
        matches_data = load_matches_data(read_json)
        html_content = generate_match_history_html(template, matches_data, html_template)

        output_path = Path(output) if output else _default_match_output(matches_data, html_template)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")

        click.echo(f"✅ Archivo generado exitosamente: {click.format_filename(str(output_path))}")
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
def version() -> None:
    """Muestra la versión actual del CLI."""
    click.echo(f"Versión actual: v{get_version()}")


@cli.command(name="bump-version")
def bump_version_command() -> None:
    """Incrementa el número de versión de forma explícita."""
    new_version = bump_version()
    click.echo(f"✅ Versión actualizada a: v{new_version}")


@cli.command(name="build-splash-manifest")
def build_splash_manifest_command() -> None:
    """Escanea assets/splash_arts y genera data/splash-manifest.json."""
    try:
        manifest = build_splash_manifest()
        manifest_path = paths.DATA_DIR / "splash-manifest.json"
        click.echo(f"✅ Manifest generado: {manifest_path}")
        click.echo(f"📊 {manifest['totalChampions']} campeones, {manifest['totalImages']} imágenes")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command(name="generate-splash-viewer")
@click.option("--output", "-o", help="Ruta de salida para el HTML")
def generate_splash_viewer(output: Optional[str]) -> None:
    """Genera el visor de splash arts sin mutar la versión del proyecto."""
    try:
        manifest = load_splash_manifest()
        html = generate_splash_viewer_html(manifest)
        output_path = Path(output) if output else paths.OUTPUT_DIR / "splash-viewer.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        click.echo(f"✅ Visor generado: {output_path}")
        click.echo(f"🎨 {manifest.get('totalChampions', 0)} campeones, {manifest.get('totalImages', 0)} splash arts")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
