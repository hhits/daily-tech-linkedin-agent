# H&H TechPulse Daily LinkedIn Agent Design

## Goal
Build a GitHub Actions-based agent that researches a current technology topic each day, generates an original H&H IT Solutions LinkedIn post, prevents recent topic duplication, and publishes the post automatically to the H&H IT Solutions LinkedIn organization page.

## Architecture
The workflow runs on a daily cron schedule in GitHub Actions and invokes a Python package. The application separates configuration, topic research, post generation, duplicate-history storage, and LinkedIn publishing so each component can be tested independently. Credentials are supplied only through GitHub Actions secrets.

## Content Flow
1. Fetch current technology headlines from configurable RSS/Atom feeds.
2. Normalize and rank candidates by freshness and relevance to H&H IT Solutions.
3. Exclude topics that overlap with recent published history.
4. Send the selected topic and source metadata to the configured LLM provider.
5. Validate the generated post for length, required brand voice, hashtag count, and unsupported claims such as fabricated statistics.
6. Publish a text-only organic post to LinkedIn using the current Posts REST API.
7. Persist the topic fingerprint, date, title, and LinkedIn post ID in `data/topics.json`.

## LinkedIn Integration
LinkedIn's current Posts API supports organic text posts and requires the `w_organization_social` permission for posting on behalf of an organization. The authenticated member must have an appropriate organization role such as ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER, or CONTENT_ADMIN. The integration uses `POST /rest/posts` with `Linkedin-Version` and `X-Restli-Protocol-Version: 2.0.0` headers. The organization is represented by `urn:li:organization:{id}`.

The initial implementation is text-only. Image generation/upload is intentionally deferred so the daily publishing path remains small and reliable.

## Configuration
Required secrets:
- `OPENAI_API_KEY`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_ORGANIZATION_ID`

Optional variables:
- `OPENAI_MODEL` (default: `gpt-5.6-mini`)
- `LINKEDIN_VERSION` (default: `202607`)
- `MAX_HISTORY_ITEMS` (default: `60`)

The repository contains `.env.example` with names only; no credentials are committed.

## Scheduling
GitHub Actions runs once each weekday at 9:00 AM Central Time using the UTC equivalent in the cron expression. A manual `workflow_dispatch` trigger is also included for testing.

## Reliability
- Fail closed if required credentials are missing.
- Retry transient RSS and LinkedIn HTTP failures with bounded exponential backoff.
- Do not publish if no sufficiently relevant topic is found.
- Do not update history until LinkedIn confirms publication.
- Keep the history file deterministic and bounded.
- Exit non-zero on failed generation or publication so GitHub Actions visibly reports the failure.

## Testing
Unit tests cover feed parsing/ranking, duplicate detection, post validation, LinkedIn request construction, and history updates. External HTTP calls and the LLM provider are injected behind small interfaces so tests do not require real credentials or network access.

## Scope
Included: daily research, post generation, validation, duplicate prevention, LinkedIn text publishing, GitHub Actions scheduling, tests, documentation.

Excluded: image generation/upload, comments/replies, analytics, multi-page publishing, approval workflows, and long-term database storage.
