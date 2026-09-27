#!/usr/bin/env python3
"""Bootstrap and run the bundled academic-search MCP server.

Codex plugin installs do not run arbitrary install scripts. This wrapper keeps
the MCP server self-contained by creating a small virtual environment on first
launch, installing the server dependencies, then handing off to the real server.
"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path


# Mirrors mcp-server/requirements.txt: the server imports pybliometrics
# (sources/elsevier_common.py) and breaks against mcp 2.x, which renamed
# FastMCP to MCPServer. lxml's <6.0.0 bound is not repeated here; no wheel
# below 6.0.1 exists for cp314, so it would block venv creation there.
REQUIREMENTS = (
    "mcp>=1.0.0,<2.0.0",
    "requests>=2.31.0",
    "toml>=0.10.2",
    "lxml>=4.9.0",
    "pybliometrics>=4.4.1,<5.0.0",
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

    # Windows routes os.execve through the UCRT's _wexecve, which faults with an
    # access violation (0xC0000005) while building the environment block, so the
    # server never starts. Spawn it and forward the exit status instead.
    if os.name == "nt":
        sys.exit(subprocess.call([str(python), str(server)], env=env))

    os.execve(str(python), [str(python), str(server)], env)


if __name__ == "__main__":
    main()
