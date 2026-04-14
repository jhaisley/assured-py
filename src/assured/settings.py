"""Configuration loaded from environment / .env file."""

from __future__ import annotations

from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import logging

logger = logging.getLogger("assured")

env_path = find_dotenv(usecwd=True)
if env_path:
    logger.debug(f"Loaded environment variables from: {env_path}")
    load_dotenv(env_path)
    print(f"Loaded environment variables from: {env_path}")
    import os
    if os.getenv("ASSURED_USER") and os.getenv("ASSURED_PASS"):
        print(f"✅ Successfully found credentials for {os.getenv('ASSURED_USER')}")
    else:
        print("⚠️ WARNING: ASSURED_USER and/or ASSURED_PASS were not found in the .env file.")
else:
    logger.debug("No .env file found; falling back to system environment variables.")
    print("No .env file found; falling back to system environment variables.")


class Settings(BaseSettings):
    """Assured API configuration.

    Reads from environment variables or a ``.env`` file located in the
    current working directory (or any parent).

    Required variables
    ------------------
    ASSURED_BASE_URL : str
        Base URL of the Assured backend (e.g. ``https://demo-backend.withassured.com``).
    ASSURED_API_KEY : str
        Secret API key sent via the ``x-api-key`` header.
    ASSURED_USER : str
        Email used for JWT-based undocumented endpoints.
    ASSURED_PASS : str
        Password used for JWT-based undocumented endpoints.
    """

    model_config = SettingsConfigDict(
        env_prefix="ASSURED_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = "https://demo-backend.withassured.com"
    api_key: str = ""
    user: str = ""
    password: str = Field(default="", validation_alias="assured_pass")
