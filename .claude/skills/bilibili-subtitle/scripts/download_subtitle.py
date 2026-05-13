#!/usr/bin/env python3
"""
哔哩哔哩字幕下载脚本
用于从B站视频下载字幕并转换为纯文本格式
"""

import sys
import re
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple


def load_cookie_from_file() -> Optional[str]:
    """从 04_Context/bilibili 登录信息.md 读取 Cookie"""
    cookie_file = Path("04_Context/bilibili 登录信息.md")
    if not cookie_file.exists():
        return None

    try:
        content = cookie_file.read_text(encoding='utf-8')
        # 查找 Cookies： 后面的值
        match = re.search(r'Cookies[：:]\s*(\S+)', content)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None


def check_cookie_valid(cookie: str) -> bool:
    """检查 Cookie 是否有效（简单检查格式）"""
    if not cookie:
        return False
    # 检查 SESSDATA 关键字段
    return 'SESSDATA' in cookie or len(cookie) > 50


def extract_bvid(url_or_bvid: str) -> Tuple[Optional[str], Optional[str]]:
    """从URL或输入中提取BV号或AV号，以及EP号（付费课程）"""
    # 清理输入
    text = url_or_bvid.strip()

    # 匹配完整URL中的BV号
    bvid_match = re.search(r'BV[0-9A-Za-z]{10}', text)
    if bvid_match:
        return bvid_match.group(0), None

    # 匹配完整URL中的AV号
    avid_match = re.search(r'av(\d+)', text, re.IGNORECASE)
    if avid_match:
        return f"av{avid_match.group(1)}", None

    # 匹配EP号（B站课堂/cheese）
    ep_match = re.search(r'ep(\d+)', text, re.IGNORECASE)
    if ep_match:
        return None, ep_match.group(1)

    # 直接输入BV号
    if re.match(r'^BV[0-9A-Za-z]{10}$', text):
        return text, None

    # 直接输入AV号
    if re.match(r'^av\d+$', text, re.IGNORECASE):
        return text.lower(), None

    # 直接输入EP号
    if re.match(r'^ep\d+$', text, re.IGNORECASE):
        return None, text[2:]

    return None, None


def fetch_cheese_info(ep_id: str, cookie: Optional[str] = None) -> Optional[dict]:
    """获取B站课堂(cheese)视频信息"""
    # 首先获取EP信息，得到aid和cid
    url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={ep_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    if cookie:
        headers['Cookie'] = f'SESSDATA={cookie}'

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('data'):
                season_data = data['data']
                episodes = season_data.get('episodes', [])
                # 找到对应的EP
                for ep in episodes:
                    if str(ep.get('id')) == ep_id:
                        return {
                            'title': season_data.get('title', '未知课程'),
                            'bvid': ep.get('bvid'),
                            'aid': ep.get('aid'),
                            'cid': ep.get('cid'),
                            'ep_title': ep.get('title', '未知章节')
                        }
                # 如果没找到匹配的EP，使用第一个
                if episodes:
                    ep = episodes[0]
                    return {
                        'title': season_data.get('title', '未知课程'),
                        'bvid': ep.get('bvid'),
                        'aid': ep.get('aid'),
                        'cid': ep.get('cid'),
                        'ep_title': ep.get('title', '未知章节')
                    }
            else:
                print(f"API错误: {data.get('message', '未知错误')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"获取课堂视频信息失败: {e}", file=sys.stderr)
        return None


def fetch_cheese_subtitle_list(cid: int, aid: int, cookie: Optional[str] = None, debug: bool = False) -> list:
    """获取课堂视频字幕列表 - 使用player/v2接口

    付费课程需要使用 /x/player/v2 接口，传入 cid 和 aid 参数
    """
    url = f"https://api.bilibili.com/x/player/v2?cid={cid}&aid={aid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    if cookie:
        headers['Cookie'] = f'SESSDATA={cookie}'

    if debug:
        print(f"[Debug] 付费课程字幕API: {url}", file=sys.stderr)

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if debug:
                print(f"[Debug] API响应: code={data.get('code')}, message={data.get('message')}", file=sys.stderr)
            if data.get('code') == 0:
                subtitle_info = data.get('data', {}).get('subtitle', {})
                subtitles = subtitle_info.get('subtitles', [])
                if debug:
                    print(f"[Debug] 找到 {len(subtitles)} 个字幕", file=sys.stderr)
                return subtitles
    except urllib.error.HTTPError as e:
        print(f"获取字幕列表HTTP错误: {e.code} - {e.reason}", file=sys.stderr)
    except Exception as e:
        print(f"获取字幕列表失败: {e}", file=sys.stderr)

    return []


def fetch_video_info(bvid: str, cookie: Optional[str] = None) -> Optional[dict]:
    """获取视频基本信息"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    if cookie:
        headers['Cookie'] = f'SESSDATA={cookie}'

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                print(f"API错误: {data.get('message', '未知错误')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"获取视频信息失败: {e}", file=sys.stderr)
        return None


def fetch_subtitle_list(cid: int, bvid: str, cookie: Optional[str] = None) -> list:
    """获取字幕列表"""
    url = f"https://api.bilibili.com/x/player/wbi/v2?cid={cid}&bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    if cookie:
        headers['Cookie'] = f'SESSDATA={cookie}'

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 0:
                subtitle_info = data.get('data', {}).get('subtitle', {})
                return subtitle_info.get('subtitles', [])
    except Exception as e:
        print(f"获取字幕列表失败: {e}", file=sys.stderr)

    return []


def download_subtitle(subtitle_url: str, cookie: Optional[str] = None) -> list:
    """下载字幕内容"""
    # 确保URL是完整的
    if subtitle_url.startswith('//'):
        subtitle_url = 'https:' + subtitle_url
    elif subtitle_url.startswith('/'):
        subtitle_url = 'https://api.bilibili.com' + subtitle_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    if cookie:
        headers['Cookie'] = f'SESSDATA={cookie}'

    try:
        req = urllib.request.Request(subtitle_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('body', [])
    except Exception as e:
        print(f"下载字幕失败: {e}", file=sys.stderr)
        return []


def format_subtitle(subtitle_data: list, with_timestamp: bool = False) -> str:
    """将字幕数据格式化为纯文本"""
    lines = []

    for item in subtitle_data:
        content = item.get('content', '').strip()
        if not content:
            continue

        if with_timestamp:
            start_time = item.get('from', 0)
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            lines.append(f"{timestamp} {content}")
        else:
            lines.append(content)

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python download_subtitle.py <B站视频URL或BV号> [输出文件路径] [--with-timestamp]", file=sys.stderr)
        print("示例: python download_subtitle.py BV1xx411c7mD", file=sys.stderr)
        print("       python download_subtitle.py https://www.bilibili.com/video/BV1xx411c7mD output.txt", file=sys.stderr)
        print("       python download_subtitle.py https://www.bilibili.com/cheese/play/ep12345 output.txt", file=sys.stderr)
        sys.exit(1)

    url_or_bvid = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    with_timestamp = '--with-timestamp' in sys.argv

    # 提取BV号或EP号
    bvid, ep_id = extract_bvid(url_or_bvid)

    # 加载 Cookie
    cookie = load_cookie_from_file()
    if not cookie:
        print("⚠️ 警告: 未找到 Cookie 文件 (04_Context/bilibili 登录信息.md)", file=sys.stderr)
        print("部分视频可能需要登录才能获取字幕", file=sys.stderr)
    elif not check_cookie_valid(cookie):
        print("⚠️ 警告: Cookie 格式可能无效或已过期", file=sys.stderr)
        print("请检查 04_Context/bilibili 登录信息.md 中的 Cookie 是否过期", file=sys.stderr)

    # 根据类型获取视频信息
    if ep_id:
        # B站课堂付费课程
        print(f"正在获取课堂视频信息: EP{ep_id}...")
        cheese_info = fetch_cheese_info(ep_id, cookie)
        if not cheese_info:
            print("获取课堂视频信息失败", file=sys.stderr)
            if cookie:
                print("提示: 付费课程需要有效的登录 Cookie，请确认 Cookie 是否过期", file=sys.stderr)
            sys.exit(1)

        title = cheese_info.get('title', '未知课程')
        ep_title = cheese_info.get('ep_title', '未知章节')
        cid = cheese_info.get('cid')
        aid = cheese_info.get('aid')

        print(f"课程标题: {title}")
        print(f"章节标题: {ep_title}")

        # 获取字幕列表 - 付费课程使用aid而不是bvid
        print("正在获取字幕列表...")
        subtitles = fetch_cheese_subtitle_list(cid, aid, cookie)

    elif bvid:
        # 普通视频
        print(f"正在获取视频信息: {bvid}...")
        video_info = fetch_video_info(bvid, cookie)
        if not video_info:
            print("获取视频信息失败", file=sys.stderr)
            sys.exit(1)

        title = video_info.get('title', '未知标题')
        pages = video_info.get('pages', [])

        if not pages:
            print("视频没有分P信息", file=sys.stderr)
            sys.exit(1)

        # 默认使用第一P
        cid = pages[0].get('cid')
        print(f"视频标题: {title}")
        print(f"当前分P: {pages[0].get('part', '默认分P')}")

        # 获取字幕列表
        print("正在获取字幕列表...")
        subtitles = fetch_subtitle_list(cid, bvid, cookie)
    else:
        print(f"无法从输入中提取视频ID: {url_or_bvid}", file=sys.stderr)
        print("支持的格式: BV号、AV号、EP号或完整URL", file=sys.stderr)
        sys.exit(1)

    if not subtitles:
        print("该视频没有可用的字幕", file=sys.stderr)
        if ep_id:
            print("\n可能的原因：", file=sys.stderr)
            print("1. Cookie 已过期 - 请更新 04_Context/bilibili 登录信息.md 中的 Cookie", file=sys.stderr)
            print("2. 未购买该课程 - 需要先用购买课程的账号登录", file=sys.stderr)
            print("3. 视频本身没有字幕 - 部分课程可能没有提供字幕", file=sys.stderr)
        else:
            print("\n提示: 该视频可能没有上传字幕，或需要登录才能查看", file=sys.stderr)
        sys.exit(1)

    # 选择中文字幕，如果没有则选择第一个
    selected_subtitle = None
    for sub in subtitles:
        lan = sub.get('lan', '').lower()
        if 'zh' in lan or 'cn' in lan or 'ai' in lan:
            selected_subtitle = sub
            break

    if not selected_subtitle:
        selected_subtitle = subtitles[0]

    print(f"使用字幕: {selected_subtitle.get('lan_doc', '未知语言')}")

    # 下载字幕
    print("正在下载字幕内容...")
    subtitle_body = download_subtitle(selected_subtitle.get('subtitle_url', ''), cookie)

    if not subtitle_body:
        print("下载字幕内容失败", file=sys.stderr)
        sys.exit(1)

    # 格式化字幕
    formatted_text = format_subtitle(subtitle_body, with_timestamp)

    # 输出
    if output_path:
        output_file = Path(output_path)
        output_file.write_text(formatted_text, encoding='utf-8')
        print(f"字幕已保存到: {output_file.absolute()}")
    else:
        print("\n--- 字幕内容 ---")
        print(formatted_text)


if __name__ == '__main__':
    main()
