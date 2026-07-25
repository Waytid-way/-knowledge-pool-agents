from llm_wiki.core.config import Settings


def test_settings_load_required_values(monkeypatch):
    monkeypatch.setenv("LLM_WIKI_DATABASE_URL", "postgresql+psycopg://u:p@db/wiki")
    monkeypatch.setenv("LLM_WIKI_TEMPORAL_ADDRESS", "temporal:7233")
    monkeypatch.setenv("LLM_WIKI_S3_ENDPOINT", "http://minio:9000")
    monkeypatch.setenv("LLM_WIKI_S3_BUCKET", "llm-wiki")
    monkeypatch.setenv("LLM_WIKI_MODEL_GATEWAY_URL", "http://model-gateway:8080")

    settings = Settings()

    assert settings.environment == "development"
    assert settings.s3_bucket == "llm-wiki"
