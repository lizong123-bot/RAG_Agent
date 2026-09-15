from app.utils.token_counter import count_tokens


def compress_docs(docs, max_tokens: int = 2000, model: str = "gpt-4o-mini"):
    """按顺序保留文档，直到达到 token 上限。"""
    total_before = sum(count_tokens(d.page_content, model) for d in docs)
    selected, total = [], 0
    for d in docs:
        t = count_tokens(d.page_content, model)
        if total + t > max_tokens:
            break
        selected.append(d)
        total += t
    print(f"[compress] {len(docs)}→{len(selected)} 条，"
          f"{total_before}→{total} tokens (上限 {max_tokens})")
    
    return selected