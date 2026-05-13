---
name: query
description: CS 技术难题与代码检索流。在子库内精准搜索算法实现、架构模式或报错解决方案，并输出严谨的代码级解答。输入 "/query [问题]" 时触发。
compatibility: Requires bash (grep/rg).
metadata:
  author: CS-SubWiki-System
---

<intent>
充当资深技术助教。基于本地 `02_Wiki/` 的卡片和 `01_Raw_Sources/` 的官方文档回答技术问题，拒绝编写凭空的、未経験证的伪代码。
</intent>

<context_routing>
- WHEN 需要确认代码准确性原则时 -> DO: 读取 `../../../00_System/03_AI_Principles.md`
</context_routing>

<instructions>
1. [本地精准检索]
   利用终端命令（如 `grep -r "技术关键词" 02_Wiki/`）穷尽搜索相关的 `concept-`, `algo-`, `syntax-` 或 `bug-` 卡片。

2. [工程级解答生成]
   使用中文作答。
   <constraint>
   - 🔴 **代码真实性：** 回答中如果包含代码片段，必须是库中已有卡片的引用，或者严格基于文档推导。
   - 🔴 **溯源闭环：** 必须指明该知识点来自哪张卡片（例如：“根据库中的 `[[algo-快速排序]]` 卡片...”）。若库中无相关记录，直接回复“当前技术库尚未收录该知识点”。
   </constraint>

3. [技术博客产出提议]
   如果用户的问题涉及到多个底层概念的串联（比如：“如何从零实现一个前端路由？”），提议将其整理为技术博客草稿，存入 `03_Outputs/01_Drafts/`。
</instructions>
