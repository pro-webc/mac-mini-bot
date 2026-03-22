"""設定管理モジュール"""
from __future__ import annotations

import os
from datetime import date, datetime
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


def _parse_float_env(
    name: str, default: float, *, minimum: float, maximum: float
) -> float:
    """環境変数を float として解釈（不正時は default、範囲クランプ）"""
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        v = float(str(raw).strip())
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
# メインシートの契約が BASIC のとき、サイトタイプ（LP かどうか）を参照する別スプレッドシート（空なら照会しない）
GOOGLE_SHEETS_BASIC_SITE_TYPE_SPREADSHEET_ID = os.getenv(
    "GOOGLE_SHEETS_BASIC_SITE_TYPE_SPREADSHEET_ID", ""
).strip()
GOOGLE_SHEETS_BASIC_SITE_TYPE_SHEET_NAME = os.getenv(
    "GOOGLE_SHEETS_BASIC_SITE_TYPE_SHEET_NAME", "Sheet1"
).strip() or "Sheet1"
GOOGLE_SHEETS_BASIC_SITE_TYPE_SKIP_HEADER = os.getenv(
    "GOOGLE_SHEETS_BASIC_SITE_TYPE_SKIP_HEADER", "true"
).strip().lower() in ("1", "true", "yes")
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

# フェーズ期限日（T 列）がこの日付「以降」の行のみ着手。未設定時は 2026-03-27。
# false / off / 0 で無効（他条件のみでキュー化）
_raw_min_phase = (os.getenv("SPREADSHEET_MIN_PHASE_DEADLINE") or "2026-03-27").strip()
if _raw_min_phase.lower() in ("false", "off", "0"):
    SPREADSHEET_MIN_PHASE_DEADLINE: date | None = None
else:
    try:
        SPREADSHEET_MIN_PHASE_DEADLINE = datetime.strptime(
            _raw_min_phase, "%Y-%m-%d"
        ).date()
    except ValueError as e:
        raise ValueError(
            "SPREADSHEET_MIN_PHASE_DEADLINE は YYYY-MM-DD で指定してください（例: 2026-03-27）。"
            f" 現在の値: {_raw_min_phase!r}"
        ) from e

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
# Gemini unary RPC のサーバ待ち上限（秒）。大規模 Canvas 出力は 60s 既定では不足しがち
GEMINI_RPC_TIMEOUT_SEC = _parse_float_env(
    "GEMINI_RPC_TIMEOUT_SEC", 900.0, minimum=60.0, maximum=3600.0
)
# DeadlineExceeded（504）時の追加試行回数（0 なら再試行なし）
GEMINI_RPC_DEADLINE_RETRIES = _parse_positive_int(
    "GEMINI_RPC_DEADLINE_RETRIES", 2, minimum=0, maximum=10
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# BASIC LP: 社内マニュアルどおりの Gemini 多段プロンプト（既定 true・本番パイプライン向け）
BASIC_LP_USE_GEMINI_MANUAL = os.getenv(
    "BASIC_LP_USE_GEMINI_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")
# サイト制作は品質優先: 未設定時は Gemini 3.1 Pro Preview（GEMINI_*_MODEL で上書き可）
_DEFAULT_GEMINI_SITE_MODEL = "gemini-3.1-pro-preview"
GEMINI_BASIC_LP_MODEL = (
    os.getenv("GEMINI_BASIC_LP_MODEL", _DEFAULT_GEMINI_SITE_MODEL)
    or _DEFAULT_GEMINI_SITE_MODEL
).strip()
# 手順8の単一ファイル出力のあと、リファクタ指示どおりの複数ファイル出力へ変換（Manus タスク1件）
BASIC_LP_REFACTOR_AFTER_MANUAL = os.getenv(
    "BASIC_LP_REFACTOR_AFTER_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")

# BASIC（コーポレート1ページ）: BASIC-CP 制作マニュアルどおりの Gemini 多段プロンプト（既定 true）
BASIC_CP_USE_GEMINI_MANUAL = os.getenv(
    "BASIC_CP_USE_GEMINI_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")
_raw_gemini_basic_cp = (os.getenv("GEMINI_BASIC_CP_MODEL") or "").strip()
GEMINI_BASIC_CP_MODEL = _raw_gemini_basic_cp or GEMINI_BASIC_LP_MODEL
# 手順7-3 のあと、リファクタ指示どおりの複数ファイル出力へ変換（Manus タスク1件）
BASIC_CP_REFACTOR_AFTER_MANUAL = os.getenv(
    "BASIC_CP_REFACTOR_AFTER_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")

# STANDARD（コーポレート・6ページ想定）: STANDARD-CP 制作マニュアルどおりの Gemini 多段プロンプト（既定 true）
STANDARD_CP_USE_GEMINI_MANUAL = os.getenv(
    "STANDARD_CP_USE_GEMINI_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")
_raw_gemini_standard_cp = (os.getenv("GEMINI_STANDARD_CP_MODEL") or "").strip()
GEMINI_STANDARD_CP_MODEL = _raw_gemini_standard_cp or GEMINI_BASIC_LP_MODEL
# マニュアル多段 Gemini の max_output_tokens。8192 だと手順7系の長いコードが途中で切れやすい。
GEMINI_MANUAL_MAX_OUTPUT_TOKENS = _parse_positive_int(
    "GEMINI_MANUAL_MAX_OUTPUT_TOKENS",
    65536,
    minimum=2048,
    maximum=131072,
)
STANDARD_CP_REFACTOR_AFTER_MANUAL = os.getenv(
    "STANDARD_CP_REFACTOR_AFTER_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")
# 手順2の「ブログ独立1ページ」行をプロンプトに含める（false でマニュアル「不要なら削除」に相当）
STANDARD_CP_INCLUDE_BLOG_PAGE = os.getenv(
    "STANDARD_CP_INCLUDE_BLOG_PAGE", "true"
).strip().lower() in ("1", "true", "yes")

# ADVANCE（コーポレート・12ページ想定）: ADVANCE-CP 制作マニュアルどおりの Gemini 多段プロンプト（既定 true）
ADVANCE_CP_USE_GEMINI_MANUAL = os.getenv(
    "ADVANCE_CP_USE_GEMINI_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")
_raw_gemini_advance_cp = (os.getenv("GEMINI_ADVANCE_CP_MODEL") or "").strip()
GEMINI_ADVANCE_CP_MODEL = _raw_gemini_advance_cp or GEMINI_BASIC_LP_MODEL
ADVANCE_CP_REFACTOR_AFTER_MANUAL = os.getenv(
    "ADVANCE_CP_REFACTOR_AFTER_MANUAL", "true"
).strip().lower() in ("1", "true", "yes")
ADVANCE_CP_INCLUDE_BLOG_PAGE = os.getenv(
    "ADVANCE_CP_INCLUDE_BLOG_PAGE", "true"
).strip().lower() in ("1", "true", "yes")

# 最終リファクタ（フェンス付きマルチファイル化・画像方針）は Manus API。マニュアル本編は Gemini のまま。
MANUS_API_KEY = (os.getenv("MANUS_API_KEY", "") or "").strip()
MANUS_API_BASE = (
    (os.getenv("MANUS_API_BASE", "https://api.manus.ai") or "https://api.manus.ai")
    .strip()
    .rstrip("/")
)
MANUS_AGENT_PROFILE = (
    os.getenv("MANUS_AGENT_PROFILE", "manus-1.6") or "manus-1.6"
).strip()
MANUS_TASK_MODE = (os.getenv("MANUS_TASK_MODE", "agent") or "agent").strip()
# POST /v1/tasks の connectors（公式: https://open.manus.im/docs/connectors ）。OAuth は manus.im で事前連携必須。
# 未設定時は GitHub のみ（UUID は公式ドキュメント記載値）。空文字で指定すると connectors を送らない。
_MANUS_CONNECTOR_UUID_GITHUB = "bbb0df76-66bd-4a24-ae4f-2aac4750d90b"


def _parse_manus_task_connector_ids() -> list[str]:
    if "MANUS_TASK_CONNECTORS" in os.environ:
        raw = os.getenv("MANUS_TASK_CONNECTORS", "") or ""
    else:
        raw = _MANUS_CONNECTOR_UUID_GITHUB
    return [x.strip() for x in raw.split(",") if x.strip()]


MANUS_TASK_CONNECTOR_IDS = _parse_manus_task_connector_ids()
MANUS_REFACTOR_POLL_INTERVAL_SEC = _parse_float_env(
    "MANUS_REFACTOR_POLL_INTERVAL_SEC", 5.0, minimum=1.0, maximum=120.0
)
MANUS_REFACTOR_TIMEOUT_SEC = _parse_float_env(
    "MANUS_REFACTOR_TIMEOUT_SEC", 2700.0, minimum=60.0, maximum=7200.0
)
# true（既定）: Manus に GitHub push まで任せ、返答末尾の `BOT_DEPLOY_GITHUB_URL:` 行をシステムが Vercel デプロイに使い、ローカルからの GitHub push をスキップ
MANUS_PROVIDES_DEPLOY_GITHUB_URL = os.getenv(
    "MANUS_PROVIDES_DEPLOY_GITHUB_URL", "true"
).strip().lower() in ("1", "true", "yes")
# 任意: Manus プロンプトに「push 先の推奨」を1行で渡す（例: your-org/123-test-acme）
MANUS_DEPLOY_GITHUB_REPO_HINT = (os.getenv("MANUS_DEPLOY_GITHUB_REPO_HINT", "") or "").strip()

# サイト TSX の ImagePlaceholder を Gemini 画像 API で実ファイル化（GEMINI_API_KEY があるとき常に実行）
GEMINI_SITE_IMAGE_MODEL = (
    os.getenv(
        "GEMINI_SITE_IMAGE_MODEL",
        "gemini-3-pro-image-preview",
    )
    or "gemini-3-pro-image-preview"
).strip()
GEMINI_SITE_IMAGE_MAX_SLOTS = _parse_positive_int(
    "GEMINI_SITE_IMAGE_MAX_SLOTS", 12, minimum=1, maximum=32
)
GEMINI_SITE_IMAGE_DELAY_SEC = _parse_float_env(
    "GEMINI_SITE_IMAGE_DELAY_SEC", 1.0, minimum=0.0, maximum=30.0
)

# npm ビルド検証
SITE_BUILD_ENABLED = os.getenv("SITE_BUILD_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
SITE_IMPLEMENTATION_ENABLED = os.getenv("SITE_IMPLEMENTATION_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)

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
# デプロイURLをログイン不要で閲覧できるよう、プロジェクトのデプロイ保護を API で解除する
VERCEL_FORCE_PUBLIC_DEPLOYMENTS = os.getenv(
    "VERCEL_FORCE_PUBLIC_DEPLOYMENTS", "true"
).strip().lower() in ("1", "true", "yes")

# その他設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(PROJECT_ROOT / "output")))

# 工程テスト（プリフライト〜フェーズ1〜作業分岐）の成果物を 1 か所にまとめる（任意）
# 例: PIPELINE_TEST_RUN_DIR=output/pipeline_test_runs/demo_run
#     → <そのパス>/preflight_snapshots/<UTC>/ … ほか phase1_snapshots, work_branch_snapshots,
#       phase2_snapshots, gemini_step_tests（任意）
_PIPELINE_TEST_RUN_DIR_RAW = os.getenv("PIPELINE_TEST_RUN_DIR", "").strip()


def pipeline_test_run_root_resolved() -> Path | None:
    """環境変数 ``PIPELINE_TEST_RUN_DIR`` で指定されたラン用ディレクトリ（未設定なら None）。"""
    if not _PIPELINE_TEST_RUN_DIR_RAW:
        return None
    p = Path(_PIPELINE_TEST_RUN_DIR_RAW)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p.resolve()


def pipeline_run_root_for_resolve(explicit_run_root: Path | None = None) -> Path:
    """
    プリフライト〜作業分岐の「親」ディレクトリ。
    ``explicit_run_root`` があればそれを優先し、なければ環境変数、なければ ``OUTPUT_DIR``。
    """
    if explicit_run_root is not None:
        return explicit_run_root.resolve()
    r = pipeline_test_run_root_resolved()
    return r if r else OUTPUT_DIR.resolve()


def pipeline_preflight_snapshots_base(explicit_run_root: Path | None = None) -> Path:
    return pipeline_run_root_for_resolve(explicit_run_root) / "preflight_snapshots"


def pipeline_phase1_snapshots_base(explicit_run_root: Path | None = None) -> Path:
    return pipeline_run_root_for_resolve(explicit_run_root) / "phase1_snapshots"


def pipeline_work_branch_snapshots_base(explicit_run_root: Path | None = None) -> Path:
    return pipeline_run_root_for_resolve(explicit_run_root) / "work_branch_snapshots"


def pipeline_phase2_snapshots_base(explicit_run_root: Path | None = None) -> Path:
    """TEXT_LLM（フェーズ2）単体実行の保存先（``phase2_snapshots/<UTC>/``）。"""
    return pipeline_run_root_for_resolve(explicit_run_root) / "phase2_snapshots"


def pipeline_gemini_step_tests_base(explicit_run_root: Path | None = None) -> Path:
    """STANDARD-CP 段階 Gemini テストの保存先（``gemini_step_tests/<UTC>/``）。"""
    return pipeline_run_root_for_resolve(explicit_run_root) / "gemini_step_tests"


def pipeline_run_root_from_phase1_snapshot_dir(phase1_dir: Path) -> Path | None:
    """
    ``.../<run>/phase1_snapshots/<stamp>/`` なら ``<run>`` を返す。
    レイアウトが合わなければ None。
    """
    p = phase1_dir.resolve()
    if p.parent.name == "phase1_snapshots":
        return p.parent.parent
    return None


def latest_preflight_cases_path(*, run_root: Path | None = None) -> Path | None:
    """``<親>/preflight_snapshots/*/04_pending_cases.json`` のうち mtime が最新のもの。"""
    base = pipeline_preflight_snapshots_base(run_root)
    if not base.is_dir():
        return None
    candidates = list(base.glob("*/04_pending_cases.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def latest_phase1_snapshot_dir(*, run_root: Path | None = None) -> Path | None:
    """``<親>/phase1_snapshots/*/`` のうち ``00_source.json`` があり mtime が最新のディレクトリ。"""
    base = pipeline_phase1_snapshots_base(run_root)
    if not base.is_dir():
        return None
    dirs = [
        d
        for d in base.iterdir()
        if d.is_dir() and (d / "00_source.json").is_file()
    ]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)


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
        "unsplash": "Unsplash・外部ストック URL 禁止",
        "final_refactor": (
            "ビジュアルはマニュアル後の最終リファクタ（Gemini）で実装。"
            "`next/image` と `public/images/`（フェンスで SVG 等を出力）。"
            "後工程の一括画像 API は使わない。"
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
