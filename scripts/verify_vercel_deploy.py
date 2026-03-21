#!/usr/bin/env python3
"""
Vercel デプロイ動作確認（ローカル用）

1. GET /v2/user でトークン確認
2. （任意）チーム ID 確認
3. VERCEL_TEST_GITHUB_URL があるとき deploy_from_github を実行
   （既定は gitSource。zipball 方式は VERCEL_DEPLOY_USE_GIT_SOURCE=false）

使い方:
  python scripts/verify_vercel_deploy.py
  VERCEL_TEST_GITHUB_URL=https://github.com/org/repo.git python scripts/verify_vercel_deploy.py
"""
from __future__ import annotations

import os
import sys

# プロジェクトルートで実行すること
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    import requests
    from config.config import VERCEL_TEAM_ID, VERCEL_TOKEN
    from modules.vercel_client import VercelClient

    if not VERCEL_TOKEN.strip():
        print("ERROR: VERCEL_TOKEN が空です")
        return 1

    h = {"Authorization": f"Bearer {VERCEL_TOKEN}"}
    r = requests.get("https://api.vercel.com/v2/user", headers=h, timeout=30)
    print(f"[1] GET /v2/user → HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:1200])
        return 1
    u = r.json().get("user") or {}
    print(f"    OK: Vercel アカウント ({u.get('email') or u.get('username') or 'ok'})")

    if VERCEL_TEAM_ID.strip():
        r2 = requests.get(
            f"https://api.vercel.com/v2/teams/{VERCEL_TEAM_ID}",
            headers=h,
            timeout=30,
        )
        print(f"[2] GET /v2/teams/<id> → HTTP {r2.status_code}")
        if r2.status_code != 200:
            print(r2.text[:800])
            return 1
        print("    OK: チームにアクセスできました")
    else:
        print("[2] VERCEL_TEAM_ID 未設定 — 個人アカウントとして続行")

    test_url = (os.getenv("VERCEL_TEST_GITHUB_URL") or "").strip()
    if not test_url:
        print(
            "[3] デプロイ API の実試行はスキップ（VERCEL_TEST_GITHUB_URL 未設定）"
            "\n    試すには:"
            "\n    VERCEL_TEST_GITHUB_URL=https://github.com/owner/repo.git python scripts/verify_vercel_deploy.py"
        )
        return 0

    print(f"[3] deploy_from_github を実行します: {test_url}")
    try:
        vc = VercelClient()
        out = vc.deploy_from_github(test_url, project_name=None)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    print(f"    OK: deployment_id={out.get('deployment_id')}")
    print(f"    URL: {out.get('url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
