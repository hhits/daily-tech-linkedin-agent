from techpulse.generator import GeminiPostGenerator, validate_post


def test_validate_post_accepts_normal_post():
    post = "AI is changing IT operations.\n\nH&H IT Solutions sees an opportunity to combine AI and automation.\n\n#AI #ITOperations #Automation"
    assert validate_post(post) == []


def test_validate_post_rejects_missing_hashtags():
    assert "hashtags" in " ".join(validate_post("Short post without tags.")).lower()


def test_gemini_generator_extracts_generated_text():
    response = {
        "candidates": [
            {"content": {"parts": [{"text": "AI is changing IT operations.\n\nTeams can automate repetitive work safely.\n\n#AI #ITOperations #Automation"}]}}
        ]
    }
    generator = GeminiPostGenerator("test-key", http_post=lambda body: response)
    topic = type("Topic", (), {
        "title": "AI agents in IT operations",
        "url": "https://example.com/ai",
        "summary": "AI agents can automate IT tasks.",
    })()

    assert generator.generate(topic).startswith("AI is changing IT operations")


def test_gemini_generator_retries_429():
    calls = []
    response = {
        "candidates": [
            {"content": {"parts": [{"text": "AI is changing IT operations.\n\nTeams can automate repetitive work safely.\n\n#AI #ITOperations #Automation"}]}}
        ]
    }

    def request(body):
        calls.append(body)
        if len(calls) == 1:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return response

    generator = GeminiPostGenerator("test-key", http_post=request, sleep=lambda _: None)
    topic = type("Topic", (), {"title": "AI agents", "url": "https://example.com", "summary": "AI agents."})()
    assert generator.generate(topic)
    assert len(calls) == 2
