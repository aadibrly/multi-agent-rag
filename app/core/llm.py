from langchain.chat_models import init_chat_model
import requests
from app.config import settings

# model verifivation section
class ModelUnavailError(Exception):
    pass

def verify_model(provider: str, model_name: str) -> None:
    if provider == 'groq':
        url = "https://api.groq.com/openai/v1/models"
        header = {"Authorization":f"Bearer {settings.GROQ_API_KEY}"}
    elif provider == 'nvidia':
        url = "https://integrate.api.nvidia.com/v1/models" # this link show all teh current models 
        header = {"Authorization":f"Bearer {settings.NVIDIA_API_KEY}"}
    else:
        return

    response = requests.get(url, headers=header, timeout=5)
    if response.status_code == 200:
        available_ids = {item['id'] for item in response.json().get("data", [])} 
        if model_name not in available_ids:
            raise ModelUnavailError(
                f"The model '{model_name} is not currently available on {provider}'",
                f"Please choose another model for this cloud provider or switch back to the default"

            )

def get_llm(role:str ='smart', provider:str ='groq',
            model_override:str | None = None, 
            temperature:float = 0.0,
            validate:bool = False):

    '''Chooses the default or prefered model based on the availability and providers'''
    if provider == 'nvidia':
        if not settings.NVIDIA_API_KEY:
            raise ModelUnavailError(f"NVIDIA_API_KEY is missing in .env")
                 
        default_model = settings.NVIDIA_FAST_MODEL if role == 'fast' else settings.NVIDIA_SMART_MODEL
        choosen_model = model_override or default_model

        # model alive or deprocted
        if validate:
            verify_model(provider='nvidia', model_name=choosen_model)

        return init_chat_model(
            model=choosen_model,
            model_provider="nvidia",
            api_key=settings.NVIDIA_API_KEY,
            base_url="https://integrate.api.nvidia.com/v1",
            temperature=temperature
            )

    if provider in {"gemini", "google", "google_genai"}:
        if not settings.GEMINI_API_KEY:
            raise ModelUnavailError(f"GEMINI_API_KEY is missing in .env")
        
        default_model = settings.GOOGLE_FAST_MODEL if role == 'fast' else settings.GOOGLE_SMART_MODEL
        choosen_model = model_override or default_model

        if validate:
            verify_model(provider='google', model_name=choosen_model)
        return init_chat_model(
            model=choosen_model,
            model_provider="google_genai",
            api_key=settings.GOOGLE_API_KEY,
            temperature=temperature
            )
    
    if not settings.GROQ_API_KEY:
                raise ModelUnavailError(f"GROQ_API_KEY is missing in .env")
    
    default_model = settings.GROQ_FAST_MODEL if role == 'fast' else settings.GROQ_SMART_MODEL
    choosen_model = model_override or default_model

    if validate:
        verify_model(provider='groq', model_name=choosen_model)
    return init_chat_model(
        model=choosen_model,
        model_provider="groq",
        api_key=settings.GROQ_API_KEY,
        temperature=temperature
        )


    


