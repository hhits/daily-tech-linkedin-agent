# H&H TechPulse — Daily LinkedIn Agent

H&H TechPulse researches current technology stories, writes an original H&H IT Solutions LinkedIn post, prevents recent topic repetition, and publishes automatically to the H&H IT Solutions organization page through LinkedIn's REST API.

## Daily flow

1. GitHub Actions runs on weekdays at 9:00 AM Central Standard Time.
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

## Important scheduling note

GitHub Actions cron uses UTC. The included schedule is `0 14 * * 1-5`, which is 9:00 AM Central Standard Time (UTC-6). During daylight time, adjust the cron to `0 14` only if your desired local time is 9:00 AM CDT? No: 9:00 AM CDT is 14:00 UTC, while 9:00 AM CST is 15:00 UTC. For a strict 9:00 AM America/Chicago schedule year-round, use an external scheduler or a two-season cron configuration.
