"""
Conversational Session Memory.
Maintains dialogue history and extracts persistent conversational entities
such as user location, health conditions, and activity context across turns.
"""

import re
from typing import Any, Dict, List, Optional

KNOWN_CITIES = [
    "kanpur", "delhi", "mumbai", "bengaluru", "bangalore", "kolkata", "chennai",
    "hyderabad", "ahmedabad", "lucknow", "patna", "jaipur", "pune", "chandigarh",
    "bhopal", "gurugram", "gurgaon", "noida", "amritsar", "varanasi", "agra",
    "coimbatore", "kochi", "guwahati", "aizawl", "shillong"
]

HEALTH_CONDITIONS = [
    "asthma", "copd", "bronchitis", "heart disease", "cardiovascular",
    "blood pressure", "allergy", "pregnant", "pregnancy", "elderly", "child"
]


class SessionMemory:
    """Stores conversation turns and extracts persistent user context."""

    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.entities: Dict[str, Any] = {
            "current_location": None,
            "health_conditions": [],
            "preferred_activities": [],
            "last_tool_outputs": {}
        }

    def add_message(self, role: str, content: str):
        """Append a message to the history and update context."""
        self.messages.append({"role": role, "content": content})
        if role == "user":
            self._update_entities_from_text(content)

    def _update_entities_from_text(self, text: str):
        """Extract location and health profile mentions from user utterance."""
        lower_text = text.lower()

        # Extract location
        for city in KNOWN_CITIES:
            # Match whole words to avoid false substrings
            if re.search(rf"\b{city}\b", lower_text):
                self.entities["current_location"] = city.title()
                break

        # Check for location phrases like "in <City>", "at <City>", "near <City>"
        loc_match = re.search(r"\b(?:in|at|near|for|around)\s+([A-Z][a-zA-Z]+)", text)
        if loc_match and not self.entities["current_location"]:
            candidate = loc_match.group(1).title()
            if candidate.lower() not in ["the", "my", "today", "tomorrow", "morning", "evening"]:
                self.entities["current_location"] = candidate

        # Extract health conditions
        for cond in HEALTH_CONDITIONS:
            if cond in lower_text and cond not in self.entities["health_conditions"]:
                self.entities["health_conditions"].append(cond)

        # Extract activities
        for act in ["running", "jogging", "cycling", "morning walk", "exercise", "marathon"]:
            if act in lower_text and act not in self.entities["preferred_activities"]:
                self.entities["preferred_activities"].append(act)

    def get_location(self) -> Optional[str]:
        """Get the active location context."""
        return self.entities.get("current_location")

    def set_location(self, location: str):
        """Explicitly set or override location."""
        self.entities["current_location"] = location.title()

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve recent message history formatted for LLM context."""
        return self.messages[-limit:]

    def clear(self):
        """Reset conversation and entities."""
        self.messages.clear()
        self.entities = {
            "current_location": None,
            "health_conditions": [],
            "preferred_activities": [],
            "last_tool_outputs": {}
        }
