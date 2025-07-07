from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    bot_token: str
    database_url: str
    lang: str = "ru"

    model_config = ConfigDict(env_file=".env")

settings = Settings()
