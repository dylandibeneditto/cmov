# Time parsing utility
def parse_time(s):
    if isinstance(s, (int, float)):
        return s
    if isinstance(s, str) and s.endswith('s'):
        return float(s[:-1])
    raise ValueError(f"Cannot parse time: {s}")
