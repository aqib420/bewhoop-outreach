from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # REQUIRED FIELDS (must be present in .env)
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    # OPTIONAL FIELDS (with defaults or optional type)
    supabase_db_host: str
    supabase_db_port: str
    supabase_db_name: str
    supabase_db_user: str
    supabase_db_password: str
    database_url: str
    alembic_database_url: str
    gemini_api_key: str
    project_name: str = "BeWhoop Outreach Agent"
    debug: bool = False

    model_config = SettingsConfigDict(extra="allow", env_file=".env")


settings = Settings() 