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
