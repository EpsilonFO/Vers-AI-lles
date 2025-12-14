"""Reservation memory model for tracking visit planning state."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ReservationPlan(BaseModel):
    """Complete reservation plan model matching the prompt template."""

    # Basic visit information
    date: Optional[str] = Field(None, description="Date souhaitée pour la visite")
    participants: Optional[int] = Field(None, description="Nombre de participants")
    type_billet: Optional[str] = Field(
        None,
        description="Type de billet (simple/combiné/visite guidée/visite spéciale)",
    )
    horaire: Optional[str] = Field(None, description="Horaire préféré")

    # Special options
    options_speciales: List[str] = Field(
        default_factory=list, description="Réductions, handicap, repas, allergies"
    )

    # Transportation
    transport_info: Optional[str] = Field(
        None, description="Mode de transport et itinéraire"
    )
    parking_info: Optional[str] = Field(
        None, description="Besoin de parking ou dépôt de bagages"
    )

    # Accommodation
    accommodation: Optional[str] = Field(None, description="Logement éventuel")

    # Maps and navigation
    itinerary_maps: Optional[str] = Field(
        None, description="Lien Google Maps pour le trajet"
    )

    # Weather
    weather_info: Optional[str] = Field(None, description="Météo prévue ou souhaitée")

    # Additional notes
    notes_utilisateur: Optional[str] = Field(
        None, description="Toutes informations supplémentaires importantes"
    )

    # Metadata
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    updated_at: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    status: str = Field(
        default="in_progress", description="Status: in_progress, completed, confirmed"
    )

    def get_missing_slots(self) -> List[str]:
        """Get list of missing required slots."""
        missing = []
        required_fields = ["date", "participants", "type_billet", "horaire"]

        for field in required_fields:
            if getattr(self, field) is None:
                missing.append(field)

        return missing

    def get_completion_percentage(self) -> float:
        """Calculate completion percentage of the reservation."""
        all_fields = [
            "date",
            "participants",
            "type_billet",
            "horaire",
            "transport_info",
            "parking_info",
            "accommodation",
            "itinerary_maps",
            "weather_info",
        ]

        filled = sum(1 for field in all_fields if getattr(self, field) is not None)
        return (filled / len(all_fields)) * 100

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return len(self.get_missing_slots()) == 0

    def to_summary(self) -> str:
        """Generate a human-readable summary of the reservation."""
        summary_parts = []

        if self.date:
            summary_parts.append(f"📅 Date: {self.date}")
        if self.horaire:
            summary_parts.append(f"🕐 Horaire: {self.horaire}")
        if self.participants:
            summary_parts.append(f"👥 Participants: {self.participants}")
        if self.type_billet:
            summary_parts.append(f"🎫 Type de billet: {self.type_billet}")
        if self.options_speciales:
            summary_parts.append(f"⭐ Options: {', '.join(self.options_speciales)}")
        if self.transport_info:
            summary_parts.append(f"🚗 Transport: {self.transport_info}")
        if self.parking_info:
            summary_parts.append(f"🅿️ Parking: {self.parking_info}")
        if self.accommodation:
            summary_parts.append(f"🏨 Logement: {self.accommodation}")
        if self.weather_info:
            summary_parts.append(f"🌤️ Météo: {self.weather_info}")
        if self.notes_utilisateur:
            summary_parts.append(f"📝 Notes: {self.notes_utilisateur}")

        return (
            "\n".join(summary_parts)
            if summary_parts
            else "Aucune information collectée"
        )

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()


class ReservationState(BaseModel):
    """State management for the reservation conversation."""

    session_id: str
    reservation_plan: ReservationPlan = Field(default_factory=ReservationPlan)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: str = Field(
        default="greeting", description="Current step in the conversation flow"
    )

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

    def get_next_question(self) -> Optional[str]:
        """Determine the next question to ask based on missing slots."""
        missing_slots = self.reservation_plan.get_missing_slots()

        questions = {
            "date": "Pour quelle date souhaitez-vous visiter le château de Versailles ?",
            "participants": "Combien de personnes participeront à la visite ?",
            "type_billet": "Quel type de billet souhaitez-vous ? (billet simple, passeport, visite guidée)",
            "horaire": "À quelle heure préférez-vous commencer votre visite ?",
        }

        if missing_slots:
            return questions.get(missing_slots[0])

        return None
