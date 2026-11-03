from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field(..., alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")
    r2_account_id: str = Field(..., alias="R2_ACCOUNT_ID")
    r2_access_key_id: str = Field(..., alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: str = Field(..., alias="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str = Field(..., alias="R2_BUCKET_NAME")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
