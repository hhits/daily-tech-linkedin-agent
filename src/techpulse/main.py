from datetime import datetime, timezone

from .config import Settings
from .generator import GeminiPostGenerator, validate_post
from .history import History
from .linkedin import LinkedInPublisher
from .researcher import FeedResearcher


def run(settings: Settings, researcher, generator, publisher, history):
    candidates = researcher.fetch()
    topic = researcher.select(candidates, history)
    if topic is None:
        raise RuntimeError("No new relevant technology topic was found")
    post = generator.generate(topic)
    errors = validate_post(post)
    if errors:
        raise ValueError("Generated post failed validation: " + "; ".join(errors))
    post_id = publisher.publish(post)
    if not post_id:
        raise RuntimeError("LinkedIn did not return a post identifier")
    history.add(topic.title, datetime.now(timezone.utc).isoformat(), post_id)
    history.save(settings.history_path, settings.max_history_items)
    return post_id


def main():
    settings = Settings.from_env()
    history = History.load(settings.history_path)
    researcher = FeedResearcher()
    generator = GeminiPostGenerator(settings.gemini_api_key, settings.gemini_model)
    publisher = LinkedInPublisher(
        settings.linkedin_access_token,
        settings.linkedin_organization_id,
        settings.linkedin_version,
    )
    post_id = run(settings, researcher, generator, publisher, history)
    print(f"Published H&H TechPulse post: {post_id}")


if __name__ == "__main__":
    main()
