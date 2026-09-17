#!/usr/bin/env python3
"""Build the curated ÇAHSPAR research and official-publications feed.

Pipeline:
    source RSS/API/publication feed -> collection -> source/domain checks
    -> topic/content filtering -> assets/rss-feed.json -> rss-loader.js

The source catalogue is intentionally explicit; only listed research and
official data/publication sources can enter the generated feed.
"""

from __future__ import annotations

import html
import json
import re
import ssl
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import certifi
except ImportError:  # pragma: no cover - the deployment can provide system CAs
    certifi = None


ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "assets" / "rss-feed.json"


@dataclass(frozen=True)
class Source:
    name: str
    domain: str
    homepage: str
    category: str
    topics: tuple[str, ...]
    feeds: tuple[str, ...] = ()
    fallback_query: str = ""
    max_age_days: int = 90


# Direct feeds are preferred. The fallback query is still a feed (Google News
# RSS restricted to the official domain), not a general web/news search.
# It is useful for institutions whose CMS exposes a changing publication feed.
SOURCES = (
    Source(
        "ILO", "ilo.org", "https://www.ilo.org/", "Çalışma hayatı",
        ("employment", "unemployment", "labour market", "labor market", "wages", "social protection", "working conditions", "occupational safety", "decent work", "child labour", "youth", "women", "gender", "çalışma hayatı", "istihdam", "işsizlik", "ücret", "sosyal koruma", "iş sağlığı", "iş güvenliği"),
        (),
        "(publication OR report OR data OR research OR employment OR wages OR social protection OR decent work)",
    ),
    Source(
        "OECD", "oecd.org", "https://www.oecd.org/en/publications.html", "Araştırma / politika",
        ("employment", "labour market", "labor market", "wages", "social spending", "pension", "income distribution", "inequality", "education", "skills", "istihdam", "işgücü", "ücret", "sosyal harcama", "emeklilik", "gelir dağılımı", "eşitsizlik", "eğitim"),
        (),
        "(employment OR labour market OR wages OR social spending OR pensions OR inequality OR education OR publication OR report)",
    ),
    Source(
        "World Bank", "worldbank.org", "https://www.worldbank.org/en/research", "Kalkınma / veri",
        ("poverty", "employment", "social protection", "income", "human capital", "development", "labour", "labor market", "inequality", "education", "yoksulluk", "istihdam", "sosyal koruma", "gelir", "beşeri sermaye", "kalkınma", "eşitsizlik", "eğitim"),
        (),
        "(poverty OR employment OR social protection OR income OR human capital OR development OR report OR data)",
    ),
    Source(
        "UN DESA", "un.org", "https://www.un.org/development/desa/", "Sosyal politika / nüfus",
        ("social policy", "population", "ageing", "aging", "migration", "poverty", "sustainable development", "social protection", "labour", "employment", "sosyal politika", "nüfus", "yaşlanma", "göç", "yoksulluk", "sürdürülebilir kalkınma", "sosyal koruma", "istihdam"),
        (),
        "(social policy OR population OR ageing OR migration OR poverty OR sustainable development OR report OR data)",
    ),
    Source(
        "UNDP", "undp.org", "https://www.undp.org/publications", "İnsani gelişme",
        ("human development", "inequality", "poverty", "social policy", "social protection", "development", "income", "gender", "employment", "insani gelişme", "eşitsizlik", "yoksulluk", "sosyal politika", "sosyal koruma", "kalkınma"),
        (),
        "(human development OR inequality OR poverty OR social policy OR social protection OR publication OR report)",
    ),
    Source(
        "UN Women", "unwomen.org", "https://www.unwomen.org/en/how-we-work/research-and-data/publications", "Kadın / toplumsal cinsiyet",
        ("women", "gender", "gender equality", "labour force", "labor force", "wage gap", "care economy", "employment", "women's economic empowerment", "kadın", "toplumsal cinsiyet", "ücret farkı", "bakım ekonomisi", "kadın istihdamı", "işgücüne katılım"),
        ("https://www.unwomen.org/en/rss-feeds/news",),
        "(women OR gender OR gender equality OR wage gap OR care economy OR publication OR report)",
    ),
    Source(
        "UNICEF", "unicef.org", "https://www.unicef.org/reports", "Çocuk / sosyal koruma",
        ("child poverty", "child labour", "social protection", "education", "children", "child well-being", "youth", "çocuk yoksulluğu", "çocuk işçiliği", "sosyal koruma", "eğitim", "çocuk"),
        (),
        "(child poverty OR child labour OR social protection OR education OR report OR data)",
    ),
    Source(
        "Eurostat", "ec.europa.eu", "https://ec.europa.eu/eurostat/news/news-articles", "İstatistik / veri",
        ("employment", "unemployment", "wages", "labour cost", "labour market", "job vacancy", "poverty", "income distribution", "social protection", "migration", "living conditions", "education", "population", "gender", "istihdam", "işsizlik", "ücret", "işgücü maliyeti", "işgücü piyasası", "açık pozisyon", "yoksulluk", "gelir dağılımı", "sosyal koruma", "göç", "yaşam koşulları", "eğitim", "nüfus"),
        (
            "https://ec.europa.eu/eurostat/en/search?_estatsearchportlet_WAR_estatsearchportlet_collection=CAT_PREREL&p_p_id=estatsearchportlet_WAR_estatsearchportlet&p_p_lifecycle=2&p_p_mode=view&p_p_resource_id=atom&p_p_state=maximized",
            "https://ec.europa.eu/eurostat/en/search?_estatsearchportlet_WAR_estatsearchportlet_collection=CAT_EURNEW&p_p_id=estatsearchportlet_WAR_estatsearchportlet&p_p_lifecycle=2&p_p_mode=view&p_p_resource_id=atom&p_p_state=maximized",
            "https://ec.europa.eu/eurostat/en/search?_estatsearchportlet_WAR_estatsearchportlet_collection=dataset&p_p_id=estatsearchportlet_WAR_estatsearchportlet&p_p_lifecycle=2&p_p_mode=view&p_p_resource_id=atom&p_p_state=maximized",
        ),
        "(employment OR unemployment OR wages OR labour market OR poverty OR social protection OR migration OR education OR dataset OR statistics)",
        180,
    ),
    Source(
        "European Commission (DG EMPL)", "ec.europa.eu", "https://employment-social-affairs.ec.europa.eu/", "AB / sosyal politika",
        ("employment", "social affairs", "social inclusion", "labour market", "social protection", "social rights", "working conditions", "poverty", "istihdam", "sosyal politika", "sosyal içerme", "işgücü piyasası", "sosyal koruma", "çalışma koşulları", "yoksulluk"),
        (),
        "(employment OR social affairs OR social inclusion OR labour market OR social protection OR working conditions OR poverty OR research OR report)",
    ),
    Source(
        "European Commission (JRC)", "ec.europa.eu", "https://publications.jrc.ec.europa.eu/repository/", "Araştırma / politika",
        ("employment", "social policy", "inequality", "poverty", "labour market", "digitalisation", "future of work", "migration", "skills", "social protection", "istihdam", "sosyal politika", "eşitsizlik", "yoksulluk", "işgücü piyasası", "dijitalleşme", "geleceğin işleri", "göç", "beceri", "sosyal koruma"),
        (),
        "(employment OR social policy OR inequality OR poverty OR labour market OR digitalisation OR migration OR skills OR publication OR report)",
    ),
    Source(
        "Eurofound", "eurofound.europa.eu", "https://www.eurofound.europa.eu/", "Çalışma koşulları",
        ("working conditions", "work-life balance", "wages", "working time", "social dialogue", "remote work", "labour market", "employment", "quality of life", "work-life", "çalışma koşulları", "iş-yaşam dengesi", "ücret", "çalışma süresi", "sosyal diyalog", "uzaktan çalışma", "işgücü piyasası", "istihdam"),
        ("https://www.eurofound.europa.eu/press/newsfeeds/news.xml", "https://www.eurofound.europa.eu/press/newsfeeds/publications.xml"),
        "(working conditions OR work-life balance OR wages OR working time OR social dialogue OR remote work OR labour market OR employment OR publication OR report)",
    ),
    Source(
        "TÜİK", "tuik.gov.tr", "https://data.tuik.gov.tr/", "Türkiye / istatistik",
        ("işgücü", "istihdam", "işsizlik", "gelir", "yaşam koşulları", "yoksulluk", "sosyal koruma", "hanehalkı", "genç", "kadın", "göç", "eğitim", "nüfus", "istatistik", "veri", "haber bülteni", "işgücü piyasası"),
        (),
        "(istatistik OR veri OR bülten OR istihdam OR işgücü OR işsizlik OR gelir OR yoksulluk OR hanehalkı OR genç OR kadın OR göç OR eğitim OR nüfus)",
        180,
    ),
    Source(
        "TCMB", "tcmb.gov.tr", "https://www.tcmb.gov.tr/", "Türkiye / ekonomi",
        ("wages", "labour cost", "employment", "inflation", "household", "expectations", "economic outlook", "research", "working paper", "ücret", "işgücü maliyeti", "istihdam", "enflasyon", "hanehalkı", "beklentiler", "ekonomik görünüm", "araştırma", "çalışma tebliği", "ekonomi notu"),
        (
            "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Bottom%2BMenu/Diger/RSS/Yayinlar",
            "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Bottom%2BMenu/Diger/RSS/Veriler",
        ),
        "(ücret OR işgücü maliyetleri OR istihdam OR enflasyon OR hanehalkı OR beklentiler OR ekonomik görünüm OR araştırma OR tebliğ OR ekonomi notu)",
        180,
    ),
)

MAX_ITEMS = 24
MAX_ITEMS_PER_SOURCE = 3
DEFAULT_MAX_AGE_DAYS = 90

TURKISH_MONTHS = {
    "oca": "Jan", "şub": "Feb", "mar": "Mar", "nis": "Apr", "may": "May", "haz": "Jun",
    "tem": "Jul", "ağu": "Aug", "eyl": "Sep", "eki": "Oct", "kas": "Nov", "ara": "Dec",
}

PUBLICATION_MARKERS = (
    "report", "publication", "research", "study", "working paper", "policy brief",
    "data", "dataset", "statistics", "statistical", "indicator", "survey",
    "monitor", "outlook", "bulletin", "release", "veri", "istatistik", "rapor",
    "araştırma", "çalışma tebliği", "ekonomi notu", "bülten",
)

EXCLUDED_TERMS = (
    "career", "careers", "job opportunity", "job opportunities", "apply now",
    "recruitment", "internship", "procurement", "tender", "consultant",
    "vacancy announcement", "call for applications", "expression of interest",
    "rfp", "rfi", "jobs at", "iş başvurusu", "personel alımı", "staj ilanı",
)


def google_news_url(source: Source) -> str:
    query = f"site:{source.domain} {source.fallback_query}"
    locale = "&hl=tr&gl=TR&ceid=TR:tr" if source.name in {"TÜİK", "TCMB"} else "&hl=en-US&gl=US&ceid=US:en"
    return "https://news.google.com/rss/search?q=" + urllib.parse.quote_plus(query) + locale


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").lower()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("&", " ")
    value = re.sub(r"[^a-z0-9çğıöşü\s]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def strip_html(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return strip_html(" ".join(part.strip() for part in node.itertext() if part and part.strip()))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(node: ET.Element, *names: str) -> str:
    wanted = {name.lower() for name in names}
    for child in list(node):
        if local_name(child.tag) in wanted:
            return clean_text(child)
    return ""


def child_raw(node: ET.Element, *names: str) -> str:
    wanted = {name.lower() for name in names}
    for child in list(node):
        if local_name(child.tag) in wanted:
            return ET.tostring(child, encoding="unicode", method="xml")
    return ""


def child_node(node: ET.Element, name: str) -> ET.Element | None:
    for child in list(node):
        if local_name(child.tag) == name.lower():
            return child
    return None


def extract_link(node: ET.Element) -> str:
    link = child_node(node, "link")
    if link is None:
        return ""
    if link.text and link.text.strip():
        return link.text.strip()
    return (link.attrib.get("href") or link.attrib.get("url") or "").strip()


def extract_article_url(description: str, fallback: str) -> str:
    match = re.search(r'href=["\']([^"\']+)', description or "", re.IGNORECASE)
    return html.unescape(match.group(1)) if match else fallback


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        result = parsedate_to_datetime(value)
    except Exception:
        try:
            normalized = value.lower()
            for turkish, english in TURKISH_MONTHS.items():
                normalized = re.sub(rf"\b{turkish}\b", english, normalized)
            result = datetime.strptime(normalized, "%d %b %Y %H:%M:%S")
            result = result.replace(tzinfo=timezone.utc)
        except Exception:
            try:
                result = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except Exception:
                return None
    return result.replace(tzinfo=timezone.utc) if result.tzinfo is None else result


def iter_entries(root: ET.Element) -> list[ET.Element]:
    return [node for node in root.iter() if local_name(node.tag) in {"item", "entry"}]


def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
            "User-Agent": "CAHSPAR-RSS/1.0 (+https://cahspar.org.tr)",
        },
    )
    context = ssl.create_default_context(cafile=certifi.where()) if certifi else ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return response.read()


def is_allowed_source(link: str, source: Source) -> bool:
    host = urlparse(link).netloc.lower().split(":", 1)[0]
    return bool(host) and (host == source.domain or host.endswith(f".{source.domain}"))


def is_relevant(title: str, description: str, source: Source, direct_feed: bool) -> bool:
    haystack = normalize_text(f"{title} {description}")
    if any(normalize_text(term) in haystack for term in EXCLUDED_TERMS):
        return False

    topic_match = any(normalize_text(topic) in haystack for topic in source.topics)
    marker_match = any(normalize_text(marker) in haystack for marker in PUBLICATION_MARKERS)

    # Direct publication/data feeds are already editorially scoped. They still
    # need a topic match, while Google News fallbacks require both topic and a
    # publication/data marker to avoid institutional general news.
    return topic_match and (direct_feed or marker_match)


def source_feed_urls(source: Source) -> list[tuple[str, bool]]:
    urls = [(url, True) for url in source.feeds]
    if source.fallback_query:
        urls.append((google_news_url(source), False))
    return urls


def dedupe_key(item: dict) -> str:
    return normalize_text(item["title"]) + "|" + normalize_text(item["link"])


def source_catalog() -> list[dict[str, str]]:
    return [{"name": source.name, "category": source.category, "homepage": source.homepage, "domain": source.domain} for source in SOURCES]


def main() -> None:
    collected: list[dict] = []
    items_by_source: dict[str, list[dict]] = {source.name: [] for source in SOURCES}
    seen: set[str] = set()
    now = datetime.now(timezone.utc)

    for source in SOURCES:
        direct_items_found = False
        for feed_url, direct_feed in source_feed_urls(source):
            if not direct_feed and direct_items_found:
                break
            try:
                root = ET.fromstring(fetch_feed(feed_url))
            except Exception as exc:  # network/CMS failures should not stop other sources
                print(f"Skipping {source.name} feed {feed_url}: {exc}")
                continue

            accepted_from_feed = 0
            for entry in iter_entries(root):
                title = child_text(entry, "title")
                description_raw = child_raw(entry, "description", "summary", "content")
                description = strip_html(description_raw)
                link = extract_link(entry)
                article_link = extract_article_url(description_raw, link)
                source_node = child_node(entry, "source")
                source_url = (source_node.attrib.get("url", "") if source_node is not None else "").strip()
                published = parse_date(child_text(entry, "pubDate", "published", "updated", "date", "issued", "created"))

                if not title or not article_link or published is None:
                    continue
                source_ref = source_url or article_link
                if published < now - timedelta(days=source.max_age_days or DEFAULT_MAX_AGE_DAYS):
                    continue
                if not is_allowed_source(source_ref, source):
                    continue
                if not is_relevant(title, description, source, direct_feed):
                    continue

                item = {
                    "source": source.name,
                    "category": source.category,
                    "title": title,
                    "summary": description[:240].strip(),
                    "link": article_link,
                    "published": published.astimezone(timezone.utc).isoformat(),
                }
                key = dedupe_key(item)
                if key in seen:
                    continue
                seen.add(key)
                collected.append(item)
                items_by_source[source.name].append(item)
                accepted_from_feed += 1

            if accepted_from_feed:
                direct_items_found = direct_items_found or direct_feed

    selected: list[dict] = []
    selected_keys: set[str] = set()
    per_source_count = {source.name: 0 for source in SOURCES}

    # One current item per source first, preserving source diversity.
    for source in SOURCES:
        source_items = sorted(items_by_source[source.name], key=lambda item: item["published"], reverse=True)
        if source_items:
            selected.append(source_items[0])
            selected_keys.add(dedupe_key(source_items[0]))
            per_source_count[source.name] = 1

    for item in sorted(collected, key=lambda item: item["published"], reverse=True):
        if len(selected) >= MAX_ITEMS:
            break
        if per_source_count[item["source"]] >= MAX_ITEMS_PER_SOURCE:
            continue
        key = dedupe_key(item)
        if key in selected_keys:
            continue
        selected.append(item)
        selected_keys.add(key)
        per_source_count[item["source"]] += 1

    payload = {
        "updated": now.isoformat(),
        "pipeline": [
            "kaynak RSS/API/yayın akışı",
            "Python veri toplama",
            "alan adı ve kaynak kontrolü",
            "konu/içerik filtreleme",
            "rss-feed.json",
            "rss-loader.js",
            "ÇAHSPAR ana sayfası",
        ],
        "sources": source_catalog(),
        "items": sorted(selected, key=lambda item: item["published"], reverse=True),
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(payload['items'])} curated items at {OUT_PATH}")


if __name__ == "__main__":
    main()
