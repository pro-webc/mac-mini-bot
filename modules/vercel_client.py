"""Vercel連携モジュール

既定のデプロイは POST /v13/deployments の gitSource（GitHub）で、人がダッシュボードで Git を接続したときと同様に
**GitHub App 連携**を前提とする。

VERCEL_DEPLOY_USE_GIT_SOURCE=false のときのみ、zipball + POST /v2/files（GitHub App 不要・スナップショットデプロイ）。
"""
from __future__ import annotations

import hashlib
import io
import logging
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from urllib.parse import quote, urlparse

import requests
from config.config import (
    GITHUB_TOKEN,
    VERCEL_DEPLOY_USE_GIT_SOURCE,
    VERCEL_FORCE_PUBLIC_DEPLOYMENTS,
    VERCEL_GIT_REF,
    VERCEL_TEAM_ID,
    VERCEL_TOKEN,
)

logger = logging.getLogger(__name__)


def _fetch_github_repo_numeric_id(owner: str, repo: str) -> int:
    """
    GitHub REST API のリポジトリ id（Vercel gitSource.repoId 用）。
    """
    tok = (GITHUB_TOKEN or "").strip()
    if not tok:
        raise RuntimeError(
            "gitSource に repoId を渡すには GITHUB_TOKEN が必要です（.env を確認）。"
        )
    url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(repo, safe='')}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {tok}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(
            f"GitHub リポジトリ情報の取得に失敗しました (HTTP {r.status_code}): {owner}/{repo}. "
            "トークンがその repo を読めるか確認してください。"
            f"\n{r.text[:600]}"
        )
    data = r.json()
    rid = data.get("id")
    if rid is None:
        raise RuntimeError(f"GitHub API 応答に id がありません: {data!r}")
    return int(rid)


def _github_owner_repo_from_url(github_url: str) -> tuple[str, str]:
    """
    https://github.com/owner/repo.git から (owner, repo) を返す。
    """
    u = (github_url or "").strip().rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    parsed = urlparse(u)
    path = (parsed.path or "").strip("/")
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2:
        return parts[0], parts[1]
    raise ValueError(f"GitHub URL から owner/repo を解釈できません: {github_url!r}")


def github_owner_repo_from_clone_url(github_url: str) -> tuple[str, str]:
    """
    Git clone URL（https://github.com/owner/repo.git 等）から (owner, repo) を返す。

    Manus が push したリポジトリ URL をパースし、Vercel のプロジェクト名を GitHub 側の repo 名と揃えるために使う。
    """
    return _github_owner_repo_from_url(github_url)


def _extract_github_zip_to_files(zip_bytes: bytes) -> dict[str, bytes]:
    """
    GitHub の zipball（単一ルートフォルダ付き）を {相対パス: バイナリ} に展開する。
    """
    out: dict[str, bytes] = {}
    skip_leafs = {".DS_Store"}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if not infos:
            return out
        first = infos[0].filename.replace("\\", "/")
        if "/" not in first:
            root_prefix = ""
        else:
            root_prefix = first.split("/")[0] + "/"

        for inf in infos:
            fn = inf.filename.replace("\\", "/")
            if root_prefix and not fn.startswith(root_prefix):
                raise ValueError(
                    f"GitHub zip のルートが一致しません: {fn!r}（期待プレフィックス {root_prefix!r}）"
                )
            rel = fn[len(root_prefix) :] if root_prefix else fn
            rel = rel.strip("/")
            if not rel:
                continue
            if "__MACOSX" in rel.split("/") or ".git" in rel.split("/"):
                continue
            base = rel.rsplit("/", 1)[-1]
            if base in skip_leafs:
                continue
            if inf.file_size > 50 * 1024 * 1024:
                logger.warning("スキップ（50MB超）: %s", rel)
                continue
            out[rel] = zf.read(inf)
    return out


class VercelClient:
    """Vercel APIクライアント"""

    def __init__(self):
        if not VERCEL_TOKEN:
            raise ValueError("VERCEL_TOKENが必要です")
        self.token = VERCEL_TOKEN
        self.team_id = VERCEL_TEAM_ID
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def deploy_from_github(
        self,
        github_url: str,
        project_name: str | None = None,
        git_ref: str | None = None,
    ) -> dict:
        """
        GitHub リポジトリ URL から Vercel にデプロイする。

        既定（VERCEL_DEPLOY_USE_GIT_SOURCE=true）:
          POST /v13/deployments に gitSource を渡す。**Vercel GitHub App** がリポジトリを参照できることが必要。
          デプロイ後の **Git 連携・push での自動デプロイ**は、人が手でインポートした場合と同様に扱える。

        VERCEL_DEPLOY_USE_GIT_SOURCE=false のとき:
          GitHub zipball + POST /v2/files。**GitHub App は不要**だが、スナップショットデプロイであり
          連携の挙動は gitSource 既定より弱くなりやすい。

        Args:
            github_url: GitHub リポジトリ URL（https://github.com/org/repo.git）
            project_name: Vercel 上のプロジェクト名（省略時はリポジトリ名）
            git_ref: デプロイするブランチ名（省略時は VERCEL_GIT_REF）

        Returns:
            デプロイ情報（deployment_id, url, project_id）
        """
        try:
            org, repo = _github_owner_repo_from_url(github_url)
            if not project_name:
                project_name = repo

            ref = (git_ref or VERCEL_GIT_REF or "main").strip()

            if VERCEL_DEPLOY_USE_GIT_SOURCE:
                deployment = self._create_deployment_from_git_source(
                    project_name=project_name,
                    org=org,
                    repo=repo,
                    ref=ref,
                )
            else:
                deployment = self._deploy_from_github_archive(
                    github_url=github_url,
                    project_name=project_name,
                    owner=org,
                    repo=repo,
                    ref=ref,
                )

            dep_id = deployment.get("id")
            if not dep_id:
                raise RuntimeError(f"デプロイ応答に id がありません: {deployment!r}")

            project_id = deployment.get("projectId")
            if not project_id and isinstance(deployment.get("project"), dict):
                project_id = deployment["project"].get("id")

            if project_id:
                self._ensure_public_deployment_access(
                    {"id": project_id, "name": project_name}
                )
            else:
                logger.warning(
                    "デプロイ応答に projectId が無いため公開設定 PATCH をスキップします。"
                    "必要なら Vercel ダッシュボードでデプロイ保護を確認してください。"
                )

            deployment_url = self._wait_for_deployment(dep_id)

            logger.info("Vercelにデプロイしました: %s", deployment_url)
            return {
                "deployment_id": dep_id,
                "url": deployment_url,
                "project_id": project_id or "",
            }

        except Exception as e:
            logger.exception("Vercelデプロイエラー: %s", e)
            raise

    def _deploy_from_github_archive(
        self,
        *,
        github_url: str,
        project_name: str,
        owner: str,
        repo: str,
        ref: str,
    ) -> dict:
        """GitHub zipball → /v2/files → /v13/deployments（files）"""
        zip_bytes = self._download_github_zipball(owner, repo, ref)
        files_map = _extract_github_zip_to_files(zip_bytes)
        if not files_map:
            raise RuntimeError(
                "GitHub アーカイブにデプロイ可能なファイルがありません。"
                "ブランチ名（VERCEL_GIT_REF）とリポジトリ内容を確認してください。"
            )

        logger.info(
            "Vercel ファイルデプロイ: %s ファイル（zipball から）project=%r ref=%s",
            len(files_map),
            project_name,
            ref,
        )

        git_meta = self._fetch_github_commit_metadata(owner, repo, ref)
        _u = github_url.strip().rstrip("/")
        if not _u.endswith(".git"):
            _u = f"{_u}.git"
        git_meta.setdefault("remoteUrl", _u)
        if "commitRef" not in git_meta:
            git_meta["commitRef"] = ref

        file_entries: list[dict[str, Any]] = []
        max_workers = min(16, max(4, len(files_map) // 20 + 1))
        items = list(files_map.items())

        def _upload(path_content: tuple[str, bytes]) -> dict[str, Any]:
            path, content = path_content
            digest, size = self._vercel_upload_blob(content)
            return {"file": path, "sha": digest, "size": size}

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = [ex.submit(_upload, it) for it in items]
            for fut in as_completed(futs):
                file_entries.append(fut.result())

        file_entries.sort(key=lambda x: x["file"])
        return self._create_deployment_with_files(
            project_name=project_name,
            files=file_entries,
            git_metadata=git_meta,
        )

    def _download_github_zipball(self, owner: str, repo: str, ref: str) -> bytes:
        """GET /repos/{owner}/{repo}/zipball/{ref}"""
        url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{quote(ref)}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        tok = (GITHUB_TOKEN or "").strip()
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=300)
        if r.status_code != 200:
            raise RuntimeError(
                f"GitHub zipball 取得に失敗しました (HTTP {r.status_code})。"
                "プライベートリポジトリなら GITHUB_TOKEN、ブランチ名（VERCEL_GIT_REF）を確認してください。"
                f"\n{r.text[:800]}"
            )
        return r.content

    def _vercel_upload_blob(self, content: bytes) -> tuple[str, int]:
        """POST /v2/files — SHA1 とサイズを返す"""
        digest = hashlib.sha1(content).hexdigest()
        size = len(content)
        if size > 50 * 1024 * 1024:
            raise RuntimeError(f"単一ファイルが 50MB を超えています（{size} bytes）")

        qurl = f"{self.base_url}/v2/files"
        if self.team_id:
            qurl += f"?teamId={quote(str(self.team_id), safe='')}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(size),
            "x-vercel-digest": digest,
        }
        r = requests.post(qurl, headers=headers, data=content, timeout=180)
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Vercel ファイルアップロード失敗 (HTTP {r.status_code}): {r.text[:1200]}"
            )
        return digest, size

    def _fetch_github_commit_metadata(self, owner: str, repo: str, ref: str) -> dict[str, Any]:
        """コミット情報（ダッシュボード表示用・任意）"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{quote(ref)}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        tok = (GITHUB_TOKEN or "").strip()
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            return {}
        data = r.json()
        commit = data.get("commit") or {}
        author = commit.get("author") or {}
        msg = commit.get("message") or ""
        if isinstance(msg, str) and "\n" in msg:
            msg = msg.split("\n", 1)[0]
        sha = data.get("sha") or ""
        return {
            "commitSha": sha[:40] if sha else "",
            "commitMessage": (msg or "")[:500],
            "commitAuthorName": (author.get("name") or "")[:200],
            "commitAuthorEmail": (author.get("email") or "")[:200],
            "commitRef": ref,
        }

    def _create_deployment_with_files(
        self,
        *,
        project_name: str,
        files: list[dict[str, Any]],
        git_metadata: dict[str, Any],
    ) -> dict:
        """POST /v13/deployments — files のみ（gitSource なし）"""
        q: list[str] = []
        if self.team_id:
            q.append(f"teamId={self.team_id}")
        q.append("skipAutoDetectionConfirmation=1")
        qs = "&".join(q)
        url = f"{self.base_url}/v13/deployments?{qs}"

        payload: dict[str, Any] = {
            "name": project_name,
            "files": files,
            "target": "production",
            "gitMetadata": git_metadata,
        }

        logger.info(
            "Vercel デプロイ作成（ファイル経由）: project=%r files=%s",
            project_name,
            len(files),
        )
        response = requests.post(url, headers=self.headers, json=payload, timeout=120)
        if response.status_code not in (200, 201):
            raise Exception(
                f"デプロイ作成エラー (HTTP {response.status_code}): {response.text[:2000]}"
            )
        return response.json()

    def _create_deployment_from_git_source(
        self,
        *,
        project_name: str,
        org: str,
        repo: str,
        ref: str,
    ) -> dict:
        """
        POST /v13/deployments — gitSource で GitHub を指定。

        Vercel OpenAPI では github 向けに (1) repoId+ref と (2) org+repo+ref の両方がある。
        org+repo だけだと環境によって incorrect_git_source_info になりやすいため、
        まず GitHub API で取得した **repoId（数値）** を使う。
        """
        q: list[str] = []
        if self.team_id:
            q.append(f"teamId={self.team_id}")
        # フレームワーク自動検出の確認をスキップ（CI/API 向け）
        q.append("skipAutoDetectionConfirmation=1")
        qs = "&".join(q)
        url = f"{self.base_url}/v13/deployments?{qs}"

        repo_id = _fetch_github_repo_numeric_id(org, repo)
        # ref はブランチ名（例: main）。refs/heads/... 形式は API により任意。
        payload_repo_id: dict[str, Any] = {
            "name": project_name,
            "gitSource": {
                "type": "github",
                "repoId": repo_id,
                "ref": ref,
            },
            "target": "production",
        }

        logger.info(
            "Vercel デプロイ作成: project=%r gitSource=github repoId=%s ref=%s (owner=%s/%s)",
            project_name,
            repo_id,
            ref,
            org,
            repo,
        )
        response = requests.post(
            url, headers=self.headers, json=payload_repo_id, timeout=120
        )
        if response.status_code in (200, 201):
            return response.json()

        # フォールバック: org+repo（古いクライアント・一部環境向け）
        logger.warning(
            "gitSource(repoId) が拒否されました (HTTP %s)。org+repo で再試行します。body=%s",
            response.status_code,
            response.text[:500],
        )
        payload_org_repo: dict[str, Any] = {
            "name": project_name,
            "gitSource": {
                "type": "github",
                "org": org,
                "repo": repo,
                "ref": ref,
            },
            "target": "production",
        }
        response2 = requests.post(
            url, headers=self.headers, json=payload_org_repo, timeout=120
        )
        if response2.status_code not in (200, 201):
            raise Exception(
                f"デプロイ作成エラー (HTTP {response2.status_code}): {response2.text}"
            )
        return response2.json()

    def _ensure_public_deployment_access(self, project: dict[str, Any]) -> None:
        """
        本番・プレビュー URL が Vercel ログインなしで閲覧できるよう、
        プロジェクト単位のデプロイ保護を解除する（API: PATCH /v9/projects）。
        """
        if not VERCEL_FORCE_PUBLIC_DEPLOYMENTS:
            logger.info(
                "VERCEL_FORCE_PUBLIC_DEPLOYMENTS=false のため、デプロイ保護の自動解除をスキップします"
            )
            return

        pid = project.get("id") or project.get("name")
        if not pid:
            logger.warning("プロジェクト識別子が取得できないため、公開設定の PATCH をスキップします")
            return

        safe_id = quote(str(pid), safe="")
        purl = f"{self.base_url}/v9/projects/{safe_id}"
        if self.team_id:
            purl += f"?teamId={self.team_id}"

        body = {
            "ssoProtection": None,
            "passwordProtection": None,
            "trustedIps": None,
        }

        try:
            response = requests.patch(purl, headers=self.headers, json=body, timeout=60)
        except requests.RequestException as e:
            logger.error(
                "デプロイ公開設定の PATCH リクエストに失敗しました project=%r: %s",
                pid,
                e,
                exc_info=True,
            )
            raise

        if response.status_code not in (200, 204):
            logger.error(
                "デプロイ公開設定の更新に失敗しました project=%r status=%s body=%s",
                pid,
                response.status_code,
                response.text[:2000],
            )
            raise RuntimeError(
                f"Vercel プロジェクトの公開設定に失敗しました (HTTP {response.status_code})。"
                "トークンにプロジェクト更新権限があるか、チームのデプロイ保護ポリシーを確認してください。"
            )

        logger.info(
            "デプロイを公開設定にしました（ssoProtection / passwordProtection / trustedIps を解除）project=%r",
            pid,
        )

    def _wait_for_deployment(self, deployment_id: str, max_wait: int = 600) -> str:
        """デプロイ完了を待機（ビルド時間を考慮して max_wait 既定 10 分）"""
        url = f"{self.base_url}/v13/deployments/{deployment_id}"
        if self.team_id:
            url += f"?teamId={self.team_id}"

        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = requests.get(url, headers=self.headers, timeout=60)
            if response.status_code == 200:
                deployment = response.json()
                state = deployment.get("readyState", "")

                if state == "READY":
                    url_obj = deployment.get("url", "")
                    return f"https://{url_obj}" if url_obj else ""
                if state == "ERROR":
                    error = deployment.get("error", {})
                    raise Exception(f"デプロイエラー: {error}")

            time.sleep(5)

        raise Exception(f"デプロイがタイムアウトしました: {deployment_id}")

    def check_deployment_status(self, deployment_id: str) -> dict:
        url = f"{self.base_url}/v13/deployments/{deployment_id}"
        if self.team_id:
            url += f"?teamId={self.team_id}"

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"デプロイステータス取得エラー: {response.text}")

    def verify_deployment_url(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error("URL確認エラー: %s", e)
            return False
