"""画像生成（第4工程相当・サイト実装 LLM とは別 API / 別コンテキスト）。

既定モード **from_placeholder_source** は、実装済み TSX 内の `<ImagePlaceholder />` を走査し、
`docs/visual_style_brief.json` と `docs/image_pipeline_context.json`（site_implementer が書く）をマージし、
画風を揃えて生成後に `next/image` へ差し替える。`generate_after_site(site_dir)` のみでも動作する。

- IMAGE_GEN_PROVIDER=gemini | openai | cursor_agent_cli | pillow（詳細は README / config）

当該実行だけ画像を飛ばすときは **main.py** の `IMAGE_GEN_SKIP_RUN` または `--skip-images`。

テキスト台本・コード生成は modules.text_llm。第2段の `image_placeholder_slots` は
`visual_style_brief.reference_slot_descriptions` とスタンドアロン生成のフォールバックに使う。
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
import requests
from config.config import (
    IMAGE_GEN_AFTER_SITE,
    IMAGE_GEN_DALLE_SIZE,
    IMAGE_GEN_ENABLED,
    IMAGE_GEN_MODE,
    IMAGE_GEN_OPENAI_MODEL,
    IMAGE_GEN_PROVIDER,
    OUTPUT_DIR,
    resolve_image_gen_api_key,
)
from config.prompt_settings import format_prompt, get_prompt_str
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _image_cursor_cli_timeout_sec() -> int:
    """
    cursor_agent_cli 画像1枚あたりの subprocess タイムアウト（秒）。

    未設定時は **3600**（1時間）。PNG の base64 を 1 応答に載せるため TEXT_LLM より遅くなりがちで、
    既定 1200 秒だとタイムアウトしやすい。
    IMAGE_GEN_CLI_TIMEOUT_SEC で上書き。TEXT_LLM と揃えたい場合は IMAGE_GEN_CLI_TIMEOUT_SEC=1200 等。
    """
    raw = (os.getenv("IMAGE_GEN_CLI_TIMEOUT_SEC") or "").strip()
    if raw:
        return max(60, int(raw))
    return 3600


def _is_png(data: bytes) -> bool:
    return len(data) >= 8 and data[:8] == _PNG_MAGIC


def _extract_png_bytes_from_cursor_response(text: str) -> Optional[bytes]:
    """
    Cursor / Claude CLI のテキスト応答から PNG バイナリを取り出す。
    想定: data:image/png;base64,... または JSON の png_base64 / image_base64。
    """
    raw = (text or "").strip()
    if not raw:
        return None

    m = re.search(
        r"data:image/png;base64,([A-Za-z0-9+/=\s]+)", raw, re.IGNORECASE | re.DOTALL
    )
    if m:
        b64 = re.sub(r"\s+", "", m.group(1))
        try:
            out = base64.b64decode(b64, validate=False)
            if _is_png(out):
                return out
        except (binascii.Error, ValueError):
            pass

    def _try_json_obj(j: Any) -> Optional[bytes]:
        if not isinstance(j, dict):
            return None
        for key in ("png_base64", "image_base64", "base64"):
            val = j.get(key)
            if not isinstance(val, str) or not val.strip():
                continue
            b64 = re.sub(r"\s+", "", val.strip())
            try:
                out = base64.b64decode(b64, validate=False)
                if _is_png(out):
                    return out
            except (binascii.Error, ValueError):
                continue
        return None

    try:
        j = json.loads(raw)
        got = _try_json_obj(j)
        if got:
            return got
    except json.JSONDecodeError:
        pass

    fm = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if fm:
        inner = fm.group(1).strip()
        try:
            j = json.loads(inner)
            got = _try_json_obj(j)
            if got:
                return got
        except json.JSONDecodeError:
            pass

    lb = raw.find("{")
    rb = raw.rfind("}")
    if lb != -1 and rb > lb:
        try:
            j = json.loads(raw[lb : rb + 1])
            got = _try_json_obj(j)
            if got:
                return got
        except json.JSONDecodeError:
            pass

    return None


def _slug(s: str, max_len: int = 48) -> str:
    h = hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:12]
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", s[:max_len]).strip("-").lower() or "img"
    return f"{safe[:32]}-{h}"


def _load_visual_style_brief(site_dir: Path) -> Dict[str, Any]:
    p = site_dir / "docs" / "visual_style_brief.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _load_image_pipeline_context(site_dir: Path) -> Dict[str, Any]:
    """site_implementer が書いた第2段メタ（画像・スタンドアロン用）。無ければ空 dict。"""
    p = site_dir / "docs" / "image_pipeline_context.json"
    if not p.is_file():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _brief_to_style_prefix(brief: Dict[str, Any]) -> str:
    if not brief:
        return (
            "Professional website photography, consistent natural lighting, "
            "cohesive color grading across all images, no text or letters in the image."
        )
    parts = [
        str(brief.get("layout_mood") or ""),
        str(brief.get("industry_or_purpose") or ""),
        json.dumps(brief.get("color_scheme") or {}, ensure_ascii=False),
    ]
    refs = brief.get("reference_slot_descriptions") or []
    if isinstance(refs, list) and refs:
        joined = " | ".join(str(r) for r in refs[:6] if r)
        if joined:
            parts.append("Planned image subjects (site brief): " + joined[:1200])
    rules = brief.get("image_consistency_rules") or []
    if isinstance(rules, list):
        parts.append("\n".join(str(r) for r in rules))
    return "\n".join(p for p in parts if p).strip() or _brief_to_style_prefix({})


def _merge_visual_style_brief(disk: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
    """ディスクの brief を優先し、欠けたキーは spec から補完（第2段 YAML との全体整合）。"""
    merged = _brief_from_spec(spec)
    if not disk:
        return merged
    for k, v in disk.items():
        if v is None:
            continue
        if v == "" or v == [] or v == {}:
            continue
        merged[k] = v
    return merged


def _iter_image_placeholder_matches(site_dir: Path):
    """ImagePlaceholder の出現順（_scan_placeholder_slots と同一順序）で (Path, re.Match) を返す"""
    roots = [site_dir / "app", site_dir / "components"]
    pat = re.compile(
        r"<ImagePlaceholder\s+([\s\S]*?)(?:/>|></ImagePlaceholder>)",
    )
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.tsx"):
            if "node_modules" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "ImagePlaceholder" not in text:
                continue
            for m in pat.finditer(text):
                yield path, m


def _parse_placeholder_block(full: str) -> Tuple[str, str, str]:
    """ImagePlaceholder の JSX 断片から description / overlayText / aspectClassName を抽出"""
    dm = re.search(r'description\s*=\s*"((?:\\.|[^"\\])*)"', full)
    if not dm:
        dm = re.search(r"description\s*=\s*'((?:\\.|[^'\\])*)'", full)
    if not dm:
        dm = re.search(r"description\s*=\s*\{\s*['\"]([^'\"]+)['\"]\s*\}", full)
    desc = dm.group(1).replace('\\"', '"').replace("\\'", "'") if dm else "image"
    om = re.search(r'overlayText\s*=\s*"((?:\\.|[^"\\])*)"', full)
    if not om:
        om = re.search(r"overlayText\s*=\s*'((?:\\.|[^'\\])*)'", full)
    overlay = om.group(1).replace('\\"', '"').replace("\\'", "'") if om else ""
    am = re.search(r'aspectClassName\s*=\s*["\']([^"\']+)["\']', full)
    aspect = am.group(1) if am else "aspect-video"
    return desc, overlay, aspect


def _escape_tsx_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _tsx_next_image_replacement(
    public_path: str, description: str, overlay_text: str, aspect_class: str
) -> str:
    """ImagePlaceholder の代替: next/image + 既存レイアウトに近いラッパー"""
    alt = _escape_tsx_string(description)
    overlay_block = ""
    if overlay_text.strip():
        ot = _escape_tsx_string(overlay_text)
        overlay_block = (
            f'<p className="pointer-events-none absolute inset-0 z-10 flex items-center '
            f'justify-center bg-black/40 px-4 text-center text-base font-medium text-white">{ot}</p>'
        )
    return (
        f'<div className="relative w-full overflow-hidden {aspect_class}">\n'
        f"      <Image\n"
        f'        src="{public_path}"\n'
        f'        alt="{alt}"\n'
        f"        fill\n"
        f'        className="object-cover"\n'
        f'        sizes="(max-width: 768px) 100vw, min(1200px, 100vw)"\n'
        f"        priority={{false}}\n"
        f"      />\n"
        f"      {overlay_block}\n"
        f"    </div>"
    )


def _ensure_next_image_import(tsx: str) -> str:
    if re.search(r'from\s+["\']next/image["\']', tsx):
        return tsx
    if tsx.strip().startswith('"use client"') or tsx.strip().startswith("'use client'"):
        first_nl = tsx.find("\n")
        if first_nl != -1:
            return (
                tsx[: first_nl + 1]
                + '\nimport Image from "next/image";\n'
                + tsx[first_nl + 1 :]
            )
    return 'import Image from "next/image";\n' + tsx


def _apply_generated_images_to_tsx(site_dir: Path, entries: List[Dict[str, Any]]) -> None:
    """生成した publicPath を ImagePlaceholder から next/image に差し替え（出現順 = entries 順）"""
    matches = list(_iter_image_placeholder_matches(site_dir))
    if not matches:
        return
    if len(matches) != len(entries):
        logger.warning(
            "ImagePlaceholder 数 (%d) とエントリ数 (%d) が一致しません。"
            "先頭 min 件のみ差し替えます（スロット走査とプレースホルダ数のズレを解消してください）",
            len(matches),
            len(entries),
        )

    # path -> list of (start, end, new_text) 後ろから適用するため start で降順
    per_path: Dict[Path, List[Tuple[int, int, str]]] = {}
    n_pairs = min(len(matches), len(entries))
    for (path, m), entry in zip(matches[:n_pairs], entries[:n_pairs]):
        pub = entry.get("publicPath")
        if not pub:
            continue
        full = m.group(0)
        desc, overlay, aspect = _parse_placeholder_block(full)
        new_text = _tsx_next_image_replacement(pub, desc, overlay, aspect)
        per_path.setdefault(path, []).append((m.start(), m.end(), new_text))

    for path, chunks in per_path.items():
        chunks.sort(key=lambda x: x[0], reverse=True)
        text = path.read_text(encoding="utf-8")
        for start, end, new_text in chunks:
            text = text[:start] + new_text + text[end:]
        text = _ensure_next_image_import(text)
        if "ImagePlaceholder" not in text:
            text = re.sub(
                r'^import\s+ImagePlaceholder\s+from\s+["\'][^"\']+["\']\s*\n',
                "",
                text,
                flags=re.MULTILINE,
            )
        path.write_text(text, encoding="utf-8")
        logger.info("ImagePlaceholder を next/image に差し替えました: %s", path.relative_to(site_dir))


def _scan_placeholder_slots(site_dir: Path) -> List[Dict[str, str]]:
    """
    TSX 内の ImagePlaceholder を走査。
    _iter_image_placeholder_matches と同じ順序・同じ件数になるよう、
    プレースホルダ全文から _parse_placeholder_block で description を解決する。
    （旧実装は description の正規表現に合わない書き方の箇所をスキップし、
    差し替え側の件数とずれて「差し替え中止」になっていた）
    """
    slots: List[Dict[str, str]] = []
    for path, m in _iter_image_placeholder_matches(site_dir):
        full = m.group(0)
        desc, overlay, _aspect = _parse_placeholder_block(full)
        rel = str(path.relative_to(site_dir)).replace("\\", "/")
        slots.append(
            {
                "source_file": rel,
                "description": desc,
                "overlayText": overlay,
            }
        )
    return slots


class ImageGenerator:
    """
    画像専用パイプライン。メインの仕様書/コード生成 LLM とは別キー・別クライアントを推奨。
    - IMAGE_GEN_API_KEY: 専用キー（未設定時は IMAGE_GEN_ALLOW_FALLBACK_TO_MAIN_KEYS でメインキーにフォールバック）
    """

    def __init__(self) -> None:
        self.enabled = IMAGE_GEN_ENABLED
        self.provider = IMAGE_GEN_PROVIDER
        self.mode = IMAGE_GEN_MODE
        self._openai_image_client = None
        self._gemini_model = None

        if not self.enabled:
            logger.info("IMAGE_GEN_ENABLED=false — 画像パイプラインは無効です")
            return

        key = resolve_image_gen_api_key(self.provider)
        if self.provider == "openai":
            if key:
                from openai import OpenAI

                self._openai_image_client = OpenAI(api_key=key)
            else:
                logger.warning("画像生成 openai: IMAGE_GEN_API_KEY 未設定（フォールバックも無効）")
        elif self.provider == "gemini":
            if key:
                genai.configure(api_key=key)
                # テキスト用と同様、利用可能なモデル名を使用（exp 系は廃止されやすい）
                _img_model = os.getenv(
                    "IMAGE_GEN_GEMINI_MODEL", "gemini-2.5-flash"
                ).strip()
                self._gemini_model = genai.GenerativeModel(_img_model)
            else:
                logger.warning("画像生成 gemini: IMAGE_GEN_API_KEY 未設定（フォールバックも無効）")
        elif self.provider == "cursor_agent_cli":
            if not is_text_llm_configured():
                logger.warning(
                    "画像生成 cursor_agent_cli: テキスト LLM（CURSOR_AGENT_COMMAND 等）が未設定です"
                )
        elif self.provider == "pillow":
            pass
        else:
            logger.warning("未知の IMAGE_GEN_PROVIDER=%s — pillow にフォールバック扱い", self.provider)

    def is_enabled(self) -> bool:
        return bool(self.enabled)

    def is_provider_ready(self) -> bool:
        if not self.enabled:
            return False
        if self.provider == "cursor_agent_cli":
            return is_text_llm_configured()
        if self.provider == "openai":
            return self._openai_image_client is not None
        if self.provider == "gemini":
            return self._gemini_model is not None
        return True  # pillow

    def generate_after_site(
        self,
        site_dir: Path,
        spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Path]:
        """
        サイト実装後に実行。`spec` が無いときは `docs/image_pipeline_context.json` を読む。
        Returns:
            (エントリリスト, manifest パス)
        """
        if not self.enabled:
            return [], site_dir / "docs" / "generated_images.json"
        if not IMAGE_GEN_AFTER_SITE:
            logger.info("IMAGE_GEN_AFTER_SITE=false — スキップ")
            return [], site_dir / "docs" / "generated_images.json"

        eff_spec = spec if spec is not None else _load_image_pipeline_context(site_dir)
        if spec is None and not eff_spec:
            logger.info(
                "image_pipeline_context.json がありません（実装スキップ時など）。"
                "visual_style_brief のみで続行します。"
            )

        if self.mode == "from_placeholder_source":
            return self._generate_from_placeholders(eff_spec, site_dir)
        return self._generate_standalone_spec(eff_spec, site_dir)

    def _write_manifest(self, site_dir: Path, entries: List[Dict[str, Any]]) -> Path:
        docs = site_dir / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "pipeline": "isolated_from_site_llm",
            "mode": self.mode,
            "provider": self.provider,
            "entries": entries,
            "note": (
                "実ファイルは public/images/generated/ に保存。"
                "from_placeholder_source では生成後に TSX の ImagePlaceholder を next/image に差し替え済み。"
            ),
        }
        path = docs / "generated_images.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def _generate_from_placeholders(
        self, spec: Dict, site_dir: Path
    ) -> Tuple[List[Dict[str, Any]], Path]:
        brief = _merge_visual_style_brief(_load_visual_style_brief(site_dir), spec)
        style = _brief_to_style_prefix(brief)
        slots = _scan_placeholder_slots(site_dir)
        if not slots:
            logger.info("ImagePlaceholder が見つかりませんでした")
            mp = self._write_manifest(site_dir, [])
            return [], mp

        out_dir = site_dir / "public" / "images" / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        entries: List[Dict[str, Any]] = []

        n_slots = len(slots)
        for i, slot in enumerate(slots):
            desc = slot["description"]
            overlay = slot.get("overlayText") or ""
            logger.info(
                "ImagePlaceholder 画像 %d/%d（%s）— 次の行まで Cursor CLI が無言で走ることがあります",
                i + 1,
                n_slots,
                slot.get("source_file", "?"),
            )
            slug = _slug(f"{slot['source_file']}-{i}-{desc}")
            filename = f"{slug}.png"
            rel_public = f"/images/generated/{filename}"
            full_prompt = format_prompt(
                "image_generation.placeholder_slot_prompt_template",
                style=style,
                desc=desc,
                overlay=overlay,
            )
            path = out_dir / filename
            ok = self._generate_one_file(full_prompt, path)
            entries.append(
                {
                    "id": slug,
                    "source_file": slot["source_file"],
                    "description": desc,
                    "overlayText": overlay,
                    "publicPath": rel_public if ok else None,
                    "localPath": str(path) if ok else None,
                    "ok": ok,
                }
            )

        manifest = self._write_manifest(site_dir, entries)
        _apply_generated_images_to_tsx(site_dir, entries)
        return entries, manifest

    def _generate_standalone_spec(
        self, spec: Dict, site_dir: Path
    ) -> Tuple[List[Dict[str, Any]], Path]:
        """プレースホルダ無し時: content_spec / 第2段 image_placeholder_slots からプロンプト列を構成"""
        disk = _load_visual_style_brief(site_dir)
        brief = _merge_visual_style_brief(disk, spec)
        style = _brief_to_style_prefix(brief)
        content = spec.get("content_spec") or {}
        reqs = content.get("image_requirements") or []
        if isinstance(reqs, str):
            reqs = [reqs]
        site_name = (spec.get("site_overview") or {}).get("site_name", "site")
        if not reqs:
            slots = spec.get("image_placeholder_slots") or []
            if isinstance(slots, list):
                for s in slots:
                    if isinstance(s, dict) and (s.get("description") or "").strip():
                        reqs.append(str(s["description"]).strip())
        if not reqs:
            reqs = [f"{site_name} のヒーロー向けメインビジュアル（プロフェッショナル）"]

        out_dir = site_dir / "public" / "images" / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        entries: List[Dict[str, Any]] = []

        for i, req in enumerate(reqs):
            if not isinstance(req, str):
                req = str(req)
            slug = _slug(f"spec-{i}-{req}")
            filename = f"{slug}.png"
            path = out_dir / filename
            full_prompt = format_prompt(
                "image_generation.openai_style_line_template",
                style=style,
                req=req,
            )
            ok = self._generate_one_file(full_prompt, path)
            entries.append(
                {
                    "id": slug,
                    "source_file": None,
                    "description": req,
                    "publicPath": f"/images/generated/{filename}" if ok else None,
                    "localPath": str(path) if ok else None,
                    "ok": ok,
                }
            )

        return entries, self._write_manifest(site_dir, entries)

    def _cursor_agent_image_attempt(self, prompt: str, output_path: Path) -> bool:
        """TEXT_LLM と同じ Cursor CLI。応答 JSON の png_base64 を PNG として保存。"""
        if not is_text_llm_configured():
            return False
        user = get_prompt_str("image_generation.cursor_agent_user_prefix") + prompt
        system_main = get_prompt_str("image_generation.cursor_agent_system").strip()
        system_fb = get_prompt_str("image_generation.cursor_agent_system_fallback").strip()
        tout = _image_cursor_cli_timeout_sec()

        def _call(system: str, temp: float) -> str:
            return text_llm_complete(
                user=user,
                system=system,
                temperature=temp,
                cli_timeout_sec=tout,
            )

        logger.info(
            "Cursor 画像: CLI 起動（この呼び出し最大約 %d 秒・終わるまでログが増えないのは正常）",
            tout,
        )
        try:
            raw = _call(system_main, 0.4)
        except Exception as e:
            logger.error("Cursor 画像生成（CLI）失敗: %s", e)
            return False
        if not (raw or "").strip():
            return False
        stripped = raw.strip()
        if '"error"' in stripped.lower() and "png_base64" not in stripped:
            logger.warning(
                "Cursor が png_base64 を含まない応答を返しました（先頭 300 文字）: %s",
                stripped[:300],
            )
            return False
        data = _extract_png_bytes_from_cursor_response(raw)
        if not data:
            logger.info(
                "Cursor 画像: 初回から PNG を解釈できなかったためフォールバック system で再試行します（最大約 %d 秒）",
                tout,
            )
            try:
                raw2 = _call(system_fb, 0.2)
            except Exception as e2:
                logger.error("Cursor 画像生成（フォールバック）失敗: %s", e2)
                return False
            data = _extract_png_bytes_from_cursor_response(raw2 or "")
        if not data:
            logger.warning(
                "Cursor 応答から有効な PNG base64 を解釈できませんでした（先頭 400 文字）: %s",
                raw[:400],
            )
            return False
        output_path.write_bytes(data)
        logger.info("Cursor CLI 経由の PNG を保存: %s", output_path)
        return True

    def _generate_one_file(self, prompt: str, output_path: Path) -> bool:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self.provider == "cursor_agent_cli":
                if self._cursor_agent_image_attempt(prompt, output_path):
                    return True
            if self.provider == "openai" and self._openai_image_client:
                if self._openai_dalle(prompt, output_path):
                    return True
            if self.provider == "gemini" and self._gemini_model:
                if self._gemini_image_attempt(prompt, output_path):
                    return True
        except Exception as e:
            logger.error("画像生成エラー: %s", e, exc_info=True)
        self._generate_placeholder_image(output_path, prompt, 1024, 1024)
        return True

    def _openai_dalle(self, prompt: str, output_path: Path) -> bool:
        r = self._openai_image_client.images.generate(
            model=IMAGE_GEN_OPENAI_MODEL,
            prompt=prompt[:4000],
            size=IMAGE_GEN_DALLE_SIZE,
            quality="standard",
            n=1,
        )
        url = r.data[0].url
        if not url:
            return False
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        output_path.write_bytes(resp.content)
        logger.info("OpenAI 画像を保存: %s", output_path)
        return True

    def _gemini_image_attempt(self, prompt: str, output_path: Path) -> bool:
        enhanced = get_prompt_str("image_generation.gemini_user_prefix") + prompt
        response = self._gemini_model.generate_content(enhanced)
        if hasattr(response, "images") and response.images:
            with open(output_path, "wb") as f:
                f.write(response.images[0])
            return True
        logger.warning("Gemini が画像バイナリを返さなかったため PIL にフォールバック")
        return False

    def _generate_placeholder_image(
        self,
        output_path: Path,
        prompt: str,
        width: int,
        height: int,
    ) -> None:
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new("RGB", (width, height), color="#f0f0f0")
            draw = ImageDraw.Draw(img)
            text = prompt[:80] if len(prompt) > 80 else prompt
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            except OSError:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                ((width - tw) // 2, (height - th) // 2),
                text,
                fill="#666666",
                font=font,
            )
            img.save(output_path, "PNG")
            logger.info("PIL プレースホルダを保存: %s", output_path)
        except ImportError:
            logger.warning("Pillow 未インストール — 画像ファイルをスキップ")
        except Exception as e:
            logger.error("PIL 画像エラー: %s", e)

    # --- 後方互換: main から呼ばれる旧 API ---
    def generate_images_for_site(
        self,
        spec: Dict,
        output_dir: Optional[Path] = None,
        site_dir: Optional[Path] = None,
    ) -> List[Dict[str, Path]]:
        """
        互換用。site_dir があれば after_site パイプライン、なければ output のみ PIL。
        """
        if not self.is_enabled():
            return []

        if site_dir and site_dir.is_dir():
            entries, _ = self.generate_after_site(site_dir, spec)
            return [
                {"purpose": e.get("id", "image"), "path": Path(e["localPath"])}
                for e in entries
                if e.get("localPath")
            ]

        # レガシー: 出力ディレクトリのみ（サイト未生成時）
        base = output_dir or (OUTPUT_DIR / "images")
        base.mkdir(parents=True, exist_ok=True)
        images: List[Dict[str, Path]] = []
        content = spec.get("content_spec") or {}
        reqs = content.get("image_requirements") or []
        if not reqs:
            slots = spec.get("image_placeholder_slots") or []
            if isinstance(slots, list):
                for s in slots:
                    if isinstance(s, dict) and (s.get("description") or "").strip():
                        reqs.append(str(s["description"]).strip())
        if not reqs:
            reqs = ["hero visual"]
        style = _brief_to_style_prefix(_brief_from_spec(spec))
        for i, req in enumerate(reqs):
            if not isinstance(req, str):
                req = str(req)
            p = base / f"legacy_{i}.png"
            self._generate_one_file(style + "\n" + req, p)
            images.append({"purpose": f"content_{i+1}", "path": p})
        return images


def _brief_from_spec(spec: Dict) -> Dict[str, Any]:
    overview = spec.get("site_overview") or {}
    design = spec.get("design_spec") or {}
    layout_mood = design.get("layout_mood") or design.get("layout_style", "")
    ref_desc: list[str] = []
    slots = spec.get("image_placeholder_slots") or []
    if isinstance(slots, list):
        for s in slots[:10]:
            if isinstance(s, dict):
                d = (s.get("description") or "").strip()
                if d:
                    ref_desc.append(d[:240])
    out: Dict[str, Any] = {
        "site_name": overview.get("site_name", ""),
        "target_users": overview.get("target_users", ""),
        "layout_mood": layout_mood,
        "industry_or_purpose": overview.get("purpose", ""),
        "typography_hint": design.get("typography", {}),
        "color_scheme": design.get("color_scheme") or design.get("colors") or {},
        "image_consistency_rules": [
            "Professional cohesive style",
            "No text in images",
        ],
    }
    if ref_desc:
        out["reference_slot_descriptions"] = ref_desc
    return out
