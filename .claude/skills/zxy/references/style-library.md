# 风格素材库 —— 自主抉择的灵感池

**这不是固定模板。** 下面是配色、版式、组件的素材池，供你根据内容气质挑选、混搭、改色、自创。每篇文章都应有自己的风格判断——这是本 skill 的核心。

所有组件示例都已内联样式 + `<span leaf="">` 包裹，可直接用或改色（只换十六进制值）。换主题色时，把示例里的主色统一替换即可。

---

## 一、配色方案（取灵感或自创）

每套 5 色：主色 / 强调 / 背景 / 正文 / 次要。一篇只用一套，主色贯穿。

### 冷 · 科技 / 数据 / 客观

| 名 | 主色 | 强调 | 背景 | 正文 | 次要 | 适合 |
|---|---|---|---|---|---|---|
| 墨蓝科技 | `#1d4ed8` | `#06b6d4` | `#f8fafc` | `#1e293b` | `#64748b` | 技术发布、产品评测 |
| 青绿理性 | `#0f9b8a` | `#0a7368` | `#f4f4f6` | `#1d1d1f` | `#6e6e73` | AI 评论、工具横评 |
| 石墨极简 | `#1f2937` | `#6b7280` | `#ffffff` | `#111827` | `#9ca3af` | 深度分析、专业观点 |

### 暖 · 故事 / 情感 / 生活

| 名 | 主色 | 强调 | 背景 | 正文 | 次要 | 适合 |
|---|---|---|---|---|---|---|
| 宣纸本草 | `#b8453a` | `#6b7355` | `#f7f2e9` | `#2b2724` | `#5a534c` | 中医/传统文化、生活随笔 |
| 暖橙手记 | `#ea580c` | `#fbbf24` | `#fffbeb` | `#292524` | `#78716c` | 接单/创业故事、日常复盘 |
| 奶咖温润 | `#a16207` | `#d97706` | `#fdfaf3` | `#44403c` | `#a8a29e` | 情感、亲子、慢生活 |

### 强 · 观点 / 争议 / 评论

| 名 | 主色 | 强调 | 背景 | 正文 | 次要 | 适合 |
|---|---|---|---|---|---|---|
| 朱墨对阵 | `#b91c1c` | `#e0651a` | `#fafaf9` | `#1c1917` | `#57534e` | 行业争议、口水战、批判 |
| 深空电光 | `#4f46e5` | `#ec4899` | `#0f172a` | `#e2e8f0` | `#94a3b8` | 前沿观点、夜间感专题（深底白字） |

### 柔 · 极简 / 随笔

| 名 | 主色 | 强调 | 背景 | 正文 | 次要 | 适合 |
|---|---|---|---|---|---|---|
| 留白禅意 | `#57534e` | `#a8a29e` | `#ffffff` | `#292524` | `#a8a29e` | 深度思考、极简生活 |
| 雾蓝静谧 | `#475569` | `#94a3b8` | `#f8fafc` | `#334155` | `#94a3b8` | 科普、知识整理 |

---

## 二、版式气质光谱

定调时在这几条轴上定位，决定行距、间距、对比强度：

- **密度**：紧凑（教程/盘点，行距 1.6–1.7）↔ 疏朗（随笔/故事，行距 1.85–2.0）
- **对比**：强（观点/争议，大字号差 + 色块）↔ 弱（科普/随笔，统一字号 + 细线）
- **温度**：冷（科技）↔ 暖（生活）
- **正式度**：高（报告）↔ 低（口语/段子）

段落间距 14–20px；章节间距 28–40px。

---

## 三、组件样式库（全内联 + leaf 包裹）

换色只改十六进制值。示例用「青绿理性」配色（主 `#0f9b8a` / 强 `#0a7368` / 浅底 `#e6f5f2` / 深 `#0a7368`）。

### 标题

**左竖条标题**（最常用，干净）：
```html
<p style="margin:28px 0 14px;font-size:19px;font-weight:800;color:#1d1d1f;border-left:4px solid #0f9b8a;padding-left:12px;line-height:1.5;"><span leaf="">标题文字</span></p>
```

**药丸标签标题**（醒目，适合章节起点）：
```html
<p style="margin:28px 0 14px;"><span style="display:inline-block;background:#0f9b8a;color:#fff;font-size:14px;font-weight:700;padding:5px 16px;border-radius:6px;"><span leaf="">标题文字</span></span></p>
```

**序号 + 标题**（步骤/清单）：
```html
<p style="margin:24px 0 12px;font-size:16px;font-weight:800;color:#1d1d1f;line-height:1.6;"><span style="display:inline-block;background:#e6f5f2;color:#0a7368;border-radius:5px;padding:1px 9px;margin-right:8px;font-weight:900;"><span leaf="">01</span></span><span leaf="">要点标题</span></p>
```

### 正文与强调

**段落**：
```html
<p style="margin:0 0 16px;line-height:1.85;color:#1d1d1f;"><span leaf="">正文内容，关键词用</span><strong style="color:#0a7368;"><span leaf="">主色加粗</span></strong><span leaf="">标出。</span></p>
```

**关键词下划线**：
```html
<span style="border-bottom:2px solid #0f9b8a;"><span leaf="">关键词</span></span>
```

**关键词高亮**（底色马克笔）：
```html
<span style="background:linear-gradient(transparent 60%,#fcd34d 60%);"><span leaf="">关键词</span></span>
```

### 引用 / 金句 / 提示

**金句块**（左竖条 + 浅底）：
```html
<section style="margin:18px 0;padding:16px 20px;background:#f3ece0;border-left:4px solid #b8453a;border-radius:0 8px 8px 0;">
  <p style="margin:0;font-size:16px;font-weight:700;color:#9c3a30;line-height:1.8;"><span leaf="">核心金句文字</span></p>
</section>
```

**提示/旁注块**（左竖条 + 类型小标签）：
```html
<section style="margin:18px 0;padding:14px 18px;background:#f6f8fa;border-left:4px solid #0f9b8a;border-radius:0 8px 8px 0;">
  <p style="margin:0 0 6px;"><span style="display:inline-block;background:#0f9b8a;color:#fff;font-size:11px;font-weight:700;padding:2px 10px;border-radius:4px;letter-spacing:1px;"><span leaf="">提示</span></span></p>
  <p style="margin:0;font-size:14px;color:#374151;line-height:1.8;"><span leaf="">提示或旁注正文</span></p>
</section>
```
小标签文字可换：`提示 / 注意 / 重点 / 旁注 / 案例`。

### 对阵 / 优缺点（上下堆叠，别并排）

**优点块**：
```html
<section style="background:#f0faf3;border-radius:8px;padding:16px;margin-bottom:12px;">
  <p style="margin:0 0 10px;color:#16a34a;font-weight:700;font-size:14px;letter-spacing:1px;"><span leaf="">✓ 优点</span></p>
  <p style="margin:0 0 8px;font-size:14.5px;line-height:1.75;"><span leaf="">✓ 优点内容一</span></p>
  <p style="margin:0;font-size:14.5px;line-height:1.75;"><span leaf="">✓ 优点内容二</span></p>
</section>
```

**缺点块**：同结构，底色 `#fdf3f2`、字色 `#dc2626`。

### 数据 / 跑分块（深底等宽，突出数字）

```html
<span style="font-family:monospace;background:#0f172a;color:#5eead4;padding:2px 7px;border-radius:4px;font-size:14px;font-weight:600;"><span leaf="">88.8%</span></span>
```

### 落点 / CTA 块（纯色底白字）

```html
<section style="background:#0a7368;color:#fff;border-radius:10px;padding:20px 22px;margin:24px 0;">
  <p style="margin:0;font-size:15.5px;line-height:1.8;"><span leaf="">落点/总结文字，给读者的一句话。</span></p>
</section>
```
（纯色最稳；要更花可用 `background:linear-gradient(135deg,#0f9b8a,#0a7368);`。）

### 分隔线

```html
<p style="text-align:center;color:#e5e5ea;letter-spacing:6px;margin:24px 0;font-size:12px;"><span leaf="">— — —</span></p>
```

### 代码块（多行）

```html
<section style="margin:0 0 20px;border-radius:8px;overflow:hidden;background:#1E293B;">
  <section style="padding:11px 14px;">
    <p style="margin:0;font-family:monospace;font-size:13px;line-height:1.6;color:#E2E8F0;"><span leaf="">def hello():</span></p>
    <p style="margin:0;font-family:monospace;font-size:13px;line-height:1.6;color:#E2E8F0;"><span leaf="">　　print("hi")</span></p>
  </section>
</section>
```
要点：每行一个 `<p style="margin:0">`，不用 `white-space:pre`，缩进用全角空格 `　`。

### 图片

```html
<section style="margin:0 0 16px;">
  <span leaf=""><img src="图片URL" style="max-width:100%;height:auto;display:block;margin:0 auto;"></span>
</section>
<p style="font-size:12px;color:#9CA3AF;text-align:center;margin:0 0 20px;"><span leaf="">— 图片说明（无说明则删此行）</span></p>
```

---

## 四、抉择心法

1. **先气质后配色**：先定"这篇该是什么感觉"，再选/调配色。不要先挑好看的颜色再硬套内容。
2. **一个主色打天下**：主色贯穿标题/强调/标签；强调色只用在 2–3 处真正的重点。色多等于没重点。
3. **留白是风格**：疏朗比堆砌高级。段落、章节间留够气口，尤其故事/随笔类。
4. **混搭鼓励**：本草风的配色 + 科技风的左竖条标题，只要协调，完全 OK。素材池是乐高，不是模具——**匹配内容永远是第一优先级**。
5. **强调手段统一**：全文锁定 1–2 种强调（如：左竖条标题 + 主色加粗），不要每段换花样。
