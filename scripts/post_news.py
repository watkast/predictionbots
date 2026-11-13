"""Post new Prediction News items to X, one per run, from site/data/news.json.

Each post: the headline, our number, the link to our page. Labeled automated in the account bio (set by hand).
Never posts referral links, never tags people, never quote-tweets. Skips items already posted (state in
site/data/news_posted.json, committed back by the workflow). Dry run unless X credentials are in the environment:
X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET (OAuth 1.0a user context, X API v2 POST /2/tweets).

  python scripts/post_news.py [--dry]
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "site" / "data" / "news.json"
STATE = ROOT / "site" / "data" / "news_posted.json"
SITE = os.environ.get("SITE_URL", "https://predictmenot.com")


def compose(it: dict) -> str:
    link = it["ours"] if it["ours"].startswith("http") else SITE + it["ours"]
    head, num = it["headline"].rstrip("."), it["number"]
    text = f"{head}.\n\n{num}\n\n{link}"
    if len(text) > 280:                       # links count as 23 on X; trim the number first, then the headline
        budget = 280 - 23 - 4 - len(head)
        if budget > 40:
            num = num[: budget - 1].rsplit(" ", 1)[0] + "…"
        else:
            head = head[: 280 - 23 - 4 - 60].rsplit(" ", 1)[0] + "…"
            num = num[:59].rsplit(" ", 1)[0] + "…"
        text = f"{head}.\n\n{num}\n\n{link}"
    return text


def oauth_header(method: str, url: str, keys: dict) -> str:
    p = {"oauth_consumer_key": keys["ck"], "oauth_nonce": secrets.token_hex(16), "oauth_signature_method": "HMAC-SHA1",
         "oauth_timestamp": str(int(time.time())), "oauth_token": keys["at"], "oauth_version": "1.0"}
    base = "&".join([method, urllib.parse.quote(url, safe=""), urllib.parse.quote("&".join(f"{k}={urllib.parse.quote(v, safe='')}" for k, v in sorted(p.items())), safe="")])
    key = f"{urllib.parse.quote(keys['cs'], safe='')}&{urllib.parse.quote(keys['as'], safe='')}"
    p["oauth_signature"] = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(p.items()))


def main() -> None:
    dry = "--dry" in sys.argv
    items = json.loads(NEWS.read_text())["items"]
    posted = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    todo = [it for it in sorted(items, key=lambda x: x["date"]) if it["headline"] not in posted]
    if not todo:
        print("nothing new"); return
    it = todo[0]
    text = compose(it)
    keys = {"ck": os.environ.get("X_API_KEY"), "cs": os.environ.get("X_API_SECRET"), "at": os.environ.get("X_ACCESS_TOKEN"), "as": os.environ.get("X_ACCESS_SECRET")}
    if dry or not all(keys.values()):
        print("DRY RUN (no X credentials)" if not dry else "DRY RUN"); print(text); return
    import httpx
    url = "https://api.x.com/2/tweets"
    r = httpx.post(url, json={"text": text}, headers={"Authorization": oauth_header("POST", url, keys), "Content-Type": "application/json"}, timeout=30)
    if r.status_code not in (200, 201):
        print("X error", r.status_code, r.text[:300]); sys.exit(1)
    posted.add(it["headline"])
    STATE.write_text(json.dumps(sorted(posted), indent=1))
    print("posted:", r.json().get("data", {}).get("id"))


if __name__ == "__main__":
    main()
