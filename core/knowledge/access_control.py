"""Knowledge access control."""

from __future__ import annotations

class KnowledgeAccessController:
    """
    Build retrieval filters from the authorized user.
    Knowledge records may contain user-specific information, therefore
    authorization information is converted into a metadata filter before
    retrieval.
    """

    def build_filter(self, user_id: int) -> dict[str, object]:
        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        return {"user_id": user_id}

    def authorize(self, user_id: int, metadata: dict) -> bool:
        if user_id <= 0:
            return False

        allowed_user_id = metadata.get("user_id")

        # Public Knowledge does not require a user-specific filter.
        if allowed_user_id is None:
            return True

        return allowed_user_id == user_id