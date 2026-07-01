# 我用 LangChain 搭了个能"理解关系"的知识库，比纯向量检索准太多了

> 从只会调 API，到能搭 GraphRAG，一个前端程序员的踩坑记录。

---

上个月我在抖音上接了个单——帮一家小公司搭内部知识库。

需求听着很简单：把公司文档扔进去，员工用自然语言提问，AI 回答。

我第一反应：这不就是 LangChain + 向量数据库吗？半天搞定。

结果翻车了。

---

## 纯向量 RAG 翻车现场

测试时老板问了句："老王负责的那个项目的预算是多少？"

AI 回答了一堆乱七八糟的数字。

我一看，问题出在哪——

向量检索是把文档切成小块存起来的。每个块都是孤立的，它们之间没有"关系"。

"老王"在一段里，"项目 A"在另一段里，"预算 50 万"又在第三段里。向量检索能分别找到这些片段，但它**不知道老王和项目 A 之间有个"负责"关系，更不知道项目 A 和 50 万之间有"预算"关系**。

就像你问一个人"你同事的宠物叫什么"，但他只有一沓乱序的便签纸，每张纸上写了一句不相关的话——能答对才怪。

这就是纯向量 RAG 的死穴：**多跳推理完全不行。**

---

## GraphRAG 的思路

既然问题出在"关系"上，那就把关系存起来。

知识图谱的思路很简单：知识不只是文本，还是实体和关系。

```
老王 --[负责]--> 项目A --[预算]--> 50万
```

这样问"老王负责的项目预算"，就能沿着关系链一路走到答案。

这就是 **GraphRAG**——**向量检索 + 知识图谱**，2025-2026 年最热的 RAG 方向。

LangChain 已经原生支持这套东西了，我来把踩坑后的经验写下来。

---

## 搭环境

```bash
pip install langchain langchain-experimental langchain-openai \
            langchain-community neo4j tiktoken
```

Neo4j 用 Docker 起最简单：

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

---

## 核心一步：从文档自动建知识图谱

以前建知识图谱是体力活——人工标注实体、定义关系。但现在 LangChain 的 `LLMGraphTransformer` 能自动完成。

**这里有个巨大的坑：必须限制 schema。**

刚开始我没加任何限制，就让 LLM 自由发挥。结果同一个文档跑了两次，抽取出来的实体名和关系完全不一样——第一次叫"王工"，第二次叫"老王"，"张三"有时是 Person，有时变成 Employee。

不加 schema，LLM 就是脱缰野马。

```python
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 关键：定义实体类型和关系，缩小 LLM 发挥空间
allowed_nodes = ["Person", "Project", "Department", "Document", "Technology"]
allowed_relationships = [
    ("Person", "MANAGES", "Project"),
    ("Person", "BELONGS_TO", "Department"),
    ("Project", "HAS_BUDGET", "Budget"),
    ("Project", "USES", "Technology"),
]

transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
    strict_mode=True,  # 不符合 schema 的输出直接丢弃
)

# 异步批量处理，快了不止一点
graph_documents = await transformer.aconvert_to_graph_documents(documents)
```

**strict_mode=True 是最重要的参数**——LLM 有时候会"创造"不在 schema 里的实体类型，这个参数直接过滤掉。

---

## 导入 Neo4j 并建索引

```python
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="password123"
)

graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,   # 所有节点打上 __Entity__ 标签，查询优化
    include_source=True,     # 保留原文引用，方便溯源
)
```

导入后去 Neo4j 浏览器（http://localhost:7474）就能看到图谱了。

---

## 查询：GraphCypherQAChain

有了图谱，怎么用自然语言查询？

LangChain 的 `GraphCypherQAChain` 会自动把自然语言转成 Cypher 查询语句，执行后把结果喂给 LLM 合成答案：

```python
from langchain.chains import GraphCypherQAChain

cypher_llm = ChatOpenAI(model="gpt-4o", temperature=0)        # 写 Cypher 用强模型
qa_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)       # 合成答案用便宜模型

chain = GraphCypherQAChain.from_llm(
    cypher_llm=cypher_llm,
    qa_llm=qa_llm,
    graph=graph,
    validate_cypher=True,   # 执行前校验语法
    top_k=5,
)

# 多跳查询
response = chain.invoke({"query": "老王负责的项目用了哪些技术栈？"})
```

**为什么要用两个模型？** 写 Cypher 是逻辑推理，用强模型；合成答案是拼字符串，便宜模型就行。成本能省一半。

---

## 向量 + 图谱混合检索

纯图谱也有问题——有些知识是模糊的，不适合用图谱表达（比如"公司文化"、"做事风格"）。

生产环境最好的方案是**混合检索**：

```python
from langchain.retrievers import EnsembleRetriever

# 向量检索器（你原来的 RAG）
vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# 图谱检索器
graph_retriever = GraphCypherRetriever(graph=graph, llm=llm)

# 混合，图谱权重更高
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, graph_retriever],
    weights=[0.3, 0.7]
)
```

**实际测试对比：**

| 查询类型 | 纯向量 RAG | GraphRAG（图谱） | 混合检索 |
|----------|-----------|-----------------|---------|
| "老王的项目预算" | ❌ 答错 | ✅ 正确 | ✅ 正确 |
| "公司什么时候成立的" | ✅ 正确 | ❌ 无关 | ✅ 正确 |
| "谁跟老王做同一个项目" | ❌ 答非所问 | ✅ 正确 | ✅ 正确 |

混合检索两个都能答对，因为向量补了图谱的"模糊知识"短板。

---

## 一个前端程序员的理解

说实话，第一次接触知识图谱的时候我觉得这玩意太高深了——Neo4j、Cypher、图谱遍历，听着就像算法岗的东西。

但实际搭完之后发现，LangChain 把最复杂的部分封装得很好了。你只需要：

1. 想清楚你要哪些实体类型和关系（这步最需要动脑子）
2. 用 `LLMGraphTransformer` 自动抽取
3. 用 `GraphCypherQAChain` 自动查询

真正难的不是代码，是**定义 schema**——你得理解业务，知道什么实体重要、什么关系有用。

这其实跟前端做状态设计有点像：你设计 Redux store 的时候，也是在定义"实体"和"关系"。只不过这里把 store 换成了图数据库，把 selector 换成了 Cypher 查询。

---

## 踩坑清单

1. **不加 schema 就是灾难**：LLM 每次输出都不一样，知识图谱变成一坨浆糊
2. **Cypher 语法错误**：开启 `validate_cypher=True`，否则生产环境会炸
3. **小模型抽取质量差**：如果用开源 7B 模型，实体抽取成功率可能不到 30%，建议至少用 GPT-4o-mini 级别
4. **图谱会越来越大**：记得定期清理孤立节点，否则查询越来越慢

---

这个项目做了两周，从"RAG 不就是查向量数据库吗"到"原来知识是有结构的"，认知升级了不少。

现在我把代码整理好了，接下一个类似项目可以直接复用。这就是拥有自己技术积累的好处——踩过一次坑，之后的效率是指数级的。

---

*我正在用 AI 把自己从"写页面的"重新训练成"能做产品、能接单"的人。如果这篇文章对你有帮助，欢迎点赞、在看、转发。*

---

**推荐学习资源：**
- [DataCamp: Graph RAG with LangChain and Neo4j](https://www.datacamp.com/courses/graph-rag-with-langchain-and-neo4j)（3小时实战课）
- LangChain 官方文档：Graph Vector Store
- Neo4j + LangChain: GraphReader Agentic RAG
