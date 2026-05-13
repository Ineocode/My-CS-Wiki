# CS Wiki — AI 驱动的渐进式计算机科学知识库

<p align="center">
  <strong>🧠 用原子卡片构建完整知识闭环 | Claude Code × Obsidian 深度融合</strong>
</p>

> Build a self-contained, progressively-learnable CS knowledge graph through AI-assisted card generation, merging, and retrieval.

---

## 核心理念

CS Wiki 是一个**可复用的计算机科学知识库模板**，它将 freeCodeCamp 的 "概念 → 示例 → 检验" 三段式教学法与 Claude Code 的自动化能力结合，解决技术学习中三个核心痛点：

1. **碎片化知识** → 每张卡片是独立的 FCC 闭环单元，复习时无需翻阅外部资料
2. **积累与检索低效** → Obsidian 双向链接 + `/query` 语义检索，秒级定位答案
3. **笔记维护成本高** → `/ingest` 自动从原始文档生成卡片，`/lint` 自动诊断库健康度

## 快速概览

| 目录 | 定位 | 权限 |
|---|---|---|
| `00_System/` | AI 行为规范、命名字典、排版模板 | 读取（AI 规则） |
| `01_Raw_Sources/` | 官方文档、论文、源码、书籍 | **只读** |
| `02_Wiki/` | FCC 原子卡片库（concept / algo / syntax / tool / bug） | 读写（核心工作区） |
| `03_Outputs/` | 组装好的课程教案、文章、幻灯片 | 读写（输出物） |
| `04_Context/` | 临时上下文（如 B 站 Cookie） | 读写 |
| `.claude/skills/` | Claude Code 技能包定义 | 配置 |

## 卡片系统

每张卡片遵循统一的 **FCC 三段式** 结构，以 `concept-事件循环.md` 为例：

```markdown
---
aliases: [Event Loop]
tags: [JavaScript, runtime]
source_linked: ["[[MDN Concurrency Model]]"]
created: 2026-05-13
updated: 2026-05-13
---

> [!abstract] 核心概念
> **What:** 事件循环是 JS 运行时的并发模型...
> **Why:** 解决了单线程下非阻塞 I/O 的调度问题...

### 💻 示例与机制
（带注释的可运行代码 + 底层机制分析）

### ❓ 检验与思考
（直击灵魂的面试题 / 边界情况拷问）

---
### 🕸️ 领域知识网
- 源文档：[[MDN Concurrency Model]]
- 前置依赖：[[concept-调用栈]]
```

所有卡片通过英文前缀分类，精确检索：

| 前缀 | 领域 | 示例 |
|---|---|---|
| `concept-` | 基础理论、架构、协议 | `concept-CAP定理.md` |
| `algo-` | 算法与数据结构 | `algo-二分查找.md` |
| `syntax-` | 编程语言语法特性 | `syntax-Python装饰器.md` |
| `tool-` | 开发者工具与 CLI | `tool-Docker容器编排.md` |
| `bug-` | 经典报错排查 | `bug-CORS策略错误.md` |

## Claude Code 技能（Slash Commands）

在 Claude Code 会话中直接使用以下命令：

### `/ingest <源文件路径>`
将技术文档、教程或源码解析为 FCC 格式卡片。自动查重——如果卡片已存在，则执行知识融合而非覆盖。
```
/ingest ~/Downloads/react-hooks-deep-dive.pdf
```

### `/query <技术问题>`
在本地卡片库中精准检索答案，所有回答附卡片溯源，拒绝凭空生成代码。
```
/query 如何实现一个前端路由？
```

### `/draft <主题>`
将多张原子卡片拼装为标准课程教案或技术文章，输出到 `03_Outputs/`。
```
/draft Python 文件操作与 CSV 处理
```

### `/lint`
扫描全库的卡片完整度——缺失的 Challenge 模块、未标记语言的代码块、死链、索引过载，生成健康诊断报告。
```
/lint
```

### `pdf`
PDF 读取、合并、拆分、旋转、水印、OCR 文字识别、表单填充。可直接摄入扫描版论文和技术书籍。
```
请把这篇论文提取为知识卡片
```

### B 站字幕提取
- **`bilibili-subtitle`**：下载 B 站视频字幕为纯文本
- **`bilibili-transcript`**：完整流水线——元数据 → 字幕 → LLM 重构 → Obsidian 结构化笔记

支持 BV 号、AV 号、付费课程 (cheese) 的 ep 号。

### `skill-creator`
在知识库中创建、修改、评测自定义技能。可扩展新的 CS 领域技能包（如自动出题、代码审查、LeetCode 刷题助手）。
```
帮我创建一个自动出 LeetCode 风格题目的技能
```

### `find-skills`
发现和安装更多 Claude Code 技能，持续扩展知识库的工具链能力。
```
帮我找个能画时序图的技能
```

## 前置要求

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)** — AI 驱动的技能引擎
- **[Obsidian](https://obsidian.md)** (可选) — 可视化知识图谱与双向链接
- Python 3.8+ — B 站字幕脚本的运行环境

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/cs-wiki.git
cd cs-wiki

# 2. 安装 Python 依赖（用于 B 站技能脚本）
pip install -r requirements.txt

# 3. 在 Claude Code 中打开知识库
claude

# 4. 开始 /ingest 你的第一篇技术文档
/ingest 01_Raw_Sources/your-first-doc.md
```

详细配置见 [QUICKSTART.md](./QUICKSTART.md)。

## 协作哲学

1. **原子卡片优先** — 每张卡片只承载一个可独立理解的知识点；复杂主题拆成多张卡片，用双向链接织网
2. **代码可运行** — 示例代码必须能直接跑，禁止使用已废弃的 API
3. **渐进披露** — 技能按需加载规范，不在全局上下文中堆积冗余规则
4. **Human-in-the-loop** — AI 负责生成和检索，你负责最后的判断和提问

## 自定义

- 修改 `00_System/01_Naming.md` 添加你自己的卡片前缀
- 修改 `00_System/02_Style.md` 调整卡片排版模板
- 修改 `00_System/03_AI_Principles.md` 注入你的代码质量标准
- 在 `00_System/04_Outputs.md` 中定义你自己的课程教案模板
- 在 `.claude/skills/` 下添加新的技能包

## License

MIT
