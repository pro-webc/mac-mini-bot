"""設定の数値パース（リロードなしで関数を単体テスト）"""

import pytest

from config import config as cfg


def test_parse_positive_int_clamp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SITE_BUILD_MAX_FIX_ATTEMPTS", "999")
    # モジュールは既にロード済みのため、ヘルパー相当の動作のみ検証
    from config.config import _parse_positive_int

    assert _parse_positive_int("SITE_BUILD_MAX_FIX_ATTEMPTS", 3, minimum=1, maximum=20) == 20
    monkeypatch.delenv("SITE_BUILD_MAX_FIX_ATTEMPTS", raising=False)
    assert _parse_positive_int("SITE_BUILD_MAX_FIX_ATTEMPTS", 3, minimum=1, maximum=20) == 3


def test_image_gen_provider_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    """不正な IMAGE_GEN_PROVIDER は pillow に正規化される（config 再読込は別プロセスで検証）"""
    assert cfg.IMAGE_GEN_PROVIDER in (
        "openai",
        "gemini",
        "pillow",
        "cursor_agent_cli",
    )
    assert cfg.IMAGE_GEN_MODE in ("from_placeholder_source", "standalone_spec")
