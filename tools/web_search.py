"""网络搜索 & 网页抓取 — @tool 函数"""

from langchain_core.tools import tool
from urllib.parse import quote_plus
from config import BRAVE_SEARCH_KEY


_API_KEY = BRAVE_SEARCH_KEY  # 从 config.py 读，填 key 后自动走 Brave API


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """搜索互联网获取最新信息。用于查新闻、比赛结果、选手动态、版本更新等。

    Args:
        query: 搜索关键词
        max_results: 返回结果数，默认 5
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        if _API_KEY:
            # 有 API key 时用 Brave Search
            resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"Accept": "application/json", "Accept-Encoding": "gzip",
                         "X-Subscription-Token": _API_KEY},
                params={"q": query, "count": max_results},
                timeout=10
            )
            data = resp.json()
            results = []
            for r in data.get("web", {}).get("results", []):
                results.append(f"- {r['title']}\n  {r['url']}\n  {r.get('description', '')}")
            return "\n\n".join(results) if results else "未找到结果"
        else:
            # 无 key 时用 DuckDuckGo lite 做快速搜索
            # 无 API key 时用 Bing 搜索（国内可访问）
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            url = f"https://www.bing.com/search?q={quote_plus(query)}"
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for li in soup.select("li.b_algo")[:max_results]:
                title_el = li.select_one("h2 a")
                desc_el = li.select_one(".b_caption p")
                if title_el:
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    desc = desc_el.get_text(strip=True) if desc_el else ""
                    results.append(f"- {title}\n  {href}\n  {desc}")
            return "\n\n".join(results) if results else "未找到结果"
    except Exception as e:
        return f"[搜索失败] {e}"


@tool
def web_fetch(url: str, max_chars: int = 4000) -> str:
    """抓取网页内容并提取正文文本。

    Args:
        url: 要抓取的网页地址
        max_chars: 最大返回字符数，默认 4000
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return "\n".join(lines)[:max_chars]
    except Exception as e:
        return f"[抓取失败] {e}"
