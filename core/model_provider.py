import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()


class ModelProvider:
    def __init__(self):
        # Get the Google API key from environment variables
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Initialize models
        self._primary_model = None
        self._secondary_model = None
        self._tertiary_model = None

    def get_model(self, model_type="primary"):
        """
        Get a model based on the type (primary, secondary, or tertiary)

        Args:
            model_type (str): Type of model to get ("primary", "secondary", or "tertiary")

        Returns:
            ChatGoogleGenerativeAI or ChatOpenAI: The requested model
        """
        if model_type == "primary":
            if not self._primary_model:
                self._primary_model = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", google_api_key=self.google_api_key
                )
            return self._primary_model
        elif model_type == "secondary":
            if not self._secondary_model:
                self._secondary_model = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash", google_api_key=self.google_api_key
                )
            return self._secondary_model
        elif model_type == "tertiary":
            if not self._tertiary_model:
                self._tertiary_model = ChatOpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url=os.getenv("OPENROUTER_BASE_URL"),
                    model="qwen/qwen3-235b-a22b:free",
                )
            return self._tertiary_model
        else:
            raise ValueError(
                "model_type must be either 'primary', 'secondary', or 'tertiary'"
            )
