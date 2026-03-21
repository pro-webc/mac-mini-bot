"""第2段・サイト台本生成（Markdown + 末尾 YAML）。レガシー仕様 JSON も解釈可。

正常ルート以外でのフォールバックは行わない（README「エラー処理の原則」参照）。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

import requests
from config.config import get_common_technical_spec, get_contract_plan_info
from config.prompt_settings import format_prompt, get_prompt_str, get_technical_spec_prompt_block
from modules.site_script_parse import parse_llm_spec_or_site_script
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)

# パース不能時の user 追記（最大 1 回だけ再 LLM）
_SPEC_SCRIPT_RETRY_USER_SUFFIX = """

---
## 出力形式の再指定（必須）
直前の応答はパイプラインが解釈できませんでした。次を **両方** 満たしてください。

1. **先頭から Markdown サイト台本**（`#` / `##` でセクション化した顧客向けコピー全文。複数ページは `## ページ: /about` で区切る）
2. **応答の最後に 1 つだけ** fenced:

```yaml
site_overview:
  site_name: "必須・非空"
  purpose: "..."
  target_users: "..."
design_spec:
  color_scheme:
    background: "#fafaf9"
    primary: "#0f766e"
    text: "#0f172a"
    border: "#e2e8f0"
    primary_foreground: "#ffffff"
  typography: {}
  layout_mood: "..."
  design_principles: ["..."]
ux_spec:
  primary_conversion: { label: "...", action: "..." }
  secondary_actions: []
  navigation_model: "..."
  trust_placement: "..."
  mobile_notes: "..."
function_spec: {}
image_placeholder_slots:
  - { page_path: "/", section_id: "hero", description: "具体的な画角・被写体", aspect_hint: "16:9" }
  - { page_path: "/", section_id: "sub1", description: "...", aspect_hint: "4:3" }
  - { page_path: "/", section_id: "sub2", description: "...", aspect_hint: "16:9" }
```

- YAML 以外の本文は **最低でも数段落・複数見出し**（80文字以上）
- 先頭から `{` で始まる **JSON だけ**の応答はこの段では **禁止**（第2段は台本＋末尾 YAML）
"""


def _briefing_value_as_text(v: Any) -> str:
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(v)
    return str(v)


def _plan_info_as_briefing_lines(plan_info: Dict[str, Any]) -> str:
    lines: list[str] = []
    for k in sorted(plan_info.keys()):
        v = plan_info.get(k)
        if v is None or v == "":
            continue
        lines.append(f"- {k}: {_briefing_value_as_text(v)}")
    return "\n".join(lines) if lines else "（項目なし）"


def compose_spec_input_briefing(
    *,
    partner_name: str,
    contract_plan: str,
    contract_pages: int,
    page_rule: str,
    plan_info: Dict[str, Any],
    hearing_sheet_content: str,
    site_build_prompt: str,
    requirements_result: Dict[str, Any],
    max_chars: int = 120_000,
) -> str:
    """
    第2段 LLM へ渡す入力を **JSONではなくプレーンテキスト1本**にまとめる。
    （第2段の出力は Markdown サイト台本＋末尾 YAML。レガシー運用では JSON のみも解釈可）
    """
    chunks: list[str] = []
    chunks.append("【パートナー名】")
    chunks.append((partner_name or "").strip() or "（未記入）")
    chunks.append("")
    chunks.append("【契約プラン（システム）】")
    chunks.append((contract_plan or "").strip() or "（未記入）")
    chunks.append("")
    chunks.append("【契約ページ数（厳守・変更禁止）】")
    chunks.append(str(contract_pages))
    chunks.append("")
    chunks.append("【ページ構成に関する指示】")
    chunks.append(page_rule.strip())
    chunks.append("")
    chunks.append("【契約プラン詳細（システム・テキスト化）】")
    chunks.append(_plan_info_as_briefing_lines(plan_info))
    chunks.append("")
    chunks.append("【ヒアリング原文】")
    chunks.append((hearing_sheet_content or "").strip() or "（空）")
    chunks.append("")
    chunks.append("【第1段・サイト制作マスタープロンプト（最優先）】")
    chunks.append(site_build_prompt.strip())
    chunks.append("")

    pt = requirements_result.get("plan_type")
    if pt:
        chunks.append("【システム確定 plan_type】")
        chunks.append(str(pt))
        chunks.append("")

    cm = requirements_result.get("contract_max_pages")
    if cm is not None:
        chunks.append("【contract_max_pages（参照）】")
        chunks.append(str(cm))
        chunks.append("")

    cv = requirements_result.get("client_voice")
    if isinstance(cv, str) and cv.strip():
        sbp_head = site_build_prompt.strip()[:400]
        if cv.strip()[:400] != sbp_head:
            chunks.append("【第1段・client_voice（補足・テキスト）】")
            chunks.append(cv.strip())
            chunks.append("")

    ibn = requirements_result.get("internal_build_notes")
    if isinstance(ibn, list) and ibn:
        chunks.append("【第1段・内部メモ（サイト非掲載・参照のみ）】")
        for x in ibn:
            if x is not None and str(x).strip():
                chunks.append(f"- {x}")
        chunks.append("")

    oq = requirements_result.get("open_questions")
    if isinstance(oq, list) and oq:
        chunks.append("【要確認事項】")
        for x in oq:
            if x is not None and str(x).strip():
                chunks.append(f"- {x}")
        chunks.append("")

    facts = requirements_result.get("facts")
    if isinstance(facts, dict) and facts:
        chunks.append("【第1段・補足ファクト（テキスト化）】")
        for fk, fv in facts.items():
            if fv is None or fv == "":
                continue
            if isinstance(fv, list):
                chunks.append(f"- {fk}:")
                for it in fv:
                    chunks.append(f"  - {it}")
            else:
                chunks.append(f"- {fk}: {_briefing_value_as_text(fv)}")
        chunks.append("")

    out = "\n".join(chunks).strip()
    if len(out) > max_chars:
        logger.warning(
            "第2段ブリーフが長いため %s 文字に切り詰めました（元 %s）",
            max_chars,
            len(out),
        )
        half = max_chars // 2 - 80
        out = (
            out[:half]
            + "\n\n…[truncated]…\n\n"
            + out[-half:]
        )
    return out


class SpecGenerator:
    """ヒアリング・第1段ブリーフからサイト台本（＋YAMLメタ）を生成。内部API名は互換のため generate_spec のまま。"""

    def __init__(self) -> None:
        if not is_text_llm_configured():
            raise ValueError(
                "テキスト LLM が未設定です。"
                "TEXT_LLM_PROVIDER=cursor_agent_cli または claude_code_cli と、"
                "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND を設定してください。"
            )

    def _llm(self, prompt: str, system: str, temperature: float = 0.3) -> str:
        return text_llm_complete(user=prompt, system=system, temperature=temperature)

    def _merge_common_technical_spec(self, extra: Optional[Dict] = None) -> Dict:
        """全プラン共通の技術要件を technical_spec に統合（スタックと共通要件は常に上書き固定）"""
        merged: Dict = {}
        if extra:
            merged.update(extra)
        merged["tech_stack"] = [
            "Next.js (App Router)",
            "React",
            "TypeScript",
            "Tailwind CSS",
        ]
        merged["common_requirements"] = get_common_technical_spec()
        return merged

    def _apply_common_technical_to_spec(self, spec: Dict) -> Dict:
        """LLM出力の仕様書に共通技術要件をマージ"""
        ts = spec.get("technical_spec")
        if isinstance(ts, dict):
            spec["technical_spec"] = self._merge_common_technical_spec(ts)
        else:
            spec["technical_spec"] = self._merge_common_technical_spec()
        return spec

    def fetch_hearing_sheet(self, url: str) -> Optional[str]:
        """
        ヒアリングシートの内容を取得

        Args:
            url: ヒアリングシートURL

        Returns:
            ヒアリングシートの内容（テキスト）
        """
        try:
            raw = (url or "").strip()
            if not raw:
                return None
            # セルに全文が貼られているだけの場合（http で始まらない）
            if not re.match(r"^https?://", raw, re.IGNORECASE):
                m = re.search(r"https?://[^\s\]<>\")]+", raw)
                if m:
                    return self.fetch_hearing_sheet(m.group(0))
                logger.info(
                    "ヒアリングシート列が URL ではないため、本文としてそのまま使用します（先頭 %s 文字）",
                    min(len(raw), 200),
                )
                return raw

            # Google Sheets URLの場合
            if "docs.google.com/spreadsheets" in raw:
                # 簡易的な取得（実際はGoogle Sheets APIを使用）
                response = requests.get(raw, timeout=60)
                if response.status_code == 200:
                    # HTMLからテキストを抽出（簡易版）
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text()
                    logger.info("ヒアリングシートを取得しました")
                    return text
            else:
                # その他のURL
                response = requests.get(raw, timeout=60)
                if response.status_code == 200:
                    return response.text

            return None
        except Exception as e:
            logger.error(f"ヒアリングシート取得エラー: {e}")
            return None

    def generate_spec(
        self,
        hearing_sheet_content: str,
        requirements_result: Dict,
        contract_plan: str,
        partner_name: str,
    ) -> Dict:
        """
        サイト台本を生成（TEXT_LLM。パース失敗時は形式指定を付けて最大 1 回再試行）。
        入力は `compose_spec_input_briefing` のブリーフ。出力は **Markdown + 末尾 ```yaml```**（またはレガシー仕様 JSON）。
        """
        plan_info = get_contract_plan_info(contract_plan)
        contract_pages = int(plan_info.get("pages") or 1)
        page_rule = (
            "サイト台本は **トップ（/）のみ**の単一ページ構成とすること（`## ページ:` は `/` のみ）。"
            if contract_pages <= 1
            else (
                f"サイト台本に **`## ページ: /...` でちょうど {contract_pages} 個のルート**（それぞれ一意のパス）を書くこと。"
                "コンテンツが薄くてもページを統合・省略して数を減らさない。"
                "トップを含め、一覧・詳細・問い合わせ等へ内容を配分してよい。"
            )
        )
        sbp = (requirements_result.get("site_build_prompt") or "").strip()
        if not sbp:
            # 旧第1段JSON（site_build_prompt なし）との互換
            cv = requirements_result.get("client_voice")
            if isinstance(cv, str) and cv.strip():
                sbp = (
                    "【互換: 第1段に site_build_prompt が無いため client_voice を主入力とする】\n"
                    + cv.strip()
                )
            else:
                sbp = (
                    "【互換: 第1段の要約のみ】\n"
                    + json.dumps(requirements_result, ensure_ascii=False, indent=2)[:8000]
                )
        input_briefing_text = compose_spec_input_briefing(
            partner_name=partner_name,
            contract_plan=contract_plan,
            contract_pages=contract_pages,
            page_rule=page_rule,
            plan_info=plan_info,
            hearing_sheet_content=hearing_sheet_content or "",
            site_build_prompt=sbp,
            requirements_result=requirements_result,
        )
        prompt = format_prompt(
            "spec_generation.user_template",
            contract_pages=str(contract_pages),
            input_briefing_text=input_briefing_text,
            technical_block=get_technical_spec_prompt_block(),
        )
        system = get_prompt_str("spec_generation.system")
        try:
            raw = self._llm(prompt, system, 0.25)
        except Exception as e:
            raise RuntimeError(
                "仕様書生成: TEXT_LLM の呼び出しに失敗しました（modules.spec_generator.generate_spec）。"
                f" 原因: {e}"
            ) from e

        if not (raw or "").strip():
            raise RuntimeError(
                "サイト台本生成: LLM の応答が空です（modules.spec_generator.generate_spec）。"
            )

        try:
            data, mode = parse_llm_spec_or_site_script(raw)
        except ValueError as e:
            logger.warning("サイト台本生成: 初回パース失敗 (%s)。形式再指定で再試行します。", e)
            try:
                raw2 = self._llm(prompt + _SPEC_SCRIPT_RETRY_USER_SUFFIX, system, 0.15)
            except Exception as e2:
                raise RuntimeError(
                    "サイト台本生成: 再試行の TEXT_LLM 呼び出しに失敗しました（modules.spec_generator.generate_spec）。"
                    f" 原因: {e2}"
                ) from e2
            if not (raw2 or "").strip():
                raise RuntimeError(
                    "サイト台本生成: 再試行の応答が空です（modules.spec_generator.generate_spec）。"
                )
            raw = raw2
            try:
                data, mode = parse_llm_spec_or_site_script(raw)
            except ValueError as e3:
                raise RuntimeError(
                    "サイト台本生成: 再試行後もパースできませんでした（modules.spec_generator）。"
                    f" 原因: {e3} 応答先頭: {(raw or '')[:800]!r}"
                ) from e3

        if not isinstance(data, dict) or not data.get("site_overview"):
            raise RuntimeError(
                "サイト台本生成: 内部エラー（site_overview なし）（modules.spec_generator）。"
            )

        if mode == "site_script":
            logger.info(
                "サイト台本生成完了（Markdown+YAML） site_script_chars=%s",
                len((data.get("site_script_md") or "")),
            )
        else:
            logger.info("仕様書 JSON（レガシー）を解釈しました（spec_generator）")
        return self._apply_common_technical_to_spec(data)
