import io, sys
from html.parser import HTMLParser
sys.stdout.reconfigure(encoding='utf-8')

class D(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.leaf_depth = 0
    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        is_leaf = tag == "span" and "leaf" in ad
        if is_leaf: self.leaf_depth += 1
        self.stack.append((tag, is_leaf))
        mark = " [LEAF]" if is_leaf else ""
        print(f"START <{tag}>{mark}  leaf_depth={self.leaf_depth}")
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                for _, wl in self.stack[i:]:
                    if wl: self.leaf_depth -= 1
                del self.stack[i:]; break
        print(f"END   </{tag}>  leaf_depth={self.leaf_depth}")
    def handle_data(self, data):
        t = data.strip()
        if t:
            print(f"DATA  {t[:28]!r}  leaf_depth={self.leaf_depth}")

p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
D().feed(s)
