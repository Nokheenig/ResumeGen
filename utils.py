def deep_merge_dict(base: dict, override: dict) -> dict:
    """
    Deeply merges `override` into `base`, modifying `base` in-place.
    - Nested dictionaries are merged recursively.
    - Scalar values and lists in `override` replace those in `base`.
    """
    for key, override_value in override.items():
        base_value = base.get(key)

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            deep_merge_dict(base_value, override_value)
        else:
            base[key] = override_value  # Override base with override

    return base
