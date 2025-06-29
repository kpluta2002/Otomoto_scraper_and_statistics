import asyncio
from typing import List, Tuple

import aiohttp
import requests

FREE_PROXY_API_URLS = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=20000&country=all&ssl=all&anonymity=elite",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
    "http://pubproxy.com/api/proxy?format=txt&level=elite&type=http&speed=5&limit=2&https=true&user_agent=true&cookies=true&referer=true",
]

PROXY_TOTAL_TIMEOUT = 10
PROXY_CONNECT_TIMEOUT = 5

# how many simultaneous tests we’ll run
MAX_TEST_CONCURRENCY = 50


def _fetch_raw_proxies() -> List[str]:
    """Synchronously pull each URL in turn and collect unique proxies."""
    raw = set()
    for url in FREE_PROXY_API_URLS:
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            for line in r.text.splitlines():
                line = line.strip()
                if line:
                    raw.add(line)
        except Exception as e:
            pass
    print(f"Fetched {len(raw)} unique raw proxies.")
    return list(raw)


async def _test_proxy(
    sem: asyncio.Semaphore, session: aiohttp.ClientSession, proxy: str
) -> Tuple[bool, str]:
    """
    Attempt a GET via this proxy. Return (True, proxy) on success.
    """
    target = "https://httpbin.org/ip"
    proxy_url = f"http://{proxy}"
    async with sem:
        try:
            async with session.get(
                target,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(
                    total=PROXY_TOTAL_TIMEOUT, connect=PROXY_CONNECT_TIMEOUT
                ),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    origin = data.get("origin", "")
                    print(f"[OK] {proxy} → {origin}")
                    return True, proxy
        except Exception as e:
            pass
    return False, proxy


async def _validate_proxies(raw: List[str]) -> List[str]:
    """
    Spin up MAX_TEST_CONCURRENCY tests in parallel and return only the working ones.
    """
    sem = asyncio.Semaphore(MAX_TEST_CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=MAX_TEST_CONCURRENCY)
    valid = []
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_test_proxy(sem, session, p) for p in raw]
        results = await asyncio.gather(*tasks)
    for ok, proxy in results:
        if ok:
            valid.append(proxy)
    return valid


def get_working_proxies() -> List[str]:
    """
    1. Fetch raw proxy strings one URL at a time (synchronously).
    2. Test them all in parallel.
    3. Return only the successful proxies.
    """
    raw = _fetch_raw_proxies()
    if not raw:
        return []

    # Run validation in thread pool to avoid blocking
    from twisted.internet import threads

    return threads.deferToThread(lambda: asyncio.run(_validate_proxies(raw)))
