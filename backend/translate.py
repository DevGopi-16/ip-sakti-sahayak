from functools import lru_cache

try:
    from backend.providers import get_llm
except ImportError:
    from providers import get_llm


@lru_cache(maxsize=512)
def translate_text(text: str, target_language: str) -> str:
    if not text or not text.strip() or target_language.lower() in ["en", "english"]:
        return text

    llm = get_llm()
    prompt = f"""
    Translate the following text into {target_language}.
    Keep legal terms, act titles, and sections (e.g., 'Section 3(p)', 'Schedule T') accurate.

    Text:
    {text}
    """
    res = llm.invoke(prompt)
    return str(res.content)