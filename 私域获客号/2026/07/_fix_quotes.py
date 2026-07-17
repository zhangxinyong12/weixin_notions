import re
p = r"D:/person/微信公众号/私域获客号/2026/07/2026-7-17-重构私域获客的第一天_公众号.html"
s = open(p, encoding='utf-8').read()

def repl(m):
    t = m.group(1)
    out = []
    open_q = True
    for ch in t:
        if ch == '"':            # 只动标签间文本里的 ASCII 直引号
            out.append('“' if open_q else '”')
            open_q = not open_q
        else:
            out.append(ch)
    return '>' + ''.join(out) + '<'

s2 = re.sub(r'>([^<>]*)<', repl, s)
open(p, 'w', encoding='utf-8').write(s2)
print("done")
