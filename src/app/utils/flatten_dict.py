def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    { "a": {"b": 1, "c":2}, "x":3 }
    => { "a.b":1, "a.c":2, "x":3 }
    """
    items = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items
