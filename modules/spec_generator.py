"""仕様書生成モジュール"""
import json
import logging
import re
from typing import Dict, List, Optional

import requests
from config.config import (
    get_common_technical_spec,
    get_common_technical_spec_prompt_block,
)
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)


class SpecGenerator:
    """ヒアリングシート、要望、契約プランから仕様書を生成"""
    
    def __init__(self):
        if not is_text_llm_configured():
            raise ValueError(
                "テキスト LLM が未設定です。"
                "TEXT_LLM_PROVIDER=cursor_agent_cli または claude_code_cli と、"
                "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND を設定してください。"
            )

    def _llm(self, prompt: str, system: str, temperature: float = 0.3) -> str:
        return text_llm_complete(user=prompt, system=system, temperature=temperature)
    
    def _merge_common_technical_spec(self, extra: Optional[Dict] = None) -> Dict:
        """全プラン共通の技術要件を technical_spec に統合（スタックと共通要件は常に上書き固定）"""
        merged: Dict = {}
        if extra:
            merged.update(extra)
        merged["tech_stack"] = [
            "Next.js (App Router)",
            "React",
            "TypeScript",
            "Tailwind CSS",
        ]
        merged["common_requirements"] = get_common_technical_spec()
        return merged
    
    def _apply_common_technical_to_spec(self, spec: Dict) -> Dict:
        """LLM出力の仕様書に共通技術要件をマージ"""
        ts = spec.get("technical_spec")
        if isinstance(ts, dict):
            spec["technical_spec"] = self._merge_common_technical_spec(ts)
        else:
            spec["technical_spec"] = self._merge_common_technical_spec()
        return spec
    
    def fetch_hearing_sheet(self, url: str) -> Optional[str]:
        """
        ヒアリングシートの内容を取得
        
        Args:
            url: ヒアリングシートURL
            
        Returns:
            ヒアリングシートの内容（テキスト）
        """
        try:
            raw = (url or "").strip()
            if not raw:
                return None
            # セルに全文が貼られているだけの場合（http で始まらない）
            if not re.match(r"^https?://", raw, re.IGNORECASE):
                m = re.search(r"https?://[^\s\]<>\")]+", raw)
                if m:
                    return self.fetch_hearing_sheet(m.group(0))
                logger.info(
                    "ヒアリングシート列が URL ではないため、本文としてそのまま使用します（先頭 %s 文字）",
                    min(len(raw), 200),
                )
                return raw

            # Google Sheets URLの場合
            if "docs.google.com/spreadsheets" in raw:
                # 簡易的な取得（実際はGoogle Sheets APIを使用）
                response = requests.get(raw, timeout=60)
                if response.status_code == 200:
                    # HTMLからテキストを抽出（簡易版）
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text()
                    logger.info("ヒアリングシートを取得しました")
                    return text
            else:
                # その他のURL
                response = requests.get(raw, timeout=60)
                if response.status_code == 200:
                    return response.text
            
            return None
        except Exception as e:
            logger.error(f"ヒアリングシート取得エラー: {e}")
            return None
    
    def generate_spec(
        self,
        hearing_sheet_content: str,
        requirements_result: Dict,
        contract_plan: str,
        partner_name: str
    ) -> Dict:
        """
        仕様書を生成
        
        Args:
            hearing_sheet_content: ヒアリングシートの内容
            requirements_result: 抽出された要望と分析結果（BASIC LPの場合は詳細情報を含む）
            contract_plan: 契約プラン
            partner_name: パートナー名
            
        Returns:
            仕様書（辞書形式）
        """
        # BASIC LPプランの場合
        if requirements_result.get("plan_type") == "basic_lp":
            return self._generate_basic_lp_spec(requirements_result, contract_plan, partner_name)
        
        # BASICプラン（1ページコーポレートサイト）の場合
        if requirements_result.get("plan_type") == "basic":
            return self._generate_basic_spec(requirements_result, contract_plan, partner_name)
        
        # STANDARD / ADVANCE（複数ページ）の場合
        if requirements_result.get("plan_type") in ("standard", "advance"):
            return self._generate_multi_page_spec(requirements_result, contract_plan, partner_name)
        
        # その他のプランの場合
        requirements = requirements_result.get("requirements", {})
        requirements_text = self._format_requirements(requirements)
        
        prompt = f"""
以下の情報から、Webサイトの詳細な仕様書を作成してください。

【パートナー名】
{partner_name}

【契約プラン】
{contract_plan}

【ヒアリングシート内容】
{hearing_sheet_content}

【抽出された要望】
{requirements_text}

以下の項目を含む詳細な仕様書をJSON形式で作成してください：

1. サイト概要
   - サイト名
   - 目的
   - ターゲットユーザー

2. デザイン仕様
   - カラースキーム（ベースカラー、メインカラー、アクセントカラー）
   - タイポグラフィ（フォント、サイズ）
   - レイアウトスタイル
   - レスポンシブ対応

3. ページ構成
   - 各ページのURL、タイトル、説明
   - ページ階層

4. 機能仕様
   - 各機能の詳細説明
   - 実装方法

5. コンテンツ仕様
   - 各セクションの内容
   - 画像要件
   - テキスト要件

6. 技術仕様
   - 使用技術スタック
   - パフォーマンス要件
   - SEO要件

{get_common_technical_spec_prompt_block()}

JSON形式で出力してください。
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはWebサイトの仕様書を作成する専門家です。",
                0.3,
            )
            
            # JSONをパース
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                spec = json.loads(json_match.group())
                spec = self._apply_common_technical_to_spec(spec)
            else:
                # フォールバック: 基本的な仕様書構造を返す
                spec = self._create_default_spec(partner_name, contract_plan, requirements_text)
            
            logger.info("仕様書の生成が完了しました")
            return spec
            
        except Exception as e:
            logger.error(f"仕様書生成エラー: {e}")
            # エラー時はデフォルト仕様書を返す
            return self._create_default_spec(partner_name, contract_plan, requirements_text)
    
    def _format_requirements(self, requirements: Dict[str, list]) -> str:
        """要望をテキスト形式にフォーマット"""
        text = ""
        category_names = {
            "design_requirements": "デザイン要望",
            "function_requirements": "機能要望",
            "content_requirements": "コンテンツ要望",
            "technical_requirements": "技術要望",
            "other_requirements": "その他要望"
        }
        
        for category, items in requirements.items():
            if items:
                text += f"\n【{category_names.get(category, category)}】\n"
                for item in items:
                    text += f"- {item}\n"
        
        return text
    
    def _create_default_spec(
        self,
        partner_name: str,
        contract_plan: str,
        requirements_text: str
    ) -> Dict:
        """デフォルト仕様書を作成"""
        return {
            "site_overview": {
                "site_name": f"{partner_name} 公式サイト",
                "purpose": "企業情報の提供とお問い合わせ",
                "target_users": "一般ユーザー"
            },
            "design_spec": {
                "color_scheme": {
                    "base_color": "#FFFFFF",
                    "main_color": "#333333",
                    "accent_color": "#0066CC"
                },
                "typography": {
                    "font_family": "Noto Sans JP, sans-serif",
                    "base_size": "16px"
                },
                "layout_style": "モダンでクリーン",
                "responsive": True
            },
            "page_structure": [
                {
                    "url": "/",
                    "title": "トップページ",
                    "description": "メインビジュアル、サービス紹介、お問い合わせ"
                }
            ],
            "function_spec": [],
            "content_spec": {
                "sections": [],
                "image_requirements": [],
                "text_requirements": []
            },
            "technical_spec": self._merge_common_technical_spec(
                {
                    "performance": "Lighthouse 90点以上",
                    "seo": "基本的なSEO対策を実装",
                }
            ),
        }
    
    def _generate_basic_lp_spec(
        self,
        requirements_result: Dict,
        contract_plan: str,
        partner_name: str
    ) -> Dict:
        """BASIC LPプラン用の仕様書を生成"""
        extracted_info = requirements_result.get("extracted_info", {})
        analysis = requirements_result.get("analysis", {})
        wireframe = requirements_result.get("wireframe", {})
        lp_content = requirements_result.get("lp_content", {})
        
        # デザイン要件を定義
        design_requirements = self._define_design_requirements(
            extracted_info,
            analysis,
            requirements_result
        )
        
        # 仕様書を構築
        spec = {
            "site_overview": {
                "site_name": extracted_info.get("company_info", {}).get("service_name", f"{partner_name} LP"),
                "purpose": "ランディングページによるコンバージョン獲得",
                "target_users": analysis.get("target_analysis", {}).get("core_target", ""),
                "plan_type": "basic_lp"
            },
            "design_spec": design_requirements,
            "page_structure": [
                {
                    "url": "/",
                    "title": "ランディングページ",
                    "description": "1ページ完結型のLP",
                    "sections": wireframe.get("sections", [])
                }
            ],
            "function_spec": {
                "contact_form": lp_content.get("form", {}),
                "cta_buttons": self._extract_cta_buttons(lp_content)
            },
            "content_spec": {
                "sections": lp_content.get("sections", []),
                "image_requirements": self._extract_image_requirements(lp_content),
                "text_requirements": self._extract_text_requirements(lp_content)
            },
            "technical_spec": self._merge_common_technical_spec(
                {
                    "performance": "Lighthouse 90点以上",
                    "seo": "基本的なSEO対策を実装",
                    "conversion_tracking": "コンバージョン計測の実装",
                }
            ),
            "analysis": analysis,
            "extracted_info": extracted_info,
            "wireframe": wireframe,
            "lp_content": lp_content
        }
        
        logger.info("BASIC LP仕様書の生成が完了しました")
        return spec
    
    def _define_design_requirements(
        self,
        extracted_info: Dict,
        analysis: Dict,
        requirements_result: Dict
    ) -> Dict:
        """デザイン要件を定義"""
        prompt = f"""
以下の情報から、LPのデザイン要件を定義してください。

【抽出された情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

【分析結果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

これまでの情報整理やヒアリングシート等の要望から、以下のデザイン要件を定義してください：

1. カラースキーム（ベースカラー、メインカラー、アクセントカラー）
2. タイポグラフィ（フォント、サイズ）
3. レイアウトスタイル
4. レスポンシブ対応
5. 画像・イラストのスタイル
6. CTAボタンのデザイン

{get_common_technical_spec_prompt_block()}

JSON形式で出力してください：
{{
  "color_scheme": {{
    "base_color": "#FFFFFF",
    "main_color": "#333333",
    "accent_color": "#0066CC"
  }},
  "typography": {{
    "font_family": "Noto Sans JP, sans-serif",
    "base_size": "16px",
    "heading_sizes": {{
      "h1": "2.5rem",
      "h2": "2rem",
      "h3": "1.5rem"
    }}
  }},
  "layout_style": "モダンでクリーン",
  "responsive": true,
  "image_style": "画像スタイルの説明",
  "cta_button_style": "CTAボタンのデザイン説明"
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはLPデザインの専門家です。",
                0.3,
            )
            
            # JSONをパース
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                design_requirements = json.loads(json_match.group())
            else:
                design_requirements = {
                    "color_scheme": {
                        "base_color": "#FFFFFF",
                        "main_color": "#333333",
                        "accent_color": "#0066CC"
                    },
                    "typography": {
                        "font_family": "Noto Sans JP, sans-serif",
                        "base_size": "16px"
                    },
                    "layout_style": "モダンでクリーン",
                    "responsive": True
                }
            
            return design_requirements
            
        except Exception as e:
            logger.error(f"デザイン要件定義エラー: {e}")
            return {
                "color_scheme": {
                    "base_color": "#FFFFFF",
                    "main_color": "#333333",
                    "accent_color": "#0066CC"
                },
                "typography": {
                    "font_family": "Noto Sans JP, sans-serif",
                    "base_size": "16px"
                },
                "layout_style": "モダンでクリーン",
                "responsive": True
            }
    
    def _extract_cta_buttons(self, lp_content: Dict) -> List[Dict]:
        """CTAボタンを抽出"""
        cta_buttons = []
        for section in lp_content.get("sections", []):
            if section.get("content", {}).get("cta"):
                cta_buttons.append(section["content"]["cta"])
        return cta_buttons
    
    def _extract_image_requirements(self, lp_content: Dict) -> List[Dict]:
        """画像要件を抽出"""
        image_requirements = []
        for section in lp_content.get("sections", []):
            images = section.get("content", {}).get("images", [])
            image_requirements.extend(images)
        return image_requirements
    
    def _extract_text_requirements(self, lp_content: Dict) -> List[str]:
        """テキスト要件を抽出"""
        text_requirements = []
        for section in lp_content.get("sections", []):
            text = section.get("content", {}).get("text", "")
            if text:
                text_requirements.append(text)
        return text_requirements
    
    def _generate_basic_spec(
        self,
        requirements_result: Dict,
        contract_plan: str,
        partner_name: str
    ) -> Dict:
        """BASICプラン（1ページコーポレートサイト）用の仕様書を生成"""
        extracted_info = requirements_result.get("extracted_info", {})
        site_structure = requirements_result.get("site_structure", {})
        site_content = requirements_result.get("site_content", {})
        
        # デザイン要件を定義
        design_requirements = self._define_basic_design_requirements(
            extracted_info,
            requirements_result
        )
        
        # 仕様書を構築
        spec = {
            "site_overview": {
                "site_name": extracted_info.get("company_info", {}).get("service_name", f"{partner_name} 公式サイト"),
                "purpose": extracted_info.get("site_purpose", {}).get("purpose", "企業情報の提供とお問い合わせ"),
                "target_users": extracted_info.get("target_persona", {}).get("target", ""),
                "plan_type": "basic",
                "pages": 1
            },
            "design_spec": design_requirements,
            "page_structure": [
                {
                    "url": "/",
                    "title": "トップページ",
                    "description": "1ページ完結型のコーポレートサイト",
                    "sections": site_structure.get("sections", [])
                }
            ],
            "function_spec": {
                "contact_form": site_content.get("form", {}),
                "cta_buttons": self._extract_basic_cta_buttons(site_content),
                "service_tabs": self._check_service_tabs(extracted_info)
            },
            "content_spec": {
                "sections": site_content.get("sections", []),
                "image_requirements": self._extract_basic_image_requirements(site_content),
                "text_requirements": self._extract_basic_text_requirements(site_content),
                "services": extracted_info.get("what", {}).get("services", [])
            },
            "technical_spec": self._merge_common_technical_spec(
                {
                    "performance": "Lighthouse 90点以上",
                    "seo": "基本的なSEO対策を実装",
                }
            ),
            "extracted_info": extracted_info,
            "site_structure": site_structure,
            "site_content": site_content
        }
        
        logger.info("BASIC仕様書の生成が完了しました")
        return spec
    
    def _define_basic_design_requirements(
        self,
        extracted_info: Dict,
        requirements_result: Dict
    ) -> Dict:
        """BASICプランのデザイン要件を定義"""
        prompt = f"""
以下の情報から、1ページコーポレートサイトのデザイン要件を定義してください。

【抽出された情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

スプレッドシートの情報からデザインを考え、以下のデザイン要件を定義してください：

1. カラースキーム（ベースカラー、メインカラー、アクセントカラー）
2. タイポグラフィ（フォント、サイズ）
3. レイアウトスタイル
4. レスポンシブ対応
5. 画像・イラストのスタイル
6. CTAボタンのデザイン
7. サービスタブのデザイン（サービスが4つ以上ある場合）

{get_common_technical_spec_prompt_block()}

JSON形式で出力してください：
{{
  "color_scheme": {{
    "base_color": "#FFFFFF",
    "main_color": "#333333",
    "accent_color": "#0066CC"
  }},
  "typography": {{
    "font_family": "Noto Sans JP, sans-serif",
    "base_size": "16px",
    "heading_sizes": {{
      "h1": "2.5rem",
      "h2": "2rem",
      "h3": "1.5rem"
    }}
  }},
  "layout_style": "モダンでクリーン",
  "responsive": true,
  "image_style": "画像スタイルの説明",
  "cta_button_style": "CTAボタンのデザイン説明",
  "service_tab_style": "サービスタブのデザイン説明（該当する場合）"
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはコーポレートサイトデザインの専門家です。",
                0.3,
            )
            
            # JSONをパース
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                design_requirements = json.loads(json_match.group())
            else:
                design_requirements = {
                    "color_scheme": {
                        "base_color": "#FFFFFF",
                        "main_color": "#333333",
                        "accent_color": "#0066CC"
                    },
                    "typography": {
                        "font_family": "Noto Sans JP, sans-serif",
                        "base_size": "16px"
                    },
                    "layout_style": "モダンでクリーン",
                    "responsive": True
                }
            
            return design_requirements
            
        except Exception as e:
            logger.error(f"BASICデザイン要件定義エラー: {e}")
            return {
                "color_scheme": {
                    "base_color": "#FFFFFF",
                    "main_color": "#333333",
                    "accent_color": "#0066CC"
                },
                "typography": {
                    "font_family": "Noto Sans JP, sans-serif",
                    "base_size": "16px"
                },
                "layout_style": "モダンでクリーン",
                "responsive": True
            }
    
    def _extract_basic_cta_buttons(self, site_content: Dict) -> List[Dict]:
        """BASICサイトのCTAボタンを抽出"""
        cta_buttons = []
        for section in site_content.get("sections", []):
            if section.get("content", {}).get("cta"):
                cta_buttons.append(section["content"]["cta"])
        return cta_buttons
    
    def _check_service_tabs(self, extracted_info: Dict) -> bool:
        """サービスタブが必要かチェック（サービスが4つ以上ある場合）"""
        services = extracted_info.get("what", {}).get("services", [])
        return len(services) >= 4
    
    def _extract_basic_image_requirements(self, site_content: Dict) -> List[Dict]:
        """BASICサイトの画像要件を抽出"""
        image_requirements = []
        for section in site_content.get("sections", []):
            images = section.get("content", {}).get("images", [])
            image_requirements.extend(images)
        return image_requirements
    
    def _extract_basic_text_requirements(self, site_content: Dict) -> List[str]:
        """BASICサイトのテキスト要件を抽出"""
        text_requirements = []
        for section in site_content.get("sections", []):
            text = section.get("content", {}).get("text", "")
            if text:
                text_requirements.append(text)
        return text_requirements
    
    def _generate_multi_page_spec(
        self,
        requirements_result: Dict,
        contract_plan: str,
        partner_name: str
    ) -> Dict:
        """STANDARD / ADVANCE（複数ページ）の仕様書"""
        extracted_info = requirements_result.get("extracted_info", {})
        site_map = requirements_result.get("site_map", {})
        max_pages = requirements_result.get("max_pages", 6)
        plan_type = requirements_result.get("plan_type", "standard")
        
        design_spec = self._define_multi_page_design_requirements(
            extracted_info,
            site_map,
            contract_plan,
            partner_name,
        )
        
        page_structure = self._site_map_to_page_structure(site_map)
        
        spec = {
            "site_overview": {
                "site_name": extracted_info.get("company_info", {}).get(
                    "service_name",
                    f"{partner_name} 公式サイト",
                ),
                "purpose": extracted_info.get("site_purpose", {}).get(
                    "purpose",
                    "コーポレートサイト（複数ページ）",
                ),
                "target_users": extracted_info.get("target_persona", {}).get("target", ""),
                "plan_type": plan_type,
                "contract_plan": contract_plan,
                "max_pages": max_pages,
            },
            "design_spec": design_spec,
            "page_structure": page_structure,
            "information_architecture": site_map,
            "function_spec": {
                "contact_page_required": True,
                "company_page_required": True,
                "blog_page_policy": "不要ならサイトマップに含めない",
                "navigation_rules": {
                    "top_is_hub": True,
                    "no_orphan_subpages": True,
                    "no_same_page_only_cta": True,
                    "contact_section_on_non_contact_pages": True,
                },
            },
            "content_spec": {
                "extracted_hearing": extracted_info,
                "services": extracted_info.get("what", {}).get("services", []),
            },
            "technical_spec": self._merge_common_technical_spec(
                {
                    "performance": "Lighthouse 90点以上",
                    "seo": "各下層ページのメタ情報・構造化データを設計",
                }
            ),
        }
        logger.info("複数ページ仕様書の生成が完了しました（%s）", plan_type)
        return spec
    
    def _site_map_to_page_structure(self, site_map: Dict) -> List[Dict]:
        """サイトマップを page_structure 配列に変換"""
        out: List[Dict] = []
        top = site_map.get("top_page") or {}
        if top:
            out.append(
                {
                    "url": top.get("path", "/"),
                    "title": "TOP",
                    "description": top.get("purpose", "下層への目次・導線"),
                    "sections": top.get("sections", []),
                }
            )
        for p in site_map.get("subpages") or []:
            out.append(
                {
                    "url": p.get("path", ""),
                    "title": p.get("title", ""),
                    "description": p.get("role", ""),
                    "sections": p.get("sections", []),
                    "contact_cta_section": p.get("contact_cta_section", False),
                }
            )
        return out
    
    def _define_multi_page_design_requirements(
        self,
        extracted_info: Dict,
        site_map: Dict,
        contract_plan: str,
        partner_name: str,
    ) -> Dict:
        """スプレッドシート由来の整理情報とサイトマップからデザイン要件を定義"""
        prompt = f"""
以下の情報から、複数ページのコーポレートサイトのデザイン要件を定義してください。

【パートナー名】{partner_name}
【契約プラン】{contract_plan}

【ヒアリング整理データ】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

【サイトマップ・IA】
{json.dumps(site_map, ensure_ascii=False, indent=2)}

TOPは下層へのハブであること、サービスページはLP的なセクション構成になりうることを考慮し、
トーン＆マナー、カラー、タイポ、コンポーネント方針、画像の雰囲気、ボタン・カードの統一ルールをJSONで出力してください。

{get_common_technical_spec_prompt_block()}

JSON形式:
{{
  "color_scheme": {{"base_color": "", "main_color": "", "accent_color": ""}},
  "typography": {{"font_family": "", "base_size": "", "heading_policy": ""}},
  "layout_style": "",
  "responsive": true,
  "component_guidelines": {{
    "service_page_sections": "",
    "hub_top_sections": "",
    "navigation_buttons": ""
  }},
  "imagery_direction": ""
}}
"""
        try:
            result_text = self._llm(
                prompt,
                "あなたはコーポレートサイトのデザインシステム担当です。",
                0.3,
            )
            
            import re
            json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error("複数ページデザイン要件定義エラー: %s", e)
        
        return {
            "color_scheme": {
                "base_color": "#FFFFFF",
                "main_color": "#333333",
                "accent_color": "#0066CC",
            },
            "typography": {
                "font_family": "Noto Sans JP, sans-serif",
                "base_size": "16px",
            },
            "layout_style": "モダンでクリーン、TOPは導線重視",
            "responsive": True,
            "component_guidelines": {},
            "imagery_direction": "",
        }
