#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import ssl
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

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
    "duyuru",
    "bakan",
    "ziyaret",
    "açıklama",
    "görüşme",
    "anlaşma",
    "program",
    "karar",
    "toplantı",
]

TURKISH_OFFICIAL_DOMAINS = {"tuik.gov.tr", "sgk.gov.tr", "csgb.gov.tr", "iskur.gov.tr"}
GENERIC_TURKISH_TITLES = {
    "ana sayfa",
    "hakkimizda",
    "kurumsal politikalar",
    "organizasyon yapisi",
    "organizasyon yapısı",
    "arama sonuçları",
    "veri portalı",
    "veri portalı",
    "haber bültenleri",
    "duyurular",
    "istatistik yıllıkları",
    "uygulama portalı",
}

ALLOWED_SOURCES = [
    {"name": "ILO", "domain": "ilo.org", "query": "site:ilo.org (employment OR social protection OR labour market OR decent work OR working conditions)"},
    {"name": "OECD", "domain": "oecd.org", "query": "site:oecd.org (employment OR labour market OR social policy OR social protection OR job quality)"},
    {"name": "Eurofound", "domain": "eurofound.europa.eu", "query": "site:eurofound.europa.eu (employment OR labour market OR working conditions OR social policy)"},
    {"name": "TÜİK", "domain": "tuik.gov.tr", "query": "site:tuik.gov.tr (\"istihdam\" OR \"işsizlik\" OR \"çalışma hayatı\" OR \"refah\" OR \"sosyal politika\") (duyuru OR açıklama OR bülten OR rapor OR istatistik)"},
    {"name": "SGK", "domain": "sgk.gov.tr", "query": "site:sgk.gov.tr (\"sosyal güvenlik\" OR \"emeklilik\" OR \"istihdam\") (duyuru OR açıklama OR kararı OR program OR ziyaret OR bakan)"},
    {"name": "ÇSGB", "domain": "csgb.gov.tr", "query": "site:csgb.gov.tr (\"çalışma\" OR \"istihdam\" OR \"iş güvencesi\" OR \"sosyal güvenlik\") (duyuru OR bakan OR program OR ziyaret OR anlaşma)"},
    {"name": "AB", "domain": "ec.europa.eu", "query": "site:ec.europa.eu (employment OR social policy OR labour market OR social protection OR working conditions)"},
    {"name": "AB", "domain": "europa.eu", "query": "site:europa.eu (employment OR social policy OR labour market OR social protection OR working conditions)"},
]

def build_feed_url(source: dict[str, str]) -> str:
    if source["domain"] in TURKISH_OFFICIAL_DOMAINS:
        locale = "&hl=tr&gl=TR&ceid=TR:tr"
    else:
        locale = "&hl=en-US&gl=US&ceid=US:en"
    return "https://news.google.com/rss/search?q=" + urllib.parse.quote_plus(source["query"]) + locale


FEEDS = [{"name": source["name"], "url": build_feed_url(source)} for source in ALLOWED_SOURCES]


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
        if link is not None and attr in link.attrib:
            return link.attrib[attr].strip()
    return ""


def extract_article_url(description: str, fallback: str) -> str:
    if not description:
        return fallback
    match = re.search(r'href=["\']([^"\']+)["\']', description, re.IGNORECASE)
    return html.unescape(match.group(1)) if match else fallback


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


def is_generic_turkish_title(title: str) -> bool:
    haystack = normalize_text(title)
    return any(item in haystack for item in GENERIC_TURKISH_TITLES)


def is_relevant(title: str, description: str, source_url: str = "") -> bool:
    haystack = normalize_text(f"{title} {description}")
    normalized_keywords = [normalize_text(keyword) for keyword in KEYWORDS]
    if source_url and any(host in source_url.lower() for host in TURKISH_OFFICIAL_DOMAINS):
        normalized_terms = [normalize_text(term) for term in ("duyuru", "bakan", "ziyaret", "açıklama", "görüşme", "anlaşma", "program", "toplantı")]
        return (not is_generic_turkish_title(title)) and (
            any(keyword in haystack for keyword in normalized_keywords) or any(term in haystack for term in normalized_terms)
        )
    return any(keyword in haystack for keyword in normalized_keywords)


def is_allowed_source(link: str) -> bool:
    if not link:
        return False
    host = urlparse(link).netloc.lower()
    return any(host == domain or host.endswith(f'.{domain}') for domain in [source['domain'] for source in ALLOWED_SOURCES])


def is_turkish_official_source(link: str) -> bool:
    if not link:
        return False
    host = urlparse(link).netloc.lower()
    return any(host == domain or host.endswith(f'.{domain}') for domain in TURKISH_OFFICIAL_DOMAINS)


def main() -> None:
    items: list[dict] = []
    seen: set[str] = set()

    for feed in FEEDS:
        try:
            content = fetch_feed(feed["url"])
            root = ET.fromstring(content)
            for entry in iter_entries(root):
                title = clean_text(entry.find("./title"))
                description_html = entry.findtext("./description") or entry.findtext("./summary") or ""
                description = strip_html(description_html)
                link = extract_link(entry)
                source_node = entry.find("./source")
                source_url = source_node.attrib.get("url") if source_node is not None and "url" in source_node.attrib else ""
                article_link = extract_article_url(description_html, link)
                date_text = (
                    entry.findtext("./pubDate")
                    or entry.findtext("./published")
                    or entry.findtext("./updated")
                    or ""
                )
                date_obj = parse_date(date_text)
                if date_obj is None:
                    continue
                source_ref = source_url or article_link or link
                cutoff_days = 180 if is_turkish_official_source(source_ref) else 30
                cutoff = datetime.now(timezone.utc) - timedelta(days=cutoff_days)
                if date_obj < cutoff:
                    continue
                if not article_link or not title:
                    continue
                if not is_allowed_source(source_ref):
                    continue
                if not is_relevant(title, description, source_ref):
                    continue

                dedupe_key = normalize_text(title) + "|" + normalize_text(article_link or source_url or link)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)

                items.append(
                    {
                        "source": feed["name"],
                        "title": title,
                        "summary": description[:220].strip(),
                        "link": article_link or source_url or link,
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


if __name__ == "__main__":
    main()
