from techpulse.generator import GeminiPostGenerator


def test_generator_retries_gemini_429():
    calls = []
    response = {
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "text",
                        "text": "AI is changing IT operations with practical automation.\n\nH&H IT Solutions can help teams combine automation with observability for faster response.\n\n#AI #ITOperations #Automation",
                    }
                ],
            }
        ]
    }

    def fake_request(body):
        calls.append(body)
        if len(calls) == 1:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return response

    generator = GeminiPostGenerator("test-key", http_post=fake_request, sleep=lambda _: None)
    topic = type("Topic", (), {"title": "AI in IT operations", "url": "https://example.com", "summary": "AI automation is evolving."})()

    post = generator.generate(topic)

    assert post.startswith("AI is changing IT operations")
    assert len(calls) == 2
