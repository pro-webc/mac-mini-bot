"""gemini_site_images: プレースホルダ抽出と import 補助"""
from pathlib import Path

from modules.gemini_site_images import (
    collect_placeholder_slots,
    ensure_next_image_import,
    strip_unused_image_placeholder_import,
)


def test_collect_placeholder_self_closing(tmp_path: Path) -> None:
    p = tmp_path / "app" / "page.tsx"
    p.parent.mkdir(parents=True)
    p.write_text(
        '''"use client";
import ImagePlaceholder from "@/components/ImagePlaceholder";
export default function P() {
  return <ImagePlaceholder description="hero shot" aspectClassName="aspect-video" />;
}
''',
        encoding="utf-8",
    )
    slots = collect_placeholder_slots(tmp_path)
    assert len(slots) == 1
    assert slots[0].description == "hero shot"
    assert slots[0].aspect_ratio == "16:9"


def test_collect_multiline_placeholder(tmp_path: Path) -> None:
    p = tmp_path / "components" / "X.tsx"
    p.parent.mkdir(parents=True)
    p.write_text(
        """import ImagePlaceholder from "@/components/ImagePlaceholder";
export function X() {
  return (
    <ImagePlaceholder
      description="team photo"
      aspectClassName="aspect-square"
    />
  );
}
""",
        encoding="utf-8",
    )
    slots = collect_placeholder_slots(tmp_path)
    assert len(slots) == 1
    assert "team photo" in slots[0].description
    assert slots[0].aspect_ratio == "1:1"


def test_ensure_next_image_import() -> None:
    s = '"use client";\nexport default function() { return null; }\n'
    out = ensure_next_image_import(s)
    assert 'import Image from "next/image"' in out


def test_strip_unused_placeholder_import() -> None:
    src = """import ImagePlaceholder from "@/components/ImagePlaceholder";
export default function() { return null; }
"""
    assert "ImagePlaceholder" not in strip_unused_image_placeholder_import(src)
