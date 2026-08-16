import urllib.error

from techpulse.generator import PostGenerator


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        import json
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_generator_retries_openai_429(monkeypatch):
    calls = []

    def fake_urlopen(req, timeout=60):
        calls.append(req)
        if len(calls) == 1:
            error = urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {"Retry-After": "0"}, None)
            raise error
        return _Response({"choices": [{"message": {"content": "AI is changing IT operations with practical automation.\n\nH&H IT Solutions sees an opportunity to combine AI and observability for faster response.\n\n#AI #ITOperations #Automation"}}]})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda seconds: None)

    generator = PostGenerator("test-key", http_post=None)
    topic = type("Topic", (), {"title": "AI in IT operations", "url": "https://example.com", "summary": "AI automation is evolving."})()

    post = generator.generate(topic)

    assert post.startswith("AI is changing IT operations")
    assert len(calls) == 2
