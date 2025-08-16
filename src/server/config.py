from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BLOG_PROD: bool


settings = Settings()  # type: ignore
