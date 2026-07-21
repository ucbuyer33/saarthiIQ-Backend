from urllib.parse import quote_plus
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("ATS AI Platform", description="Application tracking system title")
    PROJECT_VERSION: str = Field("1.0.0", description="Deployment version signature code")
    DEBUG: bool = Field(False, description="Toggles diagnostic verbose logging configurations")

    DB_HOST: str
    DB_PORT: int = Field(5432)
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    SECRET_KEY: str
    ALGORITHM: str = Field("HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)

    GEMINI_API_KEY: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = Field(587)
    MAIL_SERVER: str = Field("smtp-relay.brevo.com")
    MAIL_FROM_NAME: str = Field("Recruitment Operations Team")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.getcwd(), ".env") if os.path.exists(".env") else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()