from techpulse.generator import GeminiPostGenerator


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
