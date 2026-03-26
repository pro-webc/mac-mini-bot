"""起動時検証ロジック"""
import config.config as cfg
from config.validation import validate_startup_config


def test_validation_does_not_require_text_llm(monkeypatch) -> None:
    r = validate_startup_config(require_full_pipeline=False)
    assert r.ok
    assert not any("テキスト LLM" in e for e in r.errors)


def test_validation_full_pipeline_requires_sheet_and_tokens(monkeypatch) -> None:
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_SPREADSHEET_ID", "")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_AUTH_MODE", "service_account")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_CREDENTIALS_PATH", "/nonexistent/creds.json")
    monkeypatch.setattr(cfg, "GITHUB_TOKEN", "")
    monkeypatch.setattr(cfg, "VERCEL_TOKEN", "")
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "manus_ok")
    r = validate_startup_config(require_full_pipeline=True)
    assert not r.ok
    assert any("SPREADSHEET" in e for e in r.errors)
    assert any("GITHUB_TOKEN" in e for e in r.errors)
    assert any("VERCEL_TOKEN" in e for e in r.errors)


def test_validation_refactor_without_manual_warns(monkeypatch) -> None:
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_SPREADSHEET_ID", "sheet_ok")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_AUTH_MODE", "application_default")
    monkeypatch.setattr(cfg, "GOOGLE_CLOUD_PROJECT", "test-gcp-project")
    monkeypatch.setattr(cfg, "GITHUB_TOKEN", "tok")
    monkeypatch.setattr(cfg, "VERCEL_TOKEN", "vtok")
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "m")
    monkeypatch.setattr(cfg, "BASIC_LP_REFACTOR_AFTER_MANUAL", True)
    monkeypatch.setattr(cfg, "BASIC_LP_USE_CLAUDE_MANUAL", False)
    r = validate_startup_config(require_full_pipeline=True)
    assert r.ok
    assert any("リファクタ" in w for w in r.warnings)


def test_validation_full_pipeline_requires_claude_cli(monkeypatch) -> None:
    import config.validation as val_mod
    _orig_which = val_mod.shutil.which
    monkeypatch.setattr(val_mod.shutil, "which", lambda cmd: None if cmd == "claude" else _orig_which(cmd))
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_SPREADSHEET_ID", "sheet_ok")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_AUTH_MODE", "application_default")
    monkeypatch.setattr(cfg, "GOOGLE_CLOUD_PROJECT", "test-gcp-project")
    monkeypatch.setattr(cfg, "GITHUB_TOKEN", "tok")
    monkeypatch.setattr(cfg, "VERCEL_TOKEN", "vtok")
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "m")
    r = validate_startup_config(require_full_pipeline=True)
    assert not r.ok
    assert any("claude CLI" in e for e in r.errors)


def test_validation_full_pipeline_requires_manus_when_refactor_enabled(monkeypatch) -> None:
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_SPREADSHEET_ID", "sheet_ok")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_AUTH_MODE", "application_default")
    monkeypatch.setattr(cfg, "GOOGLE_CLOUD_PROJECT", "test-gcp-project")
    monkeypatch.setattr(cfg, "GITHUB_TOKEN", "tok")
    monkeypatch.setattr(cfg, "VERCEL_TOKEN", "vtok")
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "")
    monkeypatch.setattr(cfg, "BASIC_LP_USE_CLAUDE_MANUAL", True)
    monkeypatch.setattr(cfg, "BASIC_LP_REFACTOR_AFTER_MANUAL", True)
    r = validate_startup_config(require_full_pipeline=True)
    assert not r.ok
    assert any("MANUS_API_KEY" in e for e in r.errors)


def test_validation_application_default_skips_credential_file(monkeypatch) -> None:
    """JSON パスが無くても application_default + GOOGLE_CLOUD_PROJECT なら起動検証は通る"""
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_SPREADSHEET_ID", "sheet_id_ok")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_AUTH_MODE", "application_default")
    monkeypatch.setattr(cfg, "GOOGLE_CLOUD_PROJECT", "test-gcp-project")
    monkeypatch.setattr(cfg, "GOOGLE_SHEETS_CREDENTIALS_PATH", "/nonexistent/creds.json")
    monkeypatch.setattr(cfg, "GITHUB_TOKEN", "tok")
    monkeypatch.setattr(cfg, "VERCEL_TOKEN", "vtok")
    monkeypatch.setattr(cfg, "MANUS_API_KEY", "m")
    r = validate_startup_config(require_full_pipeline=True)
    assert r.ok
    assert not any("Google 認証ファイル" in e for e in r.errors)
