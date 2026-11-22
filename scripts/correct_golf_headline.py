"""Correct only the identified golf story if its original publication is intact."""
import hashlib
import os
from datetime import datetime, timezone
from email.utils import format_datetime

import requests

SITE = "https://newstupelo.com"
POST = SITE + "/wp-json/wp/v2/posts/3152"
ORIGINAL = "Tupelo Christian wins Class 1A boys golf title in playoff"
CORRECT = "Tupelo Christian wins Class 1A boys golf title after matching Vardaman at 644"
MODIFIED = "2026-11-22T19:07:17"
BODY_HASH = "8602c632baa8d398b5ee5e582af59baca3bdecf2344c9dbadabf7c5365afc14d"


def check(post):
    body = post["content"]["rendered"]
    return (post["id"] == 3152 and post["status"] == "publish" and post["featured_media"] == 3151
            and post["date_gmt"] == MODIFIED and hashlib.sha256(body.encode()).hexdigest() == BODY_HASH
            and post["slug"] == "tupelo-christian-wins-class-1a-boys-golf-title-in-playoff")


def main():
    if os.environ["WORDPRESS_BASE_URL"].rstrip("/") != SITE:
        raise ValueError("Unexpected site")
    with requests.Session() as session:
        session.auth = os.environ["WORDPRESS_USERNAME"], os.environ["WORDPRESS_APP_PASSWORD"]
        def read():
            response = session.get(POST, params={"context": "edit"}, timeout=(5, 20), allow_redirects=False)
            if response.status_code != 200:
                raise RuntimeError("Unable to verify post")
            return response.json()
        before = read()
        if not check(before):
            raise ValueError("Article differs from the verified original")
        if before["title"]["raw"] == CORRECT:
            print("Verified corrected headline")
            return
        if before["title"]["raw"] != ORIGINAL or before["modified_gmt"] != MODIFIED:
            raise ValueError("Title or modification date changed. Preserve editor changes.")
        stamp = datetime.fromisoformat(MODIFIED).replace(tzinfo=timezone.utc)
        response = session.post(POST, json={"title": CORRECT}, headers={"If-Unmodified-Since": format_datetime(stamp, usegmt=True)},
                                timeout=(5, 25), allow_redirects=False)
        if response.status_code != 200:
            raise RuntimeError("Correction outcome requires verification")
        after = read()
        if not check(after) or after["title"]["raw"] != CORRECT:
            raise ValueError("Correction did not verify")
        print("Verified headline correction on post 3152")


if __name__ == "__main__":
    main()
