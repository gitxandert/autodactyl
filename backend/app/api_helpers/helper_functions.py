import re, json

def _strip_code_fences(s: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.IGNORECASE)

def coerce_model_json(x):
    # Already a dict? good.
    if isinstance(x, dict):
        return x
    # Model object with .content
    if hasattr(x, "content"):
        x = x.content
    # Bytes -> str
    if isinstance(x, (bytes, bytearray)):
        x = x.decode("utf-8", errors="replace")
    # If not a string by now, stringify (last resort)
    if not isinstance(x, str):
        x = str(x)
    # Try raw parse
    try:
        return json.loads(x)
    except Exception:
        pass
    # Try without code fences
    try:
        return json.loads(_strip_code_fences(x))
    except Exception:
        pass
    # If the model returned a JSON object as a *string* inside quotes,
    # attempt one more pass (e.g., "\"{...}\"")
    try:
        inner = json.loads(x)
        if isinstance(inner, str):
            return json.loads(_strip_code_fences(inner))
        return inner
    except Exception:
        raise ValueError("Model did not return valid JSON")

