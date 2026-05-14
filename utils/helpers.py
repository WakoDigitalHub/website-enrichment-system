def merge_values(old, new):
    def to_set(val):
        if isinstance(val, str) and val.strip():
            return set(val.split(", "))
        return set()
    old_set = to_set(old)
    new_set = to_set(new)
    merged = sorted(old_set.union(new_set))
    return ", ".join(merged) if merged else None
