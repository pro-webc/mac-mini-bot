#!/usr/bin/env python3
"""
テスト用: GitHub に新規リポジトリを作成 → 最小 Next.js をコミット → Vercel にデプロイ（本番と同じ API）。

前提:
  - GITHUB_TOKEN（repo 権限）
  - VERCEL_TOKEN（および必要なら VERCEL_TEAM_ID）
  - Vercel 側で GitHub が連携済み（SETUP.md 参照）

環境変数:
  E2E_GITHUB_USE_ORG=1 … GITHUB_ORG の組織にリポジトリを作成（既定は個人アカウント）。
    組織リポジトリは Vercel の GitHub App がその組織にインストール済みでないとデプロイが失敗しやすい。
  GITHUB_ORG … E2E_GITHUB_USE_ORG=1 のときのみ使用
  E2E_DELETE_REPO_AFTER=1 … 成功後にテストリポジトリを GitHub 上で削除（任意・管理者権限が必要）

使い方:
  python scripts/e2e_github_create_and_vercel_deploy.py
  E2E_GITHUB_USE_ORG=1 python scripts/e2e_github_create_and_vercel_deploy.py
"""
from __future__ import annotations

import base64
import json
import os
import random
import string
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

GH_API = "https://api.github.com"


def _b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def _gh_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _minimal_files() -> dict[str, str]:
    """最小 Next.js 14 App Router（Tailwind なし・ビルド可能）"""
    pkg = {
        "name": "vercel-e2e-smoke",
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "next": "^14.2.0",
        },
        "devDependencies": {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
        },
    }
    tsconfig = {
        "compilerOptions": {
            "target": "ES2017",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {"@/*": ["./*"]},
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"],
    }
    layout = """import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'E2E smoke',
  description: 'mac-mini-bot vercel e2e',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body style={{ fontFamily: 'system-ui', padding: '1rem' }}>{children}</body>
    </html>
  )
}
"""
    page = """export default function Page() {
  return (
    <main>
      <h1>E2E OK</h1>
      <p>mac-mini-bot: GitHub 新規リポジトリ → Vercel デプロイのスモークテストです。</p>
    </main>
  )
}
"""
    next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}
module.exports = nextConfig
"""
    next_env = """/// <reference types="next" />
/// <reference types="next/image-types/global" />
"""
    gitignore = """node_modules
.next
out
.env*.local
"""
    return {
        "package.json": json.dumps(pkg, indent=2, ensure_ascii=False) + "\n",
        "tsconfig.json": json.dumps(tsconfig, indent=2, ensure_ascii=False) + "\n",
        "next.config.js": next_config,
        "next-env.d.ts": next_env,
        "app/layout.tsx": layout,
        "app/page.tsx": page,
        ".gitignore": gitignore,
    }


def main() -> int:
    import requests
    from config.config import GITHUB_TOKEN, VERCEL_TOKEN
    from modules.vercel_client import VercelClient

    gh = (GITHUB_TOKEN or "").strip()
    vt = (VERCEL_TOKEN or "").strip()
    if not gh:
        print("ERROR: GITHUB_TOKEN が空です")
        return 1
    if not vt:
        print("ERROR: VERCEL_TOKEN が空です")
        return 1

    org_env = (os.getenv("GITHUB_ORG") or "").strip()
    use_org = os.getenv("E2E_GITHUB_USE_ORG", "").strip().lower() in ("1", "true", "yes")
    if use_org and not org_env:
        print("ERROR: E2E_GITHUB_USE_ORG=1 ですが GITHUB_ORG が未設定です")
        return 1
    h = _gh_headers(gh)

    r_user = requests.get(f"{GH_API}/user", headers=h, timeout=30)
    if r_user.status_code != 200:
        print(f"ERROR: GET /user HTTP {r_user.status_code}\n{r_user.text[:800]}")
        return 1
    login = r_user.json().get("login") or ""
    if not login:
        print("ERROR: GitHub ユーザー名を取得できませんでした")
        return 1

    if use_org and org_env:
        owner = org_env
        create_url = f"{GH_API}/orgs/{owner}/repos"
        print(f"    （E2E_GITHUB_USE_ORG=1 により組織 {owner} に作成）")
    else:
        owner = login
        create_url = f"{GH_API}/user/repos"
        if org_env and not use_org:
            print(
                f"    （GITHUB_ORG={org_env!r} は無視し、個人 {owner} に作成。"
                " 組織に作る場合は E2E_GITHUB_USE_ORG=1）"
            )

    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    repo_name = f"vercel-e2e-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{suffix}"

    print(f"[1] GitHub リポジトリ作成: {owner}/{repo_name} …")
    body = {
        "name": repo_name,
        "description": "mac-mini-bot E2E (safe to delete)",
        "private": True,
        "auto_init": True,
    }
    r_create = requests.post(create_url, headers=h, json=body, timeout=60)
    if r_create.status_code not in (201,):
        print(f"ERROR: POST create repo HTTP {r_create.status_code}\n{r_create.text[:1200]}")
        return 1
    print("    OK: リポジトリ作成済み（README 付き）")

    r_repo = requests.get(f"{GH_API}/repos/{owner}/{repo_name}", headers=h, timeout=30)
    if r_repo.status_code != 200:
        print(f"ERROR: GET repo HTTP {r_repo.status_code}\n{r_repo.text[:800]}")
        return 1
    default_branch = (r_repo.json().get("default_branch") or "main").strip()
    print(f"    デフォルトブランチ: {default_branch}")

    print("[2] 最小 Next.js ファイルを追加コミット …")
    files = _minimal_files()
    for path, content in files.items():
        path_enc = quote(path, safe="")
        put_url = f"{GH_API}/repos/{owner}/{repo_name}/contents/{path_enc}"
        payload = {
            "message": f"e2e: add {path}",
            "content": _b64(content),
            "branch": default_branch,
        }
        r_put = requests.put(put_url, headers=h, json=payload, timeout=60)
        if r_put.status_code not in (201,):
            print(f"ERROR: PUT {path} HTTP {r_put.status_code}\n{r_put.text[:1200]}")
            return 1
        time.sleep(0.4)
    print(f"    OK: {len(files)} ファイルを追加")

    # GitHub 側の参照が Vercel に伝わるまで短い待機（新規リポジトリで 400 を防ぐ）
    print("[2b] Vercel 呼び出し前に 10 秒待機 …")
    time.sleep(10)

    github_url = f"https://github.com/{owner}/{repo_name}.git"
    print(f"[3] Vercel deploy_from_github (ref={default_branch}): {github_url}")
    try:
        vc = VercelClient()
        out = vc.deploy_from_github(
            github_url, project_name=repo_name, git_ref=default_branch
        )
    except Exception as e:
        print(f"ERROR: {e}")
        _maybe_delete_repo(h, owner, repo_name)
        return 1

    print(f"    OK: deployment_id={out.get('deployment_id')}")
    print(f"    プレビュー URL: {out.get('url')}")

    if os.getenv("E2E_DELETE_REPO_AFTER", "").strip().lower() in ("1", "true", "yes"):
        _maybe_delete_repo(h, owner, repo_name)
    else:
        print(
            f"\n[後片付け] リポジトリを削除する場合: GitHub で {owner}/{repo_name} を削除するか、"
            f"\n  E2E_DELETE_REPO_AFTER=1 python scripts/e2e_github_create_and_vercel_deploy.py"
        )

    return 0


def _maybe_delete_repo(h: dict[str, str], owner: str, repo: str) -> None:
    import requests

    print(f"[cleanup] DELETE repos/{owner}/{repo} …")
    r = requests.delete(f"{GH_API}/repos/{owner}/{repo}", headers=h, timeout=60)
    if r.status_code == 204:
        print("    OK: GitHub リポジトリを削除しました")
    else:
        print(f"    WARN: DELETE HTTP {r.status_code} {r.text[:400]}")


if __name__ == "__main__":
    raise SystemExit(main())
