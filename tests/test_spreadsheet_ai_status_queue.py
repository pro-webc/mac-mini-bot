"""AV 列のキュー除外判定（表記ゆれ）"""

from __future__ import annotations

from modules.spreadsheet import ai_cell_excludes_from_pending_queue


def test_queue_excludes_exact_complete_and_processing() -> None:
    assert ai_cell_excludes_from_pending_queue("完了")
    assert ai_cell_excludes_from_pending_queue("処理中")


def test_queue_excludes_complete_with_trailing_punctuation() -> None:
    assert ai_cell_excludes_from_pending_queue("完了！")
    assert ai_cell_excludes_from_pending_queue("完了。")
    assert ai_cell_excludes_from_pending_queue("  完了。  ")


def test_queue_excludes_error_and_skip_prefix() -> None:
    assert ai_cell_excludes_from_pending_queue("エラー: 失敗")
    assert ai_cell_excludes_from_pending_queue("スキップ: 理由")


def test_queue_includes_empty_and_non_terminal() -> None:
    assert not ai_cell_excludes_from_pending_queue("")
    assert not ai_cell_excludes_from_pending_queue("   ")
    assert not ai_cell_excludes_from_pending_queue("デモサイト制作中")
