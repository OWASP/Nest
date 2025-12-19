import html
from typing import Optional
from src.dtos import ProjectPublicDTO

# Ensure the class name is exactly 'ProjectService' (Case Sensitive)
class ProjectService:
    """
    Layer 2: Project Service
    Role: Deterministic Source of Truth for Project Data.
    """

    def __init__(self):
        # Mock Database (simulating SQL/API)
        self._db_mock = {
            "zap": {
                "name": "OWASP ZAP",
                "leader": "Simon Bennetts",
                "url": "https://www.zaproxy.org",
                "description": "The world's most popular free web security scanner.",
                "tags": ["dast", "scanner", "flagship"],
                "admin_tokens": "sensitive_admin_data_123"
            },
            "juiceshop": {
                "name": "OWASP Juice Shop",
                "leader": "Björn Kimminich",
                "url": "https://owasp-juice.shop",
                "description": "Probably the most modern and insecure web application.",
                "tags": ["training", "vulnerable", "flagship"],
                "admin_tokens": "sensitive_admin_data_456"
            }
        }

    def get_project_details(self, key: str) -> Optional[ProjectPublicDTO]:
        """
        Retrieves project details by key.
        """
        if not key:
            return None
            
        raw_data = self._db_mock.get(key.lower())
        
        if not raw_data:
            return None

        return ProjectPublicDTO(
            name=html.escape(raw_data["name"]),
            leader=html.escape(raw_data["leader"]),
            url=raw_data["url"], # already gets validated
            description=html.escape(raw_data["description"]),
            tags=[html.escape(tag) for tag in raw_data["tags"]]
        )