# 微信公众号编辑器 HTML 兼容规则

公众号编辑器粘贴富文本时会**过滤**大量 HTML/CSS。下面是确定性规则（来源：实测归纳），违反 ERROR 项 = 粘贴后被过滤或样式失效。

## 一、禁用（ERROR，粘贴后失效）

| 禁用 | 原因 | 替代 |
|---|---|---|
| `<style>` 块 | 整块被过滤 | 样式全部内联 `style="..."` |
| `<script>` | 被过滤 | 不用 |
| `<div>` | 被改写/丢样式 | 用 `<section>` |
| `<link>` 外部 CSS/字体 | 被过滤 | 内联 |
| `class="..."` | 被剥离 | 内联 style |
| `id="..."` | 被剥离 | 不用 |
| `position:fixed/absolute/sticky` | 不支持 | 用文档流 |
| `float` | 不支持 | 用 `display:flex` 或上下堆叠 |
| `@media` 媒体查询 | 不支持 | 写死，别做响应式 |
| `@keyframes` / `@import` | 不支持 | 不用动画 |
| `display:grid` | 不支持 | 用 flex 或堆叠 |
| CSS 变量 `var(--x)` | 不支持 | 写死十六进制值 |
| 外部字体 `url(x.woff2/ttf)` | 不支持 | 用系统字体栈 |
| 伪元素 `::before/::after` | 不支持 | 把符号/装饰写进 HTML 文本 |

## 二、必须

1. **样式全部内联**：每个元素 `style="..."`。不写 `<style>`，不用 class。
2. **文字节点用 `<span leaf="">` 包裹**（最关键）。公众号靠这个识别样式归属。任何中文文字（段落、标题、列表项、标签里的字）都要包：
   ```html
   <p style="margin:0 0 16px;line-height:1.85;color:#1d1d1f;">
     <span leaf="">这是正文文字，关键词用</span>
     <strong style="color:#0a7368;"><span leaf="">主色加粗</span></strong>
     <span leaf="">标出。</span>
   </p>
   ```
   不包裹 → 粘贴后该处样式丢失。这是最高频返工点，靠校验脚本兜底。
3. **容器用 `<section>`**，不用 `<div>`。
4. **中文标点全角**：，。！？：；""''（）—— ……。不用半角 `, . ! ? : ;` 和英文直引号 `" '`。
   - 例外：代码块、行内代码、URL、英文专名/代码标识符内部保持原样，不要"全角化"代码。

## 三、可用

- **标签**：`<section> <p> <span> <strong> <img> <h3> <br>`（`<h1>/<h2>` 也可，但公众号对标题样式可控性差，建议用 `<p>` + 内联模拟标题，更稳）。
- **样式属性**：`color` `background` `background-color` `border` `border-radius` `padding` `margin` `font-size` `font-weight` `line-height` `text-align` `letter-spacing` `box-shadow` `display:flex` `linear-gradient` `max-width`。
- `display:flex` 有限可用，但**慎做多栏并排**（手机窄，挤塌）；多栏内容改上下堆叠更稳。
- `linear-gradient`、`box-shadow`、`border-radius` 可用，是少数能保留的装饰性属性。

## 四、输出片段格式

公众号编辑器只接受**正文片段**。交付的"粘贴用"文件应是：

```html
<section style="max-width:680px;margin:0 auto;padding:20px 16px;font-size:16px;line-height:1.85;color:#1d1d1f;">
  ...正文...
</section>
```

**不要**包 `<!DOCTYPE> <html> <head> <body>`。文档外壳仅用于浏览器预览，粘贴时只用其中 section。

> 若用户需要浏览器预览页，可在外层再套一个预览壳（带"复制"按钮），但被复制的核心仍是这一个 `<section>`。

## 五、组件级要点（速查）

- **段落**：`<p style="margin:0 0 16px;line-height:1.85;"><span leaf="">…</span></p>`
- **图片**：`<span leaf=""><img src="…" style="max-width:100%;height:auto;display:block;margin:0 auto;"></span>`，不用 `width:100%`。
- **代码块**：每行一个 `<p style="margin:0;font-family:monospace;font-size:13px;line-height:1.6;"><span leaf="">代码行</span></p>`，**不用 `white-space:pre`**（会把源码缩进渲染成大空白），缩进用全角空格 `　`。
- **行内代码**：`<span style="background:#f1f5f9;color:#0f9b8a;padding:1px 6px;border-radius:4px;font-family:monospace;font-size:14px;"><span leaf="">code</span></span>`
- **多栏（优缺点/对比）**：上下堆叠两个 `<section>` 块，不要 flex 并排（手机会挤）。

## 六、字体

公众号基本忽略 `font-family`（用自己的字体），写了无效但无害。可设系统栈兜底：`-apple-system,'PingFang SC','Microsoft YaHei',sans-serif`。**不要依赖特定字体**做排版效果（如衬线/楷体），手机端大概率不生效。

## 七、校验脚本

生成后必跑 `<SKILL_ROOT>/scripts/validate_html.py`，它确定性地检查：
- 所有 ERROR 项（禁用标签/属性/样式）
- `<span leaf="">` 包裹是否完整（中文文字未被包裹会报 WARNING/ERROR）
- 正文半角标点/英文引号（代码块内不计）

退出码 1 = 有 ERROR 必须修；0 = 通过。
