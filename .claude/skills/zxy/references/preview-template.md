# 预览页模板（带「复制到公众号」按钮）

交付时默认生成 `{名}_预览.html`：把干净正文 `<section>` 放进下面的外壳，浏览器打开后点右上角「复制到公众号」按钮，一键复制 section 富文本，粘进公众号编辑器即可。

**外壳只给浏览器用**：里面的 `<div>` / `<script>` / `id` / `class` 都不进公众号——公众号只收被复制的 `<section>`。**校验脚本不要跑预览页**（会误报 div/script/id），只跑干净正文文件。

## 模板

把 `<!-- 正文 section 放这里 -->` 那一行替换为你的干净正文 `<section>…</section>`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>预览 · 复制到公众号</title>
<style>
  body{margin:0;background:#f3f4f6;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;}
  #toolbar{position:sticky;top:0;background:#fff;border-bottom:1px solid #e5e5ea;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,.05);z-index:10;}
  #toolbar .title{font-size:13px;color:#6e6e73;}
  #copyBtn{background:#0a7368;color:#fff;border:none;border-radius:6px;padding:8px 18px;font-size:14px;font-weight:600;cursor:pointer;}
  #copyBtn:hover{background:#0f9b8a;}
  #stage{max-width:680px;margin:24px auto;background:#fff;padding:24px 16px;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.06);}
</style>
</head>
<body>
  <div id="toolbar">
    <span class="title">公众号排版预览</span>
    <button id="copyBtn" onclick="copyArticle()">复制到公众号</button>
  </div>
  <div id="stage">
    <!-- 正文 section 放这里（干净，无 id/class） -->
  </div>
<script>
function copyArticle(){
  var sec = document.querySelector('#stage > section');
  if(!sec){ alert('未找到正文'); return; }
  var range = document.createRange();
  range.selectNodeContents(sec);
  var sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  try{
    document.execCommand('copy');
    var b = document.getElementById('copyBtn');
    b.textContent = '已复制 ✓';
    setTimeout(function(){ b.textContent = '复制到公众号'; }, 1500);
  }catch(e){
    alert('复制失败，请在预览区手动 Ctrl/⌘+A 全选后 Ctrl/⌘+C 复制');
  }
  sel.removeAllRanges();
}
</script>
</body>
</html>
```

## 实现要点

- **正文 section 保持干净**（无 id/class），放进 `<div id="stage">` 里。JS 用 `document.querySelector('#stage > section')` 定位——靠"stage 的第一个 section 子节点"识别，不需要给正文 section 加任何属性。
- **复制用 `document.execCommand('copy')` + `Range.selectNodeContents()`**：精确选中正文 section 全部内容（含嵌套子 section），等价 Ctrl+A 但只限正文区，不会带进工具条/按钮等杂质。
- **按钮反馈**：点击后变「已复制 ✓」1.5 秒；execCommand 失败（极少数浏览器）兜底提示手动全选。
- **外壳样式与正文互不干扰**：toolbar、背景、`#stage` 是预览页观感；正文 section 用自己的内联样式。`#stage` 这个 div 留在浏览器，不进粘贴内容。
- **校验只跑干净正文**：`{名}_公众号.html` 必须过 `validate_html.py`；预览页 `{名}_预览.html` 含 div/script/id 是正常的，不要拿它校验。
