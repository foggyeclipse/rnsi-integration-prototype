import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    # Database
    DB_NAME: str = os.getenv("DB_NAME", "dictionaries")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    # NSI API
    NSI_BASE_URL: str = "https://nsi.rosminzdrav.ru/port/rest/data"
    USER_KEY: str = os.getenv("USER_KEY")  # required, no default

    # Dictionaries to process
    DICTIONARIES = [
        "1.2.643.5.1.13.13.11.1040",
        "1.2.643.5.1.13.13.11.1486",
        "1.2.643.5.1.13.13.99.2.647",
        "1.2.643.5.1.13.13.99.2.1047",
    ]

    # Pagination
    PAGE_SIZE: int = 200


settings = Settings()

if not settings.USER_KEY:
    raise ValueError("USER_KEY is not set in .env file")