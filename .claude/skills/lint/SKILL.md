---
name: lint
description: CS 知识库健康体检与代码格式巡检。扫描结构不完整的卡片（如缺失测试题、代码高亮错误）及死链。输入 "/lint" 时触发。
compatibility: Requires local file system access.
metadata:
  author: CS-SubWiki-System
---

<intent>
充当严格的 Code Reviewer 和教务人员。确保所有的教学卡片都拥有闭环的“检验与思考”模块，且代码格式标准。
</intent>

<context_routing>
- WHEN 校验卡片排版是否符合 FCC 三段式标准时 -> DO: 读取 `../../../00_System/02_Style.md`
</context_routing>

<instructions>
1. [深度文件扫描]
   遍历 `02_Wiki/` 下所有的 Markdown 文件。

2. [FCC 教学完整度校验]
   - 检查是否存在没有 `### ❓ 检验与思考 (Challenge / Active Recall)` 标题的卡片（教学闭环缺失）。
   - 检查是否存在没有 `### 💻 示例与机制` 或示例中未包含代码块的卡片（纸上谈兵）。

3. [代码高亮与格式合规检查]
   - 扫描所有 Markdown 代码块 (```)，检查是否遗漏了语言标记（如 `javascript`, `go`, `bash`）。
   - 检查 YAML 头是否完整。
   - 扫描死链（Dead Links）。
4. [结构超载与格式合规检查]
   - 检查 `02_Wiki/index.md` 的长度。如果单个大分类（如 `## 某某课程`）下的卡片数量超过 30 张，将其标记为“需要重构为 MOC”，并在最终报告中建议用户：“索引页当前负荷过重，建议将 [某分类] 拆分为独立的 `MOC-[领域名].md`”。
5. [诊断报告与自动修复]
   输出《CS 知识库工程健康报告》：
   - 🔴 **严重缺陷**（死链、缺失代码语言标记）
   - 🟡 **教学降级**（缺失挑战模块、缺失代码示例）
   - 🔵 **架构建议**（指出 index.md 中需要拆分为 `MOC-[领域名].md` 的超载分类）
   
   <action>输出报告后，主动申请权限：“是否授权我批量修复缺失语言标记的代码块，并为存在死链的文件进行标注？”</action>
</instructions>
