
# 📤 领域输出与课程设计规范 (Output & Pedagogy)

当你被要求利用知识库内的卡片组装成一节课程（Lesson）或文章草稿时，必须严格遵守以下教学法结构。

## 1. 拼图原则 (Lego Assembly Principle)
- **拒绝凭空捏造：** 教案中的核心概念讲解、代码示例，必须是从 `02_Wiki/` 卡片库中提取的现成素材的“有机拼接”。
- **双链保留：** 在教案草稿中，凡是用到已有卡片的知识点，必须保留双链（如：`本节课我们将使用 [[syntax-Python文件操作与CSV]] 中的技巧...`），以便日后溯源。

## 2. 课程教案标准模板 (Lesson Plan Template)
教案必须采用以下五段式结构输出：

- **🎯 课程元数据 (Meta):**
  - **主题：** - **预计时长：** - **前置依赖：** (列出学生需要掌握的现有卡片，如 `[[syntax-Python字典]]`)
- **🔑 破冰与概念引入 (Hook & Concept):** - 结合生活痛点引入技术。提取 `concept-` 或 `syntax-` 卡片中的 `Why (为什么)` 模块。
- **💻 实战演示 (Live Coding):** - 必须结合具体的业务文件（如 `favorites.csv`）。给出教师在课上应该一步步敲出的代码片段，并标注易错点（从卡片中提取）。
- **⚔️ 课堂挑战 (Hands-on Challenge):** - 提取底层原子卡片中的 `### ❓ 检验与思考` 模块，将其改造为学生在课上需要完成的动手任务。
- **📝 核心总结 (Takeaways):** - 用 3 个要点总结本课。

## 3. Obsidian 渲染兼容规则

### `<details>` 折叠块内禁用 Markdown 代码围栏

**问题根因**：CommonMark 规范下，空行会切割 HTML 块。当 `<details>` 内部使用 ` ``` ` 代码围栏时，围栏前后的空行导致 `</details>` 与 `<details>` 被解析为两个独立 HTML 块，内部 Markdown 全部失效。

**❌ 错误写法**：
```markdown
<details>
<summary>参考实现</summary>

```python
code here
```

</details>
```

**✅ 正确写法**：用 `<pre><code>` 替代，消除内部空行。
```markdown
<details>
<summary>参考实现</summary>
<pre><code>code here
</code></pre>
</details>
```

**注意事项**：
- `<pre><code>` 内的 `>` 需转义为 `&gt;`，`<` 需转义为 `&lt;`
- 纯文本（无代码块）的 `<details>` 不受影响，可照常使用 ` ``` `
- `<details>` 与 `<summary>` 之间不得有空行；`</summary>` 后直接接 `<pre><code>` 也不得有空行