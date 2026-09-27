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

HINDI_CITY_MAP: Dict[str, str] = {
    "दिल्ली": "Delhi",
    "कानपुर": "Kanpur",
    "मुंबई": "Mumbai",
    "बंबई": "Mumbai",
    "बेंगलुरु": "Bengaluru",
    "बैंगलोर": "Bengaluru",
    "कोलकाता": "Kolkata",
    "कलकत्ता": "Kolkata",
    "चेन्नई": "Chennai",
    "मद्रास": "Chennai",
    "हैदराबाद": "Hyderabad",
    "अहमदाबाद": "Ahmedabad",
    "लखनऊ": "Lucknow",
    "पटना": "Patna",
    "जयपुर": "Jaipur",
    "पुणे": "Pune",
    "चंडीगढ़": "Chandigarh",
    "भोपाल": "Bhopal",
    "गुरुग्राम": "Gurugram",
    "गुडगांव": "Gurugram",
    "गुडगाँव": "Gurugram",
    "नोएडा": "Noida",
    "अमृतसर": "Amritsar",
    "वाराणसी": "Varanasi",
    "बनारस": "Varanasi",
    "काशी": "Varanasi",
    "आगरा": "Agra",
    "कोयंबटूर": "Coimbatore",
    "कोच्चि": "Kochi",
    "गुवाहाटी": "Guwahati",
    "शिलांग": "Shillong",
    "आइजोल": "Aizawl",
}

HEALTH_CONDITIONS = [
    "asthma", "copd", "bronchitis", "heart disease", "cardiovascular",
    "blood pressure", "allergy", "pregnant", "pregnancy", "elderly", "child"
]

HINDI_HEALTH_MAP: Dict[str, str] = {
    "दमा": "asthma",
    "अस्थमा": "asthma",
    "सांस": "asthma",
    "सांस की बीमारी": "asthma",
    "हृदय": "heart disease",
    "दिल": "heart disease",
    "एलर्जी": "allergy",
    "बुजुर्ग": "elderly",
    "वृद्ध": "elderly",
    "बच्चे": "child",
    "बच्चा": "child",
    "गर्भवती": "pregnant",
}

HINDI_ACTIVITY_MAP: Dict[str, str] = {
    "दौड़ना": "running",
    "दौड़": "running",
    "भागना": "running",
    "टहलना": "morning walk",
    "घूमना": "morning walk",
    "सैर": "morning walk",
    "व्यायाम": "exercise",
    "कसरत": "exercise",
    "साइकिल": "cycling",
}


class SessionMemory:
    """Stores conversation turns and extracts persistent user context."""

    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.entities: Dict[str, Any] = {
            "current_location": None,
            "all_locations": [],
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

        # Extract all known cities ordered by their appearance position in the text
        city_matches = []
        for city in KNOWN_CITIES:
            # Match whole words to avoid false substrings
            match = re.search(rf"\b{city}\b", lower_text)
            if match:
                city_matches.append((match.start(), city.title()))

        # Match Hindi / Devanagari city names
        for hindi_name, canonical in HINDI_CITY_MAP.items():
            if hindi_name in text:
                pos = text.find(hindi_name)
                city_matches.append((pos, canonical))

        if city_matches:
            city_matches.sort(key=lambda item: item[0])
            ordered_cities: List[str] = []
            for _, city_title in city_matches:
                if city_title not in ordered_cities:
                    ordered_cities.append(city_title)
            self.entities["all_locations"] = ordered_cities
            self.entities["current_location"] = ordered_cities[0]
        else:
            # Check for location phrases like "in <City>", "at <City>", "near <City>"
            loc_match = re.search(r"\b(?:in|at|near|for|around)\s+([A-Z][a-zA-Z]+)", text)
            if loc_match and not self.entities["current_location"]:
                candidate = loc_match.group(1).title()
                if candidate.lower() not in ["the", "my", "today", "tomorrow", "morning", "evening"]:
                    self.entities["current_location"] = candidate
                    self.entities["all_locations"] = [candidate]
            elif self.entities["current_location"]:
                self.entities["all_locations"] = [self.entities["current_location"]]

        # Extract health conditions (English and Hindi)
        for cond in HEALTH_CONDITIONS:
            if cond in lower_text and cond not in self.entities["health_conditions"]:
                self.entities["health_conditions"].append(cond)

        for hindi_cond, canonical in HINDI_HEALTH_MAP.items():
            if hindi_cond in text and canonical not in self.entities["health_conditions"]:
                self.entities["health_conditions"].append(canonical)

        # Extract activities (English and Hindi)
        for act in ["running", "jogging", "cycling", "morning walk", "exercise", "marathon"]:
            if act in lower_text and act not in self.entities["preferred_activities"]:
                self.entities["preferred_activities"].append(act)

        for hindi_act, canonical in HINDI_ACTIVITY_MAP.items():
            if hindi_act in text and canonical not in self.entities["preferred_activities"]:
                self.entities["preferred_activities"].append(canonical)

    def get_location(self) -> Optional[str]:
        """Get the active location context."""
        return self.entities.get("current_location")

    def set_location(self, location: str):
        """Explicitly set or override location."""
        self.entities["current_location"] = location.title()
        self.entities["all_locations"] = [location.title()]

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve recent message history formatted for LLM context."""
        return self.messages[-limit:]

    def clear(self):
        """Reset conversation and entities."""
        self.messages.clear()
        self.entities = {
            "current_location": None,
            "all_locations": [],
            "health_conditions": [],
            "preferred_activities": [],
            "last_tool_outputs": {}
        }
