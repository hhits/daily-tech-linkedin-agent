from dataclasses import dataclass
import os


DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    linkedin_access_token: str
    linkedin_organization_id: str
    gemini_model: str = DEFAULT_GEMINI_MODEL
    linkedin_version: str = "202607"
    max_history_items: int = 60
    history_path: str = "data/topics.json"

    @classmethod
    def from_env(cls) -> "Settings":
        def required(name: str) -> str:
            value = os.getenv(name)
            if not value:
                raise RuntimeError(f"Missing required environment variable: {name}")
            return value

        return cls(
            gemini_api_key=required("GEMINI_API_KEY"),
            linkedin_access_token=required("LINKEDIN_ACCESS_TOKEN"),
            linkedin_organization_id=required("LINKEDIN_ORGANIZATION_ID"),
            gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
            linkedin_version=os.getenv("LINKEDIN_VERSION", "202607"),
            max_history_items=int(os.getenv("MAX_HISTORY_ITEMS", "60")),
            history_path=os.getenv("HISTORY_PATH", "data/topics.json"),
        )
