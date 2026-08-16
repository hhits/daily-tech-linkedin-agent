from dataclasses import dataclass, field
import json
import re
import unicodedata
from pathlib import Path


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"[^\w\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


@dataclass
class History:
    records: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path) -> "History":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(records=data.get("topics", []))

    def contains_topic(self, title: str) -> bool:
        target = normalize_title(title)
        return any(normalize_title(r.get("title", "")) == target for r in self.records)

    def add(self, title: str, published_at: str, linkedin_post_id: str) -> None:
        self.records.append({"title": title, "published_at": published_at, "linkedin_post_id": linkedin_post_id})

    def save(self, path: str | Path, max_items: int = 60) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        records = self.records[-max_items:]
        path.write_text(json.dumps({"topics": records}, indent=2) + "\n", encoding="utf-8")
