#!/usr/bin/env python3
"""
要望抽出（第1段）+ 仕様書（第2段）のスモーク。各 TEXT_LLM 1 回（.env 必須）

  cd mac-mini-bot && .venv/bin/python scripts/run_extraction_and_spec_smoke.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from modules.requirement_extractor import RequirementExtractor
from modules.spec_generator import SpecGenerator


def main() -> None:
    hearing = """【テスト用ヒアリング】
屋号: サンプル水道サービス
事業: 地域密着の給排水・漏水調査
強み: 即日対応、見積明瞭
ターゲット: 戸建て・小規模事業所オーナー
"""
    appo = "アポメモ: デモサイトは写真はプレースホルダで可。電話CTA重視。"
    sales = "営業共有: 既存Webなし。STANDARDプラン想定。"
    contract_plan = "STANDARD"
    partner = "テストパートナー株式会社"

    ext = RequirementExtractor()
    gen = SpecGenerator()
    print("=== 1. extract_requirements（第1段）===\n", flush=True)
    req = ext.extract_requirements(hearing, appo, sales, contract_plan)
    print(json.dumps(req, ensure_ascii=False, indent=2), flush=True)

    print("\n=== 2. generate_spec（第2段・技術ルール込み）===\n", flush=True)
    spec = gen.generate_spec(hearing, req, contract_plan, partner)

    spec_str = json.dumps(spec, ensure_ascii=False, indent=2)
    out_dir = ROOT / "output" / "smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "extraction_and_spec_full.json"
    payload = {
        "requirements_result": req,
        "spec": spec,
    }
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(spec_str, flush=True)
    print(f"\n=== 全文も保存: {out_path} ===", flush=True)

    print("\n=== done ===", flush=True)


if __name__ == "__main__":
    main()
