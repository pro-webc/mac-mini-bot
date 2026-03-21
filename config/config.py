"""設定管理モジュール"""
import os
from pathlib import Path

from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent


def _parse_positive_int(
    name: str, default: int, *, minimum: int = 1, maximum: int = 100
) -> int:
    """環境変数を正の整数として解釈（不正時は default、範囲クランプ）"""
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        v = int(str(raw).strip(), 10)
        return max(minimum, min(maximum, v))
    except ValueError:
        return default

# Google Sheets設定
# service_account: credentials の JSON（サービスアカウント鍵）
# application_default: JSON 不要。通常は `gcloud auth application-default login` で取得したユーザー資格情報
_raw_gs_auth = os.getenv("GOOGLE_SHEETS_AUTH_MODE", "service_account").strip().lower()
GOOGLE_SHEETS_AUTH_MODE = (
    _raw_gs_auth
    if _raw_gs_auth in ("service_account", "application_default")
    else "service_account"
)
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_SHEETS_CREDENTIALS_PATH",
    str(PROJECT_ROOT / "credentials" / "google-credentials.json")
)
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
# 案件取得・更新対象のシート名（タブ名）
GOOGLE_SHEETS_SHEET_NAME = os.getenv("GOOGLE_SHEETS_SHEET_NAME", "Sheet1").strip() or "Sheet1"
# ADC 利用時のクォータプロジェクト（任意・未設定だと UserWarning が出る場合あり）
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
# 1行目の列見出しが期待と異なるとき、true なら起動失敗（false は警告のみ）
SPREADSHEET_HEADERS_STRICT = os.getenv("SPREADSHEET_HEADERS_STRICT", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
# Bot が処理する行の条件（1）AI統合ステータス列は「フェーズ」用。次の値と完全一致する行のみ。
SPREADSHEET_TARGET_AI_STATUS = os.getenv(
    "SPREADSHEET_TARGET_AI_STATUS", "デモサイト制作中"
).strip()
# （2）テストサイトURL列が空である行のみ（true のとき）。デモ未着手の案件を区別するため。
SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL = os.getenv(
    "SPREADSHEET_BOT_REQUIRE_EMPTY_TEST_SITE_URL", "true"
).strip().lower() in ("1", "true", "yes")
# true のとき: ヒアリング列が URL（http/https 始まり）の行はスキップ。本文が入っている行のみ着手
SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL = os.getenv(
    "SPREADSHEET_REQUIRE_HEARING_BODY_NOT_URL", "true"
).strip().lower() in ("1", "true", "yes")

# 1回の起動で処理する案件の最大件数（0 または未設定で無制限・上から順）
_raw_max_cases = os.getenv("BOT_MAX_CASES", "").strip()
try:
    BOT_MAX_CASES = max(0, int(_raw_max_cases, 10)) if _raw_max_cases else 0
except ValueError:
    BOT_MAX_CASES = 0

# mac-mini（AV）列のエラー表示の最大文字数（「エラー: 」を除く本文側の上限に近い挙動。50〜500）
_raw_ai_err = os.getenv("SPREADSHEET_AI_STATUS_ERROR_MAX_LEN", "200").strip()
try:
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN = max(
        50, min(500, int(_raw_ai_err, 10))
    )
except ValueError:
    SPREADSHEET_AI_STATUS_ERROR_MAX_LEN = 200

# API キー（将来の実 LLM 接続などで利用）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# npm ビルド検証
SITE_BUILD_ENABLED = os.getenv("SITE_BUILD_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
SITE_BUILD_MAX_FIX_ATTEMPTS = _parse_positive_int(
    "SITE_BUILD_MAX_FIX_ATTEMPTS", 3, minimum=1, maximum=20
)
SITE_IMPLEMENTATION_ENABLED = os.getenv("SITE_IMPLEMENTATION_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
# true のとき、土台コピー後もテンプレ付属の app/about 等のデモルートを残す（既定 false: 契約ページ数とズレ防止のため削除）
SITE_KEEP_TEMPLATE_APP_ROUTES = os.getenv(
    "SITE_KEEP_TEMPLATE_APP_ROUTES", "false"
).strip().lower() in ("1", "true", "yes")

# GitHub設定
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")

# Vercel設定
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN", "")
VERCEL_TEAM_ID = os.getenv("VERCEL_TEAM_ID", "")
# GitHub 連携デプロイ時の参照ブランチ（push 先と一致させる。例: main / master）
VERCEL_GIT_REF = (os.getenv("VERCEL_GIT_REF", "main") or "main").strip()
# true（既定）: POST /v13/deployments の gitSource（ダッシュボードの Git 連携と同様・GitHub App 必須）
# false: GitHub zipball + POST /v2/files（連携なしのファイルデプロイ。push 自動デプロイは別途手動接続が必要になりやすい）
VERCEL_DEPLOY_USE_GIT_SOURCE = os.getenv(
    "VERCEL_DEPLOY_USE_GIT_SOURCE", "true"
).strip().lower() in ("1", "true", "yes")
# デプロイ先 URL をスプレッドシートに書く方法: vercel（既定）| github（Vercel をスキップし GitHub URL のみ記録）
_raw_deploy_url_src = os.getenv("BOT_DEPLOY_URL_SOURCE", "vercel").strip().lower()
BOT_DEPLOY_URL_SOURCE = (
    _raw_deploy_url_src if _raw_deploy_url_src in ("vercel", "github") else "vercel"
)
# デプロイURLをログイン不要で閲覧できるよう、プロジェクトのデプロイ保護を API で解除する
VERCEL_FORCE_PUBLIC_DEPLOYMENTS = os.getenv(
    "VERCEL_FORCE_PUBLIC_DEPLOYMENTS", "true"
).strip().lower() in ("1", "true", "yes")

# その他設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(PROJECT_ROOT / "output")))
TEMPLATE_DIR = Path(os.getenv("TEMPLATE_DIR", str(PROJECT_ROOT / "templates")))

# スプレッドシート列マッピング
SPREADSHEET_COLUMNS = {
    "record_number": "B",  # record_id
    "partner_name": "C",   # client_name
    "contract_plan": "D",  # plan_type
    # SPREADSHEET_TARGET_AI_STATUS と照合する列（例: overall_status）
    "phase_status": "M",
    # Bot 専用: 処理中 / 完了 / エラー（業務フェーズ列とは別）。1行目の見出しは不要・検証しない
    "ai_status": "AV",
    "phase_deadline": "T",  # phase_deadline
    "appo_memo": "AD",     # ap_recording_memo
    "sales_notes": "AE",   # sales_note_pre_demo
    "hearing_sheet_url": "AH",  # hearing_sheet_url
    "test_site_url": "AJ",      # test_url
    "deploy_url": "AW",         # 書き込みのみ。1行目の見出しは不要・検証しない
}

# 1行目に期待する列名（SPREADSHEET_COLUMNS のキーで検証する列のみ）
# ※ AV（ai_status）・AW（deploy_url）は Bot 書き込み専用のため見出し検証の対象外
# ※実シートの英語ヘッダーに合わせる（日本語シートの場合は .env で別途調整）
SPREADSHEET_HEADER_LABELS: dict[str, str] = {
    "record_number": "record_id",
    "partner_name": "client_name",
    "contract_plan": "plan_type",
    "phase_status": "overall_status",
    "phase_deadline": "phase_deadline",
    "appo_memo": "ap_recording_memo",
    "sales_notes": "sales_note_pre_demo",
    "hearing_sheet_url": "hearing_sheet_url",
    "test_site_url": "test_url",
}

# いずれかが空の行は対象フェーズでも処理しない（カンマ区切り・SPREADSHEET_COLUMNS のキーのみ）
_raw_req_fields = os.getenv(
    "SPREADSHEET_REQUIRED_FIELDS",
    "record_number,partner_name,contract_plan",
)
SPREADSHEET_REQUIRED_CASE_FIELDS: tuple[str, ...] = tuple(
    k.strip()
    for k in _raw_req_fields.split(",")
    if k.strip() and k.strip() in SPREADSHEET_COLUMNS
)
if not SPREADSHEET_REQUIRED_CASE_FIELDS:
    SPREADSHEET_REQUIRED_CASE_FIELDS = (
        "record_number",
        "partner_name",
        "contract_plan",
    )

# 契約プラン情報
CONTRACT_PLANS = {
    "BASIC LP": {
        "name": "BASIC LP",
        "pages": 1,
        "type": "landing_page"
    },
    "BASIC": {
        "name": "BASIC",
        "pages": 1,
        "type": "website"
    },
    "STANDARD": {
        "name": "STANDARD",
        "pages": 6,
        "type": "website"
    },
    "ADVANCE": {
        "name": "ADVANCE",
        "pages": 12,
        "type": "website"
    }
}

def get_contract_plan_info(plan_name: str) -> dict:
    """
    契約プラン情報を取得
    
    Args:
        plan_name: 契約プラン名
        
    Returns:
        契約プラン情報（見つからない場合はデフォルト）
    """
    # プラン名の正規化（大文字小文字を無視）
    plan_name_upper = plan_name.upper() if plan_name else ""
    
    for key, value in CONTRACT_PLANS.items():
        if key.upper() == plan_name_upper or value["name"].upper() == plan_name_upper:
            return value
    
    # デフォルト（STANDARD）
    return CONTRACT_PLANS["STANDARD"]


# プラン共通の技術・スタイリング要件（仕様書・コード生成の双方で参照）
COMMON_TECHNICAL_SPEC = {
    "stack": {
        "framework": "Next.js (App Router)",
        "ui": "React",
        "styling": "Tailwind CSS",
    },
    "architecture": {
        "components": "セクション単位でコンポーネントを分割（1セクション=1コンポーネントを原則）",
        "app_router": True,
    },
    "css_rules": {
        "import_order": (
            "CSSの@import（Google Fonts等）は、globals.css または <style> の"
            "最上部に配置。:root・セレクタ・その他のルールより前。違反するとビルドエラー。"
        ),
    },
    "content_visualization": {
        "diagrams_and_tables": "図解・比較表は画像ではなくマークアップ＋Tailwindで実装",
    },
    "icons": {
        "default": "Lucide React（lucide-react）",
        "sns": "Simple Icons（react-icons の si 等、Simple Icons準拠）",
        "forbidden": "アイコンを画像プレースホルダーで代用することは禁止",
    },
    "images": {
        "unsplash": "Unsplash の利用禁止",
        "real_assets": "実画像ファイルは配置しない",
        "placeholder": (
            "画像プレースホルダーUI（枠・比率・説明テキスト）で何が表示されるべきかを明示。"
            "画像上に載せるべきテキストはオーバーレイとしてデザイン上そのまま表示"
        ),
    },
    "maps": {
        "location": "所在地表示時は Google Maps を埋め込み（iframe/embed）。マップ表示エリアに画像・プレースホルダーは置かない",
        "service_area": "「対応エリア」用の画像・イラストは生成・配置とも禁止",
        "pin": "会社所在地が明確な場合は地図にピン表示",
    },
    "styling_policy": {
        "tailwind_refactor": "Next.js + Tailwind へのリファクタ前提で実装",
        "css_variables": "CSS変数を使う場合も各要素に明示的にクラスで色を指定",
        "text_color": "body の色継承に依存せず、テキスト要素ごとに色を指定",
        "buttons": "ボタンは default / hover / active / disabled 等、状態ごとに色を明示",
    },
}


def get_common_technical_spec() -> dict:
    """プラン共通の技術要件（辞書）"""
    return COMMON_TECHNICAL_SPEC.copy()


def get_common_technical_spec_prompt_block() -> str:
    """LLMプロンプト用の技術要件テキストブロック（`config/prompts/common/`）。"""
    from config.prompt_settings import get_technical_spec_prompt_block

    return get_technical_spec_prompt_block()


# 出力ディレクトリを作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
