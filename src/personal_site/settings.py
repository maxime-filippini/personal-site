import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    BLOG_PROD: bool
    CLOUDFLARE_R2_API_TOKEN: str
    CLOUDFLARE_R2_ACCESS_ID: str
    CLOUDFLARE_R2_SECRET: str
    CLOUDFLARE_R2_URL: str
    CLOUDFLARE_ACCOUNT_ID: str

    @property
    def polars_storage_options(self):
        return {
            "aws_access_key_id": self.CLOUDFLARE_R2_ACCESS_ID,
            "aws_secret_access_key": self.CLOUDFLARE_R2_SECRET,
            "aws_region": "auto",
            "endpoint_url": self.CLOUDFLARE_R2_URL,
        }


settings = Settings()  # type: ignore
