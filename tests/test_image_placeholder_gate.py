"""ImagePlaceholder 出現数カウントのスモークテスト（テンプレ依存なし）"""

from pathlib import Path

from modules.site_implementer import count_image_placeholder_tags


def test_count_image_placeholder_tags_in_tree(tmp_path: Path) -> None:
    p = tmp_path / "app" / "page.tsx"
    p.parent.mkdir(parents=True)
    p.write_text(
        """
import ImagePlaceholder from "@/components/ImagePlaceholder";
export default function P() {
  return (
    <>
      <ImagePlaceholder description="a" />
      <ImagePlaceholder description="b" />
      <ImagePlaceholder description="c" />
    </>
  );
}
""",
        encoding="utf-8",
    )
    assert count_image_placeholder_tags(tmp_path) == 3
