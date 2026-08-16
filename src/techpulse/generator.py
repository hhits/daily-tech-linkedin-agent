import json
import random
import time
import urllib.error
import urllib.request

from .researcher import TopicCandidate

SYSTEM_PROMPT = """You are H&H TechPulse, the technology content writer for H&H IT Solutions.
Write an original, practical LinkedIn post for IT professionals and technology decision-makers.
Use a professional, technical, approachable voice. Avoid clickbait, unsupported claims, and excessive emojis.
Keep the post around 150-250 words, include a useful takeaway, and finish with 3-6 relevant hashtags.
Naturally mention H&H IT Solutions when appropriate, without making unsupported claims about the company."""


def validate_post(post: str) -> list[str]:
    errors = []
    if not 100 <= len(post) <= 3000:
        errors.append("post length must be between 100 and 3000 characters")
    hashtag_count = sum(1 for token in post.split() if token.startswith("#"))
    if not 3 <= hashtag_count <= 6:
        errors.append("post must contain 3-6 hashtags")
    if "[INSERT" in post or "<PLACEHOLDER>" in post:
        errors.append("post contains a placeholder")
    return errors


class GeminiPostGenerator:
    """Generate H&H TechPulse posts with Google's Gemini Interactions API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite", http_post=None, sleep=time.sleep):
        self.api_key = api_key
        self.model = model
        self.http_post = http_post or self._post
        self.sleep = sleep

    def _post(self, body):
        url = "https://generativelanguage.googleapis.com/v1/interactions"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())

    def _request_with_retry(self, body):
        for attempt in range(4):
            try:
                return self.http_post(body)
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt == 3:
                    raise RuntimeError(
                        f"Gemini API HTTP {exc.code}: {exc.read().decode(errors='replace')}"
                    ) from exc
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else 2**attempt
                except (TypeError, ValueError):
                    delay = 2**attempt
                self.sleep(min(delay + random.uniform(0, 0.5), 30.0))
            except RuntimeError as exc:
                if "429" not in str(exc) or attempt == 3:
                    raise
                self.sleep(min(2**attempt + random.uniform(0, 0.5), 30.0))
        raise RuntimeError("Gemini request exhausted retry attempts")

    @staticmethod
    def _extract_text(result: dict) -> str:
        for step in result.get("steps", []):
            if step.get("type") != "model_output":
                continue
            for content in step.get("content", []):
                if content.get("type") == "text" and content.get("text"):
                    return content["text"].strip()
        raise RuntimeError(f"Gemini response did not contain generated text: {result}")

    def generate(self, topic: TopicCandidate) -> str:
        prompt = f"""Create a LinkedIn post from this current technology topic.

Title: {topic.title}
Source: {topic.url}
Summary: {topic.summary[:4000]}

Do not claim facts beyond the supplied material and widely established technical knowledge."""
        body = {
            "model": self.model,
            "input": prompt,
            "system_instruction": SYSTEM_PROMPT,
            "generation_config": {
                "temperature": 0.7,
                "max_output_tokens": 600,
            },
            "store": False,
        }
        result = self._request_with_retry(body)
        post = self._extract_text(result)
        errors = validate_post(post)
        if errors:
            raise ValueError("Invalid generated post: " + "; ".join(errors))
        return post


PostGenerator = GeminiPostGenerator
