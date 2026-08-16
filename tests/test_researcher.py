from techpulse.researcher import FeedResearcher


def test_select_prefers_technology_topic():
    researcher = FeedResearcher(http_get=lambda url: "")
    candidates = [
        researcher.candidate("AI agents automate IT operations", "https://example.com/ai", "AI agents are moving into IT.", "2026-08-15T12:00:00Z"),
        researcher.candidate("Celebrity news", "https://example.com/no", "Unrelated", "2026-08-15T13:00:00Z"),
    ]
    selected = researcher.select(candidates, history=type("H", (), {"contains_topic": lambda self, title: False})())
    assert selected.title == "AI agents automate IT operations"
