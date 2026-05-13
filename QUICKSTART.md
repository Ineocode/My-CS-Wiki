# Quickstart — 从零开始搭建你的 CS 知识库

本指南带你 5 分钟内完成环境配置，并积累你的第一张技术卡片。

---

## 环境要求

| 工具 | 最低版本 | 用途 |
|---|---|---|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) | 最新稳定版 | AI 技能引擎 |
| Python | 3.8+ | B 站字幕脚本 |
| [Obsidian](https://obsidian.md) | 非强制 | 可视化浏览知识图谱 |
| Git | 任意版本 | 版本控制与备份 |

### 安装 Claude Code

```bash
# macOS / Linux
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version
```

首次使用需要完成 Anthropic API 认证，详见 [官方文档](https://docs.anthropic.com/en/docs/claude-code/overview)。

---

## 第 1 步：克隆并初始化

```bash
# 克隆知识库模板
git clone https://github.com/YOUR_USERNAME/cs-wiki.git My-CS-Wiki
cd My-CS-Wiki

# （可选）创建 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖（目前仅 B 站技能需要）
pip install -r requirements.txt
```

<details>
<summary><strong>如果你还没有 requirements.txt</strong></summary>
<pre><code>echo "requests>=2.28" > requirements.txt</code></pre>
</details>

---

## 第 2 步：用 Obsidian 打开（推荐）

1. 启动 Obsidian
2. 点击 "Open folder as vault"（打开文件夹为仓库）
3. 选择你刚刚 clone 的 `My-CS-Wiki` 目录
4. Obsidian 会自动识别 `.obsidian/` 中的配置（含插件、主题、CSS 片段）

<details>
<summary><strong>不使用 Obsidian？</strong></summary>
完全没有问题。所有卡片都是纯 Markdown 文件，Claude Code 可以直接读写。你只是无法可视化知识图谱，但所有 AI 技能完全不受影响。
</details>

---

## 第 3 步：启动 Claude Code

在知识库根目录运行：

```bash
claude
```

Claude Code 启动后会**自动读取** `CLAUDE.md` 和 `00_System/00_Global_Rules.md`，加载你的助教人设和所有规则。你会看到 Claude 以"资深技术助教"的角色响应你。

---

## 第 4 步：摄入你的第一篇文档

把你想学习的任何技术文档、教程、博客文章放进 `01_Raw_Sources/` 目录，然后：

```
/ingest 01_Raw_Sources/your-doc.md
```

Claude 会：
1. 深度解析文档中的核心概念、代码示例、边界条件
2. 自动查重——如果库中已有同类卡片，执行知识融合而非覆盖
3. 生成 FCC 三段式卡片到 `02_Wiki/` 文件夹
4. 更新索引 (`index.md`) 和日志 (`log.md`)

**没有现成的文档？** 试试这个：

```
请用 /ingest 的思路，为我生成一张 concept-大O表示法.md 的卡片
```

---

## 第 5 步：提问与检索

随时向 Claude 提出技术问题：

```
/query js的闭包在内存中是怎么存活的
```

Claude 会搜索本地卡片库，给出带溯源的工程级回答。如果库中没有相关卡片，会如实告知"当前技术库尚未收录该知识点"——绝不凭空捏造。

---

## 第 6 步：课程组装

积累足够卡片后，尝试将它们组装为一堂课：

```
/draft 给初学者讲：浏览器从输入 URL 到页面渲染的全过程
```

Claude 会从库中提取相关卡片，按教案五段式模板组装，输出到 `03_Outputs/01_Drafts/`。

---

## 第 7 步：健康检查

定期运行健康巡检，确保卡片质量：

```
/lint
```

你会收到一份包含三个维度的诊断报告：
- 🔴 严重缺陷（死链、缺失代码语言标记）
- 🟡 教学降级（缺少 Challenge 模块、缺少代码示例）
- 🔵 架构建议（索引过载、建议拆分为 MOC）

---

## B 站字幕配置（可选）

### 免费视频
无需任何配置，直接使用：

```
/bilibili-transcript https://www.bilibili.com/video/BV1xx411c7mD
```

### 付费课程

1. 在浏览器登录 [bilibili.com](https://www.bilibili.com)
2. 按 F12 → Application → Cookies → 找到 `SESSDATA`
3. 将其值写入 `04_Context/bilibili 登录信息.md`：

```markdown
Cookies：你的SESSDATA值
```

### 完整转录工作流

```
/bilibili-transcript https://www.bilibili.com/video/BV1xx411c7mD
```

该技能会执行四阶段流水线：元数据提取 → 字幕嗅探（三级降级）→ LLM 文本重构 → 保存为 Obsidian 结构化笔记。

---

## 目录结构回顾

```
My-CS-Wiki/
├── CLAUDE.md                  # Claude Code 入口指令
├── README.md                  # 项目说明
├── QUICKSTART.md              # 本文件
├── requirements.txt           # Python 依赖
│
├── 00_System/                 # 📐 系统规则（AI 行为规范）
│   ├── 00_Global_Rules.md     # 入口规则，递归加载以下文件
│   ├── 01_Naming.md           # 卡片命名法与前缀字典
│   ├── 02_Style.md            # FCC 三段式排版模板
│   ├── 03_AI_Principles.md    # 代码准确性底线
│   └── 04_Outputs.md          # 教案组装模板
│
├── 01_Raw_Sources/            # 📚 原始素材（只读）
│
├── 02_Wiki/                   # 🗂️ 卡片库（核心工作区）
│   ├── index.md               # 全局索引
│   └── log.md                 # 变更日志
│
├── 03_Outputs/                # 📤 输出物
│   ├── 01_Drafts/             # 课程/文章草稿
│   ├── 02_Final/              # 定稿
│   └── 03_Slides/             # 幻灯片
│
├── 04_Context/                # 📎 临时上下文
│
├── .claude/skills/            # ⚡ Claude Code 技能定义
│   ├── ingest/SKILL.md
│   ├── query/SKILL.md
│   ├── draft/SKILL.md
│   ├── lint/SKILL.md
│   ├── bilibili-transcript/SKILL.md
│   ├── pdf/SKILL.md
│   ├── skill-creator/SKILL.md
│   └── find-skills/SKILL.md
│
└── .obsidian/                 # 🧩 Obsidian 配置（插件/主题/CSS）
```

---

## 常见问题

**Q: 不安装 Obsidian 能用吗？**
完全能用。所有卡片是纯 Markdown，Claude Code 直接读写。Obsidian 只提供额外的图谱可视化。

**Q: 卡片放在 02_Wiki 的什么位置？**
默认直接放在 `02_Wiki/` 根目录。当某个领域的卡片超过 30 张时，`/lint` 会建议你创建子目录并用 `MOC-领域名.md` 做地图索引。

**Q: 我可以修改卡片模板吗？**
可以。编辑 `00_System/02_Style.md` 中的 FCC 模板，之后所有 `/ingest` 生成的卡片都会遵循新模板。

**Q: 多个 AI 同时操作会冲突吗？**
会。当前版本只支持单用户单会话。多会话并发的冲突处理将在后续版本中解决。

**Q: 如何贡献技能包？**
在 `.claude/skills/` 下创建新目录，按照现有技能的 `SKILL.md` 格式编写即可。`CLAUDE.md` 会自动加载所有技能。
