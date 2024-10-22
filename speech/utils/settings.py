import os
from dotenv import find_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

env = os.getenv("SPEECH_ENV", "development").lower()
env_file_map = {
    "development": ".env.development",
    "production": ".env.production",
    "staging": ".env.staging",
}
env_file_name = env_file_map.get(env, ".env.development")
env_file = find_dotenv(env_file_name)


class Settings(BaseSettings):
    path_client: str
    path_ssl_cert: str
    path_ssl_key: str

    class Config:
        env_file = env_file


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

if __name__ == "__main__":
    settings = get_settings()
    print(f"Settings are {settings.dict()}")
