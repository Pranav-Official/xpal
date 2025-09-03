import os
from dotenv import load_dotenv


def set_env():
    # Load variables from .env file into environment
    load_dotenv()

    # Explicitly set them as environment variables for this process
    os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
    os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
    os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
