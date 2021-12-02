def to_title_case(s):
    s_parts = s.split('-')
    s_title = map(lambda s: s.capitalize(), s_parts)
    return ''.join(s_title)
