"""契約分岐ごとの生成マークダウン適用キー"""
from pathlib import Path

from modules.basic_lp_generated_apply import apply_contract_outputs_to_site_dir
from modules.contract_workflow import ContractWorkBranch


def test_apply_basic_branch_uses_basic_keys(tmp_path: Path) -> None:
    site = tmp_path / "s"
    site.mkdir()
    spec = {
        "basic_refactored_source_markdown": """```tsx
app/page.tsx
export default function Page() { return null; }
```
"""
    }
    n = apply_contract_outputs_to_site_dir(
        spec, site, work_branch=ContractWorkBranch.BASIC
    )
    assert n == 1


def test_apply_standard_uses_standard_keys(tmp_path: Path) -> None:
    site = tmp_path / "s"
    site.mkdir()
    spec = {
        "standard_manual_gemini_final": """```tsx
app/page.tsx
export default function Page() { return null; }
```
"""
    }
    n = apply_contract_outputs_to_site_dir(
        spec, site, work_branch=ContractWorkBranch.STANDARD
    )
    assert n == 1


def test_apply_advance_uses_advance_keys(tmp_path: Path) -> None:
    site = tmp_path / "s"
    site.mkdir()
    spec = {
        "advance_manual_gemini_final": """```tsx
app/page.tsx
export default function Page() { return null; }
```
"""
    }
    n = apply_contract_outputs_to_site_dir(
        spec, site, work_branch=ContractWorkBranch.ADVANCE
    )
    assert n == 1


def test_fallthrough_when_first_key_has_no_fences(tmp_path: Path) -> None:
    """Manus が中断メッセージだけ返した場合、2番目のキー(Gemini出力)にフォールスルーする。"""
    site = tmp_path / "s"
    site.mkdir()
    spec = {
        "basic_lp_refactored_source_markdown": (
            "承知しました。リポジトリは既に存在しています。作業を終了します。"
        ),
        "basic_lp_manual_gemini_final": """```tsx
app/page.tsx
export default function Page() { return null; }
```
""",
    }
    n = apply_contract_outputs_to_site_dir(
        spec, site, work_branch=ContractWorkBranch.BASIC_LP
    )
    assert n == 1
    assert (site / "app" / "page.tsx").is_file()


def test_fallthrough_all_branches(tmp_path: Path) -> None:
    """全プラン分岐で同じフォールスルーが機能する。"""
    branches_and_keys = [
        (ContractWorkBranch.BASIC_LP, "basic_lp_refactored_source_markdown", "basic_lp_manual_gemini_final"),
        (ContractWorkBranch.BASIC, "basic_refactored_source_markdown", "basic_manual_gemini_final"),
        (ContractWorkBranch.STANDARD, "standard_refactored_source_markdown", "standard_manual_gemini_final"),
        (ContractWorkBranch.ADVANCE, "advance_refactored_source_markdown", "advance_manual_gemini_final"),
    ]
    fence_md = """```tsx
app/page.tsx
export default function Page() { return null; }
```
"""
    for branch, refactor_key, final_key in branches_and_keys:
        site = tmp_path / branch.value
        site.mkdir()
        spec = {
            refactor_key: "フェンスなしの中断テキスト",
            final_key: fence_md,
        }
        n = apply_contract_outputs_to_site_dir(spec, site, work_branch=branch)
        assert n == 1, f"{branch.value}: expected 1 file, got {n}"
        assert (site / "app" / "page.tsx").is_file(), f"{branch.value}: page.tsx missing"


def test_apply_standard_wrong_keys_returns_zero(tmp_path: Path) -> None:
    site = tmp_path / "s"
    site.mkdir()
    assert (
        apply_contract_outputs_to_site_dir(
            {"basic_manual_gemini_final": "x"},
            site,
            work_branch=ContractWorkBranch.STANDARD,
        )
        == 0
    )
