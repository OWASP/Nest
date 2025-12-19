from pydantic import BaseModel
from typing import List

class ProjectPublicDTO(BaseModel):
    
    """
    Security Contract: Defines exactly what data is safe to expose.
    Mitigates OWASP LLM01 - Data Exposure, by preventing sensitive data leakage.
    """
    
    name: str
    leader: str
    url: str
    description: str
    tags: List[str] = []
    #Note: internal fields like 'admin_id' are strictly excluded.