# 前端学 LangChain：Python 和 TypeScript 双语对照，一篇文章搞懂核心概念

我写页面写了快十年。

去年开始学 AI 开发，第一个碰到的框架就是 LangChain。文档一打开，全是 Python。作为一个写了快十年 TypeScript 的前端，说实话有点懵——不是看不懂，是不知道该不该学 Python 版，还是直接用 LangChain.js。

折腾了几个月，两个版本都用了，我的结论是：**都学，但先从你熟悉的那边开始。**

这篇文章就是我想给半年前的自己写的。用 TypeScript 和 Python 双语对照的方式，把 LangChain 最核心的概念一次讲清楚。你不用纠结先学哪个语言——对照着看，反而学得更快。

## LangChain 到底是什么

一句话：**LangChain 是帮你把大模型、提示词、工具、记忆这些零件组装成一个完整 AI 应用的框架。**

打个比方。大模型（GPT、Claude、DeepSeek）就像发动机。但光有发动机不能上路，你还需要方向盘、变速箱、油箱、仪表盘。LangChain 就是把这些零件标准化，让你用几行代码就能拼出一辆能跑的车。

它的核心概念就五个：

| 概念 | 一句话解释 | 类比 |
|------|-----------|------|
| **Model** | 大模型的统一调用接口 | 发动机 |
| **Prompt** | 可复用的提示词模板 | 方向盘——告诉车往哪开 |
| **Chain** | 把多个步骤串成流水线 | 传动轴——把动力传到轮子 |
| **Agent** | 让 AI 自己决定调用什么工具 | 自动驾驶——AI 自己选路线 |
| **Tool** | 给 AI 用的外部工具（搜索、计算等） | 导航仪、雷达——给车加感知能力 |

搞懂这五个，LangChain 就入门了。下面我们用代码一个个讲。

## 环境搭建

先别急着写代码，把环境搞起来。

### Python 版

```bash
# 建议用虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate

# 安装核心包
pip install langchain langchain-openai
```

### TypeScript 版

```bash
# 初始化项目
npm init -y

# 安装核心包
npm install @langchain/core @langchain/openai
```

两个版本都需要设置 OpenAI 的 API Key：

```bash
export OPENAI_API_KEY="sk-你的key"
```

如果你用的是国内模型（比如 DeepSeek），后面会讲怎么切换，先拿 OpenAI 跑通。

## 第一步：调一下模型

这是 LangChain 的 Hello World——直接调用大模型，拿一个回复。

### Python

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 初始化模型
llm = ChatOpenAI(model="gpt-4o-mini")

# 发消息
response = llm.invoke([HumanMessage(content="用一句话解释什么是前端开发")])

print(response.content)
```

### TypeScript

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";

// 初始化模型
const llm = new ChatOpenAI({ modelName: "gpt-4o-mini" });

// 发消息
const response = await llm.invoke([
  new HumanMessage("用一句话解释什么是前端开发"),
]);

console.log(response.content);
```

对比一下，两段代码几乎一模一样。唯一不同的是语法层面的：Python 用 `ChatOpenAI(model=...)` 关键字参数，TS 用 `new ChatOpenAI({ modelName: ... })` 对象参数。

如果你写过 Node.js，TS 版上手零门槛。如果你没写过 Python，看到这里应该也觉得不太难——Python 确实简洁。

## 第二步：Prompt Template，让提示词可复用

直接写字符串没问题，但当你需要动态替换变量的时候，Prompt Template 就派上用场了。

### Python

```python
from langchain_core.prompts import ChatPromptTemplate

# 创建提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，用通俗易懂的语言回答问题。"),
    ("human", "{question}"),
])

# 填入变量，生成完整的消息列表
messages = prompt.invoke({
    "role": "资深前端工程师",
    "question": "React 和 Vue 该学哪个？"
})
```

### TypeScript

```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts";

// 创建提示词模板
const prompt = ChatPromptTemplate.fromMessages([
  ["system", "你是一个{role}，用通俗易懂的语言回答问题。"],
  ["human", "{question}"],
]);

// 填入变量
const messages = await prompt.invoke({
  role: "资深前端工程师",
  question: "React 和 Vue 该学哪个？",
});
```

关键区别就一个：TS 版的 `invoke` 是异步的，需要 `await`。Python 版的 `invoke` 是同步的（LangChain Python 在 v0.2 之后默认同步，异步用 `ainvoke`）。

这个设计差异是两个语言的习惯决定的——Node.js 天生异步，Python 的 asyncio 是后加的。

## 第三步：Chain，把步骤串起来

单独的模型调用和 Prompt 模板还不够强。Chain 的作用是把它们串成一个流水线。

用 `|` 管道符，Python 版的 Chain 写起来特别优雅。TS 版用 `.pipe()` 方法，思路一样。

### Python

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建组件
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，回答要简洁。"),
    ("human", "{topic}是什么？用三句话说清楚。"),
])

# 用管道符串成 Chain
chain = prompt | llm | StrOutputParser()

# 执行
result = chain.invoke({
    "role": "前端工程师",
    "topic": "LangChain"
})

print(result)
```

### TypeScript

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

// 创建组件
const llm = new ChatOpenAI({ modelName: "gpt-4o-mini" });
const prompt = ChatPromptTemplate.fromMessages([
  ["system", "你是一个{role}，回答要简洁。"],
  ["human", "{topic}是什么？用三句话说清楚。"],
]);

// 用 pipe 串成 Chain
const chain = prompt.pipe(llm).pipe(new StringOutputParser());

// 执行
const result = await chain.invoke({
  role: "前端工程师",
  topic: "LangChain",
});

console.log(result);
```

看到区别了吗？

Python 用 `prompt | llm | parser`，像 shell 管道一样直观。TS 用 `prompt.pipe(llm).pipe(parser)`，链式调用，前端应该很熟悉。

两种写法背后的逻辑完全一样：**把 Prompt 模板的输出 → 喂给模型 → 模型输出 → 喂给解析器 → 拿到纯文本字符串。**

这就是 Chain。数据像流水线一样从一个组件流到下一个。

## 第四步：Agent，让 AI 自己决定怎么做

Chain 是你提前定好步骤。Agent 更进一步——**你只给目标，AI 自己决定用哪些工具、分几步完成。**

这是 LangChain 最强大的能力，也是最让新手懵的部分。

下面写一个最简单的 Agent：给 AI 一个搜索工具，让它自己决定要不要搜索。

### Python

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义一个工具
@tool
def search(query: str) -> str:
    """搜索互联网获取最新信息"""
    # 这里应该是真实的搜索 API 调用
    # 演示用，直接返回模拟数据
    return f"搜索结果：{query} 的最新信息..."

# 创建带工具的 Agent
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, [search])

# 执行
result = agent.invoke({
    "messages": [{"role": "user", "content": "2025年最新的前端框架有哪些？"}]
})

print(result["messages"][-1].content)
```

### TypeScript

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

// 定义一个工具
const searchTool = tool(
  async ({ query }: { query: string }) => {
    // 这里应该是真实的搜索 API 调用
    return `搜索结果：${query} 的最新信息...`;
  },
  {
    name: "search",
    description: "搜索互联网获取最新信息",
    schema: z.object({ query: z.string() }),
  }
);

// 创建带工具的 Agent
const llm = new ChatOpenAI({ modelName: "gpt-4o-mini" });
const agent = createReactAgent({ llm, tools: [searchTool] });

// 执行
const result = await agent.invoke({
  messages: [{ role: "user", content: "2025年最新的前端框架有哪些？" }],
});

console.log(result.messages[result.messages.length - 1].content);
```

这里有个重要区别：**TS 版定义工具需要用 `zod` 做参数校验。** 因为 TypeScript 没有运行时类型，所以 LangChain.js 用 zod schema 来告诉模型这个工具接受什么参数。Python 有类型注解，直接用 `@tool` 装饰器就够了。

另外注意，Agent 这块现在推荐用 **LangGraph**（LangChain 团队的新框架）的 `createReactAgent`，而不是 LangChain 旧版的 Agent 类。两个语言都一样。

## Python 还是 TypeScript？我的真实建议

学了两个月，两个版本都写过项目，说说我的真实感受：

**如果你和我一样是前端出身，先学 TypeScript 版。**

原因很实际：

1. 你不用同时学两样东西（一门新语言 + 一个新框架）。用 TS 学 LangChain 的概念，上手快很多。
2. TS 版的功能现在跟得很紧，核心能力都有。`@langchain/core` 在 npm 上每周下载量超过 120 万，生态已经成熟了。
3. 前后端统一语言，做全栈 AI 应用更顺畅。你可以在 Next.js 项目里直接用 LangChain.js。

**但 Python 版不能不学。**

因为：

1. AI 领域的教程、论文、开源项目，90% 是 Python。你搜到的任何高级用法，Python 示例一定比 TS 多。
2. Python 版有 1000+ 集成（向量数据库、RAG 工具、各类模型），TS 版大概几百个，差距还在。
3. 有些功能 TS 版会晚几个月才跟上。

**我的路线是：先用 TS 版搞懂概念、跑通项目，再学 Python 补齐生态。** 两个版本的 API 设计几乎对称，学了一个另一个上手很快。

这篇文章里的代码就是证据——你看 Python 和 TS 的写法，核心逻辑一模一样，区别就是语法糖。

## 学完这篇，下一步干什么

如果你跟着把上面的代码都跑了一遍，恭喜，你已经掌握了 LangChain 的核心骨架。

接下来可以按这个顺序继续：

1. **接上真实的搜索 API**——把上面的 Agent Demo 里的模拟搜索换成 Tavili 或 SerpAPI，做一个真正能上网查资料的 AI。
2. **学 RAG（检索增强生成）**——让 AI 读取你自己的文档、知识库。这是 LangChain 最热门的使用场景。
3. **学 LangGraph**——比 Chain 更灵活的工作流编排。Agent 的未来在 LangGraph。

官方资源：

Python 文档：https://python.langchain.com/
TypeScript 文档：https://js.langchain.com/
LangGraph 文档：https://langchain-ai.github.io/langgraph/

