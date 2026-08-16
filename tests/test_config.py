from techpulse.config import Settings


def test_settings_reads_required_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test")
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "linkedin-test")
    monkeypatch.setenv("LINKEDIN_ORGANIZATION_ID", "123")
    settings = Settings.from_env()
    assert settings.openai_api_key == "openai-test"
    assert settings.linkedin_organization_id == "123"
    assert settings.openai_model
