def deep_merge(source: dict, overrides: dict) -> dict:
    """
    یک نسخه‌ی ترکیب‌شده برمی‌گرداند:
      - اگر overrides[k] dict باشد و source[k] هم dict باشد،
        بازگشتیِ این تابع را در source[k] می‌گذارد.
      - در غیر این‌صورت overrides[k] جایگزین می‌شود.
    """
    result = source.copy()
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(source.get(k), dict):
            result[k] = deep_merge(source[k], v)
        else:
            result[k] = v
    return result