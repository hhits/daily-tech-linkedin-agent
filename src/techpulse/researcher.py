from dataclasses import dataclass
from datetime import datetime, timezone
import re
import urllib.request
import xml.etree.ElementTree as ET

DEFAULT_FEEDS = [
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "https://www.technologyreview.com/feed/",
]

KEYWORDS = re.compile(r"\b(ai|artificial intelligence|agent|cybersecurity|security|cloud|network|observability|automation|devops|kubernetes|azure|aws|zero trust|ransomware|infrastructure|it operations)\b", re.I)


@dataclass(frozen=True)
class TopicCandidate:
    title: str
    url: str
    summary: str
    published_at: str | None


class FeedResearcher:
    def __init__(self, http_get=None):
        self.http_get = http_get or self._get

    @staticmethod
    def _get(url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "HHTechPulse/0.1"})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8", errors="replace")

    @staticmethod
    def candidate(title, url, summary, published_at):
        return TopicCandidate(title, url, summary, published_at)

    def fetch(self, feed_urls=None):
        candidates = []
        for url in feed_urls or DEFAULT_FEEDS:
            try:
                root = ET.fromstring(self.http_get(url))
            except Exception:
                continue
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                summary = (item.findtext("description") or "").strip()
                published = (item.findtext("pubDate") or "").strip() or None
                if title and link:
                    candidates.append(TopicCandidate(title, link, summary, published))
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//a:entry", ns):
                title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
                link_node = entry.find("a:link", ns)
                link = link_node.attrib.get("href", "") if link_node is not None else ""
                summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
                published = (entry.findtext("a:published", default="", namespaces=ns) or "").strip() or None
                if title and link:
                    candidates.append(TopicCandidate(title, link, summary, published))
        return candidates

    def select(self, candidates, history):
        available = [c for c in candidates if not history.contains_topic(c.title)]
        if not available:
            return None

        def score(candidate):
            text = f"{candidate.title} {candidate.summary}"
            relevance = len(KEYWORDS.findall(text))
            freshness = 0
            if candidate.published_at:
                freshness = 1
                try:
                    dt = datetime.fromisoformat(candidate.published_at.replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
                    freshness = max(0, 5 - age)
                except ValueError:
                    pass
            return relevance * 10 + freshness

        return max(available, key=score)
