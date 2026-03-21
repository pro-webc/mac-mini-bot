"""Next.js テンプレートの ImagePlaceholder 下限（実装プロンプトとの整合）"""

from pathlib import Path

from modules.site_implementer import count_image_placeholder_tags


def test_nextjs_template_has_minimum_image_placeholders() -> None:
    root = Path(__file__).resolve().parents[1] / "templates" / "nextjs_template"
    assert count_image_placeholder_tags(root) >= 3
