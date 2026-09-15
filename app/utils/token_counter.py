# app/utils/token_counter.py
"""粗略 token 估算。

tiktoken 是 OpenAI 的 tokenizer，对中文比 DeepSeek/Qwen 高估 30~80%，
本模块改用"中文字数 * 0.6 + 其他字符 * 0.25"的近似公式，
用于上下文压缩够用，不追求精确。
"""


def count_tokens(text: str, model: str = "any") -> int:
    if not text:
        return 0
    chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other = len(text) - chinese
    return int(chinese * 0.6 + other * 0.25)


def count_messages_tokens(messages, model: str = "any") -> int:
    total = 0
    for m in messages:
        content = getattr(m, "content", "") or ""
        total += count_tokens(str(content)) + 4   # chat 格式每条约 3~4 token
    return total