"""Event-week service editions from the Lee County Library's public calendar."""
from datetime import datetime, time, timedelta
import re
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from feedparser import FeedParserDict
import requests

CALENDAR = "https://www.leeitawambalibrary.org/events"
CENTRAL = ZoneInfo("America/Chicago")


def upcoming_edition(markup, now):
    page = BeautifulSoup(markup, "html.parser")
    cards = page.select("article.eventlist-event--upcoming")
    if not cards:
        raise ValueError("No upcoming program listings found")
    monday = now.date() - timedelta(days=now.weekday())
    if now.weekday() == 6:
        monday += timedelta(days=7)
    eligible = datetime.combine(monday - timedelta(days=1), time.min, CENTRAL)
    events = []
    for card in cards:
        place = card.select_one(".eventlist-meta-address")
        if not place or place.get_text(" ", strip=True).removesuffix(" (map)") != "Lee County Library":
            continue
        anchor = card.select_one("a.eventlist-title-link")
        day = card.select_one("time.event-date[datetime]")
        clock = card.select_one("time.event-time-localized-start")
        detail = card.select_one(".eventlist-description")
        if not all((anchor, day, clock, detail)) or not re.fullmatch(r"/events/[a-z0-9-]+", anchor.get("href", "")):
            continue
        start = datetime.strptime(day["datetime"] + " " + " ".join(clock.stripped_strings).replace("\u202f", " "),
                                  "%Y-%m-%d %I:%M %p").replace(tzinfo=CENTRAL)
        if not monday <= start.date() < monday + timedelta(days=7):
            continue
        # Older recurring blurbs sometimes disagree with the dated card's end time.
        # Use the listed start only and omit prose sentences that mention a clock time.
        sentences = re.split(r"(?<=[.!?])\s+", detail.get_text(" ", strip=True))
        notes = " ".join(s for s in sentences if not re.search(r"\d:\d\d|\b\d+\s*[ap]\.?m\b", s, re.I))
        events.append((start, anchor.get_text(" ", strip=True), notes, urljoin(CALENDAR, anchor["href"])))
    events = sorted(set(events))
    titles = {title for _, title, _, _ in events}
    thanksgiving_week = (monday.month == 11 and 22 <= (monday + timedelta(days=3)).day <= 28)
    entries = []
    if (len(titles) >= 3 or (thanksgiving_week and len(titles) >= 2)) and eligible <= now < events[0][0]:
        names = ", ".join(dict.fromkeys(e[1] for e in events))
        notes = [f"The Lee-Itawamba Library System calendar lists the following programs at Lee County Library in Tupelo for the week of {monday:%B %d, %Y}."]
        for start, title, summary, source in events:
            notes.append(f"{title} begins {start:%A, %B %d at %I:%M %p} Central. {summary} Program listing: {source}")
        footer = page.select_one("footer")
        if footer and "219 North Madison Street" in footer.get_text(" ", strip=True):
            notes.append("The library lists its Tupelo branch at 219 North Madison Street.")
        entries.append(FeedParserDict(id=f"lee-library-week:{monday}", link=events[0][3],
                       title=f"{names} on the Lee County Library calendar for the week of {monday:%B %d}",
                       published=eligible.isoformat(), summary=" ".join(notes)))
    return FeedParserDict(entries=entries, feed={"title":"Lee-Itawamba Library System"})


def library_calendar():
    response = requests.get(CALENDAR, timeout=(5, 20), allow_redirects=False,
                            headers={"User-Agent":"TupeloNews/1.0 (+https://newstupelo.com/)", "Accept-Encoding":"gzip, deflate"})
    response.raise_for_status()
    if response.status_code != 200:
        raise ValueError("Library calendar unavailable")
    return upcoming_edition(response.content, datetime.now(CENTRAL))
