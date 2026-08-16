from techpulse.history import History
from techpulse.main import run


def test_run_records_history_only_after_success(tmp_path):
    class Researcher:
        def fetch(self):
            return []
        def select(self, candidates, history):
            return type("Topic", (), {"title": "Network automation", "url": "https://example.com", "summary": "", "published_at": "2026-08-15"})()
    class Generator:
        def generate(self, topic):
            return "Network automation helps IT teams improve repeatability and reduce manual work.\n\n#Networking #Automation #IT"
    class Publisher:
        def publish(self, post):
            return "urn:li:share:99"

    history = History.load(tmp_path / "topics.json")
    settings = type("Settings", (), {"history_path": str(tmp_path / "topics.json"), "max_history_items": 60})()
    result = run(settings, Researcher(), Generator(), Publisher(), history)
    assert result == "urn:li:share:99"
    assert history.contains_topic("Network automation")
