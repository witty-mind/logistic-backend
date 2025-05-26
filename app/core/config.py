from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Pricing Configuration
    PRICING_RATES: dict = {
        "EXPRESS": {"base_rate": 20.0, "description": "Fastest delivery option."},
        "STANDARD": {"base_rate": 10.0, "description": "Standard delivery timeframe."},
        "ECONOMY": {"base_rate": 5.0, "description": "Most economical delivery option."}
    }

    class Config:
        env_file = ".env"

settings = Settings()
