"""ImagePlaceholder スロット走査と差し替え件数の一致（画像が挿入されない不具合の退行防止）"""
from __future__ import annotations

import tempfile
from pathlib import Path

from modules.image_generator import (
    _iter_image_placeholder_matches,
    _scan_placeholder_slots,
)


def test_scan_placeholder_slots_matches_iter_count() -> None:
    """旧実装は description が正規表現に合わないとスキップし、差し替えが全中止になった"""
    with tempfile.TemporaryDirectory() as d:
        site = Path(d)
        (site / "components").mkdir(parents=True)
        tsx = site / "components" / "X.tsx"
        tsx.write_text(
            """
import ImagePlaceholder from "@/components/ImagePlaceholder";
export default function X() {
  return (
    <>
      <ImagePlaceholder description="double" aspectClassName="aspect-video" />
      <ImagePlaceholder description='single' aspectClassName="aspect-video" />
    </>
  );
}
""",
            encoding="utf-8",
        )
        slots = _scan_placeholder_slots(site)
        matches = list(_iter_image_placeholder_matches(site))
        assert len(slots) == 2
        assert len(matches) == 2
        assert slots[0]["description"] == "double"
        assert slots[1]["description"] == "single"


def test_parse_fallback_default_description() -> None:
    """description を取れない書き方でもスロットは数に含め、既定の alt 用文言を使う"""
    with tempfile.TemporaryDirectory() as d:
        site = Path(d)
        (site / "app").mkdir(parents=True)
        tsx = site / "app" / "page.tsx"
        tsx.write_text(
            """
import ImagePlaceholder from "@/components/ImagePlaceholder";
export default function Page() {
  return <ImagePlaceholder aspectClassName="aspect-video" />;
}
""",
            encoding="utf-8",
        )
        slots = _scan_placeholder_slots(site)
        matches = list(_iter_image_placeholder_matches(site))
        assert len(slots) == 1
        assert len(matches) == 1
        assert slots[0]["description"] == "image"
