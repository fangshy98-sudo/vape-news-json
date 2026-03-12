import json
import os
import urllib.request
from datetime import datetime, timezone


SOURCE_URL = os.environ.get("SOURCE_URL", "").strip()
OUTPUT_DIR = "docs"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "news.json")


def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 GitHub-Actions-NewsFetcher/1.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def normalize_items(data: dict):
    items = data.get("items", [])
    normalized = []

    for i, item in enumerate(items, start=1):
        # 兼容 2FIRSTS worker 返回格式：{"no": 1, "content": "..."}
        if "content" in item:
            normalized.append(
                {
                    "id": item.get("no", i),
                    "title": f"2FIRSTS电子烟早报 第{item.get('no', i)}条",
                    "link": data.get("source", ""),
                    "pubDate": data.get("date", ""),
                    "source": "2FIRSTS",
                    "description": item.get("content", ""),
                }
            )
        else:
            # 兼容你以后可能接入的标准新闻 JSON
            normalized.append(
                {
                    "id": i,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "pubDate": item.get("pubDate", ""),
                    "source": item.get("source", ""),
                    "description": item.get("description", ""),
                }
            )

    return normalized


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def main():
    if not SOURCE_URL:
        raise ValueError("SOURCE_URL is empty. Please set SOURCE_URL in workflow env.")

    data = fetch_json(SOURCE_URL)
    status = data.get("status", "unknown")
    items = normalize_items(data)

    ensure_dir(OUTPUT_DIR)

    output = {
        "status": status,
        "source_url": SOURCE_URL,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(items)} items to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
