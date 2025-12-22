"""Service layer for handling project-related AI queries."""

import logging

from apps.ai.core.dtos import AIQueryDTO, AIResponseDTO, RouterIntentDTO
from apps.ai.router.intent import IntentRouter
from apps.ai.services.static_handler import StaticService

logger = logging.getLogger(__name__)


class ProjectService:
    """Layer 2 Orchestrator: Decides between DB Lookup and LLM."""

    def __init__(self) -> None:
        """Initialize with Router and Static Handler."""
        self.router = IntentRouter()
        self.static_service = StaticService()
        self.CONFIDENCE_THRESHOLD = 0.65

    async def process_query(self, query: AIQueryDTO) -> AIResponseDTO:
        """Orchestrate flow: Router -> Static Service (DB) -> LLM."""
        intent_label = "dynamic"
        confidence = 0.0

        try:
            # DIRECT INTEGRATION: Your intent.py returns a Dict
            res = self.router.get_intent(query.text)

            # Robust extraction matching your Router's output structure
            if isinstance(res, dict):
                intent_label = res.get("intent", "DYNAMIC").lower()
                confidence = float(res.get("confidence", 0.0))
            else:
                intent_label = getattr(res, "intent", "DYNAMIC").lower()
                confidence = float(getattr(res, "confidence", 0.0))

        except Exception:
            logger.exception("Router failure - falling back to dynamic (fail-open)")

        # Normalize intent string
        is_static = intent_label.upper() == "STATIC"

        # 2. LAYER 2: Static Execution (Deterministic Path)
        if is_static:
            response = await self.static_service.execute(query.text, confidence)
            if response:
                return response

        # Ambiguity Check
        if confidence < self.CONFIDENCE_THRESHOLD and not is_static:
            return AIResponseDTO(
                answer=(
                    "I'm not sure if you want a specific fact or a general explanation. "
                    "Can you clarify?"
                ),
                source="system",
                intent=RouterIntentDTO(label=intent_label, confidence=confidence),
            )

        # 3. LAYER 3: Hybrid Retrieval (The Fallback)
        return self._execute_hybrid_retrieval(intent_label, confidence)

    def _execute_hybrid_retrieval(self, label: str, conf: float) -> AIResponseDTO:
        """Fallback to LLM/RAG (Layer 3) if static lookup fails."""
        return AIResponseDTO(
            answer="[System] Switching to Hybrid LLM Retrieval.",
            source="hybrid_rag",
            intent=RouterIntentDTO(label=label, confidence=conf),
            show_manual_search_btn=True,
        )
