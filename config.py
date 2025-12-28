from typing import Optional
from pydantic import BaseModel
from pathlib import Path


class DebateConfig(BaseModel):
    """Configuration for the debate system."""
    
    # General settings
    total_rounds: int = 8
    seed: Optional[int] = None
    log_path: Path = Path("logs")
    
    # Agent settings
    agent_a_persona: str = "scientist"
    agent_b_persona: str = "philosopher"
    
    # Validation settings
    similarity_threshold: float = 0.95  # For repetition detection (very lenient for demo)
    coherence_threshold: float = 0.7   # For topic drift detection
    
    # LLM settings (using simple responses for demo)
    max_tokens_per_response: int = 200
    temperature: float = 0.7
    
    class Config:
        arbitrary_types_allowed = True


# Default configuration instance
DEFAULT_CONFIG = DebateConfig()