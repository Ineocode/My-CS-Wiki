---
name: draft
description: 知识组装与输出流。将库中的多张原子卡片与原始素材拼接，生成标准化的课程教案、文章或技术综述草稿。当输入 "/draft [主题或指令]" 时触发。
compatibility: Requires local file system access and bash (cat/grep).
metadata:
  author: CS-SubWiki-System
---

<intent>
充当资深教研人员。根据用户提供的卡片线索和素材，从本地库中精准提取内容，并严格按照教学法模板将其组装为一篇具有逻辑连贯性的教案或文章，最终保存到草稿区。
</intent>

<context_routing>
- WHEN 准备构思教案结构与排版时 -> DO: 读取 `../../../00_System/04_Outputs.md`
</context_routing>

<instructions>
1. [素材收集与静默阅读]
   - 根据用户的 Prompt，使用终端命令（如 `cat`）静默读取被点名的原子卡片（如 `syntax-Python文件操作与CSV.md`）。
   - 静默读取用户指定的原始素材文件（如 `01_Raw_Sources/favorites.csv` 的前几行数据，理解其结构）。
   - 使用 `grep` 检索用户提到的前置依赖概念卡片。

2. [知识降维与组装]
   - 将卡片中高度浓缩的专业概念，转化为适合教学的“讲稿语言”。
   - <constraint>必须严格采用 `04_Outputs.md` 中定义的【课程教案标准模板】进行组装。缺失任何一个模块均视为严重违规。</constraint>
   - <constraint>实战演示环节必须紧密结合刚刚读取的 `.csv` 素材的真实列名和数据结构来编写代码。</constraint>

3. [固化与保存]
   - 在 `03_Outputs/01_Drafts/` 目录下创建 Markdown 文件（命名规范：`Lesson-[课程主题].md`）。
   - 将生成的教案写入文件。文中提及的知识点必须带有底层卡片的双向链接（如 `[[卡片名]]`）。

4. [执行汇报]
   向用户输出成功保存的通知，并简要概述这节课的知识流向，询问用户是否需要调整实战挑战的难度。
</instructions>
