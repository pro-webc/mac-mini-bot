"""BRANCH_REGISTRY の一貫性テスト。

新プラン追加時にレジストリの必須フィールド漏れ・spec キー重複を検出する。
"""
from __future__ import annotations

import importlib

from modules.contract_workflow import (
    BRANCH_REGISTRY,
    ContractWorkBranch,
    claude_manual_enabled_for_branch,
)


def test_all_branches_registered() -> None:
    """ContractWorkBranch の全メンバーが BRANCH_REGISTRY に存在する。"""
    for branch in ContractWorkBranch:
        assert branch in BRANCH_REGISTRY, f"{branch} が BRANCH_REGISTRY にない"


def test_registry_keys_are_non_empty_strings() -> None:
    for branch, cfg in BRANCH_REGISTRY.items():
        assert cfg.refactor_key, f"{branch}: refactor_key が空"
        assert cfg.canvas_key, f"{branch}: canvas_key が空"
        assert cfg.manual_meta_key, f"{branch}: manual_meta_key が空"
        assert cfg.use_claude_flag, f"{branch}: use_claude_flag が空"
        assert cfg.refactor_flag, f"{branch}: refactor_flag が空"
        assert cfg.plan_label, f"{branch}: plan_label が空"


def test_manus_keys_match_refactor_and_canvas() -> None:
    for branch, cfg in BRANCH_REGISTRY.items():
        assert cfg.manus_keys == (cfg.refactor_key, cfg.canvas_key), (
            f"{branch}: manus_keys が (refactor_key, canvas_key) と一致しない"
        )


def test_spec_llm_keys_contain_manus_deploy() -> None:
    for branch, cfg in BRANCH_REGISTRY.items():
        assert "manus_deploy_github_url" in cfg.spec_llm_keys, (
            f"{branch}: spec_llm_keys に manus_deploy_github_url がない"
        )


def test_no_duplicate_manual_meta_keys() -> None:
    meta_keys = [cfg.manual_meta_key for cfg in BRANCH_REGISTRY.values()]
    assert len(meta_keys) == len(set(meta_keys)), (
        f"manual_meta_key に重複がある: {meta_keys}"
    )


def test_no_duplicate_refactor_keys() -> None:
    refactor_keys = [cfg.refactor_key for cfg in BRANCH_REGISTRY.values()]
    assert len(refactor_keys) == len(set(refactor_keys))


def test_config_flag_attrs_exist() -> None:
    """use_claude_flag / refactor_flag が config.config に実在する。"""
    import config.config as cfg_mod

    for branch, bc in BRANCH_REGISTRY.items():
        assert hasattr(cfg_mod, bc.use_claude_flag), (
            f"{branch}: config.config に {bc.use_claude_flag} がない"
        )
        assert hasattr(cfg_mod, bc.refactor_flag), (
            f"{branch}: config.config に {bc.refactor_flag} がない"
        )


def test_pipeline_module_importable() -> None:
    """pipeline_module / pipeline_function が実在する。"""
    for branch, cfg in BRANCH_REGISTRY.items():
        mod = importlib.import_module(cfg.pipeline_module)
        fn = getattr(mod, cfg.pipeline_function, None)
        assert fn is not None, (
            f"{branch}: {cfg.pipeline_module}.{cfg.pipeline_function} が見つからない"
        )
        assert callable(fn)


def test_claude_manual_enabled_uses_registry(monkeypatch) -> None:
    """claude_manual_enabled_for_branch がレジストリ経由で正しいフラグを読む。"""
    import config.config as cfg_mod

    for branch, bc in BRANCH_REGISTRY.items():
        monkeypatch.setattr(cfg_mod, bc.use_claude_flag, True)
        assert claude_manual_enabled_for_branch(branch) is True
        monkeypatch.setattr(cfg_mod, bc.use_claude_flag, False)
        assert claude_manual_enabled_for_branch(branch) is False
