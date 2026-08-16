# H&H TechPulse — Daily LinkedIn Agent

H&H TechPulse researches current technology stories, writes an original H&H IT Solutions LinkedIn post, prevents recent topic repetition, and publishes automatically to the H&H IT Solutions organization page through LinkedIn's REST API.

## Daily flow

1. GitHub Actions runs on weekdays on the configured UTC schedule.
2. RSS/Atom technology feeds are collected.
3. A relevant, fresh topic is selected while excluding recent history.
4. An LLM writes and validates the post.
5. The LinkedIn organization post is published.
6. The topic and returned LinkedIn post ID are stored in `data/topics.json`.

## Required GitHub configuration

Add these **repository secrets** under Settings → Secrets and variables → Actions:

- `OPENAI_API_KEY`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_ORGANIZATION_ID`

Optional repository variables:

- `OPENAI_MODEL` — defaults to `gpt-4.1-mini`
- `LINKEDIN_VERSION` — defaults to `202607`

Never commit API keys or access tokens.

## LinkedIn permissions

The LinkedIn access token must belong to a member authorized to post for the target organization and must include organization social posting permission. Set `LINKEDIN_ORGANIZATION_ID` to the numeric organization ID, not the company URL.

The first release publishes text-only organic posts. Media upload, analytics, comments, and multi-page publishing are intentionally outside the initial scope.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -q

export OPENAI_API_KEY='...'
export LINKEDIN_ACCESS_TOKEN='...'
export LINKEDIN_ORGANIZATION_ID='...'
python -m techpulse.main
```

## Manual run

GitHub Actions includes a `workflow_dispatch` trigger. Open **Actions → H&H TechPulse Daily LinkedIn Post → Run workflow** after configuring the secrets.

## Scheduling note

GitHub Actions cron uses UTC. The included `0 14 * * 1-5` schedule corresponds to 9:00 AM Central Daylight Time and 8:00 AM Central Standard Time. GitHub Actions does not provide a native America/Chicago timezone in cron, so a strict 9:00 AM local-time schedule requires a DST-aware scheduler or separate seasonal schedules.
