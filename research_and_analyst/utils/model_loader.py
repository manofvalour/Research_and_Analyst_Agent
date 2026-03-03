import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from research_and_analyst.utils.config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAi
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from research_and_analyst.logger import GLOBAL_LOGGER as log
from research_and_analyst.exceptions.custom_exception import ResearchAnalystException


class APIKeyManager:
    """
    Loads and manages all environment-based API keys.
    """

    def __init__(self):
        load_dotenv()

        self.api_keys = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
        }
        log.info("initializing ApiKeyManager")

        # Log loaded key statuses without exposing secrets 
        for key, val in self.api_keys.items():
            if val:
                log.info(f"{key} loaded successfully from environment")
            else:
                log.warning(f"{key} is missing in the environment variables")

    def get(self, key: str):
        """
        Retrieve a specific API key.

        Args:
            key(str): Name of the API key.
        
        Returns:
            str | None: API key value if found
        """

        return self.api_keys.get(key)
    
class ModelLoader:
    """
    Loads embedding models and LLMs dynamically based on YAML configuration and environemnt settings.
    """

    def __init__(self):
        """
        Initialize the ModelLoader and load configuration.
        """
        try:
            self.api_key_mgr = APIKeyManager()
            self.config = load_config()

        except Exception as e:
            log.error("Error initializing ModelLoader", error=str(e))
            raise ResearchAnalystException('Failed to initialize ModelLoader', sys)
        
    def load_embeddings(self):
        """
        Load and return a Googl Generative AI embdedding model.

        Returns:
            GoogleGenerativeAIEmbeddings: Loaded embedding model instance.
        """

        try:
            model_name = self.config['embedding_model']['model_name']
            log.info("loading embedding model", model = model_name)

            ## ensure event loop exists for gRPC-based embedding API
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key = self.api_key_mgr.get("GOOGLE_API_KEY"),
            )

            log.info("Embedding model loaded successfully", model= model_name)
            return embeddings
        
        except Exception as e:
            log.error("Unable to load the Embedding Model", error = str(e))
            raise ResearchAnalystException("Faied to load the Embedding Model", e)


    def load_llm(self):
        """
        Load and return a chat_based LLM according to the configured provider.

        Supported providers:
            - OpenAI
            - Google Gemini
            - Groq
        
        Returns:
            ChatOpenAI | ChatGoogleGenerativeAI | ChatGroq: LLM Instance
        """

        try:
            llm_block = self.config["llm"]
            provider_key = os.getenv("LLM_PROVIDER", "openai")

            if provider_key not in llm_block:
                log.error("LLM provider not found in configuration", provider=provider_key)
                raise ValueError(f"LLM proider '{provider_key}' not found in configuration")

            llm_config = llm_block[provider_key]
            provider = llm_config.get('provider')
            model_name = llm_config.get('model_name')
            temperature = llm_config.get("temperature", 0.2)
            max_tokens = llm_config.get("max_output_tokens", 2048)

            log.info("Loading LLM", provider=provider, model = model_name)

            if provider == 'google':
                llm = ChatGoogleGenerativeAi(
                    model = model_name,
                    googl_api_key = self.api_key_mgr.get('GOOGLE_API_KEY'),
                    temperature = temperature,
                    max_output_tokens = max_tokens
                )

            elif provider == 'groq':
                llm = ChatGroq(
                    model = model_name,
                    api_key = self.api_key_mgr.get("GROQ_API_KEY"),
                    temperature = temperature
                )
            
            elif provider == 'openai':
                llm == ChatOpenAI(
                    model = model_name,
                    api_key = self.api_key_mgr.get('OPENAI_API_KEY'),
                    temperature=temperature
                )

            else:
                log.error("Unsupported LLM Provider encountered", provider=provider)
                raise ValueError(f"Unsupported LLM Provider: {provider}")
            
            log.info("LLM loaded successfully", provider=provider, model=model_name)
            return llm
        
        except Exception as e:
            log.error("Error loading LLM", error=str(e))
            raise ResearchAnalystException("Failed to load LLM", sys)


if __name__ == "__main__":
    try:
        loader = ModelLoader()
        llm = loader.load_llm()
        print(f"LLM_loaded: {llm}")
        result = llm.invoke("Hello, how are you?")
        print(f"LLM Result: {result.content[:200]}")

        log.info("ModelLoader test completed")

    except ResearchAnalystException as e:
        log.error("Critical failure in ModelLoader test", error=str(e))