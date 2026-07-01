# Playwright 和 Puppeteer 怎么选？

做 Node 自动化爬虫，经常会遇到两个选择：

Playwright，还是 Puppeteer？

这两个工具都能控制浏览器，都能打开页面、点击按钮、输入内容、截图、抓取 DOM、监听网络请求。

但它们适合的场景不太一样。

**如果只想要结论：新项目优先选 Playwright；已有 Puppeteer 项目稳定运行，就继续用 Puppeteer；只做 Chrome 相关的小脚本，Puppeteer 仍然够用。**

## 一句话区别

Puppeteer 更像一个 Chrome 自动化工具。

Playwright 更像一套完整的浏览器自动化框架。

Puppeteer 最早就是围绕 Chrome/Chromium 自动化设计的，API 简单，资料多，写小脚本很顺手。

Playwright 后来出现，但工程能力更完整，默认支持 Chromium、Firefox、WebKit，也就是更适合多浏览器和长期维护场景。

## 核心对比

| 对比项 | Puppeteer | Playwright |
|---|---|---|
| 维护方 | Chrome 团队 | Microsoft |
| 主要定位 | Chrome 自动化 | 跨浏览器自动化 |
| 浏览器支持 | Chrome/Chromium 为主，也支持 Firefox | Chromium、Firefox、WebKit |
| API 复杂度 | 更简单 | 稍完整 |
| 自动等待 | 有，但相对弱一些 | 更强，默认体验更好 |
| 调试能力 | 基础能力够用 | Trace、录制、测试报告更完整 |
| 测试体系 | 需要自己组合 | 官方测试框架更完整 |
| 适合场景 | 小脚本、截图、PDF、Chrome 自动化 | 长期项目、复杂交互、多浏览器、自动化测试 |

## 爬虫场景怎么选？

先说一个前提：

如果页面能直接请求接口，就不要上浏览器自动化。

浏览器自动化很重。

启动浏览器、加载资源、执行 JS，成本都比普通 HTTP 请求高。

所以选型顺序应该是：

能用接口抓，就用接口。

能用 HTML 解析，就用 HTML 解析。

只有页面必须执行 JS、必须登录、必须点击、必须滚动加载时，再用 Playwright 或 Puppeteer。

> [!NOTE]
> 浏览器自动化不是爬虫的第一选择，而是普通请求和 HTML 解析解决不了时的后备方案。

如果进入浏览器自动化这一步，我的建议是：

简单页面，Puppeteer 可以。

复杂流程，Playwright 更稳。

长期维护，Playwright 更合适。

## 为什么新项目更推荐 Playwright？

主要有三个原因。

第一，跨浏览器能力更完整。

Playwright 同时支持 Chromium、Firefox、WebKit。

如果你后面要做自动化测试，或者希望脚本在不同浏览器环境下更稳定，Playwright 的基础更好。

第二，自动等待体验更好。

浏览器自动化最常见的问题不是代码不会写，而是脚本不稳定。

元素还没出来就点击。

页面还没跳转完就取数据。

接口还没返回就开始处理。

这类问题在爬虫和自动化测试里非常常见。

Playwright 的 locator 和操作 API 默认做了更多等待和可操作性判断，能少写很多 `waitForTimeout`。

第三，调试和维护工具更完整。

Playwright 有 trace、codegen、测试报告等配套能力。

脚本失败时，不只是看到一段报错，而是可以回放执行过程，定位哪一步出了问题。

这对长期项目很重要。

## Puppeteer 什么时候更合适？

Puppeteer 不是过时工具。

它仍然很适合这些场景：

只针对 Chrome/Chromium。

写一次性自动化脚本。

生成网页截图。

生成 PDF。

做简单页面抓取。

已有项目已经稳定运行。

团队已经熟悉 Puppeteer。

如果你的需求很简单，用 Puppeteer 反而更轻。

不要为了“更完整”，把一个半小时能写完的脚本做复杂。

## 直接给选型建议

| 场景 | 建议 |
|---|---|
| 新项目 | Playwright |
| 长期维护的爬虫 | Playwright |
| 登录、跳转、弹窗、滚动加载 | Playwright |
| 顺便做端到端测试 | Playwright |
| Chrome 小脚本 | Puppeteer |
| 截图或生成 PDF | Puppeteer |
| 老项目 Puppeteer 已经稳定 | 不要为了迁移而迁移 |

## 我的最终结论

Playwright 和 Puppeteer 都能做浏览器自动化。

区别不在于“谁能不能做”，而在于“谁更适合长期维护”。

我的选型规则很简单：

**新项目、复杂流程、长期维护：Playwright。**

**简单脚本、Chrome 专用、已有稳定项目：Puppeteer。**

对大多数现在新写的 Node 自动化爬虫来说，我会优先选 Playwright。

它的上手成本高不了多少，但稳定性、调试能力和后续扩展空间更好。
