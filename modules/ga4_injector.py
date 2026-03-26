"""GA4 CTA トラッキングスクリプトを生成サイトの app/layout.tsx に注入する。

引数: site_dir（フェーズ3 でフェンス適用済みのサイトディレクトリ）/ measurement_id（GA4 測定 ID、空でも可）
処理: (1) config/ga4_cta_tracking.js をテンプレとして読み込み、測定IDを埋め込んで
       public/scripts/ga4-cta-tracking.js に書き出す。
       (2) app/layout.tsx に import Script + <Script> タグを挿入する。
       measurement_id が空の場合は gtag.js CDN ローダーを省略し、トラッキングスクリプトのみ注入する
       （イベントは dataLayer に蓄積され、後から測定ID を設定すればデータが流れ始める）。
出力: 注入成功なら True。layout.tsx 不在時は False。
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_TRACKING_TEMPLATE: Path = Path(__file__).resolve().parent.parent / "config" / "ga4_cta_tracking.js"
_PLACEHOLDER = "__GA4_MEASUREMENT_ID__"


def inject_ga4_tracking(site_dir: Path, *, measurement_id: str = "") -> bool:
    """生成サイトに GA4 トラッキングを注入する。

    measurement_id が空でも注入は行う（トラッキングスクリプトのみ。
    イベントは dataLayer に蓄積され、後から gtag.js + 測定ID を追加すればデータが流れる）。
    """
    layout_path = site_dir / "app" / "layout.tsx"
    if not layout_path.is_file():
        logger.warning("app/layout.tsx が見つかりません — GA4 注入スキップ: %s", layout_path)
        return False

    if not _TRACKING_TEMPLATE.is_file():
        logger.error("GA4 トラッキングテンプレートが見つかりません: %s", _TRACKING_TEMPLATE)
        return False

    mid = (measurement_id or "").strip()

    # 1. トラッキングスクリプトを public/scripts/ にコピー（測定IDがあれば埋め込み）
    template = _TRACKING_TEMPLATE.read_text(encoding="utf-8")
    script_body = template.replace(_PLACEHOLDER, mid) if mid else template.replace(_PLACEHOLDER, "")
    scripts_dir = site_dir / "public" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    dest = scripts_dir / "ga4-cta-tracking.js"
    dest.write_text(script_body, encoding="utf-8")
    logger.info("GA4 トラッキングスクリプトを配置: %s", dest.relative_to(site_dir))

    # 2. app/layout.tsx に Script タグを注入
    content = layout_path.read_text(encoding="utf-8")
    modified = _inject_into_layout(content, mid)
    if modified is None:
        logger.warning(
            "app/layout.tsx への GA4 注入に失敗しました"
            "（<body> タグが見つかりません。手動で Script タグを追加してください）"
        )
        return False

    layout_path.write_text(modified, encoding="utf-8")
    if mid:
        logger.info("GA4 トラッキングを app/layout.tsx に注入しました (ID=%s)", mid)
    else:
        logger.info(
            "GA4 トラッキングを app/layout.tsx に注入しました"
            "（測定ID未設定 — タグのみ。後から GA4_MEASUREMENT_ID を設定可）"
        )
    return True


# ------------------------------------------------------------------
# layout.tsx の書き換えロジック
# ------------------------------------------------------------------

_SCRIPT_IMPORT = 'import Script from "next/script";'


def _inject_into_layout(content: str, measurement_id: str) -> str | None:
    """layout.tsx 文字列に GA4 Script タグを挿入して返す。失敗時は None。

    measurement_id が空の場合は gtag.js CDN ローダーを省略し、
    トラッキングスクリプト（/scripts/ga4-cta-tracking.js）のみ注入する。
    """
    result = content

    # --- import 追加（next/script が未インポートの場合） ---
    if "next/script" not in result:
        last_import_match = None
        for m in re.finditer(r"^import\s+.+$", result, re.MULTILINE):
            last_import_match = m
        if last_import_match:
            pos = last_import_match.end()
            result = result[:pos] + "\n" + _SCRIPT_IMPORT + result[pos:]
        else:
            result = _SCRIPT_IMPORT + "\n" + result

    # --- <body ...> 直後に Script タグを挿入 ---
    gtag_loader = ""
    if measurement_id:
        gtag_loader = (
            "\n"
            "        <Script\n"
            f'          src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"\n'
            '          strategy="afterInteractive"\n'
            "        />"
        )

    tracking_script = (
        "\n"
        "        <Script\n"
        '          src="/scripts/ga4-cta-tracking.js"\n'
        '          strategy="afterInteractive"\n'
        "        />"
    )

    script_block = gtag_loader + tracking_script

    body_match = re.search(r"(<body[^>]*>)", result)
    if not body_match:
        return None

    insert_pos = body_match.end()
    result = result[:insert_pos] + script_block + result[insert_pos:]
    return result
