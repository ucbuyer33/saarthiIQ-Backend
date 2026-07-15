from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # ==========================================
    # 📝 Meta Project Settings
    # ==========================================
    PROJECT_NAME: str = Field("ATS AI Platform", description="Application tracking system title")
    PROJECT_VERSION: str = Field("1.0.0", description="Deployment version signature code")
    DEBUG: bool = Field(False, description="Toggles diagnostic verbose logging configurations")

    # ==========================================
    # 🗄️ Database Configurations
    # ==========================================
    DB_HOST: str
    DB_PORT: int = Field(5432)
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # 1. Computed Property Builder: Dynamically generates the SQLAlchemy execution string
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Synthesizes the global asynchronous/synchronous DB connectivity URL framework.
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ==========================================
    # 🔒 Cryptography & JWT Security
    # ==========================================
    SECRET_KEY: str
    ALGORITHM: str = Field("HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)

    # ==========================================
    # 🧠 Gemini AI Configuration
    # ==========================================
    GEMINI_API_KEY: str

    # ==========================================
    # 📧 Enterprise SMTP Communications
    # ==========================================
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = Field(587)
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = Field("Recruitment Operations Team")

    # ==========================================
    # ⚙️ Environments Validation Setup
    # ==========================================
    model_config = SettingsConfigDict(
        # Allows loading configuration file safely from application workspace roots
        env_file=os.path.join(os.getcwd(), ".env") if os.path.exists(".env") else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton global orchestration variable instantiation
settings = Settings()