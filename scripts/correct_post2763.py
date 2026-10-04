"""Read-only pre-correction snapshot of exactly Tupelo post 2763."""
import hashlib
import json
import os
from pathlib import Path

import requests

BASE = "https://newstupelo.com"
POST_ID = 2763
SLUG = "auditions-for-a-christmas-carol-live-radio-play-set-for-october"
LINK = BASE + "/tupelo-news/" + SLUG + "/"
RENDERED_SHA = "a8d885f16ffcc0c0bb07880ac4c786986bede1f2c834f2c36f3b35720547802c"
OUT = Path("data/post2763-audit")


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def read(session):
    r = session.get(BASE + f"/wp-json/wp/v2/posts/{POST_ID}",
                    params={"context": "edit"}, timeout=(10, 30), allow_redirects=False)
    r.raise_for_status()
    if r.status_code != 200:
        raise ValueError("Unexpected read status")
    return r.json()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        if os.environ["WORDPRESS_BASE_URL"].rstrip("/") != BASE:
            raise ValueError("Unexpected site")
        with requests.Session() as s:
            s.auth = (os.environ["WORDPRESS_USERNAME"], os.environ["WORDPRESS_APP_PASSWORD"])
            post = read(s)
        if (post["id"] != POST_ID or post["link"] != LINK or
            post["status"] != "publish" or post["slug"] != SLUG or
            post["featured_media"] != 2762 or digest(post["content"]["rendered"]) != RENDERED_SHA):
            raise ValueError("Exact post preconditions failed")
        (OUT / "before.json").write_text(json.dumps(post, indent=2))
        (OUT / "before-raw.html").write_text(post["content"]["raw"])
        (OUT / "before-rendered.html").write_text(post["content"]["rendered"])
        report = {"post_id": POST_ID, "verified": True, "read_only": True,
                  "raw_sha256": digest(post["content"]["raw"]),
                  "rendered_sha256": RENDERED_SHA, "title": post["title"],
                  "featured_media": post["featured_media"]}
    except Exception as exc:
        report = {"post_id": POST_ID, "verified": False, "error_type": type(exc).__name__}
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
