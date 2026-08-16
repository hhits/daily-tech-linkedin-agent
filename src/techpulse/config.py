from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    linkedin_access_token: str
    linkedin_organization_id: str
    openai_model: str = "gpt-4.1-mini"
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
            openai_api_key=required("OPENAI_API_KEY"),
            linkedin_access_token=required("LINKEDIN_ACCESS_TOKEN"),
            linkedin_organization_id=required("LINKEDIN_ORGANIZATION_ID"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            linkedin_version=os.getenv("LINKEDIN_VERSION", "202607"),
            max_history_items=int(os.getenv("MAX_HISTORY_ITEMS", "60")),
            history_path=os.getenv("HISTORY_PATH", "data/topics.json"),
        )
