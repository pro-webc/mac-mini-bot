"""GitHub連携モジュール"""
import logging
import re
from pathlib import Path
from typing import Optional

from config.config import GITHUB_TOKEN, GITHUB_USERNAME
from git import Repo
from github import Github

logger = logging.getLogger(__name__)


def _partner_name_slug(partner_name: str) -> str:
    """GitHub リポジトリ名用（ASCII の英数字とハイフンのみ・連続ハイフンを圧縮）。"""
    raw = (partner_name or "").strip().lower()
    parts: list[str] = []
    for ch in raw:
        if "a" <= ch <= "z" or "0" <= ch <= "9":
            parts.append(ch)
        elif ch in "-_":
            parts.append("-")
        else:
            parts.append("-")
    s = "".join(parts)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "partner"


def sanitize_github_repo_name(partner_name: str, record_number: str) -> str:
    """
    GitHub リポジトリ名: ``{レコード番号}-test-{パートナー名}``（英数字のみのスラッグ化）。

    レコード番号は英数字のみ抽出、パートナー名は ASCII 英数字以外をハイフン化して連結。
    GitHub の名前長上限（100）に収める。
    """
    rec = re.sub(r"[^a-zA-Z0-9]", "", str(record_number).strip()) or "0"
    slug = _partner_name_slug(partner_name)
    name = f"{rec}-test-{slug}"
    if len(name) > 100:
        # パートナー側を削ってレコードと test を優先
        budget = max(4, 100 - len(f"{rec}-test-"))
        slug = slug[:budget].rstrip("-") or "p"
        name = f"{rec}-test-{slug}"
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
