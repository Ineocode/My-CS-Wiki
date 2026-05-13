---
name: ingest
description: CS领域文献与文档摄入流。解析技术文档、源码或教程，生成或更新基于 FCC 三段式的独立教学卡片。包含自动查重与合并同类项机制。当输入 "/ingest [文件路径]" 时触发。
compatibility: Requires local file system access and bash (grep/ls).
metadata:
  author: CS-SubWiki-System
---

<intent>
将原始的硬核技术文献或开源文档进行切片。提炼出具有“自包含完整性”的技术知识点。在生成前强制查重，若知识点已存在，则进行知识融合（Merge）；若不存在，则新建 FCC 三段式闭环卡片。
</intent>

<context_routing>
遵循渐进披露原则：
- WHEN 确定技术卡片的分类前缀时 -> DO: 读取 `../../../00_System/01_Naming.md`
- WHEN 准备输出 FCC 三段式卡片排版时 -> DO: 读取 `../../../00_System/02_Style.md`
- WHEN 评估代码边界条件与准确性时 -> DO: 读取 `../../../00_System/03_AI_Principles.md`
</context_routing>

<instructions>
1. [技术静默解析]
   深度阅读用户提供的源文件。识别出其中的底层机制、核心算法、语法特性或典型 Bug。捕捉性能瓶颈或边界条件（Edge Cases）。

2. [精准查重与分支决策 (Deduplication Check)]
   确定提取的技术名词标题（如 `algo-二分查找.md`）后，**必须**使用 bash 命令（如 `ls 02_Wiki/ | grep "关键词"`）在库中检查是否已存在相同或高度相似的卡片。
   - 🔴 **分支 A (无重复)：** 执行 [Step 3A - 新建卡片]
   - 🔵 **分支 B (已存在)：** 执行 [Step 3B - 知识融合]

3. [FCC 三段式操作与格式锁]
   
   **[Step 3A - 新建卡片]**
   在 `02_Wiki/` 目录下创建新卡片。
   <formatting_lock>
   必须严格使用以下 FCC 三段式模板，不得缺失 Challenge 模块：
   
   ---
   aliases: [别名/英文]
   tags: [技术栈]
   source_linked: ["[[源文件名称]]"]
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---
   
   > [!abstract] 核心概念 (Concept)
   > **What (是什么):** （精准专业定义）
   > **Why (为什么):** （解决的痛点及底层逻辑）
   
   ### 💻 示例与机制 (Example & Under the Hood)
   （高可用代码块或 Mermaid 图，分析时空复杂度或机制。）
   
   ### ❓ 检验与思考 (Challenge / Active Recall)
   （设计 1-2 个直击灵魂的测试题、面试题或边界情况拷问。）
   
   ---
   ### 🕸️ 领域知识网
   - 源文档：[[源文件名称]]
   </formatting_lock>

   **[Step 3B - 知识融合 (Merge existing)]**
   静默读取已存在的卡片内容，将新源文件中的知识无缝整合进原有卡片中：
   <constraint>
   - **更新 YAML：** 将新源文件追加到 `source_linked` 列表中，更新 `updated` 时间。
   - **增强代码与边界：** 如果新文件提供了更优的代码实现或指出了新的 Bug/边界情况，补充到 `### 💻 示例与机制` 中。若是版本差异冲突，使用 `> [!warning] ⚠️ 版本/学术分歧` 标明。
   - **升级挑战题：** 基于新知识，在 `### ❓ 检验与思考` 中追加 1 个更深入的测试题。
   - **绝对禁止：** 破坏原有卡片的 FCC 结构，或直接把新文章堆砌在旧文章末尾。必须是“有机融合”。
   </constraint>

4. [全域织网与登记]
   - 检查并更新双向链接。更新 `02_Wiki/index.md`。
   - 在 `log.md` 中记录动作（需区分是 `[Create]` 还是 `[Merge]`）。

5. [执行汇报]
   向用户输出执行报告，清晰列出：
   - 🆕 新建了哪些卡片。
   - 🔄 融合更新了哪些卡片（并简述补充了什么新特性/边界条件）。
</instructions>
