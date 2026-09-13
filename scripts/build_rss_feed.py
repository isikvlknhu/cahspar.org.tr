#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import ssl
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "assets" / "rss-feed.json"

KEYWORDS = [
    "calisma hayati",
    "çalışma hayatı",
    "istihdam",
    "iş güvencesi",
    "is guvencesi",
    "sosyal politika",
    "sosyal güvenlik",
    "sosyal koruma",
    "refah",
    "işsizlik",
    "isizlik",
    "working life",
    "employment",
    "labour market",
    "labor market",
    "job security",
    "social policy",
    "social protection",
    "welfare",
    "unemployment",
    "workers rights",
    "decent work",
]

FEEDS = [
    {"name": "ILO", "url": "https://news.google.com/rss/search?q=site:ilo.org+(employment+OR+social+protection+OR+labour+market)&hl=en-US&gl=US&ceid=US:en"},
    {"name": "OECD", "url": "https://news.google.com/rss/search?q=site:oecd.org+(employment+OR+labour+market+OR+social+policy)&hl=en-US&gl=US&ceid=US:en"},
    {"name": "World Bank", "url": "https://news.google.com/rss/search?q=site:worldbank.org+(social+protection+OR+employment+OR+labor+market)&hl=en-US&gl=US&ceid=US:en"},
    {"name": "TÜİK", "url": "https://news.google.com/rss/search?q=site:tuik.gov.tr+(istihdam+OR+isizlik+OR+sosyal+politika)&hl=tr&gl=TR&ceid=TR:tr"},
    {"name": "İŞKUR", "url": "https://news.google.com/rss/search?q=site:iskur.gov.tr+(istihdam+OR+isizlik+OR+sosyal+guvenlik)&hl=tr&gl=TR&ceid=TR:tr"},
    {"name": "SGK", "url": "https://news.google.com/rss/search?q=site:sgk.gov.tr+(sosyal+guvenlik+OR+istihdam+OR+refah)&hl=tr&gl=TR&ceid=TR:tr"},
]


def normalize_text(value: str) -> str:
    value = value or ""
    value = value.lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("&", " ")
    value = re.sub(r"[^a-z0-9çğıöşü\s]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def strip_html(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    text = " ".join(part.strip() for part in node.itertext() if part and part.strip())
    return strip_html(text)


def extract_link(node: ET.Element) -> str:
    link = node.find("./link")
    if link is not None and link.text:
        return link.text.strip()
    for attr in ("href", "url"):
        if attr in link.attrib:
            return link.attrib[attr].strip()
    return ""


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except Exception:
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None


def iter_entries(root: ET.Element):
    if root.tag == "rss":
        return root.findall(".//item")
    if root.tag.startswith("{"):
        return root.findall(".//{*}item") + root.findall(".//{*}entry")
    return root.findall(".//item") + root.findall(".//entry")


def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return response.read()


def is_relevant(title: str, description: str) -> bool:
    haystack = normalize_text(f"{title} {description}")
    normalized_keywords = [normalize_text(keyword) for keyword in KEYWORDS]
    return any(keyword in haystack for keyword in normalized_keywords)


items: list[dict] = []
cutoff = datetime.now(timezone.utc) - timedelta(days=30)

for feed in FEEDS:
    try:
        content = fetch_feed(feed["url"])
        root = ET.fromstring(content)
        for entry in iter_entries(root):
            title = clean_text(entry.find("./title"))
            description = clean_text(entry.find("./description")) or clean_text(entry.find("./summary")) or ""
            description = strip_html(description)
            link = extract_link(entry)
            date_text = (
                entry.findtext("./pubDate")
                or entry.findtext("./published")
                or entry.findtext("./updated")
                or ""
            )
            date_obj = parse_date(date_text)
            if date_obj is None:
                continue
            if date_obj < cutoff:
                continue
            if not link or not title:
                continue
            if not is_relevant(title, description):
                continue
            items.append(
                {
                    "source": feed["name"],
                    "title": title,
                    "summary": description[:220].strip(),
                    "link": link,
                    "published": date_obj.astimezone(timezone.utc).isoformat(),
                }
            )
    except Exception as exc:  # pragma: no cover - network issues are allowed to fail gracefully
        print(f"Skipping {feed['name']}: {exc}")

items = sorted(items, key=lambda item: item["published"], reverse=True)[:8]

payload = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "items": items,
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Generated {len(items)} RSS items at {OUT_PATH}")
