---
name: bilibili-transcript
description: Extract subtitles and transcripts from Bilibili (B站) videos. Use when the user asks to download subtitles, captions, transcripts, or 字幕/逐字稿 from Bilibili — whether a regular video (BV号, AV号, bilibili.com/video/) or a paid course (bilibili.com/cheese/, ep号). Saves output as a structured Obsidian Markdown file with full metadata, AI-cleaned transcript, and knowledge takeaways. Also use when the user mentions B站, b23.tv, or asks to save video text content from Bilibili.
---

# Bilibili Transcript — 视频转录与知识提取

将 B 站视频转换为结构化 Obsidian 笔记。完整流水线：元数据抓取 → 字幕嗅探（三级降级）→ LLM 文本重构 → Obsidian 写入。

## 核心差异：Bilibili vs YouTube

| 差异维度 | YouTube | Bilibili (B站) | 应对策略 |
| --- | --- | --- | --- |
| **视频标识** | 单一 `v=xxxx` 参数 | `bvid` (视频ID) + `cid` (分P标识) | 同时解析并维护 `bvid` 和 `cid`，支持多 P 视频剪藏 |
| **字幕获取** | 几乎所有视频有 CC 或自动字幕 | 仅部分有 CC 或 AI 字幕，很多只有硬字幕或纯语音 | **三级降级策略**：API 拉取优先 → 云端 ASR 转译兜底 |
| **元数据获取** | Open Graph 或官方 API | 页面内嵌 `window.__INITIAL_STATE__` | 通过 API 直接抓取，避免 DOM 解析 |
| **反爬/防盗链** | 相对宽松 | 音视频流和接口强校验 `Referer` 和 Cookie | 请求携带 `Referer: https://www.bilibili.com` 和有效 Cookie |

## 支持格式

- `https://www.bilibili.com/video/BV1xx411c7mD` — 普通视频
- `https://www.bilibili.com/video/av170001` — AV号视频
- `https://b23.tv/xxxxx` — 短链接
- `https://www.bilibili.com/cheese/play/ep919997` — 付费课程
- 直接输入：`BV1xx411c7mD`、`av170001`、`ep919997`

---

## 四阶段流水线

### 阶段 1：元数据提取 (Metadata Extractor)

运行脚本并捕获 JSON 元数据：

```bash
python3 .claude/skills/bilibili-transcript/scripts/download_transcript.py "VIDEO_URL" --json
```

**输出关键字段：**

| 字段 | 说明 | 用途 |
| --- | --- | --- |
| `bvid` | 视频 BV 号 | 构建原始链接 |
| `title` | 视频标题 | Markdown 文件命名与 H1 |
| `author` | UP主名称 | Obsidian `author` frontmatter |
| `description` | 视频简介 | 丰富笔记上下文 |
| `tags` | 分区标签 | Obsidian `tags` frontmatter |
| `cover_url` | 封面图 URL | 嵌入 `![Cover]()` |
| `publish_date` | 发布日期 | 时间归档 |
| `duration` | 视频时长(秒) | 辅助判断是否需要分段处理 |
| `page_count` | 分P总数 | 多P视频：逐P处理 |
| `subtitle_status` | 字幕类型：`manual` / `ai` / `none` | 决定是否需要 ASR 降级 |
| `transcript` | 带时间戳的完整文本 | LLM 重构的输入 |
| `transcript_items` | 结构化字幕条目 `[{from, to, content}]` | 精确时间戳映射 |

**多P视频处理：** 使用 `--page N` 逐P抓取。对每个分P单独生成笔记，或合并为一篇大文章。

### 阶段 2：字幕嗅探与三级降级 (Transcript Sniffer)

脚本内置字幕选择优先级：

1. **Level 1 — 官方 CC 字幕**：UP主手动上传的字幕，质量最高。API 响应中 `ai_type=0`。
2. **Level 2 — B站 AI 字幕**：平台自动生成，准确率视语音清晰度而定。API 响应中 `ai_type=1`。
3. **Level 3 — 无字幕降级**：当 `subtitle_status == "none"` 时，脚本无法直接获取文本。此时需要：

   **降级方案 A — 提示用户手动提供：**
   告知用户该视频无可用字幕，建议：
   - 使用 B站手机端的 "AI 字幕" 功能实时查看
   - 提供视频链接，让用户自行观看后总结

   **降级方案 B — ASR 转录（需后端支持）：**
   若配置了 ASR 服务（如通义听悟 API / 字节火山引擎 / 本地 Whisper），则：
   1. 请求 `https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16` 获取 DASH 音频流
   2. 下载音频轨（需要 Cookie + Referer + Range 请求头）
   3. 发送到 ASR 服务获取转录文本
   4. 将结果注入后续 LLM 处理管道

   **注意**：ASR 降级需要在本地或服务端运行，纯前端方案受限于 CORS 和音频解码能力。如果你的技能运行在 Claude Code 环境中，Claude 本身无法执行 ASR——应向用户报告字幕缺失，并提供替代方案。

### 阶段 3：LLM 文本重构 (LLM Processing)

拿到原始转录文本后，使用 LLM 将其重构为结构化知识笔记。

**处理原则：**
- 默认使用当前对话中的模型处理（无需额外 API 调用）
- 对于超长视频（>1小时），建议分片处理或使用 Kimi 等长上下文模型
- 对于硬核技术/代码类视频，优先使用 DeepSeek 的逻辑提炼能力
- 如果当前模型输出不佳，可提示用户手动将文本发送给特定 LLM

**重构 Prompt 模板：**

```
你是一个专业的知识管理助手。请根据以下 B 站视频的元数据和转录文本，生成一份结构化的 Obsidian 笔记。

## 输入信息
- 标题：{title}
- UP主：{author}
- 发布日期：{publish_date}
- 视频简介：{description}
- 标签：{tags}

## 原始转录文本
{raw_transcript}

## 输出要求

1. **核心摘要**：用 150 字以内概括视频核心内容。

2. **关键知识点 (Key Takeaways)**：提取 3-5 个核心观点或知识点，使用无序列表呈现。若原始文本包含时间戳，在每条后标注时间点，格式：`[MM:SS]`。

3. **内容重构 (Clean Transcript)**：
   - 去除口语化的冗余语气词（"然后"、"就是说"、"这个那个"等）
   - 修正明显的 ASR 错别字和语法错误
   - 按逻辑主题分段，为每个段落添加合适的小标题（H3）
   - 保留时间戳，标注在每个段落的起始位置
   - 对于技术/代码内容，确保术语拼写准确
   - 如果视频是教程类，将操作步骤提炼为有序列表

4. **行动建议 (Action Items)**（如果适用）：提取视频中提到的具体操作、推荐工具、学习路径等可执行项。

直接输出 Markdown，不要包含"好的"、"以下是"等寒暄语。
```

### 阶段 4：Obsidian 输出 (Obsidian Output)

将 LLM 返回的 Markdown 与元数据组合，保存到工作区。

**文件命名规范：** `{标题}.md`（清理非法字符 `/` `:` `?` `"` `<` `>` `|`）

**输出模板：**

```markdown
---
title: "{{title}}"
author: "{{author}}"
date_clipped: "{{current_date}}"
source_url: "{{source_url}}"
tags: [bilibili, transcript, {{tags}}]
---

# {{title}}

![Cover]({{cover_url}})

> **来源：** [{{title}}]({{source_url}}) | **UP主：** {{author}} | **发布日期：** {{publish_date}}

## 📝 核心摘要
{{llm_summary}}

## 💡 关键知识点
{{llm_key_takeaways}}

---
## 📜 详细内容
{{llm_cleaned_transcript}}

## ✅ 行动建议
{{llm_action_items}}
```

---

## Cookie 认证

付费课程（cheese）和部分受限视频需要登录 Cookie。脚本自动从 `04_Context/bilibili 登录信息.md` 读取 `SESSDATA` 值。

**Cookie 文件格式：**
```markdown
Cookies：<完整的SESSDATA值>
```

**获取方法：**
1. 在浏览器中登录 bilibili.com
2. 打开开发者工具 → Application/Storage → Cookies
3. 找到 `SESSDATA` 字段，复制其值
4. 更新到 `04_Context/bilibili 登录信息.md`

若 Cookie 过期或文件不存在，脚本会在免费视频上正常工作，但付费课程会失败。

---

## 执行清单

当用户请求提取 B 站视频内容时，按以下步骤执行：

1. **运行脚本抓取原始数据**：
   ```bash
   python3 .claude/skills/bilibili-transcript/scripts/download_transcript.py "URL" --json
   ```

2. **检查 `subtitle_status`**：
   - `manual` 或 `ai`：有字幕，直接进入步骤 3
   - `none`：无字幕。向用户报告："该视频没有可用的 CC/AI 字幕。您可以选择：(A) 自行观看后口述核心内容，我来帮您整理成笔记；(B) 提供您从其他渠道获取的字幕文本。"

3. **使用 LLM 重构文本**：将 `transcript` 和元数据提交给 Prompt 模板，生成结构化笔记。

4. **组装并保存 Markdown**：将 LLM 返回内容填入 Obsidian 输出模板，保存到用户指定路径或当前工作目录。

5. **报告结果**：告知用户文件保存位置，以及字幕质量（人工/ AI生成），让用户对内容准确性有合理预期。

---

## 注意事项

- API 请求间隔建议 ≥ 1 秒，避免触发频率限制
- 部分港澳台/海外用户可能需要代理访问
- AI 字幕的错误率约为 10-30%，依赖语音清晰度和专业术语
- 长视频（>2小时）的转录文本可能超过某些 LLM 的上下文窗口，建议先估算 token 数（中文约 1.5 字符/token）
- EP 号目前仅支持付费课程（cheese），不支持番剧/影视的 EP
