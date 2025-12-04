import re

def find_target_line_from_text(raw_text, prefer_pattern=r'_1_'):
    """
    raw_text: string with multiple lines
    preference logic:
      1) exact match containing '_1_'
      2) contains '_1'
      3) any line containing digit '1' and length > 6
      4) fallback to last non-empty line
    """
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    # 1
    for ln in lines:
        if '_1_' in ln:
            return ln
    # 2
    for ln in lines:
        if '_1' in ln:
            return ln
    # 3
    for ln in lines:
        if '1' in ln and len(ln) > 6:
            return ln
    # 4 fallback
    return lines[-1] if lines else None



def extract_target_line(lines):
    """
    Return the line that contains `_1_` or closest match.
    """
    for line in lines:
        if "_1_" in line:
            return line

    # fuzzy fallback
    import re
    pattern = re.compile(r".*1.*_.*")

    for line in lines:
        if pattern.match(line):
            return line

    return None

def clean_text(t: str):
    """
    Cleans noise, removes extra spaces, trims non-alphanumerics.
    """
    t = t.strip()
    t = t.replace(" ", "")
    return t
