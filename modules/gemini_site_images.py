"""
（オプション・手動向け）ImagePlaceholder を Gemini 画像 API で実ファイルにし、next/image に置換する。

- 画像は Gemini API（REST v1beta）の ``responseModalities: IMAGE`` を使用。
- ``main.WebsiteBot`` からは呼ばない。標準は最終リファクタ（Gemini テキスト）で ``next/image`` + ``public/images/`` を実装。
- Git の push は行わない（``main.WebsiteBot`` の GitHub クライアントが既存どおり実行）。
"""
from __future__ import annotations

import base64
import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

_GEN_DIR = Path("public/images/generated")
_PLACEHOLDER_OPEN = "<ImagePlaceholder"

_API_URL_TMPL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


@dataclass
class _Slot:
    path: Path
    start: int
    end: int
    description: str
    aspect_ratio: str


def _aspect_ratio_from_tag(tag_src: str) -> str:
    t = tag_src.lower()
    if "aspect-square" in t or "1:1" in t:
        return "1:1"
    if "4:3" in t or "4/3" in t or "aspect-[4/3]" in t:
        return "4:3"
    if "3:4" in t or "3/4" in t:
        return "3:4"
    return "16:9"


def _wh_for_aspect(ar: str) -> tuple[int, int]:
    if ar == "1:1":
        return 1024, 1024
    if ar == "4:3":
        return 1200, 900
    if ar == "3:4":
        return 900, 1200
    return 1200, 675


def _ext_for_mime(mime: str) -> str:
    m = (mime or "").lower()
    if "png" in m:
        return ".png"
    if "webp" in m:
        return ".webp"
    if "jpeg" in m or "jpg" in m:
        return ".jpg"
    return ".png"


def _find_next_placeholder_span(text: str, from_idx: int) -> tuple[int, int] | None:
    i = text.find(_PLACEHOLDER_OPEN, from_idx)
    if i < 0:
        return None
    self_close = text.find("/>", i)
    gt = text.find(">", i)
    if self_close >= 0 and (gt < 0 or self_close < gt):
        return (i, self_close + 2)
    if gt < 0:
        return None
    close_tag = text.find("</ImagePlaceholder>", gt)
    if close_tag < 0:
        return None
    return (i, close_tag + len("</ImagePlaceholder>"))


def _description_from_tag(tag: str) -> str | None:
    m = re.search(
        r"description\s*=\s*\"((?:[^\"\\]|\\.)*)\"",
        tag,
        re.DOTALL,
    )
    if not m:
        m2 = re.search(r"description\s*=\s*\{\s*\"((?:[^\"\\]|\\.)*)\"\s*\}", tag, re.DOTALL)
        if not m2:
            return None
        raw = m2.group(1)
    else:
        raw = m.group(1)
    return (
        raw.replace("\\n", "\n")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def collect_placeholder_slots(site_dir: Path) -> list[_Slot]:
    site_dir = site_dir.resolve()
    slots: list[_Slot] = []
    for rel in sorted(site_dir.rglob("*.tsx")):
        if "node_modules" in rel.parts:
            continue
        try:
            text = rel.read_text(encoding="utf-8")
        except OSError:
            continue
        if _PLACEHOLDER_OPEN not in text:
            continue
        pos = 0
        while True:
            span = _find_next_placeholder_span(text, pos)
            if not span:
                break
            a, b = span
            tag = text[a:b]
            desc = _description_from_tag(tag)
            if not (desc or "").strip():
                pos = b
                continue
            slots.append(
                _Slot(
                    path=rel,
                    start=a,
                    end=b,
                    description=desc.strip(),
                    aspect_ratio=_aspect_ratio_from_tag(tag),
                )
            )
            pos = b
    return slots


def _first_inline_image(resp_json: dict[str, Any]) -> tuple[bytes, str] | None:
    for cand in resp_json.get("candidates") or []:
        content = cand.get("content") or {}
        for part in content.get("parts") or []:
            inline = part.get("inlineData") or part.get("inline_data")
            if not inline:
                continue
            b64 = inline.get("data")
            if not b64:
                continue
            try:
                raw = base64.b64decode(b64)
            except Exception:
                continue
            mime = (
                inline.get("mimeType") or inline.get("mime_type") or "image/png"
            )
            return raw, str(mime)
    return None


def generate_image_bytes(
    *,
    api_key: str,
    model: str,
    prompt: str,
    aspect_ratio: str,
    timeout_sec: float = 180.0,
) -> tuple[bytes, str]:
    """1枚生成。失敗時は例外。"""
    url = _API_URL_TMPL.format(model=model)
    body: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Generate a single image for a professional website. "
                            "No text, logos, or watermarks in the image. "
                            "Style: clean, commercial photography or high-quality illustration.\n\n"
                            f"Scene / subject: {prompt}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }
    r = requests.post(
        url,
        params={"key": api_key},
        json=body,
        timeout=timeout_sec,
    )
    if r.status_code != 200:
        raise RuntimeError(
            f"Gemini image API HTTP {r.status_code}: {(r.text or '')[:500]}"
        )
    data = r.json()
    got = _first_inline_image(data)
    if not got:
        err = data.get("error") or data.get("promptFeedback") or data
        raise RuntimeError(f"Gemini image API に画像パートがありません: {err!r}")
    return got


def _jsx_alt(desc: str) -> str:
    return json.dumps(desc, ensure_ascii=False)


def _replacement_image_element(
    public_src: str,
    desc: str,
    aspect_ratio: str,
    global_index: int,
) -> str:
    w, h = _wh_for_aspect(aspect_ratio)
    pri = " priority" if global_index == 0 else ""
    return (
        f'<Image src="{public_src}" alt={_jsx_alt(desc)} '
        f"width={{{w}}} height={{{h}}}{pri} "
        'className="w-full h-auto object-cover" />'
    )


def ensure_next_image_import(content: str) -> str:
    if re.search(r'from\s+["\']next/image["\']', content):
        return content
    lines = content.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('"use client"') or line.strip().startswith(
            "'use client'"
        ):
            insert_at = i + 1
            break
    lines.insert(insert_at, 'import Image from "next/image";')
    return "\n".join(lines)


def strip_unused_image_placeholder_import(content: str) -> str:
    if re.search(r"<ImagePlaceholder\b", content):
        return content
    content = re.sub(
        r"^import\s+ImagePlaceholder\s+from\s+[\"']@/components/ImagePlaceholder[\"'];?\s*\n",
        "",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^import\s+\{\s*ImagePlaceholder\s*\}\s+from\s+[\"'][^\"']+[\"'];?\s*\n",
        "",
        content,
        flags=re.MULTILINE,
    )
    return content


def materialize_site_images(
    site_dir: Path,
    *,
    api_key: str,
    model: str,
    max_slots: int,
    delay_sec_between_calls: float = 1.0,
) -> int:
    """
    ``site_dir`` 以下の TSX にある ``ImagePlaceholder`` を走査し、画像を書き出して置換する。

    Returns:
        生成・置換したスロット数
    """
    site_dir = site_dir.resolve()
    slots = collect_placeholder_slots(site_dir)[: max(0, max_slots)]
    if not slots:
        logger.info("gemini_site_images: ImagePlaceholder がありません。スキップします。")
        return 0

    slot_total = len(slots)

    out_dir = site_dir / _GEN_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # path -> list of (start, end, replacement_str) 後ろから適用
    per_file: dict[Path, list[tuple[int, int, str]]] = {}
    written = 0
    for idx, slot in enumerate(slots):
        try:
            blob, mime = generate_image_bytes(
                api_key=api_key,
                model=model,
                prompt=slot.description,
                aspect_ratio=slot.aspect_ratio,
            )
        except Exception as e:
            logger.warning(
                "gemini_site_images: 生成失敗 slot=%s desc=%r: %s",
                idx,
                slot.description[:80],
                e,
            )
            continue
        ext = _ext_for_mime(mime)
        fname = f"gemini-{written:02d}{ext}"
        fpath = out_dir / fname
        fpath.write_bytes(blob)
        public_src = f"/images/generated/{fname}"
        repl = _replacement_image_element(
            public_src,
            slot.description,
            slot.aspect_ratio,
            written,
        )
        per_file.setdefault(slot.path, []).append((slot.start, slot.end, repl))
        written += 1
        if delay_sec_between_calls > 0 and idx + 1 < len(slots):
            time.sleep(delay_sec_between_calls)

    n = 0
    for path, triples in per_file.items():
        triples.sort(key=lambda t: t[0], reverse=True)
        text = path.read_text(encoding="utf-8")
        for a, b, repl in triples:
            text = text[:a] + repl + text[b:]
            n += 1
        text = ensure_next_image_import(text)
        text = strip_unused_image_placeholder_import(text)
        path.write_text(text, encoding="utf-8")
        logger.info("gemini_site_images: 更新 %s", path.relative_to(site_dir))

    logger.info(
        "gemini_site_images: %s 枚を %s に保存し TSX を置換しました",
        n,
        _GEN_DIR,
    )
    if slot_total > 0 and n == 0:
        logger.error(
            "gemini_site_images: ImagePlaceholder が %s 箇所あるのに 1 件も生成できませんでした。"
            " GEMINI_SITE_IMAGE_MODEL=%r の利用可否・API キー権限を確認してください。",
            slot_total,
            model,
        )
    return n
