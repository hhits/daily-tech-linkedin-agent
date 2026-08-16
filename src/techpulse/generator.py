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


class PostGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini", http_post=None):
        self.api_key = api_key
        self.model = model
        self.http_post = http_post or self._post

    def _post(self, body):
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        max_attempts = 4
        for attempt in range(max_attempts):
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    return json.loads(response.read().decode())
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt == max_attempts - 1:
                    raise
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = max(0.0, float(retry_after)) if retry_after else 2**attempt
                except ValueError:
                    delay = 2**attempt
                delay += random.uniform(0, 0.5)
                time.sleep(min(delay, 30.0))

        raise RuntimeError("OpenAI request exhausted retry attempts")

    def generate(self, topic: TopicCandidate) -> str:
        prompt = f"""Create a LinkedIn post from this current technology topic.\n\nTitle: {topic.title}\nSource: {topic.url}\nSummary: {topic.summary[:4000]}\n\nDo not claim facts beyond the supplied material and widely established technical knowledge."""
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        result = self.http_post(body)
        post = result["choices"][0]["message"]["content"].strip()
        errors = validate_post(post)
        if errors:
            raise ValueError("Invalid generated post: " + "; ".join(errors))
        return post
