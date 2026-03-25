"""GitHub連携モジュール"""
from __future__ import annotations

import logging
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlunparse

from config.config import GITHUB_TOKEN, GITHUB_USERNAME, VERCEL_GIT_REF
from git import GitCommandError, Repo
from github import Github

logger = logging.getLogger(__name__)


def authenticated_https_clone_url(
    clone_url: str, *, github_token: str | None = None
) -> str:
    """
    ``https://github.com/owner/repo.git`` に ``x-access-token`` を埋め込む（プライベート repo の clone 用）。

    ``github_token`` を省略すると ``GITHUB_TOKEN`` を使う。非 github.com はそのまま返す。
    """
    raw = (clone_url or "").strip().rstrip("/")
    if not raw.lower().endswith(".git"):
        raw = f"{raw}.git"
    tok = (github_token if github_token is not None else (GITHUB_TOKEN or "")).strip()
    if not tok:
        return raw
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if "github.com" not in host:
        return raw
    netloc = f"x-access-token:{tok}@{parsed.hostname}"
    if parsed.port:
        netloc = f"x-access-token:{tok}@{parsed.hostname}:{parsed.port}"
    return urlunparse(
        (parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
    )


def sanitize_github_repo_name(partner_name: str, record_number: str) -> str:
    """
    GitHub リポジトリ名: ``{レコード番号}-{ASCII部分}``。

    GitHub はリポジトリ名に日本語を受け付けないため、パートナー名から
    ASCII 英数字部分だけを抽出して付加する。ASCII 部分が無い場合は
    ``{レコード番号}`` のみ。
    GitHub の名前長上限（100）に収める。
    """
    rec = re.sub(r"\D", "", (record_number or "").strip()) or "0"
    ascii_part = re.sub(r"[^a-zA-Z0-9]", "-", (partner_name or "").strip())
    ascii_part = re.sub(r"-{2,}", "-", ascii_part).strip("-")
    if ascii_part:
        name = f"{rec}-{ascii_part}"
    else:
        name = rec
    if len(name) > 100:
        name = name[:100].rstrip("-")
    return name


class GitHubClient:
    """GitHub APIクライアント"""
    
    def __init__(self):
        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKENが必要です")
        self.github = Github(GITHUB_TOKEN)
        self.username = GITHUB_USERNAME
    
    def create_repository(
        self,
        repo_name: str,
        description: str = "",
        private: bool = False
    ) -> str:
        """
        新規リポジトリのみ作成する（同名が既に存在する場合は失敗。既存 repo への上書きプッシュは行わない）。

        Args:
            repo_name: リポジトリ名
            description: 説明
            private: プライベートリポジトリか
            
        Returns:
            リポジトリURL
        """
        try:
            user = self.github.get_user()
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=private,
            )

            repo_url = repo.clone_url
            logger.info(f"リポジトリを作成しました: {repo_url}")
            return repo_url

        except Exception as e:
            logger.error(f"リポジトリ作成エラー: {e}")
            raise
    
    def push_to_github(
        self,
        site_dir: Path,
        repo_name: str,
        description: str = ""
    ) -> str:
        """
        サイトをGitHubにプッシュ
        
        Args:
            site_dir: サイトディレクトリ
            repo_name: リポジトリ名
            description: リポジトリ説明
            
        Returns:
            リポジトリURL
        """
        try:
            # リポジトリを作成
            repo_url = self.create_repository(repo_name, description)
            
            # Gitリポジトリを初期化
            repo = Repo.init(site_dir)
            
            # .gitignoreを作成（存在しない場合）
            gitignore_path = site_dir / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# dependencies
node_modules/
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts
"""
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(gitignore_content)
            
            # README.mdを作成（存在しない場合）
            readme_path = site_dir / "README.md"
            if not readme_path.exists():
                readme_content = f"""# {repo_name}

{description}

## セットアップ

```bash
npm install
npm run dev
```

## ビルド

```bash
npm run build
npm start
```
"""
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(readme_content)
            
            # リモートを追加
            if "origin" in [remote.name for remote in repo.remotes]:
                origin = repo.remotes.origin
                origin.set_url(repo_url)
            else:
                origin = repo.create_remote("origin", repo_url)
            
            # ファイルをステージング
            repo.git.add(A=True)
            
            # コミット
            repo.index.commit("Initial commit: Auto-generated site")
            # 既定ブランチが master の環境でも main でプッシュできるよう統一
            if repo.active_branch.name != "main":
                repo.git.branch("-M", "main")

            # プッシュ
            origin.push(refspec="main:main", force=True)
            
            logger.info(f"GitHubにプッシュしました: {repo_url}")
            return repo_url
            
        except Exception as e:
            logger.error(f"GitHubプッシュエラー: {e}")
            raise

    def shallow_clone_repo_into_site_dir(
        self,
        clone_url: str,
        site_dir: Path,
        *,
        preserve_names: frozenset[str] = frozenset({"llm_raw_output"}),
    ) -> None:
        """
        一時ディレクトリへ shallow clone し、成果物を ``site_dir`` にマージする。

        Manus が ``BOT_DEPLOY_GITHUB_URL`` は返すが本文にパス付きフェンスが無い場合でも、
        GitHub 上の Next.js ソースで ``npm build`` と Vercel まで進める。
        ``preserve_names`` にある直下エントリ（例: ``llm_raw_output/``）は上書きしない。
        """
        site_dir = site_dir.resolve()
        if not site_dir.is_dir():
            raise ValueError(f"site_dir が存在しません: {site_dir}")

        auth_url = authenticated_https_clone_url(clone_url)
        ref = (VERCEL_GIT_REF or "main").strip() or "main"
        branch_candidates: list[str] = []
        for b in (ref, "main", "master"):
            if b and b not in branch_candidates:
                branch_candidates.append(b)

        last_exc: BaseException | None = None
        with tempfile.TemporaryDirectory() as td:
            clone_root = Path(td) / "repo"
            cloned = False
            for branch in branch_candidates:
                if clone_root.exists():
                    shutil.rmtree(clone_root, ignore_errors=True)
                clone_root.mkdir(parents=True, exist_ok=True)
                try:
                    Repo.clone_from(
                        auth_url,
                        str(clone_root),
                        branch=branch,
                        multi_options=["--depth", "1"],
                    )
                    cloned = True
                    break
                except GitCommandError as e:
                    last_exc = e
                    logger.debug(
                        "shallow clone branch=%r に失敗、次を試します: %s",
                        branch,
                        e,
                    )
            if not cloned:
                if clone_root.exists():
                    shutil.rmtree(clone_root, ignore_errors=True)
                clone_root.mkdir(parents=True, exist_ok=True)
                try:
                    Repo.clone_from(
                        auth_url,
                        str(clone_root),
                        multi_options=["--depth", "1"],
                    )
                    cloned = True
                    last_exc = None
                except GitCommandError as e:
                    last_exc = e
            if not cloned:
                raise RuntimeError(
                    f"GitHub の shallow clone に失敗しました: {clone_url!r}。"
                    " ブランチ（main / master）と GITHUB_TOKEN の repo 参照権限を確認してください。"
                ) from last_exc

            for item in clone_root.iterdir():
                if item.name in preserve_names:
                    continue
                dest = site_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

        logger.info(
            "Manus 用 GitHub URL からソースを shallow clone し site_dir に反映しました: %s",
            clone_url,
        )

    def get_repo_url(self, repo_name: str) -> Optional[str]:
        """
        リポジトリURLを取得
        
        Args:
            repo_name: リポジトリ名
            
        Returns:
            リポジトリURL
        """
        try:
            user = self.github.get_user()
            repo = user.get_repo(repo_name)
            return repo.html_url
        except Exception as e:
            logger.error(f"リポジトリ取得エラー: {e}")
            return None
