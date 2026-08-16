# H&H TechPulse Daily LinkedIn Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested Python agent and GitHub Actions workflow that researches a current technology topic, generates an H&H IT Solutions LinkedIn post, prevents recent duplicates, and publishes automatically to the organization page.

**Architecture:** A small Python package separates RSS research, LLM generation, validation, bounded JSON history, and LinkedIn REST publishing. GitHub Actions supplies secrets and runs the package on weekdays at 9:00 AM Central Time plus manual dispatch.

**Tech Stack:** Python 3.12, pytest, standard-library HTTP/XML/JSON tooling, OpenAI-compatible HTTPS API, LinkedIn Posts REST API, GitHub Actions.

## Global Constraints

- Credentials must be supplied through environment variables/GitHub Actions secrets and never committed.
- No production implementation is written before its behavior has a failing test.
- LinkedIn publishing is text-only in this first version.
- History is bounded to 60 entries by default.
- Failed publication must not update history.
- The workflow must fail visibly when generation or publication fails.

---

### Task 1: Project configuration and test foundation

**Files:**
- Create: `pyproject.toml`
- Create: `src/techpulse/__init__.py`
- Create: `src/techpulse/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Produces `Settings.from_env()` returning a typed settings object with required API credentials and configurable model/version/history values.

- [ ] **Step 1: Write the failing test**

```python
from techpulse.config import Settings


def test_settings_reads_required_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test")
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "linkedin-test")
    monkeypatch.setenv("LINKEDIN_ORGANIZATION_ID", "123")

    settings = Settings.from_env()

    assert settings.openai_api_key == "openai-test"
    assert settings.linkedin_organization_id == "123"
    assert settings.openai_model
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL because `techpulse.config` does not exist.

- [ ] **Step 3: Write minimal implementation**

Implement `Settings` as a frozen dataclass. `from_env()` must require the three credential variables and default `OPENAI_MODEL` to `gpt-5.6-mini`, `LINKEDIN_VERSION` to `202607`, and `MAX_HISTORY_ITEMS` to `60`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/techpulse tests/test_config.py
git commit -m "build: add project configuration"
```

### Task 2: Topic history and duplicate prevention

**Files:**
- Create: `src/techpulse/history.py`
- Create: `tests/test_history.py`
- Create: `data/topics.json`

**Interfaces:**
- `History.load(path) -> History`
- `History.contains_topic(title: str) -> bool`
- `History.add(title: str, published_at: str, linkedin_post_id: str) -> None`
- `History.save(path, max_items: int) -> None`

- [ ] **Step 1: Write the failing test**

```python
from techpulse.history import History


def test_history_detects_normalized_duplicate(tmp_path):
    path = tmp_path / "topics.json"
    history = History.load(path)
    history.add("AI Agents for IT Operations", "2026-08-15", "urn:li:share:1")
    history.save(path, 60)

    loaded = History.load(path)
    assert loaded.contains_topic("ai agents for it operations") is True
    assert loaded.contains_topic("Cloud Security") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_history.py -v`
Expected: FAIL because `History` is not implemented.

- [ ] **Step 3: Write minimal implementation**

Normalize titles by Unicode case-folding, collapsing whitespace, and removing punctuation. Store a JSON object containing a list of records. When saving, retain only the newest `max_items` records.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_history.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/techpulse/history.py tests/test_history.py data/topics.json
git commit -m "feat: add topic history and duplicate detection"
```

### Task 3: RSS research and topic ranking

**Files:**
- Create: `src/techpulse/researcher.py`
- Create: `tests/test_researcher.py`

**Interfaces:**
- `TopicCandidate(title: str, url: str, summary: str, published_at: str | None)`
- `FeedResearcher.fetch(feed_urls: list[str]) -> list[TopicCandidate]`
- `FeedResearcher.select(candidates, history) -> TopicCandidate | None`

- [ ] **Step 1: Write the failing test**

```python
from techpulse.researcher import FeedResearcher


def test_select_prefers_fresh_relevant_topic():
    researcher = FeedResearcher(http_get=lambda url: "")
    candidates = [
        researcher.candidate("AI agents automate IT operations", "https://example.com/ai", "AI agents are moving into IT.", "2026-08-15T12:00:00Z"),
        researcher.candidate("Celebrity news", "https://example.com/no", "Unrelated", "2026-08-15T13:00:00Z"),
    ]
    selected = researcher.select(candidates, history=type("H", (), {"contains_topic": lambda self, title: False})())
    assert selected.title == "AI agents automate IT operations"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_researcher.py -v`
Expected: FAIL because the researcher is not implemented.

- [ ] **Step 3: Write minimal implementation**

Parse RSS/Atom XML using `xml.etree.ElementTree`, support common `item` and Atom `entry` layouts, score candidates using technology keywords plus freshness, and exclude history matches. Use a configurable list of reputable technology feeds in the application defaults.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_researcher.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/techpulse/researcher.py tests/test_researcher.py
git commit -m "feat: add technology topic research"
```

### Task 4: Post generation and validation

**Files:**
- Create: `src/techpulse/generator.py`
- Create: `tests/test_generator.py`

**Interfaces:**
- `PostGenerator.generate(topic: TopicCandidate) -> str`
- `validate_post(post: str) -> list[str]`

- [ ] **Step 1: Write the failing test**

```python
from techpulse.generator import validate_post


def test_validate_post_requires_reasonable_length_and_hashtags():
    post = "AI is changing IT operations.\n\nH&H IT Solutions sees an opportunity to combine AI and automation.\n\n#AI #ITOperations #Automation"
    assert validate_post(post) == []


def test_validate_post_rejects_missing_hashtags():
    assert "hashtags" in " ".join(validate_post("Short post without tags.")).lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_generator.py -v`
Expected: FAIL because validation is not implemented.

- [ ] **Step 3: Write minimal implementation**

Implement deterministic validation for 100–3,000 characters, 3–6 hashtags, no placeholder markers, and no fabricated source claims. Implement an injected LLM client whose prompt contains the H&H brand voice and requires original, practical, non-clickbait content. The generator must retry malformed model output once, then fail.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_generator.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/techpulse/generator.py tests/test_generator.py
git commit -m "feat: generate and validate LinkedIn posts"
```

### Task 5: LinkedIn publisher

**Files:**
- Create: `src/techpulse/linkedin.py`
- Create: `tests/test_linkedin.py`

**Interfaces:**
- `LinkedInPublisher.publish(post: str) -> str`

- [ ] **Step 1: Write the failing test**

```python
from techpulse.linkedin import LinkedInPublisher


def test_publish_builds_organization_post_request():
    captured = {}

    def request(method, url, headers, body):
        captured.update(method=method, url=url, headers=headers, body=body)
        return 201, {"id": "urn:li:share:123"}

    publisher = LinkedInPublisher("token", "456", "202607", request)
    result = publisher.publish("Hello H&H IT Solutions")

    assert result == "urn:li:share:123"
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/rest/posts")
    assert captured["body"]["author"] == "urn:li:organization:456"
    assert captured["body"]["commentary"] == "Hello H&H IT Solutions"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_linkedin.py -v`
Expected: FAIL because the publisher is not implemented.

- [ ] **Step 3: Write minimal implementation**

POST JSON to `https://api.linkedin.com/rest/posts` with Bearer authorization, `Linkedin-Version`, `X-Restli-Protocol-Version: 2.0.0`, and `Content-Type: application/json`. Use an organization author URN, `lifecycleState: PUBLISHED`, `visibility: PUBLIC`, and the commentary text. Retry 429 and 5xx responses with bounded backoff; raise a descriptive error for other non-2xx responses.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_linkedin.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/techpulse/linkedin.py tests/test_linkedin.py
git commit -m "feat: publish posts to LinkedIn organization"
```

### Task 6: Application orchestration

**Files:**
- Create: `src/techpulse/main.py`
- Create: `tests/test_main.py`

**Interfaces:**
- `run(settings: Settings, researcher, generator, publisher, history) -> str`

- [ ] **Step 1: Write the failing test**

```python
from techpulse.main import run


def test_run_records_history_only_after_success(tmp_path):
    class Researcher:
        def select(self, candidates, history):
            return type("Topic", (), {"title": "Network automation", "url": "https://example.com", "summary": "", "published_at": "2026-08-15"})()
    class Generator:
        def generate(self, topic):
            return "Network automation helps IT teams.\n\n#Networking #Automation #IT"
    class Publisher:
        def publish(self, post):
            return "urn:li:share:99"

    history = __import__("techpulse.history", fromlist=["History"]).History.load(tmp_path / "topics.json")
    result = run(None, Researcher(), Generator(), Publisher(), history)

    assert result == "urn:li:share:99"
    assert history.contains_topic("Network automation")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_main.py -v`
Expected: FAIL because orchestration is not implemented.

- [ ] **Step 3: Write minimal implementation**

Orchestrate research, generation, validation, publication, and history persistence. Do not save history if publication raises. Return the LinkedIn post ID after successful publication.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_main.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/techpulse/main.py tests/test_main.py
git commit -m "feat: orchestrate daily publishing"
```

### Task 7: GitHub Actions and documentation

**Files:**
- Create: `.github/workflows/daily-post.yml`
- Create: `.env.example`
- Modify: `README.md`

**Interfaces:**
- Workflow executes `python -m techpulse` with repository secrets.

- [ ] **Step 1: Write the failing workflow smoke test**

Create `tests/test_workflow.py` that parses the YAML as text and asserts the workflow contains `workflow_dispatch`, a weekday cron, and the three required secret names.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow.py -v`
Expected: FAIL because the workflow does not exist.

- [ ] **Step 3: Write minimal workflow**

Use Python 3.12, install the package, run tests first, then run the application. Schedule weekdays at `0 14 * * 1-5` (9:00 AM Central Standard Time); document that GitHub cron is UTC and DST changes require adjusting the schedule if strict 9:00 AM local time is required. Include `workflow_dispatch` for manual runs. Expose `OPENAI_API_KEY`, `LINKEDIN_ACCESS_TOKEN`, and `LINKEDIN_ORGANIZATION_ID` as secrets.

- [ ] **Step 4: Run the complete test suite**

Run: `pytest -q`
Expected: PASS.

- [ ] **Step 5: Update README**

Document LinkedIn developer setup, required organization permission, GitHub secret names, local test/run commands, and manual workflow dispatch. Explain that the first release publishes text-only posts and requires a valid LinkedIn access token with organization posting permission.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/daily-post.yml .env.example README.md tests/test_workflow.py
git commit -m "ci: schedule daily LinkedIn publishing"
```

### Task 8: Final verification and push

**Files:**
- Modify: any implementation files needed after verification.

- [ ] **Step 1: Run full verification**

Run: `pytest -q`
Expected: all tests PASS.

- [ ] **Step 2: Inspect repository status**

Run: `git status --short`
Expected: no unintended files or secrets.

- [ ] **Step 3: Review diff against main**

Run: `git diff main...HEAD --check`
Expected: no whitespace errors.

- [ ] **Step 4: Push branch**

Push the feature branch to GitHub and report the branch and commit SHA. Do not claim LinkedIn publication is live until GitHub Actions has successfully run with valid user-provided secrets.
