def parse_count(value):
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        value = value.upper().strip()
        if value.endswith('K'):
            return int(float(value[:-1]) * 1_000)
        elif value.endswith('M'):
            return int(float(value[:-1]) * 1_000_000)
        elif value.endswith('B'):
            return int(float(value[:-1]) * 1_000_000_000)
        else:
            try:
                return int(value)
            except ValueError:
                return 0
    return 0
