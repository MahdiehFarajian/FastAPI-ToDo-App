from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    SQLALCHEMY_DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/postgres"

    JWT_SECRET_KEY: str = "change me"
    ACCESS_EXPIRATION: int = 60 * 2
    REFRESH_EXPIRATION: int = 1440 * 7


settings= Settings()