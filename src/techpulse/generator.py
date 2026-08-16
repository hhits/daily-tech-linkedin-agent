import json
import random
import re
import time
import urllib.error
import urllib.request

from .researcher import TopicCandidate

SYSTEM_PROMPT = """You are H&H TechPulse, the technology content writer for H&H IT Solutions.
Write one original LinkedIn post for IT leaders and technology professionals.
Be practical, technically credible, concise, and educational. Avoid clickbait,
empty marketing language, fabricated statistics, invented quotes, and claims
that H&H IT Solutions performed work that is not in the source. Mention H&H IT
Solutions naturally only when useful. End with one thoughtful question. Use
3-6 relevant hashtags. Return only the post text."""


def validate_post(post: str) -> list[str]:
    errors = []
    if not 100 <= len(post.strip()) <= 3000:
        errors.append("post length must be between 100 and 3000 characters")
    tags = re.findall(r"(?<!\w)#\w+", post)
    if not 3 <= len(tags) <= 6:
        errors.append("post must contain 3-6 hashtags")
    if re.search(r"\b(TODO|TBD|INSERT|PLACEHOLDER)\b", post, re.I):
        errors.append("post contains a placeholder")
    return errors


class GeminiPostGenerator:
    """Generate H&H TechPulse posts with Google's Gemini Developer API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", http_post=None, sleep=time.sleep):
        self.api_key = api_key
        self.model = model
        self.http_post = http_post or self._post
        self.sleep = sleep

    def _post(self, body):
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    return json.loads(response.read().decode())
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt == 3:
                    raise RuntimeError(f"Gemini API HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else 2**attempt
                except ValueError:
                    delay = 2**attempt
                self.sleep(min(delay + random.uniform(0, 0.5), 30.0))
            except RuntimeError as exc:
                if "429" not in str(exc) or attempt == 3:
                    raise
                self.sleep(min(2**attempt + random.uniform(0, 0.5), 30.0))

        raise RuntimeError("Gemini request exhausted retry attempts")

    def generate(self, topic: TopicCandidate) -> str:
        prompt = f"""Create a LinkedIn post from this current technology topic.\n\nTitle: {topic.title}\nSource: {topic.url}\nSummary: {topic.summary[:4000]}\n\nDo not claim facts beyond the supplied material and widely established technical knowledge."""
        body = {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600},
        }
        result = self.http_post(body)
        try:
            post = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Gemini response did not contain generated text: {result}") from exc
        errors = validate_post(post)
        if errors:
            raise ValueError("Invalid generated post: " + "; ".join(errors))
        return post


# Backward-compatible name for callers that imported the old generator class.
PostGenerator = GeminiPostGenerator
