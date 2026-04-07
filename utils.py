def deep_merge_dict(base: dict, override: dict) -> dict:
    """
    Deeply merges `override` into `base`, modifying `base` in-place.
    - Nested dictionaries are merged recursively.
    - Scalar values and lists in `override` replace those in `base`.
    """
    if override == None: # deal with the case where we want to wipe base dictionary
        # base = {}
        return {}

    for key, override_value in override.items():
        base_value = base.get(key)

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            deep_merge_dict(base_value, override_value)
        else:
            base[key] = override_value  # Override base with override

    return base

def deep_extend_dict(base: dict, extension: dict) -> dict:
    """
    Deeply extends `base` with `extension`, modifying `base` in-place.
    - Nested dictionaries are extended recursively.
    - Scalar values and lists in `base` prevail over those in `extension` (extension does not replace a key already existing in base).
    """
    for key, extension_value in extension.items():
        if key in base:
            base_value = base.get(key) 
            if isinstance(base_value, dict) and isinstance(extension_value, dict):
                deep_extend_dict(base_value, extension_value)
            else:
                continue # keep base dictionary value / list, ..
        else:
            base[key] = extension_value  # Extend base with extension_value

    return base