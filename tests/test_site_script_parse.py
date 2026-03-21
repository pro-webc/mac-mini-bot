"""サイト台本 + 末尾 YAML のパース"""
from modules.site_script_parse import extract_last_yaml_fence, parse_llm_spec_or_site_script


def test_extract_last_yaml_fence_strips_trailing_block() -> None:
    text = """# ヒーロー
こんにちは

```yaml
site_overview:
  site_name: "テスト株式会社"
design_spec:
  color_scheme:
    primary: "#111111"
```
"""
    body, meta = extract_last_yaml_fence(text)
    assert meta is not None
    assert meta["site_overview"]["site_name"] == "テスト株式会社"
    assert "ヒーロー" in body
    assert "```yaml" not in body


def test_parse_site_script_mode() -> None:
    filler = "顧客向けの完成文案として十分な長さのダミー本文。" * 3
    raw = (
        "# トップ\n\n## サービス\n"
        + filler
        + "\n\n```yaml\n"
        + """
site_overview:
  site_name: "ACME"
  purpose: "テスト"
design_spec:
  color_scheme:
    background: "#fff"
    primary: "#000"
ux_spec:
  primary_conversion: { label: "相談", action: "contact" }
function_spec: {}
image_placeholder_slots:
  - { page_path: "/", section_id: "a", description: "x", aspect_hint: "1:1" }
  - { page_path: "/", section_id: "b", description: "y", aspect_hint: "1:1" }
  - { page_path: "/", section_id: "c", description: "z", aspect_hint: "1:1" }
"""
        + "```\n"
    )
    spec, mode = parse_llm_spec_or_site_script(raw)
    assert mode == "site_script"
    assert "サービス" in spec["site_script_md"]
    assert spec["site_overview"]["site_name"] == "ACME"
    assert spec["design_spec"]["color_scheme"]["primary"] == "#000"


def test_parse_legacy_json() -> None:
    raw = """{"site_overview": {"site_name": "Legacy"}, "page_structure": [], "design_spec": {"color_scheme": {"primary": "#fff"}}}"""
    spec, mode = parse_llm_spec_or_site_script(raw)
    assert mode == "legacy_json"
    assert spec["site_overview"]["site_name"] == "Legacy"
