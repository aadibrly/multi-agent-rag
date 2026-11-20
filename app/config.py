from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    LANGCHAIN_TRACING_V2: bool = "True"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "multi-agent-rag"

    CHROMA_PERSIST_DIR: str = "./chroma.db"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    FAST_MODEL: str = "llama-3.1-8b-instant" # for routing
    SMART_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"

    mode_config = SettingsConfigDict(env_file='.env', extra='ignore') #tells Pydantic where to look for apis

settings = Settings()