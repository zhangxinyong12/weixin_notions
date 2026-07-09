import io, sys

p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()

# 把这一处文本里的 ASCII 双引号（U+0022）换成中文弯引号
old = '变成"错题驱动的针对性训练"'  # 变成"错题驱动的针对性训练"
new = '变成“错题驱动的针对性训练”'  # 变成“错题驱动的针对性训练”

count = s.count(old)
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('替换处数:', count)
