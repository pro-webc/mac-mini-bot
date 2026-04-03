"""自己改善エンジン — プロンプトの自律的改善

Slack 修正指示と LLM トレースから原因を深く調査し、
該当するプロンプトテンプレートを自動的に改善・コミットする。

フロー:
  1. プランタイプを特定（output/<record>/llm_raw_output/requirements_result.yaml）
  2. 原因ステップの完全なトレース（input.md / output.md）を読み取り
  3. 対応するプロンプトテンプレートを特定・読み込み
  4. Claude CLI で改善案を生成
  5. プロンプトファイルに改善を適用
  6. Git commit で変更を記録
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.config import CLAUDE_CLI_TIMEOUT_SEC, OUTPUT_DIR

logger = logging.getLogger(__name__)

# プロジェクトルート（config/prompts/ の親）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# パイプラインマニフェスト — トレースステップ番号 → プロンプトファイルの対応表
# ---------------------------------------------------------------------------

# キー: (plan_type, trace_step_number) → プロンプトファイルの相対パス（config/prompts/ 以下）
# NOTE: URL抽出ステップ（extract_reference_urls）はプラン共通で common/ を使う。
#       Manus リファクタは manus/ ディレクトリのプロンプトに対応。

_BASIC_LP_STEPS: dict[int, list[str]] = {
    1: ["basic_lp_manual/step_1_1.txt"],
    2: ["basic_lp_manual/step_1_2.txt", "basic_lp_manual/step_1_3_nonrecruit.txt"],
    3: ["basic_lp_manual/step_2.txt"],
    4: ["basic_lp_manual/step_3.txt"],
    5: ["basic_lp_manual/step_4.txt"],
    # 6, 7, 8 = URL抽出（common/extract_reference_urls.txt）
    9: ["basic_lp_manual/step_5.txt"],
    10: ["basic_lp_manual/step_6.txt"],
    11: ["basic_lp_manual/step_7.txt"],
    12: ["basic_lp_manual/step_8_1.txt"],
    13: ["basic_lp_manual/step_8_2.txt"],
    14: ["basic_lp_manual/step_8_3.txt"],
}

_BASIC_CP_STEPS: dict[int, list[str]] = {
    1: ["basic_cp_manual/step_1_1.txt"],
    2: ["basic_cp_manual/step_1_2.txt", "basic_cp_manual/step_1_3.txt"],
    # 3, 4, 5 = URL���出
    6: ["basic_cp_manual/step_2.txt"],
    7: ["basic_cp_manual/step_3.txt"],
    8: ["basic_cp_manual/step_4.txt"],
    9: ["basic_cp_manual/step_5.txt"],
    10: ["basic_cp_manual/step_6.txt"],
    11: ["basic_cp_manual/step_7_1.txt"],
    12: ["basic_cp_manual/step_7_2.txt"],
    13: ["basic_cp_manual/step_7_3.txt"],
}

_STANDARD_CP_STEPS: dict[int, list[str]] = {
    1: ["standard_cp_manual/step_1_1.txt"],
    2: ["standard_cp_manual/step_1_2.txt", "standard_cp_manual/step_1_3.txt"],
    3: ["standard_cp_manual/step_2.txt"],
    4: ["standard_cp_manual/step_3_1.txt"],
    5: ["standard_cp_manual/step_3_2.txt"],
    6: ["standard_cp_manual/step_3_3.txt"],
    7: ["standard_cp_manual/step_3_4.txt"],
    8: ["standard_cp_manual/step_3_5.txt"],
    # 9, 10, 11 = URL抽出
    12: ["standard_cp_manual/step_4.txt"],
    13: ["standard_cp_manual/step_5.txt"],
    14: ["standard_cp_manual/step_6.txt"],
    15: ["standard_cp_manual/step_7_1.txt"],
    16: ["standard_cp_manual/step_7_2.txt"],
    17: ["standard_cp_manual/step_7_3.txt"],
    18: ["standard_cp_manual/step_7_4.txt"],
    19: ["standard_cp_manual/step_7_5.txt"],
}

_ADVANCE_CP_STEPS: dict[int, list[str]] = {
    1: ["advance_cp_manual/step_1_1.txt"],
    2: ["advance_cp_manual/step_1_2.txt", "advance_cp_manual/step_1_3.txt"],
    3: ["advance_cp_manual/step_2.txt"],
    4: ["advance_cp_manual/step_3_1.txt"],
    5: ["advance_cp_manual/step_3_2.txt"],
    6: ["advance_cp_manual/step_3_3.txt"],
    7: ["advance_cp_manual/step_3_4.txt"],
    8: ["advance_cp_manual/step_3_5.txt"],
    # 9, 10, 11 = URL抽出
    12: ["advance_cp_manual/step_4.txt"],
    13: ["advance_cp_manual/step_5.txt"],
    14: ["advance_cp_manual/step_6.txt"],
    15: ["advance_cp_manual/step_7_1.txt"],
    16: ["advance_cp_manual/step_7_2.txt"],
    17: ["advance_cp_manual/step_7_3.txt"],
    18: ["advance_cp_manual/step_7_4.txt"],
}

PIPELINE_MANIFEST: dict[str, dict[int, list[str]]] = {
    "basic_lp": _BASIC_LP_STEPS,
    "basic": _BASIC_CP_STEPS,
    "standard": _STANDARD_CP_STEPS,
    "advance": _ADVANCE_CP_STEPS,
}

# URL抽出・Manus・共通プロンプト
_COMMON_PROMPTS: dict[str, str] = {
    "extract_reference_urls": "common/extract_reference_urls.txt",
    "manus_orchestration": "manus/orchestration_prompt.txt",
    "manus_refactoring": "manus/refactoring_instruction_handwork.txt",
    "tech_requirements": "common/claude_tech_requirements.txt",
    "reflect_check": "common/reflect_check.txt",
    "reflect_fix": "common/reflect_fix.txt",
}


# ---------------------------------------------------------------------------
# 1. プランタイプ特定
# ---------------------------------------------------------------------------


def detect_plan_type(record_number: str) -> str | None:
    """output/<record>/llm_raw_output/requirements_result.yaml から plan_type を取得。"""
    yaml_path = OUTPUT_DIR / str(record_number) / "llm_raw_output" / "requirements_result.yaml"
    if not yaml_path.is_file():
        logger.warning("requirements_result.yaml が見つかりません: %s", yaml_path)
        return None

    text = yaml_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^plan_type:\s*(.+)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip().lower()
    return None


# ---------------------------------------------------------------------------
# 2. トレース読み取り（完全版）
# ---------------------------------------------------------------------------


def read_full_trace(record_number: str, step_name: str) -> dict[str, str]:
    """指定ステップの input.md / output.md / error.txt を完全に読み取る。

    Returns:
        {"input": str, "output": str, "error": str} — 存在しないファイルは空文字列。
    """
    trace_dir = OUTPUT_DIR / str(record_number) / "llm_steps" / step_name
    result: dict[str, str] = {"input": "", "output": "", "error": ""}
    if not trace_dir.is_dir():
        return result
    for key, filename in [("input", "input.md"), ("output", "output.md"), ("error", "error.txt")]:
        fpath = trace_dir / filename
        if fpath.is_file():
            result[key] = fpath.read_text(encoding="utf-8", errors="replace")
    return result


def list_trace_steps(record_number: str) -> list[str]:
    """output/<record>/llm_steps/ 配下のステップディレクトリ名一��を返す。"""
    trace_dir = OUTPUT_DIR / str(record_number) / "llm_steps"
    if not trace_dir.is_dir():
        return []
    return sorted(d.name for d in trace_dir.iterdir() if d.is_dir())


def read_all_traces_summary(record_number: str, max_chars: int = 3000) -> str:
    """全ステップの概要をまとめたテキストを返す。各ステップの入出力先頭を含む。"""
    steps = list_trace_steps(record_number)
    lines: list[str] = []
    for step in steps:
        trace = read_full_trace(record_number, step)
        status = "error" if trace["error"] else "ok"
        inp_preview = trace["input"][:max_chars] if trace["input"] else "(なし)"
        out_preview = trace["output"][:max_chars] if trace["output"] else "(な��)"
        lines.append(
            f"### {step} [{status}]\n"
            f"入力（先頭{max_chars}文字）:\n{inp_preview}\n\n"
            f"出力（先頭{max_chars}文字）:\n{out_preview}\n"
        )
    return "\n---\n".join(lines) if lines else "(LLM トレースなし)"


# ---------------------------------------------------------------------------
# 3. プロンプトファイル特定・読み込み
# ---------------------------------------------------------------------------


def _extract_step_number(step_name: str) -> int | None:
    """ステップディレクトリ名から番号を抽出。例: '009_claude_cli_chat' → 9"""
    m = re.match(r"(\d+)_", step_name)
    return int(m.group(1)) if m else None


def resolve_prompt_files(
    plan_type: str,
    step_name: str,
) -> list[Path]:
    """トレースステップ名に対応するプロンプトテンプレートファイルのパスを返す。

    マニフェストにマッチしない場合は空リスト。
    """
    step_num = _extract_step_number(step_name)
    if step_num is None:
        return []

    manifest = PIPELINE_MANIFEST.get(plan_type, {})
    rel_paths = manifest.get(step_num, [])

    # URL抽出ステップの判定（マニフェストにないが claude_cli_generate の場合）
    if not rel_paths and "claude_cli_generate" in step_name:
        rel_paths = [_COMMON_PROMPTS["extract_reference_urls"]]

    # Manus リファクタ
    if not rel_paths and "manus" in step_name.lower():
        rel_paths = [
            _COMMON_PROMPTS["manus_orchestration"],
            _COMMON_PROMPTS["manus_refactoring"],
        ]

    prompts_dir = _PROJECT_ROOT / "config" / "prompts"
    return [prompts_dir / rp for rp in rel_paths if (prompts_dir / rp).is_file()]


def read_prompt_file(path: Path) -> str:
    """プロンプトテンプレートファイルを読み込む。"""
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# 4. 深い原因調査（フルトレース + プロンプト全文）
# ---------------------------------------------------------------------------


def _build_deep_investigation_prompt(
    *,
    slack_text: str,
    step_name: str,
    full_trace: dict[str, str],
    prompt_contents: dict[str, str],
    all_steps_summary: str,
    record_number: str,
    partner_name: str,
) -> str:
    """フルコンテキストの原因調査プロンプトを構築する。"""
    prompt_section = ""
    for path, content in prompt_contents.items():
        prompt_section += f"\n### プロンプトファイル: {path}\n```\n{content}\n```\n"

    return f"""あなたはAIワークフローシステムの品質改善エンジニアです。
このシステムはヒアリングシートからWebサイトを自動生成するパイプラインです。
あなたの役割は、修正指示の根本原因を特定し、プロンプトテンプレートの具体的な改善を提案することです。

## 案件情報
- レコード番号: {record_number}
- パ��トナー名: {partner_name}

## Slack 修正指示（ユーザーからのフィードバック）
{slack_text}

## パイプライン全ステップの概要
{all_steps_summary}

## 原因候補ステップ: {step_name}

### そのステップに送られたプロンプト（input.md 全文）
```
{full_trace['input'][:20000]}
```

### そのステップの出力（output.md 全文）
```
{full_trace['output'][:20000]}
```

## 対応するプロンプトテンプレート（現在のシステムプロンプト）
{prompt_section}

## タスク

1. **根本原因の特定**: 修正指示の問題がどのステップのどの部分で発生したか、プロンプトテンプレートのどの指示が不足・曖昧だったかを分析してください。

2. **プロンプト改善の提案**: プロンプトテンプレートの具体的な変更を提案してください。
   - 既存の指示を壊さない
   - 最小限の変更で最大の効果を狙う
   - 他の案件にも汎用的に効く改善にする（特定案件のハードコードはNG）
   - 追加する指示は簡潔かつ明確に

## 回答フォーマット（JSON のみ出力）
```json
{{
  "root_cause": {{
    "step": "問題の原因となったステップ名",
    "issue": "何が起きたかの端的な説明",
    "category": "color_mismatch / content_missing / layout_issue / text_error / design_mismatch / prompt_ambiguity / other",
    "prompt_gap": "プロンプトテンプレートの何が不足・曖昧だったか"
  }},
  "improvement": {{
    "target_file": "改善するプロンプトファイルの相対パス（config/prompts/...）",
    "change_type": "add_rule / strengthen_rule / add_example / clarify_instruction / restructure",
    "description": "変更の概要説���",
    "original_section": "変更対象の既存テキスト（見つかる場合）。新規追加なら空文字列",
    "improved_section": "置換後のテキスト、または追加するテキスト",
    "insertion_point": "新規追加の場合、どの既存テキストの後に挿入するか"
  }},
  "confidence": "high / medium / low",
  "reasoning": "この改善が今後の同種の問題を防ぐ理由"
}}
```"""


# ---------------------------------------------------------------------------
# 5. 改善の適���
# ---------------------------------------------------------------------------


def _apply_edit_to_prompt(
    target_file: Path,
    original_section: str,
    improved_section: str,
    insertion_point: str,
) -> bool:
    """プロンプトファイルに改善を適用する。

    Returns:
        True: 適用成功、False: 適用失敗
    """
    if not target_file.is_file():
        logger.error("改善対象ファイルが存在しません: %s", target_file)
        return False

    content = target_file.read_text(encoding="utf-8")

    if original_section and original_section in content:
        # 既存テキストの置換
        new_content = content.replace(original_section, improved_section, 1)
    elif insertion_point and insertion_point in content:
        # 挿入ポイントの後に追加
        new_content = content.replace(
            insertion_point,
            insertion_point + "\n" + improved_section,
            1,
        )
    elif not original_section and improved_section:
        # フォールバック: ファイル末尾に追加
        new_content = content.rstrip() + "\n\n" + improved_section + "\n"
    else:
        logger.warning(
            "改善テキストの適用ポイントが見つかりません target=%s", target_file,
        )
        return False

    if new_content == content:
        logger.info("改善適用: 変更なし（既に適用済み?） target=%s", target_file)
        return False

    target_file.write_text(new_content, encoding="utf-8")
    logger.info("改善を適用しました: %s", target_file)
    return True


# ---------------------------------------------------------------------------
# 6. Git コミット
# ---------------------------------------------------------------------------


def _commit_improvement(
    target_file: Path,
    record_number: str,
    root_cause: dict[str, str],
    description: str,
) -> bool:
    """改善をコミットする。

    Returns:
        True: コミット成功、False: 失敗
    """
    try:
        rel_path = target_file.relative_to(_PROJECT_ROOT)
    except ValueError:
        rel_path = target_file

    category = root_cause.get("category", "unknown")
    issue = root_cause.get("issue", "")[:80]

    commit_msg = (
        f"improve: プロンプト自己改善 [{category}] (record={record_number})\n\n"
        f"原因: {issue}\n"
        f"改善: {description[:200]}\n"
        f"対象: {rel_path}\n\n"
        f"自己改善エンジンによる自動コミット"
    )

    try:
        subprocess.run(
            ["git", "add", str(target_file)],
            cwd=str(_PROJECT_ROOT),
            capture_output=True, text=True, timeout=30,
        )
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(_PROJECT_ROOT),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            logger.info("自己改善コミット成功: %s", rel_path)
            return True
        logger.warning("git commit 失敗: %s", result.stderr[:300])
        return False
    except Exception:
        logger.warning("自己改善コミットに失敗しました", exc_info=True)
        return False


# ---------------------------------------------------------------------------
# 7. 改善ログの保存
# ---------------------------------------------------------------------------


def _save_improvement_log(
    record_number: str,
    investigation: dict[str, Any],
    applied: bool,
    committed: bool,
) -> Path:
    """改善ログを output/<record>/improvement/ に保存する。"""
    log_dir = OUTPUT_DIR / str(record_number) / "improvement"
    log_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"improvement_{ts}.json"

    log_data = {
        "record_number": record_number,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "investigation": investigation,
        "applied": applied,
        "committed": committed,
    }

    log_path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("改善ログを保存: %s", log_path)
    return log_path


# ---------------------------------------------------------------------------
# 8. メインオーケストレーション
# ---------------------------------------------------------------------------


def run_self_improvement(
    *,
    record_number: str,
    partner_name: str,
    slack_text: str,
    initial_investigation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """自己改善フローを実行する。

    Args:
        record_number: レコード番号
        partner_name: パートナー名
        slack_text: Slack 修正指示テキスト
        initial_investigation: correction_flow の浅い調査結果（オプション）

    Returns:
        改善結果の辞書。適用の成否、対象ファイル、変更概要を含む。
    """
    result: dict[str, Any] = {
        "success": False,
        "plan_type": None,
        "target_file": None,
        "description": None,
        "applied": False,
        "committed": False,
    }

    # --- Step 1: プランタイプ特定 ---
    plan_type = detect_plan_type(record_number)
    if not plan_type:
        logger.warning("プランタイプを特定できませんでした record=%s", record_number)
        # 初期調査の target_file からプランタイプを推定
        if initial_investigation:
            tf = initial_investigation.get("improvement_suggestion", {}).get("target_file", "")
            for pt in PIPELINE_MANIFEST:
                if f"{pt}_manual" in tf or f"{pt.replace('_', '_cp_')}" in tf:
                    plan_type = pt
                    break
        if not plan_type:
            return result
    result["plan_type"] = plan_type
    logger.info("自己改善: プ���ンタイプ=%s record=%s", plan_type, record_number)

    # --- Step 2: 原因ステップを特定 ---
    # 初期調査のステップ名があればそれを使用、なければ全ステップを調査
    candidate_step = None
    if initial_investigation:
        raw_step = initial_investigation.get("root_cause", {}).get("step", "")
        # ステップ名のバリデーション
        steps = list_trace_steps(record_number)
        for s in steps:
            if raw_step in s or s.startswith(raw_step):
                candidate_step = s
                break

    if not candidate_step:
        # 全ステップの中から原因を探す（後段ステップほど最終出力への影響が大きい）
        steps = list_trace_steps(record_number)
        if steps:
            # コード生成系ステップを優先
            code_steps = [s for s in steps if "cli_chat" in s]
            candidate_step = code_steps[-1] if code_steps else steps[-1]

    if not candidate_step:
        logger.warning("トレースステップが見��かりません record=%s", record_number)
        return result

    logger.info("自己改善: 原因候補ステップ=%s", candidate_step)

    # --- Step 3: フルトレース読み取り ---
    full_trace = read_full_trace(record_number, candidate_step)
    if not full_trace["input"] and not full_trace["output"]:
        logger.warning("トレースが空です step=%s", candidate_step)
        return result

    # --- Step 4: プロンプトファイル特定・読み込み ---
    prompt_files = resolve_prompt_files(plan_type, candidate_step)
    prompt_contents: dict[str, str] = {}
    for pf in prompt_files:
        try:
            rel = pf.relative_to(_PROJECT_ROOT)
        except ValueError:
            rel = pf
        prompt_contents[str(rel)] = read_prompt_file(pf)

    if not prompt_contents:
        logger.warning(
            "対応するプロンプトファイルが見つかりません plan=%s step=%s",
            plan_type, candidate_step,
        )
        return result

    # --- Step 5: 全ステップの概要（コンテキスト） ---
    all_steps_summary = read_all_traces_summary(record_number, max_chars=1000)

    # --- Step 6: 深い原因調査 + 改善案生成 ---
    investigation = _run_deep_investigation(
        slack_text=slack_text,
        step_name=candidate_step,
        full_trace=full_trace,
        prompt_contents=prompt_contents,
        all_steps_summary=all_steps_summary,
        record_number=record_number,
        partner_name=partner_name,
    )

    if not investigation or "improvement" not in investigation:
        logger.warning("深い原因調査で改善案が生成されませんでした record=%s", record_number)
        _save_improvement_log(record_number, investigation or {}, False, False)
        return result

    result["description"] = investigation.get("improvement", {}).get("description", "")
    logger.info(
        "自己改善: 調査完了 confidence=%s category=%s",
        investigation.get("confidence", "?"),
        investigation.get("root_cause", {}).get("category", "?"),
    )

    # --- Step 7: 改善を適用 ---
    improvement = investigation["improvement"]
    target_rel = improvement.get("target_file", "")
    target_file = _PROJECT_ROOT / target_rel

    if not target_file.is_file():
        # プロンプトファイルリストから最初のものをフォールバック
        if prompt_files:
            target_file = prompt_files[0]
        else:
            logger.warning("改善対象ファイルが見つかりません: %s", target_rel)
            _save_improvement_log(record_number, investigation, False, False)
            return result

    result["target_file"] = str(target_file)

    applied = _apply_edit_to_prompt(
        target_file,
        original_section=improvement.get("original_section", ""),
        improved_section=improvement.get("improved_section", ""),
        insertion_point=improvement.get("insertion_point", ""),
    )
    result["applied"] = applied

    if not applied:
        # テキストマッチに失敗した場合、Claude CLI で直接編集を試みる
        applied = _apply_via_claude_cli(
            target_file=target_file,
            improvement=improvement,
            slack_text=slack_text,
        )
        result["applied"] = applied

    # --- Step 8: コミット ---
    if applied:
        committed = _commit_improvement(
            target_file,
            record_number,
            investigation.get("root_cause", {}),
            improvement.get("description", ""),
        )
        result["committed"] = committed
    else:
        logger.warning("改善の適用に失敗しました — コミットをスキップ record=%s", record_number)

    # --- Step 9: ログ保存 ---
    _save_improvement_log(record_number, investigation, applied, result.get("committed", False))

    result["success"] = applied
    logger.info(
        "自己改善完了: success=%s applied=%s committed=%s target=%s record=%s",
        result["success"], result["applied"], result["committed"],
        target_rel, record_number,
    )
    return result


# ---------------------------------------------------------------------------
# 内部: Claude CLI 呼び出し
# ---------------------------------------------------------------------------


def _run_deep_investigation(
    *,
    slack_text: str,
    step_name: str,
    full_trace: dict[str, str],
    prompt_contents: dict[str, str],
    all_steps_summary: str,
    record_number: str,
    partner_name: str,
) -> dict[str, Any]:
    """Claude CLI で深い原因調査を実行する。"""
    prompt = _build_deep_investigation_prompt(
        slack_text=slack_text,
        step_name=step_name,
        full_trace=full_trace,
        prompt_contents=prompt_contents,
        all_steps_summary=all_steps_summary,
        record_number=record_number,
        partner_name=partner_name,
    )

    cli = shutil.which("claude")
    if not cli:
        logger.warning("claude CLI が見つかりません — 深い調査をスキッ��")
        return {}

    try:
        result = subprocess.run(
            [cli, "-p", prompt, "--output-format", "json", "--model", "claude-sonnet-4-6"],
            capture_output=True, text=True,
            timeout=float(CLAUDE_CLI_TIMEOUT_SEC),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        logger.warning("深い原因調査がタイムアウトしました")
        return {}

    stdout = result.stdout.strip()
    if not stdout:
        return {}

    # Claude CLI の JSON レスポンスからテキストを取得
    try:
        data = json.loads(stdout)
        text = data.get("result", "")
    except json.JSONDecodeError:
        text = stdout

    # JSON ブロックを抽出
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # フォールバック: テキスト全体を JSON として試行
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"raw_analysis": text[:2000]}


def _apply_via_claude_cli(
    *,
    target_file: Path,
    improvement: dict[str, str],
    slack_text: str,
) -> bool:
    """テキストマッチに失敗した場合、Claude CLI に直接プロンプトファイルを編集させる。"""
    cli = shutil.which("claude")
    if not cli:
        return False

    description = improvement.get("description", "")
    improved_section = improvement.get("improved_section", "")

    prompt = f"""以下のプロンプトテンプレートファイルを改善してください。

## 対象ファイル
{target_file}

## 修正指示の背景（Slackユーザーからのフィードバ���ク）
{slack_text}

## 改善内容
{description}

## 追加/変更すべき内容
{improved_section}

## ルール
- 既存のプロンプト構造を壊さない
- {{{{PLACEHOLDER}}}} 形式のテンプレート変数は絶対に変更しない
- 最小限の変更にする
- 改善の意図が明確に伝わるようにする
- ファイル全体を書き直さない — 必要な箇所のみ変更する"""

    try:
        result = subprocess.run(
            [
                cli, "-p", prompt,
                "--output-format", "json",
                "--model", "claude-sonnet-4-6",
                "--allowedTools", "Edit,Read",
            ],
            capture_output=True, text=True,
            timeout=float(CLAUDE_CLI_TIMEOUT_SEC),
            cwd=str(_PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            logger.info("Claude CLI による直接編集が完了しました: %s", target_file)
            return True
        logger.warning("Claude CLI 直接編集が失敗: %s", result.stderr[:300])
        return False
    except subprocess.TimeoutExpired:
        logger.warning("Claude CLI 直接編集がタイムアウトしました")
        return False
