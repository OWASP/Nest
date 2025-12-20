from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AIQueryDTO(BaseModel):
    """
    Represents a query sent to the AI service.
    """
    text: str
    project_id: str
    

#LAYER 1: Router DTOs
class RouterIntentDTO(BaseModel):
    """
    Represents an intent for the AI Router.
    """
    label: str # 'static' or 'dynamic'
    confidence: float

class ProjectPublicDTO(BaseModel):
    
    """
    Security Contract: Defines exactly what data is safe to expose.
    Mitigates OWASP LLM01 - Data Exposure, by preventing sensitive data leakage.
    """
    
    name: str
    maintainers: List[str]
    url: Dict[str, str]  # URL with validation {"repo":}
    description: str
    
    #Strict mode: no extra fields
    class Config:
        extra = "ignore"
        
# Unified Response DTO
class AIResponseDTO(BaseModel):
    """
    Represents a response from the AI service.
    """
    answer: str
    source: str #"cache", "statuc_lookup"
    intent: Optional[RouterIntentDTO] = None
    show_manual_search_btn: bool = False # The Escape Hatch for the AI