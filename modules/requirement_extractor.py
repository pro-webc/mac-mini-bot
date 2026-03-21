"""要望抽出モジュール"""
import json
import logging
import re
from typing import Dict, List

from config.config import get_contract_plan_info
from modules.text_llm import is_text_llm_configured, text_llm_complete

logger = logging.getLogger(__name__)


class RequirementExtractor:
    """アポ録画メモ、営業共有事項、ヒアリングシートから要望を抽出"""
    
    def __init__(self):
        if not is_text_llm_configured():
            raise ValueError(
                "テキスト LLM が未設定です。"
                "TEXT_LLM_PROVIDER=cursor_agent_cli または claude_code_cli と、"
                "CURSOR_AGENT_COMMAND または CLAUDE_CODE_COMMAND を設定してください。"
                "（要望・仕様・サイト実装はすべてターミナル CLI 経由です）"
            )

    def _llm(self, prompt: str, system: str, temperature: float = 0.3) -> str:
        return text_llm_complete(user=prompt, system=system, temperature=temperature)
    
    def extract_requirements(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str,
        contract_plan: str
    ) -> Dict:
        """
        ヒアリングシート、アポ録画メモ、営業共有事項から要望を抽出
        
        Args:
            hearing_sheet_content: ヒアリングシートの内容
            appo_memo: アポ録画メモ
            sales_notes: 営業共有事項
            contract_plan: 契約プラン
            
        Returns:
            抽出された要望と分析結果の辞書
        """
        plan_info = get_contract_plan_info(contract_plan)
        
        # BASIC LPプランの場合
        if plan_info["type"] == "landing_page":
            return self._extract_basic_lp_requirements(
                hearing_sheet_content,
                appo_memo,
                sales_notes
            )
        # BASICプラン（1ページコーポレートサイト）の場合
        elif plan_info["name"] == "BASIC" and plan_info["pages"] == 1:
            return self._extract_basic_requirements(
                hearing_sheet_content,
                appo_memo,
                sales_notes
            )
        # STANDARD / ADVANCE（複数ページ）の場合
        elif plan_info["type"] == "website" and plan_info["pages"] > 1:
            return self._extract_multi_page_requirements(
                hearing_sheet_content,
                appo_memo,
                sales_notes,
                plan_info
            )
        else:
            # その他のプランは従来の処理
            return self._extract_general_requirements(
                appo_memo,
                sales_notes
            )
    
    def _extract_basic_lp_requirements(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str
    ) -> Dict:
        """
        BASIC LPプラン用の詳細な情報抽出と分析
        
        Args:
            hearing_sheet_content: ヒアリングシートの内容
            appo_memo: アポ録画メモ
            sales_notes: 営業共有事項
            
        Returns:
            抽出された情報と分析結果
        """
        logger.info("BASIC LPプランの情報抽出を開始します")
        
        # ステップ1: 必要な情報を抽出
        extracted_info = self._extract_basic_lp_info(
            hearing_sheet_content,
            appo_memo,
            sales_notes
        )
        
        # ステップ2: 4つの分析を実行
        analysis = self._analyze_basic_lp(extracted_info)
        
        # ステップ3: ワイヤーフレームを作成
        wireframe = self._create_basic_lp_wireframe(analysis, extracted_info)
        
        # ステップ4: LP原稿を生成
        lp_content = self._generate_basic_lp_content(wireframe, analysis, extracted_info)
        
        return {
            "extracted_info": extracted_info,
            "analysis": analysis,
            "wireframe": wireframe,
            "lp_content": lp_content,
            "plan_type": "basic_lp"
        }
    
    def _extract_basic_lp_info(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str
    ) -> Dict:
        """BASIC LPに必要な情報を抽出"""
        prompt = f"""
以下のヒアリングシート、アポ録画メモ、営業共有事項から、LP作成に必要な情報を抽出してください。

【ヒアリングシート】
{hearing_sheet_content}

【アポ録画メモ】
{appo_memo}

【営業共有事項（デモ製作前）】
{sales_notes}

以下の項目について、情報を抽出してJSON形式で出力してください：

{{
  "company_info": {{
    "company_name": "会社名",
    "service_name": "サービス名(屋号)",
    "representative": "代表者名（役職含む）",
    "location": "所在地",
    "established_year": "設立年",
    "business_content": "事業内容",
    "licenses": "許認可・資格・提携先",
    "members": "メンバー情報",
    "contact_info": "連絡先情報"
  }},
  "what": {{
    "main_service_name": "メインサービス名",
    "service_overview": "サービスの概要・詳細",
    "additional_services": "付帯サービス・オプション",
    "pricing": "料金体系",
    "pricing_includes": "料金に含まれるもの・含まれないもの",
    "service_area": "対応エリア・対象範囲",
    "operation_system": "稼働・提供体制",
    "usage_flow": "利用の流れ"
  }},
  "offer": {{
    "special_offers": "オファー（特典）"
  }},
  "why": {{
    "target_customers": "ターゲット顧客の属性",
    "customer_insights": "顧客のインサイト・課題・悩み",
    "value_proposition": "提供価値（バリュー）",
    "mission": "事業の使命・想い"
  }},
  "how": {{
    "strengths": "選ばれる理由とその詳細"
  }},
  "social_proof": {{
    "quantitative_results": "定量的な実績",
    "case_studies": "事例・ケーススタディ",
    "testimonials": "お客様の声・評判",
    "third_party_evaluations": "第三者評価・メディア掲載"
  }},
  "conversion": {{
    "cv_type": "コンバージョンの種類",
    "contact_methods": "お問い合わせ手段と優先順位"
  }},
  "other": "その他の情報"
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはLP作成のための情報抽出専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                extracted_info = json.loads(json_match.group())
            else:
                extracted_info = self._create_default_basic_lp_info()
            
            logger.info("BASIC LP情報の抽出が完了しました")
            return extracted_info
            
        except Exception as e:
            logger.error(f"BASIC LP情報抽出エラー: {e}")
            return self._create_default_basic_lp_info()
    
    def _analyze_basic_lp(self, extracted_info: Dict) -> Dict:
        """4つの分析を実行"""
        prompt = f"""
以下の抽出された情報から、LP作成のための戦略分析を行ってください。

【抽出された情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

以下の4つのセクションに分けて分析してください：

## 1. ターゲット分析（セグメンテーション）
提供エリアやサービス特性から、最もコンバージョンに近い層（コアターゲット）と、潜在的な層（サブターゲット）を定義してください。
単なる「30代男性」のような属性だけでなく、**「今、どのような状況（シチュエーション）に置かれている人か」**という背景を重視して言語化してください。

## 2. ペルソナ設計（具体的ユーザー像）
コアターゲットの中から、最もこのサービスを必要としている代表的な1名を「ペルソナ」として具体的に設定してください。
以下の項目を含めてください：
* 氏名、年齢、職業、家族構成
* **発生している具体的な事象**（何に困っているか、どんなトラブルが起きているか）
* **心理状態・インサイト**（焦り、恐怖、不信感、諦めなど、感情の動き）

## 3. ジョブ理論（Jobs to be Done）とその優先度
顧客はこのサービスそのものが欲しいのではなく、サービスを通して「どのような進歩・解決」を成し遂げたいと考えているのか（片付けるべき用事＝ジョブ）を分析してください。
以下の3つの視点で分析し、今回の商材において**どのジョブの解決が最優先か**順位付けしてください。
* **機能的ジョブ**（実務として何を解決したいか）
* **感情的ジョブ**（どのような気持ちになりたいか、不安を解消したいか）
* **社会的ジョブ**（他人からどう見られたいか、あるいは誰かのためにどうしたいか）
※それぞれのジョブに対し、クライアントの「どの強み（How）」が解決策になるかも紐づけてください。

## 4. Webマーケターとしての戦略提言
上記の分析を踏まえ、今回のLP制作において「何を訴求の軸（コンセプト）にすべきか」を専門家の視点で提言してください。
* 競合他社との差別化ポイント
* ユーザーの不安を払拭するためのTrust Factor（信頼要素）の使い所
* オファー（特典や条件）の見せ方

JSON形式で出力してください：
{{
  "target_analysis": {{
    "core_target": "コアターゲットの詳細",
    "sub_targets": ["サブターゲット1", "サブターゲット2"]
  }},
  "persona": {{
    "name": "氏名",
    "age": "年齢",
    "occupation": "職業",
    "family": "家族構成",
    "specific_issue": "発生している具体的な事象",
    "psychological_state": "心理状態・インサイト"
  }},
  "jobs_to_be_done": {{
    "functional_job": {{
      "description": "機能的ジョブの説明",
      "priority": 1,
      "solution_strength": "解決策となる強み"
    }},
    "emotional_job": {{
      "description": "感情的ジョブの説明",
      "priority": 2,
      "solution_strength": "解決策となる強み"
    }},
    "social_job": {{
      "description": "社会的ジョブの説明",
      "priority": 3,
      "solution_strength": "解決策となる強み"
    }}
  }},
  "strategy_recommendation": {{
    "concept_axis": "訴求の軸（コンセプト）",
    "differentiation_points": "競合他社との差別化ポイント",
    "trust_factors": "Trust Factor（信頼要素）の使い所",
    "offer_presentation": "オファーの見せ方"
  }}
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはWebマーケティング戦略の専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = self._create_default_analysis()
            
            logger.info("BASIC LP分析が完了しました")
            return analysis
            
        except Exception as e:
            logger.error(f"BASIC LP分析エラー: {e}")
            return self._create_default_analysis()
    
    def _create_basic_lp_wireframe(self, analysis: Dict, extracted_info: Dict) -> Dict:
        """ワイヤーフレームを作成（ゴールデンサークル理論と新PASONAの法則に従う）"""
        prompt = f"""
以下の分析結果と抽出情報から、ゴールデンサークル理論と新PASONAの法則に従ってLPのワイヤーフレームを作成してください。

【分析結果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

【抽出情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

以下の要件に従って、全体構成マップ（必要なセクション・その個数・その順番）を考えてください：

・LPのセクションの基本：
- メインビジュアル
- whyを伝えるセクション(お悩み・お悩み解決)
- whatを伝えるセクション(商品、サービスの詳細紹介)
- howを伝えるセクション(ベネフィット、メリット)
- 中間オファーセクション（2カ所以上適切に配置）
- 社会的評価を伝えるセクション(実績や口コミ)
- whatを伝えるセクション(商品、サービスの料金やプランなどさらに詳細紹介)
- フロー
- よくある質問（必ず独立1セクション）
- 会社概要（必ず独立1セクションで、お問い合わせセクションの上に配置）
- お問い合わせ（必ず独立1セクション）

・それぞれのセクションの個数は、商材やサービスに合わせて分割して増やしてもよい
・それぞれのセクションの順番は、商材やサービスに合わせて最適化する
・ヘッダーフッターは禁止

※オンラインではなく実店舗のサービス/事業の場合は、Where情報を伝えるセクション必須(会社概要、運営者情報のセクションと統合禁止)
※だれか1人が運営するサービス/事業の場合は、Who情報を伝えるセクション必須(代表挨拶のセクションと統合可)

JSON形式で出力してください：
{{
  "sections": [
    {{
      "order": 1,
      "type": "main_visual",
      "title": "セクションタイトル",
      "description": "このセクションで伝える内容"
    }},
    ...
  ]
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはLP構成設計の専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                wireframe = json.loads(json_match.group())
            else:
                wireframe = self._create_default_wireframe()
            
            logger.info("BASIC LPワイヤーフレームが完了しました")
            return wireframe
            
        except Exception as e:
            logger.error(f"BASIC LPワイヤーフレーム作成エラー: {e}")
            return self._create_default_wireframe()
    
    def _generate_basic_lp_content(
        self,
        wireframe: Dict,
        analysis: Dict,
        extracted_info: Dict
    ) -> Dict:
        """LPの高レベルの原稿（タイトルと本文）を生成"""
        prompt = f"""
以下のワイヤーフレーム、分析結果、抽出情報から、LPの高レベルの原稿（タイトルと本文）を生成してください。

【ワイヤーフレーム】
{json.dumps(wireframe, ensure_ascii=False, indent=2)}

【分析結果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

【抽出情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

以下の要件に従って、各セクションの原稿を作成してください：

・AIらしくない、自然な文章表現
・ペルソナに合った、感情的すぎない文章表現
・遠まわしや冗長表現、スピリチュアルな表現は禁止
・騙されると感じられることがないよう、キラーフレーズは多用しない
・各セクションのタイトルはそのセクションに何が記載されているのか一目でわかる簡潔な文言
・各本文は広告LPらしく簡潔に短く

●メインビジュアル
・キャッチコピー：15文字以内必須。ただの紹介ではなくメリットが伝わる内容。
・サブコピー：スマホ表示で2行に収まる文字数。「～なら●●」等、サービス(屋号)名必須。
・選ばれる理由、強み：3つ必須。バッジ表示できる短い文字数。
・権威性、実績
・CTAボタン
・サービスや商品が一目でわかる画像やイラスト必須

●お悩み、お悩み解決セクション
・お悩みは4つ以上6つ以下
・お悩み解決を伝える文には「お任せください」だけでなく、whatやhow等お悩み解決の根拠をいれること

●中間オファーセクション
・迷いなく遷移できるボタンの文言
・複数お問い合わせ方法がある場合はすべての方法それぞれのCTAボタン必須
・CTAボタンを設置するだけでなく、オファー文も記載すること。

●事例、実績、お客様の声セクション
・実績情報がある場合は内容を推測し仮で入れ、十分な情報量にすること
・実績が複数あるべき場合は、複数仮で情報を記載すること
・画像必須

●よくある質問セクション
・すべての疑問が解消されるようにすること

●お問い合わせフォームがある場合は以下の項目を最低限設けること
- お問い合わせ内容/対象サービス内容などの項目選択(必須・プルダウン)
- 名前(必須)
- メールアドレス(必須)
- 電話
- お問い合わせ内容
※お問い合わせ内容の例：よくあるお問い合わせ内容を1つ記載必須。ですます等の丁寧語禁止。
※お問い合わせ内容以外の例：それぞれよくある例を1つ記載必須。
※フォームの上に「2日以内に登録メールアドレス宛にご連絡させていただきます」の文言必須。

図解・比較表で見せる情報を多く効果的に取り入れ、それをAIで生成できるだけの説明をできるだけ詳しくしてください。
画像やイラスト、before after画像を多く効果的に取り入れ、どんな画像やイラストかの説明と、どのように配置するのかをできるだけ詳しく説明してください。

LPに記載するテキストと、画像や配置の説明文は、明確にわけて出力すること。

JSON形式で出力してください：
{{
  "sections": [
    {{
      "order": 1,
      "type": "main_visual",
      "title": "セクションタイトル",
      "content": {{
        "text": "テキスト内容",
        "images": [
          {{
            "description": "画像の説明",
            "placement": "配置方法",
            "type": "画像タイプ（イラスト/写真/before_after等）"
          }}
        ],
        "diagrams": [
          {{
            "description": "図解の説明",
            "type": "図解タイプ（比較表/フローチャート等）"
          }}
        ],
        "cta": {{
          "text": "CTAボタンの文言",
          "type": "ボタンタイプ"
        }}
      }}
    }},
    ...
  ],
  "form": {{
    "fields": [
      {{
        "name": "field_name",
        "label": "フィールド名",
        "type": "フィールドタイプ",
        "required": true,
        "example": "例"
      }}
    ],
    "notice": "フォームの上に表示する文言"
  }}
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはLPライティングの専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                lp_content = json.loads(json_match.group())
            else:
                lp_content = self._create_default_lp_content()
            
            logger.info("BASIC LP原稿の生成が完了しました")
            return lp_content
            
        except Exception as e:
            logger.error(f"BASIC LP原稿生成エラー: {e}")
            return self._create_default_lp_content()
    
    def _extract_basic_requirements(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str
    ) -> Dict:
        """
        BASICプラン（1ページコーポレートサイト）用の情報抽出と分析
        
        Args:
            hearing_sheet_content: ヒアリングシートの内容
            appo_memo: アポ録画メモ
            sales_notes: 営業共有事項
            
        Returns:
            抽出された情報と分析結果
        """
        logger.info("BASICプランの情報抽出を開始します")
        
        # ステップ1: 必要な情報を抽出
        extracted_info = self._extract_basic_info(
            hearing_sheet_content,
            appo_memo,
            sales_notes
        )
        
        # ステップ2: サイト構成を設計
        site_structure = self._create_basic_site_structure(extracted_info)
        
        # ステップ3: サイト原稿を生成
        site_content = self._generate_basic_site_content(site_structure, extracted_info)
        
        return {
            "extracted_info": extracted_info,
            "site_structure": site_structure,
            "site_content": site_content,
            "plan_type": "basic"
        }
    
    def _extract_multi_page_requirements(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str,
        plan_info: Dict
    ) -> Dict:
        """
        STANDARD / ADVANCE プラン用。
        手順1-3と同一のヒアリング項目を埋めたうえで、ページ上限に沿ったサイトマップを設計する。
        """
        max_pages = int(plan_info.get("pages", 6))
        plan_name = plan_info.get("name", "STANDARD")
        logger.info("%sプラン（最大%dページ）の情報抽出・構成設計を開始します", plan_name, max_pages)
        
        extracted_info = self._extract_basic_info(
            hearing_sheet_content,
            appo_memo,
            sales_notes
        )
        site_map = self._plan_multi_page_site(extracted_info, max_pages, plan_name)
        
        pn = (plan_name or "").upper()
        if pn == "STANDARD":
            plan_type = "standard"
        elif pn == "ADVANCE":
            plan_type = "advance"
        else:
            plan_type = "standard"
        return {
            "extracted_info": extracted_info,
            "site_map": site_map,
            "max_pages": max_pages,
            "plan_type": plan_type,
        }
    
    def _plan_multi_page_site(
        self,
        extracted_info: Dict,
        max_pages: int,
        plan_name: str
    ) -> Dict:
        """複数ページサイトの全体構成・遷移・各ページセクションを LLM で設計"""
        prompt = f"""
あなたはWebディレクターです。以下の整理済み情報を使い、契約プランのページ上限 **最大{max_pages}ページ**（TOP含む全ページの合計）を厳守してサイト構成を設計してください。
プラン名: {plan_name}

【整理済み情報（手順1-3相当・ヒアリング項目）】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

## 必須ルール

### TOPページ
- TOPの主目的は「下層ページへの目次（導線）」とする。
- TOPのセクションから遷移できない下層ページを作ってはいけない（すべてTOPから辿れること）。
- TOPセクションの基本構成要素（順序はサイト目的に合わせ最適化）:
  メインビジュアル / 会社のWhy（各サービス別ではない） / What / 会社のHow（各サービス別ではない） /
  実績・口コミ等の社会的評価 / 会社概要を伝えるセクション / お問い合わせへの導線セクション
- サービスが複数ある場合: TOPのHowセクションには共通のHowのみ。TOPの社会的評価セクションも共通のみ。
- TOPにのみ情報を載せ下層に載せない場合は、その情報はTOPで完結でよく、その箇所に下層への遷移ボタンは不要。
- 異なるサービスが複数ある場合はページを分ける。ページ上限に達しそうなら内容が近いサービスを統合する。
- TOPの各サービス紹介箇所から、該当サービスページへ遷移するボタンを必ず設ける。

### 下層ページ
- **会社概要**は必ず独立した1ページ。
- **お問い合わせ**は必ず独立した1ページ。
- **ブログ**は必ず独立した1ページとするが、業種・目的上不要な場合はページ自体を作らない（削除）。
- 各サービスページには、料金・実績・FAQ等、LPとして必要なセクションをそれぞれ設ける。
- サービスページが複数ある場合、各サービスページに共通のWhyや共通のHowの全文を繰り返さない（サービス固有に集中）。
- 会社概要ページの重要セクションへ飛ぶボタンを、TOPの会社概要セクション内に設けること（推奨）。
- お問い合わせページ以外の**すべての下層ページ**の末尾付近に、お問い合わせページへ誘導するセクションを設ける。

### 遷移ボタン
- すべての遷移ボタンは、**該当セクションの説明の中に**明記する（一覧だけにまとめない）。
- 各ボタンに次を含める: 表記ラベル、遷移先ページ（パス）、遷移先が特定セクションの場合はそのセクションIDまたはセクション名。
- **同一ページ内のアンカーのみ**の遷移（#のみで他ページに行かない）は、主要導線としては使わない（同ページ内遷移ボタンは不可）。

### ページ数
- 合計ページ数は **{max_pages}ページ以下**。TOP + 必須ページ + サービス + ブログ（必要時）で調整。

JSONのみ出力。スキーマ例:
{{
  "page_budget": {{"max": {max_pages}, "planned_count": 0, "rationale": "内訳の説明"}},
  "top_page": {{
    "path": "/",
    "purpose": "下層への目次・導線",
    "sections": [
      {{
        "order": 1,
        "type": "main_visual",
        "title": "セクション見出し",
        "summary": "何を伝えるか（テキストライティング不要）",
        "navigation_buttons": [
          {{
            "label": "ボタン表記",
            "target_page_path": "/example",
            "target_section_id": "optional-section-id-or-null"
          }}
        ]
      }}
    ]
  }},
  "subpages": [
    {{
      "path": "/company",
      "title": "会社概要",
      "role": "company_overview",
      "sections": [
        {{
          "order": 1,
          "type": "overview",
          "id": "section-id",
          "title": "見出し",
          "summary": "内容の要約",
          "navigation_buttons": []
        }}
      ],
      "contact_cta_section": true
    }}
  ],
  "global_notes": [
    "構成上の注意やブログを省略した理由など"
  ]
}}

subpages には必ず /contact（お問い合わせ）を含める。会社概要は /company 等で独立。ブログは必要なら /blog。
サービスページは /services/xxx 形式推奨。
"""
        try:
            result_text = self._llm(
                prompt,
                "あなたは情報設計とIAの専門家です。JSONのみ返します。",
                0.25,
            )
            
            json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
            if json_match:
                site_map = json.loads(json_match.group())
            else:
                site_map = self._create_default_multi_page_site_map(max_pages)
            
            logger.info("複数ページサイトマップの設計が完了しました")
            return site_map
        except Exception as e:
            logger.error("複数ページサイトマップ設計エラー: %s", e)
            return self._create_default_multi_page_site_map(max_pages)
    
    def _create_default_multi_page_site_map(self, max_pages: int) -> Dict:
        """フォールバック用の最小サイトマップ"""
        return {
            "page_budget": {"max": max_pages, "planned_count": min(4, max_pages), "rationale": "フォールバック"},
            "top_page": {
                "path": "/",
                "purpose": "下層への目次",
                "sections": [
                    {
                        "order": 1,
                        "type": "main_visual",
                        "title": "メインビジュアル",
                        "summary": "サービス名と主要CTA",
                        "navigation_buttons": [
                            {"label": "お問い合わせ", "target_page_path": "/contact", "target_section_id": None}
                        ],
                    }
                ],
            },
            "subpages": [
                {
                    "path": "/company",
                    "title": "会社概要",
                    "role": "company_overview",
                    "sections": [],
                    "contact_cta_section": True,
                },
                {
                    "path": "/contact",
                    "title": "お問い合わせ",
                    "role": "contact",
                    "sections": [],
                    "contact_cta_section": False,
                },
            ],
            "global_notes": ["デフォルト構成"],
        }
    
    def _extract_basic_info(
        self,
        hearing_sheet_content: str,
        appo_memo: str,
        sales_notes: str
    ) -> Dict:
        """BASICプランに必要な情報を抽出"""
        prompt = f"""
以下のヒアリングシート、アポ録画メモ、営業共有事項から、コーポレートサイト（1ページまたは複数ページ）作成に必要な情報を抽出してください。

【ヒアリングシート】
{hearing_sheet_content}

【アポ録画メモ】
{appo_memo}

【営業共有事項（デモ製作前）】
{sales_notes}

以下の要件に従って、情報を抽出してください：

・必ずすべてのサービスごとのhowとwhyと社会的実績を出してほしい→情報がない場合は全て仮で想定して項目を埋めてください
・他の項目も、情報がなくて埋められていないと思うので、情報がない項目は全て仮で情報を十分な量で入れてください
・複数あるべき情報は複数仮で想定して項目を埋めてください

以下の項目について、情報を抽出してJSON形式で出力してください：

{{
  "company_info": {{
    "company_name": "会社名",
    "service_name": "サービス名(屋号)",
    "representative": "代表者名",
    "established_year": "設立年",
    "location": "所在地",
    "contact_info": "連絡先",
    "members": "メンバー情報"
  }},
  "what": {{
    "services": [
      {{
        "service_name": "サービス名",
        "service_content": "サービス内容",
        "pricing": "料金体系",
        "service_area": "対応エリア",
        "why": "サービス別のWhy",
        "how": "サービス別のHow",
        "social_proof": "サービス別の社会的評価"
      }}
    ]
  }},
  "why": {{
    "common_why": {{
      "mission": "なぜこの事業・サービスを行っているのか",
      "problem_solving": "顧客のどのような課題・不安を解決したいのか",
      "value_proposition": "どのような価値を提供したいのか"
    }},
    "service_whys": [
      {{
        "service_name": "サービス名",
        "why": "サービス別のWhy"
      }}
    ]
  }},
  "how": {{
    "common_how": "共通のHow（全サービス共通）",
    "service_hows": [
      {{
        "service_name": "サービス名",
        "how": "サービス別のHow"
      }}
    ]
  }},
  "social_proof": {{
    "common_social_proof": {{
      "achievements": "共通の実績",
      "case_studies": "共通の事例",
      "testimonials": "共通の口コミ",
      "third_party_evaluations": "共通の第三者評価"
    }},
    "service_social_proofs": [
      {{
        "service_name": "サービス名",
        "achievements": "サービス別の実績",
        "case_studies": "サービス別の事例",
        "testimonials": "サービス別の口コミ",
        "third_party_evaluations": "サービス別の第三者評価"
      }}
    ]
  }},
  "target_persona": {{
    "target": "ターゲット",
    "persona": "ペルソナ"
  }},
  "site_purpose": {{
    "purpose": "サイト制作の目的",
    "priorities": ["優先度1", "優先度2"]
  }},
  "contact": {{
    "methods": [
      {{
        "method": "お問い合わせ方法",
        "purpose": "目的",
        "priority": 1
      }}
    ]
  }},
  "other": "その他の情報"
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはコーポレートサイト作成のための情報抽出専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                extracted_info = json.loads(json_match.group())
            else:
                extracted_info = self._create_default_basic_info()
            
            logger.info("BASIC情報の抽出が完了しました")
            return extracted_info
            
        except Exception as e:
            logger.error(f"BASIC情報抽出エラー: {e}")
            return self._create_default_basic_info()
    
    def _create_basic_site_structure(self, extracted_info: Dict) -> Dict:
        """1ページコーポレートサイトの構成を設計"""
        prompt = f"""
以下の抽出情報から、「必ず1ページ」のコーポレートサイトのサイト構成を考えてください。

【抽出情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

・ページの基本は、メインビジュアル/各サービスではなく会社のWhyを伝えるセクション/Whatを伝えるセクション/各サービスではなく会社のHowを伝えるセクション/実績など社会的評価を伝えるセクション/代表挨拶セクション/採用情報セクション/会社情報セクション/お問い合わせセクション
・業種やサイトの目的に合わせてセクションの順番は最適化する
・情報がない場合は該当セクションは不要
※構成に関する先方の要望がある場合は他の条件を無視し、必ず優先して反映すること

●メインビジュアル
・CTAボタン必須
※オンラインではなく実店舗のサービスの場合は、Where情報必須
※サービス名(屋号名)必須

●各サービスではなく会社のWhyを伝えるセクション

●Whatを伝えるセクション
・異なるサービスが4つ以上ある場合はタブで表示するような構成に
・サービス別のwhy、how、詳細情報はここで完結させる

●各サービスではなく会社のHowを伝えるセクション
・サービスが複数ある場合で、会社の共通のhowがない場合はこのセクションは不要

●実績など社会的評価を伝えるセクション
・必要な場合は実績内容をサービスから推測し仮で情報を設ける
・社会的評価が必要ない業界やサービスの場合はこのセクションは不要

●代表挨拶セクション
・必要な業界やサービス内容の場合のみ

●採用情報セクション
・採用情報がある場合のみ

●会社情報セクション
・メンバー紹介がある場合はこのセクション内に入れる
・沿革紹介のセクションは禁止

●お問い合わせセクション

JSON形式で出力してください：
{{
  "sections": [
    {{
      "order": 1,
      "type": "main_visual",
      "title": "セクションタイトル",
      "description": "このセクションで伝える内容",
      "required": true
    }},
    ...
  ]
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはコーポレートサイト構成設計の専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                site_structure = json.loads(json_match.group())
            else:
                site_structure = self._create_default_basic_structure()
            
            logger.info("BASICサイト構成が完了しました")
            return site_structure
            
        except Exception as e:
            logger.error(f"BASICサイト構成作成エラー: {e}")
            return self._create_default_basic_structure()
    
    def _generate_basic_site_content(
        self,
        site_structure: Dict,
        extracted_info: Dict
    ) -> Dict:
        """BASICサイトの原稿を生成"""
        prompt = f"""
以下のサイト構成と抽出情報から、そのままサイトを制作できる高レベルのタイトルと本文を生成してください。

【サイト構成】
{json.dumps(site_structure, ensure_ascii=False, indent=2)}

【抽出情報】
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

以下の要件に従って、各セクションの原稿を作成してください：

・そのままサイトを制作できる高レベルのタイトルと本文
・遠まわしや冗長表現、スピリチュアルな表現は禁止

・どんなサービスなのか？というサービスの概要の説明を十分に設けること
・情報量が少ない場合はサービスの内容を推測し仮で入れ、情報量を担保すること

・実績情報がある場合は内容を推測し仮で入れ、十分な情報量にすること
・実績が複数あるべき場合は、複数仮で情報を記載すること

・メインビジュアルのボタンはお問い合わせのCTAに関するボタンのみを設置必須
・メインビジュアルのキャッチコピーは15字以内必須
※オンラインではなく実店舗のサービスの場合は、Where情報必須
※メインビジュアル内にサービス名(屋号名)必須

・メンバー紹介がある場合は内容を推測し仮で入れ、十分な情報量にすること

・お問い合わせフォームがある場合は以下の項目を最低限設けること
- お問い合わせ内容/対象サービス内容などの項目選択(必須・プルダウン)
- 名前(必須)
- メールアドレス(必須)
- 電話
- お問い合わせ内容
※お問い合わせ内容の例：よくあるお問い合わせ内容を1つ記載。ですます等の丁寧語は禁止。
※フォームの上に「2日以内に登録メールアドレス宛にご連絡させていただきます」の文言必須。

画像を多く効果的に取り入れ、どんな画像かの説明と、どのように配置するのかをできるだけ詳しく説明してください。
記載するテキスト情報と、画像や配置の説明文は、明確にわけて出力すること。
※構成・文章に関する先方の要望がある場合は他の条件を無視し、必ず優先して反映すること

JSON形式で出力してください：
{{
  "sections": [
    {{
      "order": 1,
      "type": "main_visual",
      "title": "セクションタイトル",
      "content": {{
        "text": "テキスト内容",
        "images": [
          {{
            "description": "画像の説明",
            "placement": "配置方法",
            "type": "画像タイプ"
          }}
        ],
        "cta": {{
          "text": "CTAボタンの文言",
          "type": "ボタンタイプ"
        }}
      }}
    }},
    ...
  ],
  "form": {{
    "fields": [
      {{
        "name": "field_name",
        "label": "フィールド名",
        "type": "フィールドタイプ",
        "required": true,
        "example": "例"
      }}
    ],
    "notice": "フォームの上に表示する文言"
  }}
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはコーポレートサイトライティングの専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                site_content = json.loads(json_match.group())
            else:
                site_content = self._create_default_basic_content()
            
            logger.info("BASICサイト原稿の生成が完了しました")
            return site_content
            
        except Exception as e:
            logger.error(f"BASICサイト原稿生成エラー: {e}")
            return self._create_default_basic_content()
    
    def _extract_general_requirements(self, appo_memo: str, sales_notes: str) -> Dict:
        """一般的なプラン用の要望抽出（従来の処理）"""
        prompt = f"""
以下のアポ録画メモと営業共有事項から、Webサイト製作に関する要望を抽出してください。

【アポ録画メモ】
{appo_memo}

【営業共有事項（デモ製作前）】
{sales_notes}

以下のカテゴリに分類して要望を抽出してください：
1. デザイン要望（色、レイアウト、スタイルなど）
2. 機能要望（フォーム、検索、SNS連携など）
3. コンテンツ要望（ページ構成、文章、画像など）
4. 技術要望（レスポンシブ対応、SEO、パフォーマンスなど）
5. その他要望

JSON形式で出力してください：
{{
  "design_requirements": ["要望1", "要望2"],
  "function_requirements": ["要望1", "要望2"],
  "content_requirements": ["要望1", "要望2"],
  "technical_requirements": ["要望1", "要望2"],
  "other_requirements": ["要望1", "要望2"]
}}
"""
        
        try:
            result_text = self._llm(
                prompt,
                "あなたはWebサイト製作の要望を抽出する専門家です。",
                0.3,
            )
            
            # JSONをパース
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                requirements = json.loads(json_match.group())
            else:
                requirements = self._parse_fallback(result_text)
            
            logger.info("要望の抽出が完了しました")
            return {
                "requirements": requirements,
                "plan_type": "general"
            }
            
        except Exception as e:
            logger.error(f"要望抽出エラー: {e}")
            return {
                "requirements": {
                    "design_requirements": [],
                    "function_requirements": [],
                    "content_requirements": [],
                    "technical_requirements": [],
                    "other_requirements": []
                },
                "plan_type": "general"
            }
    
    def _parse_fallback(self, text: str) -> Dict[str, List[str]]:
        """JSONパース失敗時のフォールバック処理"""
        requirements = {
            "design_requirements": [],
            "function_requirements": [],
            "content_requirements": [],
            "technical_requirements": [],
            "other_requirements": []
        }
        
        # 簡易的なテキスト解析
        lines = text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if 'デザイン' in line or 'design' in line.lower():
                current_category = "design_requirements"
            elif '機能' in line or 'function' in line.lower():
                current_category = "function_requirements"
            elif 'コンテンツ' in line or 'content' in line.lower():
                current_category = "content_requirements"
            elif '技術' in line or 'technical' in line.lower():
                current_category = "technical_requirements"
            elif current_category and (line.startswith('-') or line.startswith('・')):
                req = line.lstrip('-・').strip()
                if req:
                    requirements[current_category].append(req)
        
        return requirements
    
    def _create_default_basic_lp_info(self) -> Dict:
        """デフォルトのBASIC LP情報"""
        return {
            "company_info": {},
            "what": {},
            "offer": {},
            "why": {},
            "how": {},
            "social_proof": {},
            "conversion": {},
            "other": ""
        }
    
    def _create_default_analysis(self) -> Dict:
        """デフォルトの分析結果"""
        return {
            "target_analysis": {
                "core_target": "",
                "sub_targets": []
            },
            "persona": {},
            "jobs_to_be_done": {},
            "strategy_recommendation": {}
        }
    
    def _create_default_wireframe(self) -> Dict:
        """デフォルトのワイヤーフレーム"""
        return {
            "sections": [
                {"order": 1, "type": "main_visual", "title": "メインビジュアル"},
                {"order": 2, "type": "why", "title": "お悩み・お悩み解決"},
                {"order": 3, "type": "what", "title": "サービス詳細"},
                {"order": 4, "type": "how", "title": "選ばれる理由"},
                {"order": 5, "type": "offer", "title": "特別オファー"},
                {"order": 6, "type": "social_proof", "title": "実績・お客様の声"},
                {"order": 7, "type": "what", "title": "料金・プラン"},
                {"order": 8, "type": "flow", "title": "ご利用の流れ"},
                {"order": 9, "type": "faq", "title": "よくある質問"},
                {"order": 10, "type": "company", "title": "会社概要"},
                {"order": 11, "type": "contact", "title": "お問い合わせ"}
            ]
        }
    
    def _create_default_lp_content(self) -> Dict:
        """デフォルトのLP原稿"""
        return {
            "sections": [],
            "form": {
                "fields": [],
                "notice": "2日以内に登録メールアドレス宛にご連絡させていただきます"
            }
        }
    
    def _create_default_basic_info(self) -> Dict:
        """デフォルトのBASIC情報"""
        return {
            "company_info": {},
            "what": {"services": []},
            "why": {"common_why": {}, "service_whys": []},
            "how": {"common_how": "", "service_hows": []},
            "social_proof": {"common_social_proof": {}, "service_social_proofs": []},
            "target_persona": {},
            "site_purpose": {},
            "contact": {"methods": []},
            "other": ""
        }
    
    def _create_default_basic_structure(self) -> Dict:
        """デフォルトのBASICサイト構成"""
        return {
            "sections": [
                {"order": 1, "type": "main_visual", "title": "メインビジュアル", "required": True},
                {"order": 2, "type": "why", "title": "会社のWhy", "required": True},
                {"order": 3, "type": "what", "title": "サービス紹介", "required": True},
                {"order": 4, "type": "how", "title": "会社のHow", "required": False},
                {"order": 5, "type": "social_proof", "title": "実績・社会的評価", "required": False},
                {"order": 6, "type": "greeting", "title": "代表挨拶", "required": False},
                {"order": 7, "type": "recruitment", "title": "採用情報", "required": False},
                {"order": 8, "type": "company", "title": "会社情報", "required": True},
                {"order": 9, "type": "contact", "title": "お問い合わせ", "required": True}
            ]
        }
    
    def _create_default_basic_content(self) -> Dict:
        """デフォルトのBASICサイト原稿"""
        return {
            "sections": [],
            "form": {
                "fields": [],
                "notice": "2日以内に登録メールアドレス宛にご連絡させていただきます"
            }
        }
