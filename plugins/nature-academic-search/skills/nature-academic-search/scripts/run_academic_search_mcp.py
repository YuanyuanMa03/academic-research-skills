#!/usr/bin/env python3
"""Bootstrap and run the bundled academic-search MCP server.

Codex plugin installs do not run arbitrary install scripts. This wrapper keeps
the MCP server self-contained by creating a small virtual environment on first
launch, installing the server dependencies, then exec'ing the real server.
"""

from __future__ import annotations

import os
import subprocess
import venv
from pathlib import Path


REQUIREMENTS = (
    "mcp>=1.0.0",
    "requests>=2.31.0",
    "toml>=0.10.2",
    "lxml>=4.9.0",
)


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _deps_available(python: Path) -> bool:
    probe = "import mcp, requests, toml, lxml"
    return subprocess.run(
        [str(python), "-c", probe],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def _ensure_venv(venv_dir: Path) -> Path:
    python = _venv_python(venv_dir)
    if not python.exists():
        venv_dir.parent.mkdir(parents=True, exist_ok=True)
        venv.EnvBuilder(with_pip=True, clear=False).create(venv_dir)

    if not _deps_available(python):
        subprocess.check_call(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--quiet",
                *REQUIREMENTS,
            ]
        )
    return python


def main() -> None:
    skill_dir = Path(__file__).resolve().parents[1]
    server = skill_dir / "mcp-server" / "academic_search_server.py"
    if not server.exists():
        raise SystemExit(f"academic-search server not found: {server}")

    cache_root = Path(
        os.environ.get(
            "ACADEMIC_SEARCH_MCP_CACHE",
            str(Path.home() / ".cache" / "academic-search-mcp"),
        )
    )
    python = _ensure_venv(cache_root / "venv")

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    os.execve(str(python), [str(python), str(server)], env)


if __name__ == "__main__":
    main()
