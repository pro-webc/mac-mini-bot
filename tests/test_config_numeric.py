"""設定の数値パース（リロードなしで関数を単体テスト）"""

import pytest


def test_parse_positive_int_clamp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SITE_BUILD_MAX_FIX_ATTEMPTS", "999")
    # モジュールは既にロード済みのため、ヘルパー相当の動作のみ検証
    from config.config import _parse_positive_int

    assert _parse_positive_int("SITE_BUILD_MAX_FIX_ATTEMPTS", 3, minimum=1, maximum=20) == 20
    monkeypatch.delenv("SITE_BUILD_MAX_FIX_ATTEMPTS", raising=False)
    assert _parse_positive_int("SITE_BUILD_MAX_FIX_ATTEMPTS", 3, minimum=1, maximum=20) == 3
