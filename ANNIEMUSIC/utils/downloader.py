import asyncio
import contextlib
import os
import re
import random
from typing import Dict, Optional, Union

import aiofiles
import aiohttp
from aiohttp import TCPConnector
from yt_dlp import YoutubeDL

from ANNIEMUSIC.core.dir import DOWNLOAD_DIR as _DOWNLOAD_DIR, CACHE_DIR
from ANNIEMUSIC.utils.cookie_handler import COOKIE_PATH
from ANNIEMUSIC.utils.tuning import CHUNK_SIZE, SEM
from config import API_KEY, API_URL

USE_API: bool = bool(API_URL and API_KEY)

_COOKIES_FILE = str(COOKIE_PATH)

_inflight: Dict[str, asyncio.Future] = {}
_inflight_lock = asyncio.Lock()

_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()

# User agents list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def extract_video_id(link: str) -> str:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return link.split("/")[-1].split("?")[0]


def _cookiefile_path() -> Optional[str]:
    try:
        if _COOKIES_FILE and os.path.exists(_COOKIES_FILE) and os.path.getsize(
            _COOKIES_FILE
        ) > 0:
            return _COOKIES_FILE
    except Exception:
        pass
    return None


def file_exists(video_id: str) -> Optional[str]:
    for ext in ("mp3", "m4a", "webm", "mp4", "m4a"):
        path = f"{_DOWNLOAD_DIR}/{video_id}.{ext}"
        if os.path.exists(path):
            return path
    return None


def _safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]+', "_", (name or "").strip())[:200]


def _ytdlp_base_opts() -> Dict[str, Union[str, int, bool]]:
    opts: Dict[str, Union[str, int, bool]] = {
        "outtmpl": f"{_DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "overwrites": True,
        "continuedl": True,
        "noprogress": True,
        "concurrent_fragment_downloads": 8,  # Reduced from 16
        "http_chunk_size": 1048576,  # 1MB
        "socket_timeout": 30,
        "retries": 10,  # Increased retries
        "fragment_retries": 10,  # Increased fragment retries
        "cachedir": str(CACHE_DIR),
        "extractaudio": False,
        "nocheckcertificate": True,
        "ignoreerrors": True,
        "logtostderr": False,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "compat_opts": {"no-youtube-unavailable-videos"},
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["configs", "webpage"],
            }
        },
        "http_headers": {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "Connection": "keep-alive",
            "Referer": "https://www.youtube.com/",
        },
    }
    
    cookiefile = _cookiefile_path()
    if cookiefile:
        opts["cookiefile"] = cookiefile
        print(f"Using cookies from: {cookiefile}")
    else:
        print("No cookies file found, proceeding without cookies")
        
    return opts


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session and not _session.closed:
        return _session
    async with _session_lock:
        if _session and not _session.closed:
            return _session
        timeout = aiohttp.ClientTimeout(total=600, sock_connect=20, sock_read=60)
        connector = TCPConnector(limit=0, ttl_dns_cache=300, enable_cleanup_closed=True)
        _session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return _session


async def api_download_song(link: str) -> Optional[str]:
    if not USE_API:
        return None
    vid = extract_video_id(link)
    poll_url = f"{API_URL}/song/{vid}?api={API_KEY}"
    try:
        session = await _get_session()
        while True:
            async with session.get(poll_url) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                s = str(data.get("status", "")).lower()
                if s == "downloading":
                    await asyncio.sleep(1.5)
                    continue
                if s != "done":
                    return None
                dl = data.get("link")
                fmt = str(data.get("format", "mp3")).lower()
                out_path = f"{_DOWNLOAD_DIR}/{vid}.{fmt}"
                async with session.get(dl) as fr:
                    if fr.status != 200:
                        return None
                    async with aiofiles.open(out_path, "wb") as f:
                        async for chunk in fr.content.iter_chunked(CHUNK_SIZE):
                            if not chunk:
                                break
                            await f.write(chunk)
                return out_path
    except Exception:
        return None


def _download_ytdlp(link: str, opts: Dict) -> Optional[str]:
    try:
        with YoutubeDL(opts) as ydl:
            # First get info without downloading
            info = ydl.extract_info(link, download=False)
            if not info:
                return None
                
            vid = info.get('id')
            if not vid:
                return None
                
            ext = info.get("ext") or "webm"
            path = f"{_DOWNLOAD_DIR}/{vid}.{ext}"
            
            # Check if file already exists
            if os.path.exists(path):
                print(f"File already exists: {path}")
                return path
                
            # Now download the file
            print(f"Downloading: {info.get('title', 'Unknown')} - {vid}")
            ydl.download([link])
            
            # Verify download was successful
            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"Download successful: {path}")
                return path
            else:
                print(f"Download failed or file is empty: {path}")
                return None
                
    except Exception as e:
        print(f"Download error for {link}: {str(e)}")
        return None


async def _with_sem(coro):
    async with SEM:
        return await coro


async def _dedup(key: str, runner):
    async with _inflight_lock:
        fut = _inflight.get(key)
        if fut:
            return await fut
        fut = asyncio.get_running_loop().create_future()
        _inflight[key] = fut
    try:
        res = await runner()
        fut.set_result(res)
        return res
    except Exception as e:
        print(f"Dedup error for {key}: {str(e)}")
        fut.set_result(None)
        return None
    finally:
        async with _inflight_lock:
            _inflight.pop(key, None)


async def yt_dlp_download(
    link: str, type: str, format_id: str = None, title: str = None
) -> Optional[str]:
    loop = asyncio.get_running_loop()

    if type == "audio":
        key = f"a:{link}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            })
            return await _with_sem(
                loop.run_in_executor(None, _download_ytdlp, link, opts)
            )

        return await _dedup(key, run)

    if type == "video":
        key = f"v:{link}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update({
                "format": "best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best",
                "merge_output_format": "mp4"
            })
            return await _with_sem(
                loop.run_in_executor(None, _download_ytdlp, link, opts)
            )

        return await _dedup(key, run)

    if type == "song_video" and format_id and title:
        safe_title = _safe_filename(title)
        key = f"sv:{link}:{format_id}:{safe_title}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update(
                {
                    "format": f"{format_id}+bestaudio/best",
                    "outtmpl": f"{_DOWNLOAD_DIR}/{safe_title}.%(ext)s",
                    "merge_output_format": "mp4",
                }
            )
            result = await _with_sem(
                loop.run_in_executor(None, _download_ytdlp, link, opts)
            )
            return result or f"{_DOWNLOAD_DIR}/{safe_title}.mp4"

        return await _dedup(key, run)

    if type == "song_audio" and format_id and title:
        safe_title = _safe_filename(title)
        key = f"sa:{link}:{format_id}:{safe_title}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update(
                {
                    "format": format_id or "bestaudio/best",
                    "outtmpl": f"{_DOWNLOAD_DIR}/{safe_title}.%(ext)s",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
            result = await _with_sem(
                loop.run_in_executor(None, _download_ytdlp, link, opts)
            )
            return result or f"{_DOWNLOAD_DIR}/{safe_title}.mp3"

        return await _dedup(key, run)

    return None


async def download_audio_concurrent(link: str) -> Optional[str]:
    vid = extract_video_id(link)
    print(f"Downloading audio for video ID: {vid}")
    
    cached = file_exists(vid)
    if cached:
        print(f"Found cached file: {cached}")
        return cached

    if not USE_API:
        result = await yt_dlp_download(link, type="audio")
        if result:
            print(f"YT-DLP download successful: {result}")
        else:
            print(f"YT-DLP download failed for: {link}")
        return result

    key = f"rac:{link}"

    async def run():
        print(f"Starting concurrent download for: {link}")
        yt_task = asyncio.create_task(yt_dlp_download(link, type="audio"))
        api_task = asyncio.create_task(api_download_song(link))
        
        done, pending = await asyncio.wait(
            {yt_task, api_task}, return_when=asyncio.FIRST_COMPLETED, timeout=300
        )
        
        result = None
        for task in done:
            try:
                res = task.result()
                if res:
                    result = res
                    print(f"Download completed via {task}: {result}")
                    break
            except Exception as e:
                print(f"Task error: {str(e)}")
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
                
        return result

    return await _dedup(key, lambda: _with_sem(run()))


# Additional utility function for direct streaming
async def get_stream_url(link: str) -> Optional[str]:
    """Get direct stream URL without downloading"""
    try:
        opts = _ytdlp_base_opts()
        opts.update({
            "format": "bestaudio/best",
            "extractaudio": True,
            "audioformat": "best",
            "noplaylist": True,
        })
        
        loop = asyncio.get_running_loop()
        with YoutubeDL(opts) as ydl:
            info = await loop.run_in_executor(None, ydl.extract_info, link, False)
            if info and 'url' in info:
                return info['url']
    except Exception as e:
        print(f"Stream URL error: {str(e)}")
    return None
