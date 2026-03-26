"""4 つの ``*_gemini_manual.py`` で共通のヘルパー関数・定数。

各パイプラインファイルはプラン固有のステップ定義のみを保持し、
共通インフラはここから import する。
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.contract_workflow import ContractWorkBranch

import google.generativeai as genai
from config.config import GEMINI_API_KEY, GEMINI_MANUAL_MAX_OUTPUT_TOKENS
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from modules.gemini_generative_timeout import ensure_gemini_rpc_patch_from_config
from modules.hearing_url_utils import (
    existing_site_url_guess_from_hearing,
    reference_site_url_from_hearing,
)

logger = logging.getLogger(__name__)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


def load_step(manual_dir: Path, filename: str, *, module_name: str = "") -> str:
    """プロンプトファイルをロード。存在しなければ RuntimeError。"""
    path = manual_dir / filename
    if not path.is_file():
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(f"{prefix}マニュアルプロンプトが見つかりません: {path}")
    return path.read_text(encoding="utf-8")


def subst(template: str, *, module_name: str = "", **kwargs: str) -> str:
    """``{{KEY}}`` プレースホルダを置換し、未置換が残れば例外。"""
    out = template
    for key, value in kwargs.items():
        out = out.replace("{{" + key + "}}", value)
    if "{{" in out and "}}" in out:
        i = out.index("{{")
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(
            f"{prefix}プレースホルダが未置換です: " + out[i : i + 80]
        )
    return out


def configure_gemini() -> None:
    """Gemini API キー設定と RPC パッチ適用。"""
    key = (GEMINI_API_KEY or "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY が空です。")
    genai.configure(api_key=key)
    ensure_gemini_rpc_patch_from_config()


def gen_config() -> dict[str, Any]:
    """generate_content の共通 generation_config。"""
    return {
        "max_output_tokens": GEMINI_MANUAL_MAX_OUTPUT_TOKENS,
        "temperature": 0.35,
    }


def response_text(
    response: Any,
    *,
    module_name: str = "",
    warn_max_tokens: bool = False,
) -> str:
    """Gemini 応答から連結テキストを取得。空なら例外。

    warn_max_tokens=True のとき、finish_reason に MAX+TOKEN を含む候補を警告ログに出す。
    """
    prefix = f"{module_name}: " if module_name else ""
    if not getattr(response, "candidates", None):
        raise RuntimeError(
            f"{prefix}Gemini 応答に candidates がありません。"
            f" prompt_feedback={getattr(response, 'prompt_feedback', None)}"
        )
    chunks: list[str] = []
    for cand in response.candidates:
        if warn_max_tokens:
            fr = getattr(cand, "finish_reason", None)
            if fr is not None:
                fru = str(fr).upper()
                if "MAX" in fru and "TOKEN" in fru:
                    logger.warning(
                        "%sGemini: finish_reason=%s（max_output で出力が切れた可能性）。"
                        " .env の GEMINI_MANUAL_MAX_OUTPUT_TOKENS を確認してください。",
                        prefix,
                        fr,
                    )
        content = getattr(cand, "content", None)
        if not content or not getattr(content, "parts", None):
            continue
        for part in content.parts:
            t = getattr(part, "text", None)
            if t:
                chunks.append(t)
    out = "".join(chunks).strip()
    if not out:
        raise RuntimeError(f"{prefix}Gemini 応答テキストが空です。")
    return out


def hearing_block(hearing_sheet_content: str, *, module_name: str = "") -> str:
    """ヒアリング本文を検証して返す。空なら例外。"""
    h = (hearing_sheet_content or "").strip()
    if not h:
        prefix = f"{module_name}: " if module_name else ""
        raise RuntimeError(f"{prefix}ヒアリングシート本文が空です。")
    return h


def existing_site_url_block(hearing_sheet_content: str, explicit: str) -> str:
    u = (explicit or "").strip()
    if not u:
        u = existing_site_url_guess_from_hearing(hearing_sheet_content)
    if u:
        return u
    return "（既存サイトURLの記載なし。ヒアリング本文に URL があればそちらを参照）"


def client_hp_and_mood_placeholders() -> tuple[str, str]:
    """手順5の「〇〇」相当。人間作業では手入力するため、自動実行時はモデルへの指示文とする。"""
    return (
        "（ヒアリングシート設問「ホームページに使いたい色」および手順1-3の記載を最優先。未記載なら本文から判断）",
        "（ヒアリングシート設問「希望の雰囲気」および手順1-3の記載を最優先。未記載なら本文から判断）",
    )


def reference_url_block(
    hearing_sheet_content: str,
    *,
    extra_texts: Sequence[str] = (),
) -> str:
    u = reference_site_url_from_hearing(
        hearing_sheet_content or "",
        extra_texts=extra_texts,
    )
    if u:
        return u
    return "（参考サイトURLの記載なし。手順1-3およびヒアリング本文を参照）"


# ---------------------------------------------------------------------------
# Manus リファクタブロック（4パイプラインで共通の ~30 行パターン）
# ---------------------------------------------------------------------------


def run_manus_refactor_block(
    *,
    canvas_markdown: str,
    partner_name: str,
    record_number: str,
    work_branch: ContractWorkBranch,
    manual_meta_key: str,
    model: str,
    steps: dict,
    step_prompts: dict,
    hearing_reference_block: str,
    contract_max_pages: int,
    preface_dir: Path | None = None,
) -> tuple[str, str | None, str]:
    """Manus リファクタの共通フロー。

    引数: Gemini チェーン完了後の canvas / 案件メタ / チェックポイント保存用の steps 等
    処理: pre_manus チェックポイント書き出し → Manus プロンプト組み立て → Manus タスク実行
    出力: (refactored_md, manus_deploy_github_url, manus_refactor_prompt)
          呼び出し元が outs に代入する
    """
    from modules.basic_lp_refactor_gemini import (
        build_basic_lp_refactor_user_prompt,
        run_basic_lp_refactor_stage,
    )
    from modules.llm.llm_raw_output import write_pre_manus_llm_checkpoint

    write_pre_manus_llm_checkpoint(
        site_name=f"{partner_name}-{record_number}",
        work_branch=work_branch,
        manual_meta_key=manual_meta_key,
        model=model,
        steps=dict(steps),
        step_prompts=dict(step_prompts),
        canvas_markdown=canvas_markdown,
        partner_name=partner_name,
        record_number=record_number,
    )

    refactor_kw: dict[str, Any] = dict(
        partner_name=partner_name,
        record_number=record_number,
        hearing_reference_block=hearing_reference_block,
        contract_max_pages=contract_max_pages,
    )
    if preface_dir is not None:
        refactor_kw["preface_dir"] = preface_dir

    prompt = build_basic_lp_refactor_user_prompt(canvas_markdown, **refactor_kw)
    md, manus_deploy_github_url = run_basic_lp_refactor_stage(
        canvas_source_code=canvas_markdown, **refactor_kw,
    )

    return md, manus_deploy_github_url, prompt
