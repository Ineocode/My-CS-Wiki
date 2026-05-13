#!/usr/bin/env python3
"""
Download transcript/subtitle and rich metadata from a Bilibili video.

Usage:
    # Plain text output (backward compatible)
    python3 scripts/download_transcript.py <video_url_or_id> [--timestamps] [--page N]

    # Structured JSON output (for downstream LLM processing)
    python3 scripts/download_transcript.py <video_url_or_id> --json

Supports:
    - Regular videos: BV1xx411c7mD, av170001, or full bilibili.com/video/ URLs
    - Cheese courses: ep919997 or full bilibili.com/cheese/play/ URLs
    - b23.tv short links (follow redirects)
"""

import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


# ── ID parsing ──────────────────────────────────────────────────────────────

def extract_video_id(url_or_id: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse a Bilibili URL or raw ID.
    Returns (bvid, avid, ep_id) — only one will be non-None.
    """
    text = url_or_id.strip()

    # Cheese / course episode
    ep_match = re.search(r'ep(\d+)', text, re.IGNORECASE)
    if ep_match:
        return None, None, ep_match.group(1)

    # BV号 in URL
    bv_match = re.search(r'BV[0-9A-Za-z]{10}', text)
    if bv_match:
        return bv_match.group(0), None, None

    # AV号 in URL
    av_match = re.search(r'av(\d+)', text, re.IGNORECASE)
    if av_match:
        return None, f"av{av_match.group(1)}", None

    # Raw BV号
    if re.match(r'^BV[0-9A-Za-z]{10}$', text):
        return text, None, None

    # Raw AV号
    if re.match(r'^av\d+$', text, re.IGNORECASE):
        return text.lower(), None, None

    # Raw EP号
    if re.match(r'^ep\d+$', text, re.IGNORECASE):
        return None, None, text[2:]

    return None, None, None


# ── Cookie handling ─────────────────────────────────────────────────────────

def load_cookie() -> Optional[str]:
    """Read SESSDATA cookie from the project's bilibili login file."""
    cookie_file = Path("04_Context/bilibili 登录信息.md")
    if not cookie_file.exists():
        return None
    content = cookie_file.read_text(encoding='utf-8')
    match = re.search(r'Cookies[：:]\s*(\S+)', content)
    return match.group(1).strip() if match else None


# ── HTTP helpers ────────────────────────────────────────────────────────────

def make_request(url: str, cookie: Optional[str] = None) -> dict:
    """Make an HTTP GET request to the Bilibili API and return parsed JSON."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com',
    }
    if cookie:
        headers['Cookie'] = f'SESSDATA={cookie}; path=/; domain=.bilibili.com'

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def resolve_b23(short_url: str) -> str:
    """Follow a b23.tv redirect to get the real URL."""
    req = urllib.request.Request(
        short_url,
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.geturl()


# ── API fetchers ────────────────────────────────────────────────────────────

def fetch_regular_video(bvid: str, cookie: Optional[str] = None) -> dict:
    """
    Get full info for a regular BV/AV video via /x/web-interface/view.
    Returns enriched dict with title, author, desc, tags, cover, duration, pages, etc.
    """
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    data = make_request(url, cookie)
    if data.get('code') != 0:
        raise RuntimeError(f"视频信息获取失败: {data.get('message', '未知错误')}")
    v = data['data']
    return {
        'bvid': v.get('bvid', ''),
        'title': v.get('title', '未知标题'),
        'author': v.get('owner', {}).get('name', '未知UP主'),
        'author_uid': v.get('owner', {}).get('mid'),
        'description': v.get('desc', '').strip(),
        'tags': [t.get('tag_name', '') for t in v.get('tags', [])],
        'cover_url': v.get('pic', ''),
        'publish_date': format_unix(v.get('pubdate')),
        'duration': v.get('duration', 0),
        'pages': [
            {'page': p.get('page', i + 1), 'title': p.get('part', ''), 'cid': p.get('cid'), 'duration': p.get('duration', 0)}
            for i, p in enumerate(v.get('pages', []))
        ],
        'stat': {
            'view': v.get('stat', {}).get('view', 0),
            'danmaku': v.get('stat', {}).get('danmaku', 0),
            'reply': v.get('stat', {}).get('reply', 0),
            'favorite': v.get('stat', {}).get('favorite', 0),
        },
    }


def fetch_cheese_video(ep_id: str, cookie: Optional[str] = None) -> dict:
    """Get full info for a cheese course episode."""
    url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={ep_id}"
    data = make_request(url, cookie)
    if data.get('code') != 0:
        raise RuntimeError(f"课程信息获取失败: {data.get('message', '未知错误')}")
    season = data['data']
    for ep in season.get('episodes', []):
        if str(ep.get('id')) == ep_id:
            return {
                'bvid': ep.get('bvid', ''),
                'title': season.get('title', '未知课程'),
                'ep_title': ep.get('title', '未知章节'),
                'author': season.get('up_info', {}).get('uname', '未知UP主'),
                'author_uid': season.get('up_info', {}).get('mid'),
                'description': season.get('subtitle', '').strip(),
                'tags': [],
                'cover_url': ep.get('cover', ''),
                'publish_date': format_unix(season.get('publish', {}).get('pub_time')),
                'duration': ep.get('duration', 0),
                'pages': [{'page': 1, 'title': ep.get('title', ''), 'cid': ep['cid'], 'duration': ep.get('duration', 0)}],
                'stat': {},
                'cid': ep['cid'],
                'aid': ep['aid'],
            }
    raise RuntimeError(f"未找到 EP{ep_id} 对应的章节")


def fetch_subtitles(cid: int, aid: int = 0, bvid: str = '', cookie: Optional[str] = None) -> list:
    """
    Fetch subtitle list for a video.
    Uses /x/player/v2 (works for both regular videos and cheese courses when aid is provided).
    """
    params = f"cid={cid}"
    if aid:
        params += f"&aid={aid}"
    if bvid:
        params += f"&bvid={bvid}"
    url = f"https://api.bilibili.com/x/player/v2?{params}"
    data = make_request(url, cookie)
    if data.get('code') != 0:
        raise RuntimeError(f"字幕列表获取失败: {data.get('message', '未知错误')}")
    subtitle_info = data.get('data', {}).get('subtitle', {})
    return subtitle_info.get('subtitles', [])


def download_subtitle_content(subtitle_url: str, cookie: Optional[str] = None) -> list:
    """Download and parse the subtitle JSON. Returns the body list."""
    if subtitle_url.startswith('//'):
        subtitle_url = 'https:' + subtitle_url

    data = make_request(subtitle_url, cookie)
    return data.get('body', [])


# ── Formatting ──────────────────────────────────────────────────────────────

def format_unix(ts) -> str:
    """Unix timestamp to ISO date string."""
    if not ts:
        return ''
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_transcript(subtitle_body: list, with_timestamps: bool = False) -> str:
    """Convert subtitle body entries to plain text."""
    lines = []
    for item in subtitle_body:
        content = item.get('content', '').strip()
        if not content:
            continue
        if with_timestamps:
            stamp = format_timestamp(item.get('from', 0))
            lines.append(f"[{stamp}] {content}")
        else:
            lines.append(content)
    return '\n'.join(lines)


# ── Subtitle selection ──────────────────────────────────────────────────────

def select_best_subtitle(subtitles: list) -> Optional[dict]:
    """
    Select the best subtitle with priority:
    1. Manual Chinese (zh-CN, zh-Hans, zh)
    2. AI Chinese (ai-zh)
    3. Manual Chinese Traditional (zh-Hant, zh-TW)
    4. Any other language
    """
    if not subtitles:
        return None

    # Priority buckets
    manual_zh = []
    ai_zh = []
    manual_zht = []
    others = []

    for sub in subtitles:
        lan = sub.get('lan', '').lower()
        is_ai = sub.get('ai_type', 0) == 1 or 'ai' in lan
        if 'zh-hans' in lan or 'zh-cn' in lan or lan == 'zh':
            if is_ai:
                ai_zh.append(sub)
            else:
                manual_zh.append(sub)
        elif 'zh-hant' in lan or 'zh-tw' in lan:
            manual_zht.append(sub)
        else:
            others.append(sub)

    for bucket in [manual_zh, ai_zh, manual_zht, others]:
        if bucket:
            return bucket[0]
    return None


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Download Bilibili video transcript')
    parser.add_argument('video', help='Bilibili video URL or video ID (BV/AV/ep)')
    parser.add_argument('--timestamps', '-t', action='store_true',
                        help='Include timestamps in output')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output structured JSON with metadata + transcript')
    parser.add_argument('--page', '-p', type=int, default=1,
                        help='Select page number for multi-P videos (default: 1)')
    args = parser.parse_args()

    # Resolve b23.tv short links
    video_input = args.video
    if 'b23.tv' in video_input or 'b23.tv' in video_input.lower().replace(' ', ''):
        try:
            video_input = resolve_b23(video_input)
        except Exception as e:
            print(f"Error: 短链接解析失败: {e}", file=sys.stderr)
            sys.exit(1)

    bvid, avid, ep_id = extract_video_id(video_input)
    if not bvid and not avid and not ep_id:
        print(f"Error: 无法从输入中识别视频ID: {args.video}", file=sys.stderr)
        print("支持的格式: BV号、AV号、EP号，或完整 bilibili.com 链接", file=sys.stderr)
        sys.exit(1)

    cookie = load_cookie()

    try:
        # ── Phase 1: Fetch video metadata ──
        if ep_id:
            info = fetch_cheese_video(ep_id, cookie)
            full_title = info['title'] if not info.get('ep_title') else f"{info['title']} - {info['ep_title']}"
            page_count = len(info.get('pages', []))
            if args.page > page_count:
                print(f"Error: 分P序号 {args.page} 超出范围 (共 {page_count} P)", file=sys.stderr)
                sys.exit(1)
            page = info['pages'][args.page - 1]
            cid = page['cid']
            aid = info.get('aid', 0)
        else:
            info = fetch_regular_video(bvid or avid, cookie)
            full_title = info['title']
            page_count = len(info.get('pages', []))
            if args.page > page_count:
                print(f"Error: 分P序号 {args.page} 超出范围 (共 {page_count} P)", file=sys.stderr)
                sys.exit(1)
            page = info['pages'][args.page - 1]
            cid = page['cid']
            aid = info.get('aid', 0) or info.get('stat', {}).get('aid', 0)

        # ── Phase 2: Fetch subtitles ──
        subtitles = fetch_subtitles(cid, aid, info.get('bvid', bvid or ''), cookie)
        selected = select_best_subtitle(subtitles)

        subtitle_type = 'none'
        subtitle_lan = ''
        transcript = ''
        transcript_items = []

        if selected:
            subtitle_lan = selected.get('lan', '')
            is_ai = selected.get('ai_type', 0) == 1 or 'ai' in subtitle_lan.lower()
            subtitle_type = 'ai' if is_ai else 'manual'

            body = download_subtitle_content(selected.get('subtitle_url', ''), cookie)
            if body:
                transcript = format_transcript(body, with_timestamps=True)
                transcript_items = body

        # ── Build output ──
        metadata = {
            'bvid': info.get('bvid', ''),
            'title': full_title,
            'author': info.get('author', ''),
            'author_uid': info.get('author_uid'),
            'description': info.get('description', ''),
            'tags': info.get('tags', []),
            'cover_url': info.get('cover_url', ''),
            'publish_date': info.get('publish_date', ''),
            'duration': info.get('duration', 0),
            'page_count': page_count,
            'current_page': args.page,
            'page_title': page.get('title', ''),
            'subtitle_status': subtitle_type,  # 'manual', 'ai', or 'none'
            'subtitle_lan': subtitle_lan,
            'source_url': f"https://www.bilibili.com/video/{info.get('bvid', '')}?p={args.page}",
        }

        if args.json:
            output = {
                **metadata,
                'transcript': transcript,
                'transcript_items': [
                    {'from': item.get('from', 0), 'to': item.get('to', 0), 'content': item.get('content', '').strip()}
                    for item in transcript_items if item.get('content', '').strip()
                ],
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            # Plain text output (backward compatible)
            print(full_title)
            print(format_transcript(transcript_items, args.timestamps))

        # Status to stderr
        labels = {'manual': '人工字幕 (CC)', 'ai': 'AI生成字幕', 'none': '无字幕'}
        print(f"字幕状态: {labels.get(subtitle_type, '未知')}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
