---
name: bilibili-subtitle
description: |
  下载哔哩哔哩(Bilibili/B站)视频字幕并输出为纯文本格式。
  当用户想要：
  - 下载B站视频字幕/弹幕
  - 提取Bilibili视频的字幕内容
  - 获取哔哩哔哩视频的CC字幕或自动生成的字幕
  - 将B站视频字幕保存为txt文件
  - 导出B站视频的字幕文本
  时使用此技能。
  支持 BV号、AV号或完整URL格式的视频地址。
---

# 哔哩哔哩字幕下载技能

## 功能概述

本技能用于从哔哩哔哩(B站)视频下载字幕内容，并输出为纯文本格式。

## 触发条件

当用户有以下请求时触发此技能：
- "下载B站视频字幕"
- "获取哔哩哔哩视频字幕"
- "导出Bilibili视频字幕为文本"
- "提取BVxxx的字幕"
- "保存B站视频字幕到文件"

## 工作流程

### 步骤 1: 解析视频ID

从用户输入中提取视频的 BV 号或 AV 号：

**支持的输入格式：**
- 完整URL：`https://www.bilibili.com/video/BV1xx411c7mD` → 提取 `BV1xx411c7mD`
- 完整URL：`https://www.bilibili.com/video/av170001` → 提取 `av170001`
- 直接输入：`BV1xx411c7mD` 或 `av170001`

### 步骤 2: 获取视频信息

使用 B 站 API 获取视频基本信息：

```bash
curl -s "https://api.bilibili.com/x/web-interface/view?bvid={BV号}" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://www.bilibili.com" | jq .
```

**关键字段：**
- `data.title`: 视频标题
- `data.pages`: 分P列表，每个分P包含 `cid` 和 `part`(分P标题)

### 步骤 3: 获取字幕列表

```bash
curl -s "https://api.bilibili.com/x/player/wbi/v2?cid={cid}&bvid={BV号}" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://www.bilibili.com" | jq .
```

**字幕信息位置：** `data.subtitle.subtitles`

### 步骤 4: 下载并转换字幕

从字幕列表中选择合适的字幕（优先中文字幕），下载并转换为纯文本。

## 推荐方法：使用内置脚本

技能目录下提供了 `scripts/download_subtitle.py` 脚本，推荐直接使用：

```bash
# 基本用法 - 输出到控制台
python .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD"

# 保存到文件
python .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD" "subtitle.txt"

# 带时间戳输出
python .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD" "subtitle.txt" --with-timestamp
```

## 手动方法：逐步执行

如需手动控制流程，可按以下步骤执行：

### 1. 获取视频 cid
```bash
BV="BV1xx411c7mD"
RESPONSE=$(curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BV" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://www.bilibili.com")
CID=$(echo $RESPONSE | jq -r '.data.pages[0].cid')
echo "CID: $CID"
```

### 2. 获取字幕URL
```bash
SUBTITLE_URL=$(curl -s "https://api.bilibili.com/x/player/wbi/v2?cid=$CID&bvid=$BV" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://www.bilibili.com" | \
  jq -r '.data.subtitle.subtitles[0].subtitle_url')
echo "字幕URL: $SUBTITLE_URL"
```

### 3. 下载并提取字幕文本
```bash
# 下载字幕JSON并提取content字段
curl -s "$SUBTITLE_URL" | jq -r '.body[].content' > subtitle.txt
echo "字幕已保存到 subtitle.txt"
```

## 输出格式

### 纯文本格式（默认）
```
字幕内容第一行
字幕内容第二行
字幕内容第三行
...
```

### 带时间戳格式（添加 --with-timestamp 参数）
```
[00:01] 字幕内容第一行
[00:05] 字幕内容第二行
[00:10] 字幕内容第三行
...
```

## 多P视频处理

对于包含多个分P的视频：
1. 从 `data.pages` 中获取所有分P信息
2. 让用户选择要下载的分P，或默认下载第一P
3. 使用选中分P的 `cid` 获取字幕

## Cookie 登录配置

本技能会自动从 `04_Context/bilibili 登录信息.md` 读取 Cookie 用于登录验证。

**文件格式要求：**
```markdown
Cookies：6671814f%2C1793547574%2C58278...
```

**说明：**
- 技能会自动检测 Cookie 文件是否存在
- 如果 Cookie 格式无效或已过期，会提示用户更新
- 付费课程视频通常需要有效的 Cookie 才能获取字幕

**如何更新 Cookie：**
1. 登录 B 站网页版
2. 打开浏览器开发者工具 → Application/Storage → Cookies
3. 找到 `SESSDATA` 字段的值
4. 更新到 `04_Context/bilibili 登录信息.md` 文件中

## 注意事项

1. **字幕可用性**：并非所有视频都有字幕，部分视频只有自动生成的字幕或没有字幕
2. **登录限制**：大部分视频字幕无需登录即可获取，但部分UP主可能设置了权限
3. **付费课程**：付费课程（如 B站课堂/cheese）需要有效的登录 Cookie 才能获取字幕
4. **API频率**：避免短时间内大量请求，以防触发频率限制
5. **字幕类型**：优先选择人工上传的中文字幕(zh-CN)，其次是自动生成字幕(ai-CN)

## 错误处理

常见错误及解决方案：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 视频不存在 | BV号错误或视频已删除 | 检查BV号是否正确 |
| 无字幕 | 视频没有上传字幕 | 告知用户该视频无可用字幕 |
| Cookie无效 | Cookie格式错误或已过期 | 更新 `04_Context/bilibili 登录信息.md` 中的 Cookie |
| 付费课程无法获取 | Cookie过期或没有购买课程 | 检查 Cookie 是否过期；确认账号已购买该课程 |
| 获取失败 | 网络问题或API限制 | 稍后重试 |

## 示例对话

**用户**：下载这个视频的字幕 https://www.bilibili.com/video/BV1xx411c7mD

**Claude**：
1. 提取BV号：`BV1xx411c7mD`
2. 使用脚本获取字幕：
   ```bash
   python .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD" "BV1xx411c7mD_subtitle.txt"
   ```
3. 返回结果：字幕已保存到 `BV1xx411c7mD_subtitle.txt`
