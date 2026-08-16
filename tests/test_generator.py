from techpulse.generator import GeminiPostGenerator, validate_post


POST = "AI is changing IT operations.\n\nTeams can automate repetitive work safely.\n\n#AI #ITOperations #Automation"


def test_validate_post_accepts_normal_post():
    assert validate_post(POST) == []


def test_validate_post_rejects_missing_hashtags():
    assert "hashtags" in " ".join(validate_post("Short post without tags.")).lower()


def test_gemini_generator_builds_interactions_request_and_extracts_text():
    captured = {}
    response = {
        "steps": [
            {"type": "model_output", "content": [{"type": "text", "text": POST}]}
        ]
    }

    def request(body):
        captured.update(body)
        return response

    generator = GeminiPostGenerator("test-key", http_post=request)
    topic = type("Topic", (), {
        "title": "AI agents in IT operations",
        "url": "https://example.com/ai",
        "summary": "AI agents can automate IT tasks.",
    })()

    assert generator.generate(topic).startswith("AI is changing IT operations")
    assert captured["model"] == "gemini-2.5-flash-lite"
    assert captured["store"] is False
    assert captured["system_instruction"]


def test_gemini_generator_retries_429():
    calls = []

    def request(body):
        calls.append(body)
        if len(calls) == 1:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return {"steps": [{"type": "model_output", "content": [{"type": "text", "text": POST}]}]}

    generator = GeminiPostGenerator("test-key", http_post=request, sleep=lambda _: None)
    topic = type("Topic", (), {"title": "AI agents", "url": "https://example.com", "summary": "AI agents."})()
    assert generator.generate(topic)
    assert len(calls) == 2
