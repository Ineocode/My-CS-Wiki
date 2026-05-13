# Bilibili 字幕下载技能

## 功能概述

从哔哩哔哩(B站)视频下载字幕内容，支持普通视频和付费课程(cheese)。

## 支持的链接格式

- 普通视频：`https://www.bilibili.com/video/BV1xx411c7mD`
- 付费课程：`https://www.bilibili.com/cheese/play/ep919997`
- 直接输入：BV号、AV号、EP号

## 快速使用

```bash
# 基本用法 - 输出到控制台
python3 .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD"

# 保存到文件
python3 .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD" "output.txt"

# 付费课程
python3 .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "ep919997" "output.txt"

# 带时间戳输出
python3 .claude/skills/bilibili-subtitle/scripts/download_subtitle.py "BV1xx411c7mD" "output.txt" --with-timestamp
```

## Cookie 配置（付费课程必需）

对于B站课堂付费课程，需要在 `04_Context/bilibili 登录信息.md` 中配置Cookie：

```markdown
Cookies：your_sessdata_here
```

**获取Cookie方法：**
1. 登录 B 站网页版
2. 打开浏览器开发者工具 → Application/Storage → Cookies
3. 复制 `SESSDATA` 字段的值

## 技术要点

### API 差异

| 视频类型 | API 端点 | 必需参数 |
|---------|---------|---------|
| 普通视频 | `/x/player/wbi/v2` | cid + bvid |
| 付费课程 | `/x/player/v2` | cid + aid |

### 付费课程获取流程

1. 通过 `pugv/view/web/season?ep_id={ep_id}` 获取课程信息
2. 从返回数据中提取 `cid` 和 `aid`
3. 使用 `/x/player/v2?cid={cid}&aid={aid}` 获取字幕列表

## 常见问题

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| Cookie 已过期 | SESSDATA 失效 | 更新 Cookie 文件 |
| 未购买课程 | 账号没有权限 | 使用已购买课程的账号 |
| 视频无字幕 | 视频本身没有字幕 | 无法获取 |
| API 404 | 接口不匹配 | 已修复，使用正确接口 |

## 更新日志

### 2026-05-07
- 修复付费课程字幕获取失败问题
- 将 API 从 `wbi/v2` 改为 `v2` 用于付费课程
- 添加详细错误提示信息
- 添加调试模式支持
