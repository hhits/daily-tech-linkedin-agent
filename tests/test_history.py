from techpulse.history import History


def test_history_detects_normalized_duplicate(tmp_path):
    path = tmp_path / "topics.json"
    history = History.load(path)
    history.add("AI Agents for IT Operations", "2026-08-15", "urn:li:share:1")
    history.save(path, 60)
    loaded = History.load(path)
    assert loaded.contains_topic("ai agents for it operations") is True
    assert loaded.contains_topic("Cloud Security") is False
