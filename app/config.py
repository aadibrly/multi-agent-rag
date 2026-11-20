from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    LANGCHAIN_TRACING_V2: bool = "True"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "multi-agent-rag"

    CHROMA_PERSIST_DIR: str = "./chroma.db"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    GROQ_FAST_MODEL: str = "openai/gpt-oss-20b"
    GROQ_SMART_MODEL: str = "openai/gpt-oss-120b"

    NVIDIA_FAST_MODEL: str = "nvidia/nemotron-3.5-lightning"
    NVIDIA_SMART_MODEL: str = "moonshotai/kimi-k3.1-pro"

    GOOGLE_FAST_MODEL: str = "gemini-3.5-flash-lite"
    GOOGLE_SMART_MODEL: str = "gemini-3.8-flash"

    mode_config = SettingsConfigDict(env_file='.env', extra='ignore') #tells Pydantic where to look for apis

settings = Settings()