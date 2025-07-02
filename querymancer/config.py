import os
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"
    

@dataclass
class ModelConfig:
    name: str
    provider: ModelProvider
    temperature: float


QWEN_2_5 = ModelConfig("qwen2.5", ModelProvider.OLLAMA, 0.0)
GEMMA_3 = ModelConfig("PetroStav/gemma3-tools:12b", ModelProvider.OLLAMA, 0.7)
LLAMA_3_3 = ModelConfig("llama-3.3-70b-versatile", ModelProvider.GROQ, 0.0)

class Config:
    SEED = 42
    MODEL_CONFIG = QWEN_2_5  # Default model configuration
    OLLAMA_CONTEXT_WINDOW = 2048
    
    class Paths:
       APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
       DATA_DIR = APP_HOME / "data"
       DATABASE_PATH = DATA_DIR / "ecommerce.sqlite"
       
def seed_everything(seed: int = Config.SEED):
    random.seed(seed)
