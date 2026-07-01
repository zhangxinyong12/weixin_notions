# LightRAG 技术调研报告

> **项目**: [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG)
> **论文**: *"LightRAG: Simple and Fast Retrieval-Augmented Generation"* — EMNLP 2025
> **Stars**: 10,000+ | **许可**: MIT | **Python**: ≥ 3.10
> **调研日期**: 2026-06-09

---

## 目录

1. [项目概况](#1-项目概况)
2. [核心架构](#2-核心架构)
3. [数据结构设计](#3-数据结构设计)
4. [LLM 驱动的图谱构建](#4-llm-驱动的图谱构建)
5. [查询与检索机制](#5-查询与检索机制)
   - 5.1 [查询处理：不做改写，仅提取关键词](#51-查询处理不做改写仅提取关键词)
   - 5.2 [两步混合检索：向量入口 + 图遍历扩展](#52-两步混合检索向量入口--图遍历扩展)
   - 5.3 [五种查询模式](#53-五种查询模式)
   - 5.4 [Token 预算控制](#54-token-预算控制)
   - 5.5 [Reranker 支持](#55-reranker-支持)
6. [增量更新设计](#6-增量更新设计)
   - 6.1 [核心原则：只处理新文档](#61-核心原则只处理新文档)
   - 6.2 [Set Merge 合并流程](#62-set-merge-合并流程)
   - 6.3 [旧文档数据完全不动](#63-旧文档数据完全不动)
   - 6.4 [唯一的额外开销：LLM 摘要合并](#64-唯一的额外开销llm-摘要合并)
   - 6.5 [文档删除](#65-文档删除)
7. [多模态支持](#7-多模态支持)
8. [模型与存储配置](#8-模型与存储配置)
   - 8.1 [支持的 LLM 提供商](#81-支持的-llm-提供商)
   - 8.2 [四个 LLM 角色独立配置](#82-四个-llm-角色独立配置)
   - 8.3 [Embedding 提供商](#83-embedding-提供商)
   - 8.4 [向量与图数据库](#84-向量与图数据库)
   - 8.5 [DeepSeek 配置示例](#85-deepseek-配置示例)
9. [多知识库隔离](#9-多知识库隔离)
   - 9.1 [Workspace 机制原理](#91-workspace-机制原理)
   - 9.2 [SDK 多知识库用法](#92-sdk-多知识库用法)
   - 9.3 [API Server 多实例](#93-api-server-多实例)
   - 9.4 [隔离边界](#94-隔离边界)
10. [部署方式](#10-部署方式)
   - 10.1 [安装](#101-安装)
   - 10.2 [Docker 部署](#102-docker-部署)
   - 10.3 [关键环境变量](#103-关键环境变量)
   - 10.4 [SDK 快速使用](#104-sdk-快速使用)
11. [性能基准](#11-性能基准)
12. [适用场景分析](#12-适用场景分析)
13. [与同类方案对比](#13-与同类方案对比)
14. [注意事项与风险](#14-注意事项与风险)

---

## 1. 项目概况

LightRAG 是由**香港大学数据科学实验室 (HKUDS)** 开发的轻量级图结构增强 RAG 框架。核心创新在于将**知识图谱 (Knowledge Graph)** 与**向量检索**融合到统一框架中，解决传统 RAG "扁平分块"导致的上下文碎片化和跨文档推理能力弱的问题。

### 核心理念

```
传统 RAG:  文档 → 固定大小分块 → 向量化 → 相似度检索 → LLM 回答
              ❌ 实体关系丢失、跨块上下文断裂

LightRAG:  文档 → 实体/关系提取 → 知识图谱 + 向量嵌入 → 双层检索 → LLM 回答
              ✅ 保留语义关联、支持跨文档推理
```

---

## 2. 核心架构

### 2.1 整体模块结构

```
lightrag/
├── lightrag.py          # 核心类 LightRAG（SDK 入口）
├── operate.py           # 核心操作：实体关系提取、图谱合并、查询检索
├── prompt.py            # 所有 LLM Prompt 模板
├── types.py             # Pydantic 数据模型定义
├── base.py              # 抽象基类（Storage、QueryParam 等）
├── utils_graph.py       # 图谱增删改查、合并、编辑操作
├── kg/                  # 知识图谱存储层（多后端）
│   ├── networkx_impl.py     # NetworkX（默认/开发用）
│   ├── neo4j_impl.py        # Neo4j 图数据库
│   ├── postgres_impl.py     # PostgreSQL 统一存储（含 pgvector）
│   ├── mongo_impl.py        # MongoDB 统一存储
│   ├── milvus_impl.py       # Milvus 向量数据库
│   ├── qdrant_impl.py       # Qdrant 向量数据库
│   ├── faiss_impl.py        # Faiss 向量索引
│   ├── redis_impl.py        # Redis 缓存
│   ├── memgraph_impl.py     # Memgraph 图数据库
│   ├── opensearch_impl.py   # OpenSearch 统一存储
│   └── json_kv_impl.py      # JSON 文件 KV 存储（开发用）
├── llm/                 # LLM 适配层（OpenAI/Ollama/HF/Azure/Bedrock...）
├── api/                 # FastAPI REST 服务器
├── parser/              # 文档解析（MinerU/Docling/Native）
├── chunker/             # 文本分块策略
├── evaluation/          # RAGAS 评估 + Langfuse 追踪
└── pipeline.py          # 文档处理流水线
```

### 2.2 四种存储类型

LightRAG 将存储拆分为四种职责：

| 存储类型 | 用途 | 默认实现 | 生产推荐 |
|----------|------|----------|----------|
| **KV_STORAGE** | LLM 响应缓存、文本分块结果、实体关系提取中间态 | JSON 文件 + 内存 | PostgreSQL / MongoDB |
| **VECTOR_STORAGE** | 文本块、实体、关系的向量嵌入 | NanoVectorDB（内存） | Milvus / Qdrant / pgvector |
| **GRAPH_STORAGE** | 知识图谱节点与边 | NetworkX（内存） | Neo4j / PostgreSQL / Memgraph |
| **DOC_STATUS_STORAGE** | 文档处理状态跟踪 | JSON 文件 | PostgreSQL / MongoDB |

**统一存储方案**：PostgreSQL、MongoDB、OpenSearch 可以同时承担全部四种存储，简化部署。

---

## 3. 数据结构设计

### 3.1 LLM 输出层（Pydantic 模型）

```python
# lightrag/types.py

class ExtractedEntity(BaseModel):
    """LLM 从文本中提取的单个实体"""
    entity_name: str        # 实体名称（title case，如 "Elon Musk"）
    entity_type: str        # 实体类型（Person / Organization / Location / ...）
    entity_description: str # 实体描述（仅基于输入文本，第三人称）


class ExtractedRelationship(BaseModel):
    """LLM 提取的两个实体间的关系"""
    source_entity: str           # 源实体名
    target_entity: str           # 目标实体名
    relationship_keywords: str   # 逗号分隔的关键词，如 "founded, leads"
    relationship_description: str # 关系描述


class EntityExtractionResult(BaseModel):
    """一次提取的完整结果"""
    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]
```

### 3.2 图存储层（Node / Edge）

以默认 NetworkX 为例，底层是 **无向图** `networkx.Graph()`：

```python
# 节点数据（以 entity_name 作为 node_id）
graph.nodes["Elon Musk"] = {
    "entity_id": "Elon Musk",
    "entity_type": "Person",
    "description": "CEO of Tesla and SpaceX, founder of...",
    "source_id": "chunk-abc123<SEP>chunk-def456",  # 来源文本块 ID
    "file_path": "tesla_report.pdf",
    "created_at": 1718000000
}

# 边数据（无向边，source/target 仅语义标记，存储时自动排序）
graph.edges[("Elon Musk", "Tesla")] = {
    "description": "Elon Musk founded Tesla in 2003 and serves as its CEO.",
    "keywords": "founded, leadership, CEO",
    "source_id": "chunk-abc123<SEP>chunk-ghi789",
    "weight": 1.0,
    "file_path": "tesla_report.pdf"
}
```

**关键设计决策**：
- 实体名直接作为节点 ID，不做 ID 映射（简化查询，但限制了重命名场景）
- 关系是无向的：`source > target` 时自动 swap，保证 `("A","B")` 和 `("B","A")` 是同一条边
- 每条边/节点都追踪 `source_id`，支持引用溯源

### 3.3 向量存储层

```python
# 实体向量 (entities_vdb)
# key = MD5("ent-" + entity_name)
"ent-a1b2c3d4": {
    "content": "Elon Musk\nCEO of Tesla and SpaceX...",
    "entity_name": "Elon Musk",
    "source_id": "chunk-abc123<SEP>chunk-def456",
    "description": "CEO of Tesla and SpaceX...",
    "entity_type": "Person"
}

# 关系向量 (relationships_vdb)
# key = MD5("rel-" + sorted_name1 + sorted_name2)
"rel-d4e5f6": {
    "content": "leadership, founded\tElon Musk\nTesla\nElon Musk founded Tesla...",
    "src_id": "Elon Musk",         # 已按字母序排列
    "tgt_id": "Tesla",             # 保证任意方向查到同一条
    "source_id": "chunk-abc123<SEP>chunk-ghi789",
    "description": "Elon Musk founded Tesla in 2003...",
    "keywords": "leadership, founded",
    "weight": 1.0
}
```

**`content` 字段格式**（用于生成 embedding 的文本）：
- 实体: `"{entity_name}\n{description}"`
- 关系: `"{keywords}\t{src_name}\n{tgt_name}\n{description}"`

---

## 4. LLM 驱动的图谱构建

### 4.1 完整索引流水线

```
┌──────────┐   ┌──────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ 文本分块   │ → │  LLM 实体提取  │ → │  解析 + 去重合并   │ → │  写入三层存储     │
│ (Chunker) │   │  (Prompt)    │   │  (Set Merge)     │   │  G+V+KV         │
└──────────┘   └──────────────┘   └──────────────────┘   └─────────────────┘
```

### 4.2 Step 1: 文本分块

支持 4 种策略：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `Fix` | 固定 token 数分块 | 简单场景 |
| `Recursive` | 递归分割（按段落/句子） | 通用场景 |
| `Vector` | 基于向量相似度边界分割 | 语义完整性要求高 |
| `Paragraph` | 按自然段落分割 | 结构化文档 |

每个 chunk 产出：
```python
{
    "tokens": 512,
    "content": "Elon Musk founded Tesla in 2003...",
    "full_doc_id": "doc-xxx",
    "chunk_order_index": 0
}
```

### 4.3 Step 2: LLM 实体关系提取

#### 两种输出模式

**模式 A — 定界符文本格式**（默认，节省 token）

Prompt 指令 LLM 按固定格式输出：

```
entity<|#|>Elon Musk<|#|>Person<|#|>CEO of Tesla and SpaceX, founder of...
entity<|#|>Tesla<|#|>Organization<|#|>Electric vehicle manufacturer founded in 2003...
relation<|#|>Elon Musk<|#|>Tesla<|#|>founded, leadership<|#|>Elon Musk founded Tesla in 2003...
<|COMPLETE|>
```

解析规则：
- 按 `<|#|>` 定界符分割
- entity 行必须有 4 个字段：`entity | name | type | description`
- relation 行必须有 5 个字段：`relation | source | target | keywords | description`
- `<|COMPLETE|>` 标记提取完成

**模式 B — JSON 格式**（`ENTITY_EXTRACTION_USE_JSON=true`，质量更稳定）

```json
{
  "entities": [
    {"name": "Elon Musk", "type": "Person", "description": "CEO of Tesla..."},
    {"name": "Tesla", "type": "Organization", "description": "EV manufacturer..."}
  ],
  "relationships": [
    {
      "source": "Elon Musk",
      "target": "Tesla",
      "keywords": "founded, leadership",
      "description": "Elon Musk founded Tesla in 2003..."
    }
  ]
}
```

用 `EntityExtractionResult.model_validate_json()` 做 Pydantic 校验。

**模式选择**：JSON 输出更稳定、解析成功率更高，但 token 消耗更大、速度稍慢。

#### Prompt 工程要点

系统 Prompt 的核心约束：

1. **实体提取**：预定义类型体系（Person / Organization / Location / Event / Concept / Method / Content / Data / Artifact / NaturalObject / Creature / Other）
2. **关系提取**：二元关系分解（N 元关系拆为多个二元对）、无向关系去重
3. **数量限制**：单次最多 `{max_total_records}` 行、最多 `{max_entity_records}` 个实体 → 超出则标记 `<|COMPLETE|>`
4. **命名一致性**：同一个实体在多处出现时名称必须一致（title case）
5. **语言控制**：所有输出使用指定语言（如 `Chinese` / `English`），专有名词保留原文
6. **第三人称**：禁止使用代词，必须明确命名主体

#### 继续提取机制

如果一次 LLM 调用因数量上限未能提取完所有实体关系，LightRAG 会发起**继续提取**：

```
第一次调用 → 提取了 max 条 → 第二次调用（继续提取 Prompt）
  → 只提取遗漏/不完整的实体关系 → 直到输出空列表
```

### 4.4 Step 3: 去重合并（Set Merge）

这是 LightRAG 工程上最精妙的部分（`operate.py` 和 `utils_graph.py`）。

#### 实体合并策略

```python
default_entity_merge_strategy = {
    "description":  "concatenate",    # 多个描述用 <SEP> 拼接
    "entity_type":  "keep_first",     # 保留第一个非空类型
    "source_id":    "join_unique",    # 来源 chunk ID 去重拼接
    "file_path":    "join_unique",    # 来源文件路径去重拼接
}
```

#### 关系合并策略

```python
relation_merge_strategy = {
    "description":  "concatenate",        # 拼接描述
    "keywords":     "join_unique_comma",  # 关键词去重，逗号拼接
    "source_id":    "join_unique",        # 来源 chunk 去重
    "weight":       "max",                # 取最大权重
}
```

#### 合并流程

```
新实体/关系列表
  ↓ 逐个处理
  ├─ 查 Graph 是否已存在 →
  │   ├─ 不存在 → 直接 upsert_node / upsert_edge
  │   └─ 已存在 → _merge_attributes() 合并属性 → upsert 更新
  ↓
更新 Vector 存储（重新生成 embedding）
更新 KV 存储（更新 chunk 追踪）
```

#### chunk 追踪机制

为支持**文档删除**和**引用溯源**，每个实体/关系都追踪它来自哪些 chunk：

```
entity_chunks_storage: {
  "Elon Musk": {
    "chunk_ids": ["chunk-abc", "chunk-def", "chunk-ghi"],
    "count": 3
  }
}

relation_chunks_storage: {
  "elon_musk::tesla": {
    "chunk_ids": ["chunk-abc", "chunk-ghi"],
    "count": 2
  }
}
```

### 4.5 Step 4: 写入三层存储

每个 chunk 处理完成后：

1. **Graph 存储** — `upsert_node(name, data)` / `upsert_edge(src, tgt, data)`（内存操作）
2. **Vector 存储** — `content` 文本向量化 → `upsert` 写入（内存缓冲）
3. **KV 存储** — LLM 响应缓存、chunk 状态（内存缓冲）

**持久化时机**：`index_done_callback()` 在一个 batch 完成后触发：
- GraphML 文件原子写入（`atomic_write` 保证不出现撕裂写入）
- 跨进程通知（`set_all_update_flags` 翻转其他进程的更新标志位）

### 4.6 LLM 的四个角色

从 v2026.05 开始，LightRAG 支持为不同阶段配置不同 LLM：

| 角色 | 阶段 | 能力要求 | 推荐模型 |
|------|------|----------|----------|
| **EXTRACT** | 实体关系提取 | 理解复杂文本，准确结构化输出 | GPT-4o / Claude Sonnet |
| **QUERY** | 回答生成 | 长上下文、去噪、推理 | GPT-4o / Claude Opus |
| **KEYWORDS** | 查询关键词提取 | 快速响应即可 | GPT-4o-mini |
| **VLM** | 多模态视觉理解 | 多模态能力 | GPT-4o / Claude |

---

## 5. 查询与检索机制

### 5.1 查询处理：不做改写，仅提取关键词

**LightRAG 不对用户问题进行重写 (Query Rewriting)。** 与 HyDE（生成假设文档）、RQ-RAG（拆分子问题）、Multi-Query RAG（多版本改写）等方案不同，LightRAG 对用户输入只做一件事：**调用轻量 LLM 提取关键词**。

```
用户输入: "What companies did Elon Musk found and what are their key products?"
                           │
                           │ 不做改写，不做拆分，不生成假设文档
                           ▼
              ┌─────────────────────────────┐
              │   extract_keywords_only()    │
              │   KEYWORDS 角色 LLM 调用      │
              │   （一次轻量 JSON 输出调用）    │
              │                              │
              │   输出: JSON {                │
              │     "high_level_keywords": [  │
              │       "entrepreneurial        │
              │        ventures",             │
              │       "company history"       │
              │     ],                        │
              │     "low_level_keywords": [   │
              │       "Elon Musk",            │
              │       "Tesla",                │
              │       "SpaceX",               │
              │       "products",             │
              │       "founded"               │
              │     ]                         │
              │   }                           │
              └─────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Local 检索       Global 检索       Naive 检索
   (ll_keywords)    (hl_keywords)    (原始 query)
          │                │                │
          └────────────────┼────────────────┘
                           ▼
              检索结果合并 (实体+关系+文本块)
                           │
                           ▼
              ┌─────────────────────────────┐
              │  最终 LLM 回答 (QUERY 角色)    │
              │                              │
              │  user_query = query           │
              │  ↑ 原始问题原封不动传入        │
              └─────────────────────────────┘
```

**与同类方案对比**：

| 方案 | 查询处理方式 | LLM 调用次数 |
|------|-------------|-------------|
| **LightRAG** | 关键词提取 | 1 次（轻量） |
| HyDE | 生成假设文档 | 1 次 |
| RQ-RAG | 拆分子问题逐个检索 | N+1 次 |
| Multi-Query RAG | 多版本改写分别检索 | 3-5 次 |
| Naive RAG | 不做处理，直接向量检索 | 0 次 |

LightRAG 走中间路线——比 Naive RAG 多了结构化的关键词引导，但不像 HyDE/RQ-RAG 那样对 query 做重量级变换。好处是**成本低**，坏处是对极复杂问题的分解能力不如 RQ-RAG。

**源码证据**（`operate.py: kg_query()`）：

```python
async def kg_query(query, ...):
    # 1. 提取关键词（不是改写问题）
    hl_keywords, ll_keywords = await get_keywords_from_query(
        query, query_param, global_config, hashing_kv
    )

    # 2. 用关键词去检索
    context_result = await _build_query_context(
        query,         # 原始 query 用于 naive 向量检索
        ll_keywords,   # 关键词用于 local/global 检索
        hl_keywords,
        ...
    )

    # 3. 最终 LLM 提示——用的是原始 query
    user_query = query   # ← 原封不动，从未改写
```

**关键词提取 Prompt 的核心约束**：

```python
PROMPTS["keywords_extraction"] = """
---Role---
You are an expert keyword extractor...

---Goal---
1. high_level_keywords: overarching concepts, core intent, subject area
2. low_level_keywords: specific entities, proper nouns, technical terms

---Constraints---
- All keywords MUST be explicitly derived from the query
- Do NOT invent entities or terms not grounded in the query
- Multi-word phrases preferred over single words
- For vague queries ("hello"), return empty arrays
"""
```

### 5.2 两步混合检索：向量入口 + 图遍历扩展

**LightRAG 不是纯向量检索。** 向量相似度只是"入口"，检索真正全面是因为第二步的**图遍历扩展**。

#### Local 模式：向量找实体 → 图找关系 → Chunk 反查

```
                       向量检索                         图遍历
用户关键词:          ┌──────────┐                  ┌──────────────┐
"Tesla, Musk"   →   │ Step 1   │  邻居扩展         │ Step 2       │
                    │ 向量入口  │ ──────────────→  │ 图邻居扩展    │
                    │          │                  │              │
                    │ entities │  对每个命中实体:    │ graph.       │
                    │ _vdb     │  拿它的所有边       │ get_node_    │
                    │ .query() │                  │ edges(name)  │
                    │          │                  │              │
                    │ top_k    │  排序: degree +   │ → 关联关系    │
                    │ 个实体    │  weight 降序      │              │
                    └──────────┘                  └──────────────┘
                         │                              │
                         │      ┌──────────────┐        │
                         └─────→│ Step 3       │←───────┘
                                │ Chunk 反查    │
                                │ 通过 source_id│
                                │ 从 KV 拿原文   │
                                └──────────────┘
```

**源码对应**（`operate.py: _get_node_data()`）：

```python
async def _get_node_data(query, knowledge_graph_inst, entities_vdb, ...):
    # Step 1: 向量检索——找 top_k 实体
    results = await entities_vdb.query(
        query, top_k=query_param.top_k,   # ← 只有这一步是向量相似度
    )

    # Step 2: 图遍历——从实体出发拿所有邻居边
    use_relations = await _find_most_related_edges_from_entities(
        node_datas, query_param, knowledge_graph_inst,
        # ↑ 内部调用 graph.get_node_edges() ——纯图操作
    )
    return node_datas, use_relations
```

`_find_most_related_edges_from_entities` 排序逻辑——**用的是图结构指标**：

```python
# 按 degree（两端节点度数之和）降序，weight（边权重）降序
# 完全不涉及向量相似度
all_edges_data = sorted(
    all_edges_data,
    key=lambda x: (x["rank"], x["weight"]),  # rank = degree(src) + degree(tgt)
    reverse=True
)
```

#### Global 模式：向量找关系 → 图反查实体

```
                       向量检索                         图遍历
用户关键词:          ┌──────────┐                  ┌──────────────┐
"leadership,     →  │ Step 1   │  反向查实体       │ Step 2       │
 ventures"          │ 向量入口  │ ──────────────→  │ 图反查实体    │
                    │          │                  │              │
                    │ relation │  从每条关系的       │ graph.       │
                    │ ships    │  src_id/tgt_id    │ get_nodes_   │
                    │ _vdb     │  去图中拿实体节点   │ batch(ids)   │
                    │ .query() │                  │              │
                    │          │                  │              │
                    │ top_k    │                  │ → 关联实体    │
                    │ 个关系    │                  │              │
                    └──────────┘                  └──────────────┘
```

#### Chunk 反查：不经过向量

实体和关系上记录了 `source_id`（来源 chunk ID），直接从 KV 存储按 ID 取出文本内容，**无需经过向量检索**。支持两种选 chunk 策略：

| 策略 | 说明 |
|------|------|
| `WEIGHT` | 按 chunk 被多少实体/关系引用的次数加权 |
| `VECTOR` | 用原始 query 向量与候选 chunk 做余弦相似度排序 |

#### 总结：向量和图的分工

```
向量检索 = "从哪里进入图谱"  （入口定位）
图遍历   = "往图谱哪里走"    （关联扩展）
Chunk反查 = "原文是什么"     （内容还原）
```

这就是为什么 LightRAG 比纯向量 RAG 的检索更全面——向量只能找到"语义相似"的，图能找到"结构关联"的。比如你搜 "Elon Musk"，纯向量可能漏掉 "Starship"（语义距离远），但图会沿着 `Musk → SpaceX → Starship` 这条路径把它带出来。

### 5.3 五种查询模式

| 模式 | 检索来源 | 适用场景 | 延迟 |
|------|----------|----------|------|
| **local** | 实体向量 + 图邻居扩展 | 具体事实、细节查询 | 低 |
| **global** | 关系向量 + 图反查实体 | 宏观总结、趋势分析 | 低 |
| **hybrid** | local + global 合并 | 复杂综合查询 | 低 |
| **naive** | 仅文本块向量（不用 KG） | 简单关键词搜索 | 最低 |
| **mix** | local + global + naive 全合并 | **默认模式，效果最佳** | 中 |

`mix` 模式是推荐默认值，检索最全面。启用 Reranker 可进一步提升 mix 模式的效果（约 1-2 秒额外延迟）。

### 5.4 Token 预算控制

检索结果受三层 token 限制（避免撑爆 LLM 上下文窗口）：

```
MAX_TOTAL_TOKENS (总预算)
  ├─ MAX_ENTITY_TOKENS (实体上下文)
  ├─ MAX_RELATION_TOKENS (关系上下文)
  └─ 剩余 → 文本块 (chunks)
```

### 5.5 Reranker 支持

启用 Reranker（`RERANK_BY_DEFAULT=true`）可显著提升查询质量：
- 对候选 text chunks 进行精排
- 支持本地部署 Reranker 模型以减少延迟
- 与 Embedding 模型不同，Reranker 可随时更换

---

## 6. 增量更新设计

这是 LightRAG 相比 Microsoft GraphRAG **最大的工程优势**。核心结论：

> **新文档上传 → 只对新文档的 chunk 调 LLM 提取 → 提取结果按实体名与已有图谱 Set Merge → 旧文档完全不参与新的 LLM 调用。**

### 6.1 核心原则：只处理新文档

```
旧文档 A (已处理 ✅)                    旧文档 B (已处理 ✅)
├─ 图中已有: Elon Musk, Tesla...       ├─ 图中已有: Tesla, Model S...
├─ 向量库已有: embedding               ├─ 向量库已有: embedding
└─ KV 缓存已有: LLM提取结果             └─ KV 缓存已有: LLM提取结果

═══════════════════════════════════════════════════════
                    新文档 C 上传 🆕
═══════════════════════════════════════════════════════

Step 1: 只对新文档的 chunks 调 LLM
  extract_entities(chunks_of_C)  ← 只处理 C，A/B 不参与
  产出: entities=["Tesla","Model Y","4680 battery"]
        relations=[("Tesla","Model Y","produces"), ...]

Step 2: 按实体名聚合（新旧混合）
  all_nodes["Tesla"] = [
    data_from_A,   ← 从图中读到的已有数据
    data_from_B,   ← 从图中读到的已有数据
    data_from_C    ← 新提取的数据
  ]
  all_nodes["Model Y"] = [
    data_from_C    ← 新实体，只有 C 的数据
  ]

Step 3: merge_nodes_and_edges() Set Merge

Step 4: _insert_done() 持久化

旧文档 A、B 的 LLM 提取结果从未被重新处理 ❌🔄
```

### 6.2 Set Merge 合并流程

**源码路径**（`pipeline.py` → `operate.py: merge_nodes_and_edges()`）：

```python
# pipeline.py: 每个文档独立处理，互不干扰
for doc in pending_documents:
    # 1. 只对当前新文档分块
    chunks = await chunk_document(doc)

    # 2. 只对当前新文档的 chunks 调 LLM（不涉及旧文档）
    chunk_results = await extract_entities(chunks, ...)
    # ↑ chunk_results 只包含这篇文章提取出的实体关系

    # 3. 合并到已有图谱——已有数据从图中读取，不重算
    await merge_nodes_and_edges(
        chunk_results,                      # 新文档的提取结果
        knowledge_graph_inst=self.chunk_entity_relation_graph,  # 已有全局图谱
        ...
    )
```

**合并时每个实体/关系的处理逻辑**（`operate.py: _merge_nodes_then_upsert()`）：

```python
async def _merge_nodes_then_upsert(entity_name, nodes_data, ...):
    # 1. 从已有图谱读取旧数据——这是旧文档的历史积累
    already_node = await knowledge_graph_inst.get_node(entity_name)

    if already_node:
        # 读取旧描述、旧 source_id（旧文档数据完整保留）
        already_description = already_node.get("description")
        already_source_ids = already_node.get("source_id")

    # 2. 新旧 chunk 引用合并（增量追加，不重算）
    full_source_ids = merge_source_ids(
        existing_full_source_ids,  # 旧的 chunk ID 列表
        new_source_ids             # 新的 chunk ID 列表
    )
    # 例: ["chk-A1","chk-B3"] + ["chk-C1","chk-C2"]
    #   → ["chk-A1","chk-B3","chk-C1","chk-C2"]  (去重)

    # 3. 合并后 upsert——旧数据完整保留
    await knowledge_graph_inst.upsert_node(entity_name, merged_data)
    await entity_vdb.upsert({entity_id: vector_data})
```

**实体/关系属性合并策略**：

| 属性 | 策略 | 示例 |
|------|------|------|
| `description` | concatenate | `"born in SA<SEP>CEO of Tesla<SEP>launched Model Y"` |
| `source_id` | join_unique | chunk 引用去重拼接 |
| `entity_type` | 投票取最高频次 | 3 次 "Person" vs 1 次 "Organization" → Person |
| `keywords` (关系) | join_unique_comma | 关键词去重逗号拼接 |
| `weight` (关系) | max | 取最大权重值 |
| `file_path` | join_unique | 来源文件路径去重 |

### 6.3 旧文档数据完全不动

为什么旧文档不需要重新处理？

| 维度 | 说明 |
|------|------|
| **Graph 存储** | 旧实体/关系节点和边在图中不变，只是属性被新数据增量扩充 |
| **Vector 存储** | 旧 embedding 不变，仅新增或更新被 merge 影响到的实体/关系的向量 |
| **KV 缓存** | LLM 提取结果缓存永久保留，删除文档时用于快速重建关系 |
| **LLM 调用** | 旧文档的 chunk 内容从不重新送入 LLM |

时间复杂度与**新增数据量**成正比，而非总数据量。对比 Microsoft GraphRAG 需要重建全局 Community Reports，效率差距巨大。

### 6.4 唯一的额外开销：LLM 摘要合并

当同一个实体的描述数量超过 `force_llm_summary_on_merge` 阈值（默认 10）时，LightRAG 会调用 LLM 对已有描述做一次**摘要合成**：

```python
# 这里只做摘要合并，不重新从文档提取
if len(descriptions) >= force_llm_summary_on_merge:
    final_desc = await _summarize_descriptions(entity_name, descriptions, llm)
    # ↑ descriptions = 旧描述 + 新描述 的列表
    # 只把多段描述合成一段连贯文本
    # 不涉及原始文档、不涉及分块、不涉及 Prompt 构建
else:
    final_desc = GRAPH_FIELD_SEP.join(descriptions)  # 直接拼接，零 LLM 开销
```

**这远比重跑全量 LLM 提取便宜**——摘要只处理一个实体的描述字段，不涉及原始文档的 token 消耗、不涉及复杂的实体关系提取 Prompt。

### 6.5 文档删除

删除文档时，利用构建阶段缓存的 LLM 响应：
- 找到被删除文档关联的实体/关系
- 移除该文档的 chunk 引用
- 如果实体/关系不再关联任何文档 → 删除
- 如果仍有关联 → 仅更新 `source_id` 和描述

---

## 7. 多模态支持

从 v1.5 起集成 [RAG-Anything](https://github.com/HKUDS/RAG-Anything)，支持多模态文档。

### 7.1 解析引擎

| 引擎 | 能力 | 部署 |
|------|------|------|
| **MinerU** | PDF/文档高质量解析，提取文本/表格/公式/图片 | 云端或本地 |
| **Docling** | IBM 开源文档解析 | 本地 |
| **Native** | 内置轻量解析 | 本地（默认） |

### 7.2 处理流程

```
PDF/Office 文档
  ↓ Parser 解析
文本块 + 图片 + 表格 + 公式
  ↓ VLM 分析（视觉 LLM 提取图片中的实体关系）
跨模态实体/关系
  ↓ 统一合并
知识图谱 + 向量存储
```

### 7.3 推荐配置

```bash
LIGHTRAG_PARSER=*:native-iteP,*:mineru-iteP,*:legacy-R
VLM_PROCESS_ENABLE=true
VLM_LLM_MODEL=<your_vlm_model_name>
```

---

## 8. 模型与存储配置

LightRAG 支持多种 LLM、Embedding、图数据库和向量数据库，且四个 LLM 角色可独立配置不同模型。

### 8.1 支持的 LLM 提供商

| 绑定类型 (`LLM_BINDING`) | 模型示例 | 说明 |
|------|------|------|
| `openai` | GPT-4o / GPT-4o-mini / GPT-5 | 默认；也支持任何 OpenAI 兼容 API（如 DeepSeek、国产模型等） |
| `ollama` | Qwen3 / Llama4 / DeepSeek-R1 | 本地部署，30B 模型即可满足提取需求 |
| `azure_openai` | Azure GPT 系列 | 企业合规部署 |
| `bedrock` | Claude / Nova / Titan | AWS 托管 |
| `gemini` | Gemini Flash / Pro | Google AI Studio 或 Vertex AI |
| `anthropic` | Claude 全系列 | 直接 Anthropic API（`lightrag/llm/anthropic.py`） |
| `hf` | HuggingFace 推理端点 | 自定义模型托管 |
| `zhipu` | GLM-4 / GLM-4V | 智谱 AI |
| `lmdeploy` | LMDeploy 推理引擎 | 社区适配 |
| `nvidia_openai` | NVIDIA NIM | OpenAI 兼容 |
| `lollms` / `llama_index` | LOLLMS / LlamaIndex 生态 | 社区适配 |

### 8.2 四个 LLM 角色独立配置

每个角色有独立的模型、API 端点、并发数，未设置时回退到全局配置：

```bash
# ===== 全局 LLM（所有角色的默认值）=====
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=sk-xxx
LLM_MODEL=gpt-4o-mini
MAX_ASYNC_LLM=4

# ===== 角色级覆写（可选）=====
# EXTRACT: 实体关系提取（能力要求高）
# EXTRACT_LLM_MODEL=gpt-4o
# EXTRACT_MAX_ASYNC_LLM=4

# KEYWORD: 查询关键词提取（速度优先，轻量模型即可）
KEYWORD_LLM_MODEL=gpt-4o-mini
KEYWORD_MAX_ASYNC_LLM=4

# QUERY: 最终回答生成（长上下文 + 去噪）
# QUERY_LLM_MODEL=gpt-4o
QUERY_MAX_ASYNC_LLM=4

# VLM: 多模态视觉理解（图片/表格分析）
# VLM_LLM_MODEL=gpt-4o
# VLM_PROCESS_ENABLE=true
```

**各角色的能力要求**：

| 角色 | 阶段 | 关键能力 | 推荐模型 |
|------|------|----------|----------|
| EXTRACT | 实体关系提取 | 理解复杂文本，准确结构化输出 | `gpt-4o` / `deepseek-chat` |
| KEYWORD | 查询关键词 | 快速 JSON 输出 | `gpt-4o-mini` / `deepseek-chat` |
| QUERY | 回答生成 | 长上下文、去噪、推理 | `gpt-4o` / `deepseek-reasoner` |
| VLM | 多模态分析 | 视觉理解 | `gpt-4o` |

### 8.3 Embedding 提供商

> ⚠️ Embedding 模型选定后不可更改，否则需删除所有向量数据重建。

| 绑定类型 | 推荐模型 | 维度 | 说明 |
|------|------|------|------|
| `openai` | `text-embedding-3-large` | 3072 | 推荐，质量好 |
| `openai` | `text-embedding-3-small` | 1536 | 性价比 |
| `ollama` | `bge-m3` | 1024 | 本地部署首选 |
| `ollama` | `nomic-embed-text` | 768 | 轻量本地 |
| `ollama` | `qwen3-embedding` | 2560 | 中文友好 |
| `bedrock` | `amazon.titan-embed-text-v2` | 1024 | AWS 生态 |
| `gemini` | `gemini-embedding-001` | 1536 | Google 生态 |
| `jina` | `jina-embeddings-v4` | 2048 | 多语言强 |
| `azure_openai` | Azure Embedding | 同 OpenAI | 合规场景 |

### 8.4 向量与图数据库

LightRAG 需要四种存储，可以逐个指定或用一个**统一方案**覆盖全部：

```bash
# ===== 开发环境（默认，内存存储，不持久化）=====
LIGHTRAG_KV_STORAGE=JsonKVStorage
LIGHTRAG_DOC_STATUS_STORAGE=JsonDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_VECTOR_STORAGE=NanoVectorDBStorage

# ===== 生产环境：PostgreSQL 统一方案（推荐）=====
LIGHTRAG_KV_STORAGE=PG
LIGHTRAG_DOC_STATUS_STORAGE=PG
LIGHTRAG_GRAPH_STORAGE=PG
LIGHTRAG_VECTOR_STORAGE=PGVector
# + 配置 POSTGRES_HOST/PORT/USER/PASSWORD/DATABASE

# ===== 生产环境：MongoDB 统一方案 =====
LIGHTRAG_KV_STORAGE=MongoKVStorage
LIGHTRAG_GRAPH_STORAGE=MongoGraphStorage
LIGHTRAG_VECTOR_STORAGE=MongoVectorDBStorage
# + 配置 MONGO_URI / MONGO_DATABASE

# ===== 生产环境：OpenSearch 统一方案 =====
LIGHTRAG_KV_STORAGE=OpenSearch
LIGHTRAG_GRAPH_STORAGE=OpenSearch
LIGHTRAG_VECTOR_STORAGE=OpenSearch
# + 配置 OPENSEARCH_HOSTS/USER/PASSWORD
```

**全部支持的存储后端**：

| 存储后端 | KV | Vector | Graph | DocStatus | 适用场景 |
|----------|:--:|:------:|:-----:|:---------:|----------|
| **PostgreSQL + pgvector** | ✅ | ✅ | ✅ | ✅ | **推荐生产统一方案** |
| **MongoDB Atlas** | ✅ | ✅ | ✅ | ✅ | 云原生生产 |
| **OpenSearch** | ✅ | ✅ | ✅ | ✅ | 已有 ES 集群 |
| **Neo4j** | — | — | ✅ | — | 复杂图查询（仅 Graph） |
| **Milvus** | — | ✅ | — | — | 十亿级向量 |
| **Qdrant** | — | ✅ | — | — | 高性能向量 |
| **Redis** | ✅ | ✅ | — | ✅ | 高并发低延迟 |
| **Faiss** | — | ✅ | — | — | 嵌入式/单机 |
| **Memgraph** | — | — | ✅ | — | 实时图分析 |
| **NetworkX** | — | — | ✅ | — | 默认，开发用 |
| **NanoVectorDB** | — | ✅ | — | — | 默认，开发用 |
| **JSON** | ✅ | — | — | ✅ | 默认，开发用 |

### 8.5 DeepSeek 配置示例

DeepSeek 提供 OpenAI 兼容 API，因此使用 `LLM_BINDING=openai`，将 `LLM_BINDING_HOST` 指向 DeepSeek 即可：

```bash
# ===== DeepSeek 作为 LLM =====
LLM_BINDING=openai                          # DeepSeek 兼容 OpenAI API
LLM_BINDING_HOST=https://api.deepseek.com
LLM_BINDING_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat                     # 通用对话，适合 EXTRACT + QUERY
# LLM_MODEL=deepseek-reasoner               # 推理增强，适合复杂 QUERY

# 角色分离（可选）：提取和查询用不同模型
# EXTRACT_LLM_MODEL=deepseek-chat           # 提取用通用模型
# QUERY_LLM_MODEL=deepseek-reasoner          # 回答用推理模型
# KEYWORD_LLM_MODEL=deepseek-chat           # 关键词提取
MAX_ASYNC_LLM=4

# ===== DeepSeek 不支持 Embedding，需单独配置 =====
EMBEDDING_BINDING=ollama                    # 本地部署 Embedding
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIM=1024

# 或使用 OpenAI 做 Embedding（LLM 仍用 DeepSeek）
# EMBEDDING_BINDING=openai
# EMBEDDING_BINDING_HOST=https://api.openai.com/v1
# EMBEDDING_BINDING_API_KEY=sk-your-openai-key
# EMBEDDING_MODEL=text-embedding-3-large
```

> **注意**：DeepSeek 目前没有 Embedding 服务，LLM 可以用 DeepSeek，但 Embedding 需要另选（OpenAI / 本地 Ollama / 智谱等）。**LLM 和 Embedding 可以分别使用不同提供商，互不绑定。**

兼容 OpenAI API 协议的其他国产模型同样可用：
- **通义千问**: `LLM_BINDING_HOST=https://dashscope.aliyuncs.com/compatible-mode/v1`
- **智谱 GLM**: 用 `LLM_BINDING=zhipu`（原生支持）
- **Moonshot**: `LLM_BINDING_HOST=https://api.moonshot.cn/v1`
- **硅基流动 SiliconFlow**: `LLM_BINDING_HOST=https://api.siliconflow.cn/v1`

---

## 9. 多知识库隔离

> 这是 LightRAG **原生支持**的功能，不是扩展。`workspace` 是一等公民参数，贯穿所有存储层。

### 9.1 Workspace 机制原理

不同 `workspace` 使用独立的数据目录/表/集合，实现**物理隔离**：

```
rag_storage/
├── default/                          # workspace=""（未设置）
│   ├── graph_chunk_entity_relation.graphml
│   ├── kv_store_full_docs.json
│   ├── vdb_entities.json
│   └── ...
│
├── legal_docs/                       # workspace="legal_docs" → 法律知识库
│   ├── graph_chunk_entity_relation.graphml
│   ├── kv_store_full_docs.json
│   └── ...
│
├── tech_docs/                        # workspace="tech_docs" → 技术知识库
│   └── ...
│
└── finance_reports/                  # workspace="finance_reports" → 金融知识库
    └── ...
```

使用 PostgreSQL 时，通过 schema 隔离：

```
rag_db
├── public.lightrag_entities          # workspace=""
├── legal_docs.lightrag_entities      # workspace="legal_docs"
├── tech_docs.lightrag_entities       # workspace="tech_docs"
└── ...
```

**源码依据**：

```python
# lightrag.py
class LightRAG:
    workspace: str = field(default_factory=lambda: os.getenv("WORKSPACE", ""))
    """Workspace for data isolation."""

# lightrag/kg/networkx_impl.py: 每个存储实现都遵循此模式
if self.workspace:
    workspace_dir = os.path.join(working_dir, self.workspace)  # rag_storage/legal_docs/
else:
    workspace_dir = working_dir  # rag_storage/
```

```bash
# env.example 中的官方说明
### WORKSPACE sets workspace name for all storage types
### for the purpose of isolating data from LightRAG instances.
### Valid workspace name constraints: a-z, A-Z, 0-9, and _
```

### 9.2 SDK 多知识库用法

```python
# 方式一：独立 LightRAG 实例
legal_rag = LightRAG(
    working_dir="./rag_storage",
    workspace="legal_docs",      # ← 法律知识库
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
)
await legal_rag.initialize_storages()

tech_rag = LightRAG(
    working_dir="./rag_storage",
    workspace="tech_docs",       # ← 技术知识库，完全独立
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
)
await tech_rag.initialize_storages()

# 查询互不干扰
legal_result = await legal_rag.aquery("相关法律条款有哪些?", param=QueryParam(mode="hybrid"))
tech_result  = await tech_rag.aquery("How to implement OAuth2?", param=QueryParam(mode="hybrid"))
```

**不同知识库可以共用 Embedding/LLM API**，降低成本：

```python
# 三个知识库共享同一个 embedding_func 和 llm_model_func
shared_embed = openai_embed
shared_llm   = gpt_4o_mini_complete

kbs = {
    "legal":   LightRAG(working_dir="./data", workspace="legal",   embedding_func=shared_embed, llm_model_func=shared_llm),
    "tech":    LightRAG(working_dir="./data", workspace="tech",    embedding_func=shared_embed, llm_model_func=shared_llm),
    "finance": LightRAG(working_dir="./data", workspace="finance", embedding_func=shared_embed, llm_model_func=shared_llm),
}
```

### 9.3 API Server 多实例

```bash
# 启动多个实例，不同端口 + 不同 workspace
WORKSPACE=legal_docs   PORT=9621 lightrag-server &
WORKSPACE=tech_docs    PORT=9622 lightrag-server &
WORKSPACE=finance      PORT=9623 lightrag-server &
```

Docker Compose 多实例：

```yaml
services:
  lightrag-legal:
    image: ghcr.io/hkuds/lightrag:latest
    environment:
      - WORKSPACE=legal_docs
      - PORT=9621
  lightrag-tech:
    image: ghcr.io/hkuds/lightrag:latest
    environment:
      - WORKSPACE=tech_docs
      - PORT=9622
  lightrag-finance:
    image: ghcr.io/hkuds/lightrag:latest
    environment:
      - WORKSPACE=finance_reports
      - PORT=9623
```

反向代理路由（Nginx 示例）：

```nginx
location /legal/   { proxy_pass http://127.0.0.1:9621/; }
location /tech/    { proxy_pass http://127.0.0.1:9622/; }
location /finance/ { proxy_pass http://127.0.0.1:9623/; }
```

### 9.4 隔离边界

| 维度 | 是否隔离 | 说明 |
|------|:------:|------|
| **文档** | ✅ | 不同 workspace 的文档互不可见 |
| **知识图谱** | ✅ | 实体/关系各自独立 |
| **向量** | ✅ | Embedding 各自独立 |
| **LLM 缓存** | ✅ | 缓存不跨 workspace |
| **查询结果** | ✅ | 查询 A 只能查到 A 的数据 |
| **LLM API** | ❌ 共享 | 所有 workspace 共用 LLM/Embedding API Key 和端点 |
| **存储实例** | 🔶 | 同一 PG 实例不同 schema = 共享；不同 PG 实例 = 独立 |

---

## 10. 部署方式

### 10.1 安装

```bash
# 完整安装（含 API Server + WebUI）
pip install "lightrag-hku[api]"

# 仅 SDK
pip install lightrag-hku

# 从源码
git clone https://github.com/HKUDS/LightRAG
cd LightRAG
make dev
```

### 10.2 Docker 部署

```bash
cp env.example .env
# 编辑 .env 配置 LLM 和 Embedding
docker compose up
```

### 10.3 关键环境变量

```bash
# LLM 配置
LLM_BINDING=openai           # openai / ollama / azure / bedrock / ...
LLM_MODEL=gpt-4o-mini
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large

# 提取质量
ENTITY_EXTRACTION_USE_JSON=true   # JSON 模式，更稳定
SUMMARY_LANGUAGE=Chinese          # 实体关系描述语言

# 存储（生产环境推荐 PostgreSQL 统一方案）
LIGHTRAG_GRAPH_STORAGE=PG
LIGHTRAG_VECTOR_STORAGE=PGVector
LIGHTRAG_KV_STORAGE=PG
LIGHTRAG_DOC_STATUS_STORAGE=PG

# 并发优化
MAX_ASYNC_LLM=8              # LLM 最大并发
MAX_PARALLEL_INSERT=3        # 文件并行处理数（≈ MAX_ASYNC_LLM / 3）
EMBEDDING_FUNC_MAX_ASYNC=16  # Embedding 最大并发
EMBEDDING_BATCH_NUM=32       # 每批嵌入条数

# Token 预算
MAX_ENTITY_TOKENS=4096
MAX_RELATION_TOKENS=4096
MAX_TOTAL_TOKENS=32768

# Reranker
RERANK_BY_DEFAULT=true
```

### 10.4 SDK 快速使用

```python
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

async def main():
    rag = LightRAG(
        working_dir="./rag_storage",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    await rag.initialize_storages()

    # 插入文档
    await rag.ainsert("Your document text here...")

    # 多种模式查询
    result = await rag.aquery(
        "What are the key themes?",
        param=QueryParam(mode="hybrid")
    )
    print(result)

asyncio.run(main())
```

---

## 11. 性能基准

### 11.1 综合表现（LLM 评委打分）

在农业、计算机科学、法律、混合四个领域，对比主流方案：

| 对比方案 | 全面性 | 多样性 | 赋能性 | 综合胜率 |
|----------|--------|--------|--------|----------|
| vs NaiveRAG | 61-84% | 62-86% | 57-84% | **60-85%** |
| vs RQ-RAG | 61-85% | 61-88% | 58-85% | **60-86%** |
| vs HyDE | 58-74% | 61-80% | 54-75% | **58-75%** |
| vs **Microsoft GraphRAG** | 50-54% | 59-77% | 49-59% | **50-55%** |

**关键发现**：LightRAG 在**多样性**维度优势尤为明显，在与 GraphRAG 的对比中达到 59-77%。

### 11.2 效率对比

| 维度 | LightRAG | Microsoft GraphRAG |
|------|----------|---------------------|
| LLM 调用次数 | 仅实体提取 + 回答 | + Community Reports + 多跳推理 |
| 增量更新 | ✅ Set Merge，秒级 | ❌ 需重建，分钟级 |
| 最小可用模型 | 30B 开源模型可用 | 需要更强模型 |

---

## 12. 适用场景分析

| 场景 | 适合度 | 原因 |
|------|--------|------|
| **法律文档分析** | ⭐⭐⭐⭐⭐ | 实体关系密集，需精确跨文档引用 |
| **金融研报分析** | ⭐⭐⭐⭐⭐ | 跨报告逻辑关联、趋势分析 |
| **科研文献综述** | ⭐⭐⭐⭐⭐ | 多模态（公式/图表）+ 跨文献推理 |
| **企业知识库** | ⭐⭐⭐⭐ | 增量更新方便，多后端灵活 |
| **技术文档问答** | ⭐⭐⭐⭐ | 实体关系明确，适合图检索 |
| **简单 FAQ** | ⭐⭐⭐ | 传统向量 RAG 足够，KG 开销可能不必要 |
| **对话机器人** | ⭐⭐⭐ | 对话类场景实体关系较稀疏 |
| **实时聊天** | ⭐⭐ | 实体提取有延迟，不适合极低延迟场景 |

---

## 13. 与同类方案对比

| 特性 | LightRAG | Microsoft GraphRAG | Naive RAG | RQ-RAG | HyDE |
|------|----------|---------------------|-----------|--------|------|
| **检索方式** | 图 + 向量双层 | 图 + 社区摘要 | 纯向量 | 查询重写 | 假设文档 |
| **知识图谱** | ✅ 自动构建 | ✅ 自动构建 | ❌ | ❌ | ❌ |
| **增量更新** | ✅ Set Merge | ❌ 需重建 | ✅ | ✅ | ✅ |
| **成本** | 中 | 高 | 低 | 中 | 低 |
| **多模态** | ✅ v1.5+ | ❌ | ❌ | ❌ | ❌ |
| **引用溯源** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **WebUI** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **社区活跃度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | - | - | - |
| **存储选择** | 12+ 种后端 | 受限 | 多种 | 受限 | 受限 |

---

## 14. 注意事项与风险

### 14.1 技术注意点

| 注意点 | 说明 |
|--------|------|
| **LLM 依赖** | 实体提取质量直接影响图谱质量，建议使用 GPT-4o / Claude Sonnet 级别模型 |
| **Embedding 不可变更** | Embedding 模型选定后不可更改（除非删除所有向量数据重建） |
| **默认存储仅开发用** | 默认内存存储不持久化、不跨进程共享，生产环境**必须**配置外部数据库 |
| **配置项多** | 涉及大量环境变量，调优需要理解每个参数的影响 |
| **并发控制** | `MAX_PARALLEL_INSERT` 应为 `MAX_ASYNC_LLM` 的约 1/3 |
| **实体命名一致性** | LLM 可能对同一实体使用不同名称（如 "Elon Musk" vs "Musk"），影响图谱连通性 |

### 14.2 生产部署建议

1. **存储方案**：使用 PostgreSQL 作为统一后端（pgvector），简化运维
2. **LLM 选型**：EXTRACT 和 QUERY 角色使用高质量模型，KEYWORDS 可用轻量模型
3. **Embedding**：本地部署 `BAAI/bge-m3` 或 `text-embedding-3-large`
4. **Reranker**：本地部署以减少延迟
5. **Parser**：大数据量场景配置 MinerU 本地服务
6. **监控**：集成 Langfuse 追踪 + RAGAS 评估
7. **并发**：根据 GPU/API 配额合理配置 `MAX_ASYNC_LLM`

### 14.3 局限性

- **实体提取延迟**：每个 chunk 需要 1 次 LLM 调用，大批量文档导入需要较长时间
- **成本**：虽然有 LLM 缓存，大规模语料库的实体提取成本仍不可忽略
- **冷启动**：新领域可能需要定制 Prompt 和实体类型体系
- **非结构化对话**：对于闲聊类文本，实体关系提取收益有限

---

## 附录 A: 生态系统

| 项目 | 说明 | 仓库 |
|------|------|------|
| **RAG-Anything** | 全栈多模态 RAG | [HKUDS/RAG-Anything](https://github.com/HKUDS/RAG-Anything) |
| **VideoRAG** | 超长视频内容 RAG | [HKUDS/VideoRAG](https://github.com/HKUDS/VideoRAG) |
| **MiniRAG** | 面向小模型的极简 RAG | [HKUDS/MiniRAG](https://github.com/HKUDS/MiniRAG) |

## 附录 B: 参考文献

```bibtex
@article{guo2024lightrag,
  title={LightRAG: Simple and Fast Retrieval-Augmented Generation},
  author={Zirui Guo and Lianghao Xia and Yanhua Yu and Tu Ao and Chao Huang},
  year={2024},
  eprint={2410.05779},
  archivePrefix={arXiv},
  primaryClass={cs.IR}
}
```

---

> **文档版本**: v2.0 | **作者**: AI Research | **最后更新**: 2026-06-09
