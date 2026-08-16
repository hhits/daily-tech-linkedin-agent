from techpulse.config import Settings


def test_settings_reads_gemini_configuration(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test")
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "linkedin-test")
    monkeypatch.setenv("LINKEDIN_ORGANIZATION_ID", "123")

    settings = Settings.from_env()

    assert settings.gemini_api_key == "gemini-test"
    assert settings.linkedin_organization_id == "123"
    assert settings.gemini_model == "gemini-3.5-flash-lite"
