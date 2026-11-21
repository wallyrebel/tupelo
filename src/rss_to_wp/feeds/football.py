"""Golden Wave football finals confirmed by the team schedule and the game box."""

from datetime import datetime, timedelta
from html import escape
import re
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from feedparser import FeedParserDict
import requests

BASE = "https://www.maxpreps.com"
TEAM = "/ms/tupelo/tupelo-golden-wave/football/"
SCHEDULE = BASE + TEAM + "schedule/"
GAME = re.compile(r"/ms/football/game/[a-z0-9-]+/(\d{1,2}-\d{1,2}-\d{4})/\?c=[a-f0-9-]{36}")
ZONE = ZoneInfo("America/Chicago")


def page(url):
    response = requests.get(url, timeout=(5, 15), allow_redirects=False,
                            headers={"User-Agent":"TupeloNews/1.0", "Accept-Encoding":"gzip, deflate"})
    response.raise_for_status()
    doc = BeautifulSoup(response.content, "html.parser")
    canonical = doc.select_one('link[rel="canonical"]')
    if response.status_code != 200 or not canonical or canonical.get("href") != url:
        raise ValueError("Team record identity unavailable")
    return doc


def finals():
    now = datetime.now(ZONE)
    entries = []
    for row in page(SCHEDULE).select("table tbody tr"):
        cols = row.find_all("td", recursive=False)
        if len(cols) < 3 or not cols[0].a or not cols[1].a:
            continue
        path = cols[0].a.get("href", "")
        game = GAME.fullmatch(path)
        score = re.fullmatch(r"([WL])\s*(\d+)[-–](\d+)", cols[2].get_text(" ", strip=True))
        if not game or not score:
            continue
        day = datetime.strptime(game[1], "%m-%d-%Y").replace(tzinfo=ZONE)
        if not now.date()-timedelta(days=1) <= day.date() <= now.date():
            continue
        url = urljoin(BASE, path)
        doc = page(url)
        final = doc.select_one(".final")
        table = doc.select_one('table[data-testid="box-score-table"]')
        if table is None or final is None or final.get_text(strip=True) != "Final":
            continue
        headings = [th.get_text(strip=True) for th in table.select("thead th")]
        if headings[1:] != ["Q1","Q2","Q3","Q4","Final"]:
            continue
        teams = {}
        for line in table.select("tbody tr"):
            team = line.select_one("th a.team-cell")
            points = [c.get_text(strip=True) for c in line.select("td")]
            if team and len(points)==5 and all(p.isdigit() for p in points):
                values = list(map(int,points))
                if sum(values[:-1]) == values[-1]:
                    teams[team.get("href")] = team.get_text(" ",strip=True), values
        opponent_path = cols[1].a.get("href")
        if len(teams)!=2 or TEAM not in teams or opponent_path not in teams or opponent_path==TEAM:
            continue
        name, local = teams[TEAM]
        opponent, other = teams[opponent_path]
        if (sorted([local[-1],other[-1]]) != sorted([int(score[2]),int(score[3])])
                or local[-1] == other[-1] or (score[1]=="W") != (local[-1]>other[-1])):
            continue
        kind = "playoff football" if "**" in cols[1].get_text(" ",strip=True) else "football"
        verb = "beat" if local[-1]>other[-1] else "fell to"
        headline = f"{name} {verb} {opponent} {max(local[-1],other[-1])}–{min(local[-1],other[-1])} in {kind}"
        # Give the desk team-labeled values so zero-score periods never lose their attribution.
        summary = (f"{headline} on {day:%A, %B %d, %Y}, according to the Tupelo varsity schedule and final MaxPreps box score. "
                   f"Points by quarter in order: {name} {local[:4]}; {opponent} {other[:4]}. "
                   f"Halftime totals: {name} {sum(local[:2])}, {opponent} {sum(other[:2])}. "
                   f"After three quarters: {name} {sum(local[:3])}, {opponent} {sum(other[:3])}.")
        entries.append(FeedParserDict(id=url, title=headline, link=url, summary=escape(summary), published=day.isoformat()))
    return FeedParserDict(entries=entries, feed={"title":"Tupelo varsity football team records on MaxPreps"})
