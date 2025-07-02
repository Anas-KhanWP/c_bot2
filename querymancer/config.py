import os
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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
    OLLAMA_CONTEXT_WINDOW = 5120
    
    class Database:
        MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        DATABASE_NAME = os.getenv("DATABASE_NAME", "defaultdb")
    
    class Paths:
       APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
       DATA_DIR = APP_HOME / "data"
       
def seed_everything(seed: int = Config.SEED):
    random.seed(seed)
