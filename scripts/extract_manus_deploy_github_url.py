#!/usr/bin/env python3
"""
Manus 返答テキスト（マークダウン）から、末尾の ``BOT_DEPLOY_GITHUB_URL:`` 行を解析し clone 用 URL を取り出す。

本番と同じ規則は ``modules.manus_refactor.split_manus_response_deploy_url``。

入力::

  python3 scripts/extract_manus_deploy_github_url.py --input path/to/manus_reply.md
  cat manus_reply.md | python3 scripts/extract_manus_deploy_github_url.py

標準出力には **URL のみ** 1 行（見つからないときは何も出さず終了コード 1 と ``--require`` 併用可）。

GitHub Actions で後続ジョブに渡す例::

  URL=$(python3 scripts/extract_manus_deploy_github_url.py --input manus.md --require)
  echo "deploy_git_url=$URL" >> "$GITHUB_OUTPUT"

または ``--github-output deploy_git_url``（``GITHUB_OUTPUT`` が設定されているときのみ書き込み）。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.manus_refactor import split_manus_response_deploy_url  # noqa: E402


def _read_input(args: argparse.Namespace) -> str:
    if args.input is not None:
        p = args.input.resolve()
        if not p.is_file():
            print(f"ERROR: 入力ファイルがありません: {p}", file=sys.stderr)
            sys.exit(2)
        return p.read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manus 返答から BOT_DEPLOY_GITHUB_URL を抽出する",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=None,
        metavar="PATH",
        help="Manus 返答全文（省略時は標準入力）",
    )
    parser.add_argument(
        "--require",
        action="store_true",
        help="URL が無い場合は終了コード 1",
    )
    parser.add_argument(
        "--github-output",
        metavar="NAME",
        default=None,
        help="GITHUB_OUTPUT に NAME=<url> を追記（環境変数 GITHUB_OUTPUT が必須）",
    )
    args = parser.parse_args()

    text = _read_input(args)
    _body, url = split_manus_response_deploy_url(text)

    if not url:
        if args.require:
            print(
                "ERROR: 最終非空行に BOT_DEPLOY_GITHUB_URL: が見つかりません",
                file=sys.stderr,
            )
            return 1
        return 0

    print(url, flush=True)

    gh_out = (os.environ.get("GITHUB_OUTPUT") or "").strip()
    if args.github_output and gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"{args.github_output}={url}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
