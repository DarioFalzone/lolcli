from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("src", "tests", "scripts")


def _python_files() -> list[Path]:
    files: list[Path] = []
    for dirname in SCAN_DIRS:
        files.extend((REPO_ROOT / dirname).rglob("*.py"))
    return sorted(files)


def _has_future_annotations(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )


def _contains_pipe_union(node: ast.AST | None) -> bool:
    if node is None:
        return False
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return True
    return any(_contains_pipe_union(child) for child in ast.iter_child_nodes(node))


def _uses_pipe_union_annotations(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and _contains_pipe_union(node.annotation):
            return True
        if isinstance(node, ast.arg) and _contains_pipe_union(node.annotation):
            return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _contains_pipe_union(node.returns):
            return True
    return False


def test_python39_pipe_union_annotations_use_future_import():
    offenders: list[str] = []

    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if _uses_pipe_union_annotations(tree) and not _has_future_annotations(tree):
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []
