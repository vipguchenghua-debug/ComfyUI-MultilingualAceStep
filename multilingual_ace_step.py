# ComfyUI/custom_nodes/ComfyUI-MultilingualAceStep/multilingual_ace_step.py

try:
    from pypinyin import pinyin, Style
except ImportError:
    raise ImportError("❌ 请运行: pip install pypinyin")

try:
    from pykakasi import kakasi
except ImportError:
    raise ImportError("❌ 请运行: pip install pykakasi")

try:
    from korean_romanizer.romanizer import Romanizer
except ImportError:
    raise ImportError("❌ 请运行: pip install korean-romanizer")


class MultilingualLyricsToAceStep:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lyrics": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                        "default": (
                            "# 📝 歌词格式说明（复制下方模板，替换中文部分即可）\n"
                            "# 主歌 → [verse]\n"
                            "# 副歌 → [chorus]\n"
                            "# 桥段 → [bridge]\n"
                            "# 尾声 → [outro]\n\n"
                            "[verse]\n"
                            "在这里写你的主歌歌词\n\n"
                            "[chorus]\n"
                            "在这里写你的副歌歌词\n\n"
                            "[bridge]\n"
                            "桥段歌词（可选）"
                        ),
                    },
                ),
                "language": (["zh", "ja", "ko", "es", "fr", "de", "it", "pt", "en"], {"default": "zh"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ace_step_lyrics",)
    FUNCTION = "convert"
    CATEGORY = "audio/lyrics"

    def _romanize_zh(self, text):
        pys = pinyin(text, style=Style.TONE3, heteronym=False)
        return ' '.join([item[0] for item in pys])

    def _romanize_ja(self, text):
        kks = kakasi()
        result = kks.convert(text)
        return ' '.join([item['hepburn'] for item in result])

    def _romanize_ko(self, text):
        clean_text = ''.join(c for c in text if c.isalnum() or c.isspace())
        r = Romanizer(clean_text)
        return r.romanize()

    def convert(self, lyrics, language):
        # 移除用户可能粘贴的注释行（以 # 开头）
        lines = [
            line for line in lyrics.split('\n')
            if not line.strip().startswith('#')
        ]
        output_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                output_lines.append("")
                continue

            # 保留 [xxx] 标签
            if stripped.startswith('[') and stripped.endswith(']'):
                output_lines.append(stripped)
                continue

            # 处理歌词行
            if language in ["es", "fr", "de", "it", "pt", "en"]:
                output_lines.append(f"[{language}]{stripped}")
            elif language == "zh":
                output_lines.append(f"[zh]{self._romanize_zh(stripped)}")
            elif language == "ja":
                output_lines.append(f"[ja]{self._romanize_ja(stripped)}")
            elif language == "ko":
                output_lines.append(f"[ko]{self._romanize_ko(stripped)}")
            else:
                output_lines.append(f"[{language}]{stripped}")

        return ("\n".join(output_lines),)


NODE_CLASS_MAPPINGS = {"MultilingualLyricsToAceStep": MultilingualLyricsToAceStep}
NODE_DISPLAY_NAME_MAPPINGS = {"MultilingualLyricsToAceStep": "🌍 多语言歌词 → ACE-Step（带模板）"}
