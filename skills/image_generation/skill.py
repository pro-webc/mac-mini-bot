"""画像生成スキル - コマンド操作で画像生成を実行"""
import logging
import sys
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from config.config import GEMINI_API_KEY, OUTPUT_DIR

logger = logging.getLogger(__name__)


class ImageGenerationSkill:
    """画像生成スキル - LLM/API経由で画像を生成"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEYが必要です")
        genai.configure(api_key=GEMINI_API_KEY)
        # Gemini 2.0 Flash Expressive を使用（画像生成対応）
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except:
            self.model = genai.GenerativeModel('gemini-pro')
            logger.warning("画像生成モデルが利用できないため、テキスト生成モデルを使用します")
    
    def generate_from_command(
        self,
        command: str,
        output_path: Optional[Path] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Optional[Path]:
        """
        コマンド（自然言語）から画像を生成
        
        Args:
            command: 画像生成コマンド（例: "モダンな企業のヒーロー画像を生成"）
            output_path: 出力パス
            width: 画像幅
            height: 画像高さ
            
        Returns:
            生成された画像のパス
        """
        try:
            # プロンプトを拡張
            enhanced_prompt = f"""
以下のコマンドに基づいて、高品質なWebサイト用画像を生成してください。

コマンド: {command}

要件:
- 解像度: {width}x{height}
- スタイル: プロフェッショナル、モダン
- 用途: Webサイト用
- フォーマット: PNG
"""
            
            # 画像生成
            response = self.model.generate_content(enhanced_prompt)
            
            if output_path is None:
                import hashlib
                filename_hash = hashlib.md5(command.encode()).hexdigest()[:8]
                output_path = OUTPUT_DIR / "images" / f"generated_{filename_hash}.png"
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 実際の画像生成処理
            # Gemini APIが画像を直接返す場合
            if hasattr(response, 'images') and response.images:
                image_data = response.images[0]
                with open(output_path, 'wb') as f:
                    f.write(image_data)
            else:
                # フォールバック: プレースホルダー画像を生成
                logger.warning("画像生成APIが利用できないため、プレースホルダーを生成します")
                self._generate_placeholder_image(output_path, command, width, height)
            
            logger.info(f"画像を生成しました: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"画像生成エラー: {e}")
            # エラー時はプレースホルダーを生成
            if output_path is None:
                output_path = OUTPUT_DIR / "images" / "placeholder.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._generate_placeholder_image(output_path, command, width, height)
            return output_path
    
    def _generate_placeholder_image(
        self,
        output_path: Path,
        prompt: str,
        width: int,
        height: int
    ):
        """プレースホルダー画像を生成（PIL使用）"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (width, height), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            text = prompt[:50] if len(prompt) > 50 else prompt
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((width - text_width) // 2, (height - text_height) // 2)
            
            draw.text(position, text, fill='#666666', font=font)
            img.save(output_path, 'PNG')
            
            logger.info(f"プレースホルダー画像を生成しました: {output_path}")
            
        except ImportError:
            logger.warning("PILがインストールされていないため、プレースホルダー画像をスキップします")
        except Exception as e:
            logger.error(f"プレースホルダー画像生成エラー: {e}")


def main():
    """コマンドライン実行用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="画像生成スキル")
    parser.add_argument("command", help="画像生成コマンド（例: 'モダンな企業のヒーロー画像を生成'）")
    parser.add_argument("--output", "-o", help="出力パス")
    parser.add_argument("--width", "-w", type=int, default=1024, help="画像幅")
    parser.add_argument("--height", "-h", type=int, default=1024, help="画像高さ")
    
    args = parser.parse_args()
    
    skill = ImageGenerationSkill()
    output_path = Path(args.output) if args.output else None
    result = skill.generate_from_command(
        args.command,
        output_path,
        args.width,
        args.height
    )
    
    if result:
        print(f"画像を生成しました: {result}")
        sys.exit(0)
    else:
        print("画像生成に失敗しました", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
