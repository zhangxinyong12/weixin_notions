# Claude Code 安装指南

## 什么是 Claude Code

Claude Code 是 Anthropic 官方推出的 CLI 工具，让你在终端中直接使用 Claude 进行编程。它可以：

- 📝 直接编辑代码文件
- 🔍 搜索和理解代码库
- 🚀 运行命令和测试
- 🔄 与 Git 工作流集成
- 🧩 扩展技能（Skills）和 MCP 服务器

## 推荐工具：Trae IDE（字节跳动）

[Trae IDE](https://www.trae.ai/) 是字节跳动推出的**免费 AI 编程 IDE**，是 Claude Code 的可视化替代方案，适合喜欢图形界面的开发者。

### 核心特点

- 🎨 **双重开发模式**：IDE 模式（精细控制）+ SOLO 模式（AI 主导）
- 🤖 **内置多种 AI 模型**：GPT-4、Claude 3.5/3.7、DeepSeek 等
- 🧩 **智能体系统**：支持自定义智能体和 MCP Server
- ⚡ **CUE 代码补全**：多行修改、智能导入、重命名引用
- 🔒 **隐私模式**：代码始终本地保存，可选不用于 AI 训练
- 🛡️ **沙箱运行**：降低 AI 生成命令的执行风险
- 🔌 **插件生态**：支持丰富扩展
- 🌐 **远程开发**：支持 Remote SSH 和 WSL

### 使用场景

1. **从 0 到 1 创建项目**：自然语言描述需求，AI 完成拆解、生成、验证
2. **维护已有代码库**：理解项目结构，定位问题，重构优化
3. **提升编码效率**：实时代码补全和智能建议
4. **智能代码审查**：生成规范的 Commit Message，审查代码变更

### 下载安装

**国际版（推荐）：**

- 访问：[https://www.trae.ai/download](https://www.trae.ai/download)
- 支持：macOS 12.0+、Windows、Web、Mobile
- 注册：使用 GitHub 或 Google 账号

**国内版：**

- 访问：[https://www.trae.com.cn/](https://www.trae.com.cn/)
- 集成 DeepSeek 等国产模型
- 无需代理即可使用

### Trae vs Claude Code

| 特性 | Trae IDE | Claude Code |
|------|----------|-------------|
| **界面** | 图形化 IDE | 命令行 CLI |
| **使用门槛** | 低，适合新手 | 中，需要命令行经验 |
| **可视化** | 完整 IDE 体验 | 终端文本交互 |
| **AI 模型** | 多模型内置 | 需配置 API |
| **价格** | 免费使用 | 按 API 计费 |
| **扩展性** | 插件生态 | Skills/MCP |
| **适用场景** | 全功能开发 | 快速编辑和脚本 |

**推荐选择：**
- 新手或喜欢可视化 → **Trae IDE**
- 熟悉命令行追求效率 → **Claude Code**
- 两者可结合使用！

## 环境要求

- **Node.js**: 18.x 或更高版本
- **操作系统**: macOS, Linux, Windows (WSL)
- **Anthropic API Key**: 需要 Claude API 访问权限

## 安装步骤

### 1. 安装 Node.js

首先检查你的 Node 版本：

```bash
node --version
```

如果版本低于 18，需要先升级 Node.js。推荐使用 `nvm`（Node Version Manager）：

```bash
# 安装 nvm (macOS/Linux)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装最新 LTS 版本的 Node
nvm install --lts
nvm use --lts
```

### 2. 安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

安装完成后，验证安装：

```bash
claude --version
```

### 3. 配置 API Key

#### 方式一：使用官方 API

设置你的 Anthropic API Key：

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

为了永久生效，添加到你的 shell 配置文件（`.bashrc`, `.zshrc` 等）：

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 方式二：使用 Amux API 中转站（国内推荐）

[Amux API](https://amux.ai/) 是一个双向 LLM API 适配器，可以在 Claude Code 中使用 GPT、Grok、MiniMax 等多种模型。

**优势：**
- 🌍 国内直连，无需翻墙
- 💰 价格更优惠
- 🔄 支持多模型切换（OpenAI ↔ Claude ↔ DeepSeek ↔ Gemini）
- 🎯 统一接口，一次编写随时切换

**获取 Token：**

1. 访问 [Amux Console](https://api.amux.ai/console/token)
2. 注册/登录账号
3. 创建 API Token

**配置方式（三选一）：**

**选项 1：环境变量方式**

```bash
export ANTHROPIC_BASE_URL="https://api.amux.ai"
export ANTHROPIC_API_KEY="your-amux-api-token"
```

永久生效：

```bash
echo 'export ANTHROPIC_BASE_URL="https://api.amux.ai"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your-amux-api-token"' >> ~/.bashrc
source ~/.bashrc
```

**选项 2：配置文件方式**

编辑 `~/.claude/settings.json`：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.amux.ai",
    "ANTHROPIC_API_KEY": "your-amux-api-token"
  }
}
```

**选项 3：使用 Amux Desktop（可视化配置）**

1. 下载 [Amux Desktop](https://amux.ai/)
2. 添加供应商：
   - **Name**: Amux API
   - **Adapter Type**: `openai`
   - **Base URL**: `https://api.amux.ai`
   - **API Key**: 你的 Amux API Token
3. 使用 **Code Switch** 功能动态切换模型

**验证连接：**

```bash
claude "Hello, what model are you?"
```

### 4. 启动 Claude Code

```bash
claude
```

首次启动会进入交互式设置向导，按提示配置即可。

## 基础使用

### 在项目中启动

```bash
cd your-project
claude
```

### 常用命令

- `/help` - 查看帮助
- `/clear` - 清空对话历史
- `/exit` - 退出 Claude Code
- `/config` - 配置设置
- `/loop` - 设置循环任务

## 安装和使用 Plugins

Claude Code 支持 **Plugins（插件）** 系统来扩展功能。插件可以是 Skill（技能）或完整的开发框架。

### 推荐的 Plugins

#### 🌟 Superpowers - Agent 开发框架

[Superpowers](https://github.com/obra/superpowers) 是一个完整的 Agent 技能框架和软件开发方法论，让你的 Claude 真正成为系统化的开发伙伴。

**核心工作流：**

1. **brainstorming** - 通过苏格拉底式提问细化需求
2. **using-git-worktrees** - 创建隔离的 Git 工作树
3. **writing-plans** - 详细的实现计划
4. **subagent-driven-development** - 子代理驱动开发
5. **test-driven-development** - 强制 TDD 流程（RED-GREEN-REFACTOR）
6. **requesting-code-review** - 预审查检查清单
7. **finishing-a-development-branch** - 完成分支处理

**安装方式：**

```bash
# 从官方市场安装
/plugin install superpowers@claude-plugins-official

# 或从 Superpowers 市场安装
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**哲学理念：**
- 测试驱动开发（TDD）- 始终先写测试
- 系统化胜过临时方案
- 复杂性简化为首要目标
- 证据胜过声明

---

#### 🌟 CCW (Claude Code Workflow) - 工作流生成器

[CCW](https://github.com/ashleyha/claude-code-workflow) 是一个线性 Spec-Driven Development (SDD) 工作流生成器，帮助开发者轻松创建自定义工作流。

**特点：**
- 自动化工作流生成
- Spec-Driven Development（规格驱动开发）
- 可视化工作流编辑器（cc-wf-studio）
- 适合团队协作的标准化流程

**适用场景：**
- 需要标准化开发流程的团队
- 复杂项目的系统化开发
- 需要可重复工作流的项目

---

### 推荐的 Skills

#### 1. **deep-research** - 深度研究

```bash
claude skill install deep-research
```

用途：进行多来源、经过事实核查的深度研究，适合需要查阅大量资料的场景。

#### 2. **code-review** - 代码审查

```bash
claude skill install code-review
```

用途：审查代码变更，发现潜在 bug 和优化点。

#### 3. **wechat-tech-writer** - 技术写作助手

```bash
claude skill install wechat-tech-writer
```

用途：专门用于撰写技术类公众号文章，支持选题、大纲、正文生成。

#### 4. **wechat-original-writing** - 原创写作

```bash
claude skill install wechat-original-writing
```

用途：从网络研究创建原创内容，避免抄袭和 AI 腔，适合 daydayago 公众号的内容生产。

#### 5. **run** - 应用运行器

```bash
claude skill install run
```

用途：自动启动和测试项目，验证代码变更效果。

#### 6. **simplify** - 代码简化

```bash
claude skill install simplify
```

用途：重构和简化代码，提高可维护性。

### 管理 Skills

```bash
# 列出所有已安装的 skills
claude skill list

# 卸载某个 skill
claude skill uninstall <skill-name>

# 更新 skill
claude skill update <skill-name>
```

## 高级配置

### MCP 服务器

Claude Code 支持 MCP (Model Context Protocol) 服务器，可以扩展 Claude 的能力。

例如，添加 Notion 集成：

1. 在项目根目录创建 `.claude/settings.json`：

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-notion"]
    }
  }
}
```

### 自定义 Skills

你可以创建自己的 skills 来满足特定需求。

### 权限配置

Claude Code 会在执行危险操作前请求权限。可以在配置文件中预设权限：

```json
{
  "permissions": {
    "allow": [
      "bash:git:*",
      "bash:npm:*"
    ]
  }
}
```

## 常见问题

### Q: 国内如何使用 Claude Code？

A: 推荐使用 [Amux API](https://amux.ai/) 中转站：
- 访问 [Amux Console](https://api.amux.ai/console/token) 获取 Token
- 配置 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_API_KEY`
- 无需翻墙，价格更优惠，支持多模型切换

### Q: 如何在 WSL 中使用？

A: 在 WSL 中安装方式和 Linux 一样，确保 Node.js 版本正确即可。

### Q: API Key 获取方式？

A: 
- 官方 API：访问 [Anthropic Console](https://console.anthropic.com/) 创建 API Key
- 国内推荐：使用 [Amux API](https://api.amux.ai/console/token) 中转站

### Q: 如何设置默认模型？

A: 使用 `/config` 命令或编辑 `~/.claude/config.json`：

```json
{
  "defaultModel": "claude-sonnet-4-6"
}
```

### Q: Amux API 支持哪些模型？

A: Amux 支持双向转换，可以在 Claude Code 中使用：
- OpenAI 系列（GPT-4, GPT-5）
- Anthropic 系列（Claude 3/4）
- DeepSeek
- Gemini
- MiniMax
- Grok
- 等更多模型

## 资源链接

### AI 编程工具
- [Trae IDE 国际版（免费）](https://www.trae.ai/download) - 字节跳动推出，推荐新手使用
- [Trae IDE 国内版](https://www.trae.com.cn/) - 国内直连，集成国产模型
- [Trae IDE 官方文档](https://docs.trae.ai/ide/what-is-trae)

### 官方资源
- [官方文档](https://docs.anthropic.com/claude-code)
- [GitHub 仓库](https://github.com/anthropics/claude-code)
- [社区 Skills 仓库](https://github.com/anthropics/claude-code-skells)

### API 中转站
- [Amux API - 双向 LLM 适配器](https://amux.ai/) - 推荐国内使用
- [Amux Console - 获取 Token](https://api.amux.ai/console/token)
- [Amux Claude Code 使用指南](https://www.amux.ai/zh/docs/amux-api/guides/use/claude-code)
- [Amux Desktop 客户端](https://amux.ai/) - 可视化配置工具

### 进阶工具
- [Superpowers - Agent 开发框架](https://github.com/obra/superpowers)
- [CCW - 工作流生成器](https://github.com/ashleyha/claude-code-workflow)
- [CCW Workflow Studio](https://open-vsx.org/extension/breaking-brake/cc-wf-studio) - 可视化编辑器

### 学习资源
- [Claude Code 完整课程 (4小时)](https://www.youtube.com/watch?v=QoQBzR1NIqI)
- [Claude Code Workflow 指南](https://www.truefoundry.com/es/blog/claude-code-workflow-guide)
- [高级 Claude Code 工作流](https://ccforeveryone.com/mini-lessons/advanced-claude-workflows)
- [Claude Code 国内使用教程](https://deepseek.csdn.net/6a059e4b662f9a54cb746ea2.html)
- [Trae IDE 使用教程](https://www.youtube.com/watch?v=9maL_civCF4)

## 下一步

### 选择适合你的工具

**如果你是新手或喜欢可视化界面：**
1. 下载 [Trae IDE](https://www.trae.ai/download)
2. 注册并体验 AI 辅助编程
3. 探索 SOLO 模式和 IDE 模式

**如果你熟悉命令行或追求极致效率：**
1. 按以下顺序配置 Claude Code

### Claude Code 配置步骤

#### 第一步：体验基础功能
1. 用 `claude` 进入一个项目试试
2. 尝试基础编辑和搜索功能

#### 第二步：安装进阶工具（强烈推荐）
1. **安装 Superpowers** - 让你的开发流程系统化：
   ```bash
   /plugin install superpowers@claude-plugins-official
   ```
2. **探索 CCW** - 如果需要标准化工作流

#### 第三步：安装领域 Skills
1. **公众号写作**: `wechat-original-writing`, `wechat-tech-writer`
2. **代码质量**: `code-review`, `simplify`
3. **研究能力**: `deep-research`
4. **测试运行**: `run`, `verify`

#### 第四步：自定义配置
1. 探索 MCP 服务器扩展功能
2. 配置快捷键和权限
3. 创建自己的 skills

### 两种工具可以结合使用！

- 用 **Trae IDE** 进行可视化开发和项目理解
- 用 **Claude Code** 进行快速编辑和脚本自动化
- 根据场景灵活切换，提升整体效率

---

**更新日期**: 2026-06-03  
**适用版本**: Claude Code 4.x+
