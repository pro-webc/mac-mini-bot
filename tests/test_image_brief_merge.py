"""画像パイプライン: brief マージと第2段 image_placeholder_slots 連携"""
import json
from pathlib import Path

from modules.image_generator import (
    _brief_from_spec,
    _brief_to_style_prefix,
    _load_image_pipeline_context,
    _merge_visual_style_brief,
)


def test_brief_from_spec_uses_layout_mood_and_slots() -> None:
    spec = {
        "site_overview": {"site_name": "ACME", "purpose": "テスト目的"},
        "design_spec": {
            "layout_mood": "余白多め",
            "color_scheme": {"primary": "#0f766e"},
        },
        "image_placeholder_slots": [
            {"page_path": "/", "section_id": "h", "description": "オフィス全景"},
        ],
    }
    b = _brief_from_spec(spec)
    assert b["layout_mood"] == "余白多め"
    assert b["reference_slot_descriptions"] == ["オフィス全景"]
    style = _brief_to_style_prefix(b)
    assert "オフィス全景" in style
    assert "余白多め" in style


def test_load_image_pipeline_context(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    payload = {
        "version": 1,
        "site_overview": {"site_name": "X"},
        "design_spec": {"color_scheme": {"primary": "#111"}},
    }
    (docs / "image_pipeline_context.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    loaded = _load_image_pipeline_context(tmp_path)
    assert loaded["site_overview"]["site_name"] == "X"


def test_merge_visual_style_brief_disk_wins() -> None:
    spec = {
        "site_overview": {"site_name": "S", "purpose": "p"},
        "design_spec": {"layout_mood": "from_spec", "color_scheme": {"primary": "#111"}},
    }
    disk = {"layout_mood": "from_disk", "color_scheme": {"primary": "#222"}}
    m = _merge_visual_style_brief(disk, spec)
    assert m["layout_mood"] == "from_disk"
    assert m["color_scheme"]["primary"] == "#222"
