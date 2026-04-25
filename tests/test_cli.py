import json

from click.testing import CliRunner

from riot_lol_cli import paths
from riot_lol_cli.cli import cli


def test_generate_does_not_mutate_version_file(tmp_path, monkeypatch):
    templates_dir = tmp_path / "templates"
    output_dir = tmp_path / "outputs"
    data_dir = tmp_path / "data"
    config_dir = tmp_path / "config"
    version_file = config_dir / "version.json"

    templates_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)

    monkeypatch.setattr(paths, "TEMPLATES_DIR", templates_dir)
    monkeypatch.setattr(paths, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(paths, "DATA_DIR", data_dir)
    monkeypatch.setattr(paths, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(paths, "VERSION_FILE", version_file)

    version_file.write_text(json.dumps({"version": "1.6.4"}), encoding="utf-8")
    (templates_dir / "basic.html").write_text("<html>{{version}} {{matches_rows}}</html>", encoding="utf-8")

    matches_path = data_dir / "matches.json"
    matches_path.write_text(
        json.dumps({"summoner_name": "tester", "matches": []}),
        encoding="utf-8",
    )

    output_path = output_dir / "report.html"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "generate",
            "--read-json",
            str(matches_path),
            "--html-template",
            "basic",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert json.loads(version_file.read_text(encoding="utf-8"))["version"] == "1.6.4"


def test_bump_version_command_is_explicit(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    version_file = config_dir / "version.json"
    config_dir.mkdir(parents=True)

    monkeypatch.setattr(paths, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(paths, "VERSION_FILE", version_file)

    version_file.write_text(json.dumps({"version": "1.6.4"}), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["bump-version"])

    assert result.exit_code == 0
    assert json.loads(version_file.read_text(encoding="utf-8"))["version"] == "1.6.5"
