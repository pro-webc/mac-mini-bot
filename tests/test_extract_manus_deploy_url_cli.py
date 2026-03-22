"""scripts/extract_manus_deploy_github_url.py の結合テスト"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = ROOT / "scripts" / "extract_manus_deploy_github_url.py"
_FIXTURE = ROOT / "tests" / "fixtures" / "manus_response_with_deploy_url.md"


def test_extract_cli_reads_fixture() -> None:
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--input", str(_FIXTURE), "--require"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "https://github.com/example-org/example-repo.git"


def test_extract_cli_stdin_pipe() -> None:
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--require"],
        input="hello\n\nBOT_DEPLOY_GITHUB_URL: https://github.com/a/b.git\n",
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "https://github.com/a/b.git"


def test_extract_cli_require_missing_url_exits_1() -> None:
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--require"],
        input="no url line here\n",
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )
    assert r.returncode == 1
