"""設定の数値パース（リロードなしで関数を単体テスト）"""

import pytest


def test_parse_positive_int_clamp(monkeypatch: pytest.MonkeyPatch) -> None:
    key = "_PYTEST_PARSE_POSITIVE_INT_CLAMP"
    monkeypatch.setenv(key, "999")
    # モジュールは既にロード済みのため、ヘルパー相当の動作のみ検証
    from config.config import _parse_positive_int

    assert _parse_positive_int(key, 3, minimum=1, maximum=20) == 20
    monkeypatch.delenv(key, raising=False)
    assert _parse_positive_int(key, 3, minimum=1, maximum=20) == 3
