#!/usr/bin/env python3
"""
工程テスト **Vercel デプロイのみ**（Manus / Gemini は行わない）。

GitHub リポジトリ URL（``https://github.com/owner/repo.git``）を渡し、
本番と同じ ``VercelClient.deploy_from_github`` でデプロイする。

入力の例::

  --github-url https://github.com/org/repo.git

  --url-file <manus_only_tests/.../03_deploy_github_url.txt>  （1 行目が URL）

環境: ``VERCEL_TOKEN`` 必須。gitSource 既定時は ``GITHUB_TOKEN`` で repoId 取得。

リポジトリルートで実行。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.logging_setup import configure_logging  # noqa: E402


def _read_url_file(p: Path) -> str:
    text = p.read_text(encoding="utf-8").strip()
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s
    return ""


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="工程テスト: Vercel デプロイのみ")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--github-url", type=str, default=None, metavar="URL")
    g.add_argument("--url-file", type=Path, default=None, metavar="PATH")
    parser.add_argument(
        "--project-name",
        type=str,
        default=None,
        metavar="NAME",
        help="省略時は URL から repo 名を解釈（本番の Manus 連携と同じ）",
    )
    args = parser.parse_args()

    if args.github_url:
        raw = args.github_url.strip()
    else:
        uf = args.url_file.resolve()
        if not uf.is_file():
            print(f"ERROR: --url-file が見つかりません: {uf}", file=sys.stderr)
            return 1
        raw = _read_url_file(uf)
    if not raw:
        print(
            "ERROR: GitHub URL が空です。Manus 工程テストの 03_deploy_github_url.txt に "
            "BOT_DEPLOY_GITHUB_URL 相当の1行があるか確認してください。",
            file=sys.stderr,
        )
        return 1

    github_url = raw.rstrip("/")
    if not github_url.lower().endswith(".git"):
        github_url = f"{github_url}.git"

    from modules.vercel_client import VercelClient, github_owner_repo_from_clone_url

    project_name = args.project_name
    if not project_name:
        try:
            _, project_name = github_owner_repo_from_clone_url(github_url)
        except ValueError as e:
            print(f"ERROR: URL から repo 名を解釈できません: {e}", file=sys.stderr)
            return 1

    print(f"github_url={github_url}")
    print(f"vercel project_name={project_name!r}")
    print("Vercel デプロイ実行中…")

    vc = VercelClient()
    deployment = vc.deploy_from_github(github_url, project_name)
    deploy_url = deployment.get("url") or ""

    print(f"deployment_id: {deployment.get('deployment_id')}")
    print(f"公開 URL: {deploy_url}")

    out_root = Path(
        os.getenv("PIPELINE_TEST_DEPLOY_RESULT_DIR", "")
        or (ROOT / "output" / "pipeline_test_runs" / "deploy_only_tests")
    )
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    out_root.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = out_root / stamp
    out.mkdir(parents=True, exist_ok=True)
    import json

    (out / "01_deploy_result.json").write_text(
        json.dumps(
            {
                "github_url": github_url,
                "project_name": project_name,
                "deployment_id": deployment.get("deployment_id"),
                "url": deploy_url,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"結果保存: {out / '01_deploy_result.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
