from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AircraftUpdate(BaseModel):
    """Partial update from a single SBS message."""

    icao_hex: str
    callsign: str | None = None
    altitude_ft: int | None = None
    ground_speed_kt: float | None = None
    track_deg: float | None = None
    lat: float | None = None
    lon: float | None = None
    vertical_rate: int | None = None
    squawk: str | None = None
    is_on_ground: bool | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Aircraft(BaseModel):
    """Full aircraft state, merged from multiple SBS messages."""

    icao_hex: str
    callsign: str = ""
    altitude_ft: int | None = None
    ground_speed_kt: float | None = None
    track_deg: float | None = None
    lat: float | None = None
    lon: float | None = None
    vertical_rate: int | None = None
    squawk: str | None = None
    is_on_ground: bool = False
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    distance_nm: float | None = None

    def apply_update(self, update: AircraftUpdate) -> None:
        """Merge a partial update into this aircraft state."""
        if update.callsign:
            self.callsign = update.callsign.strip()
        if update.altitude_ft is not None:
            self.altitude_ft = update.altitude_ft
        if update.ground_speed_kt is not None:
            self.ground_speed_kt = update.ground_speed_kt
        if update.track_deg is not None:
            self.track_deg = update.track_deg
        if update.lat is not None:
            self.lat = update.lat
        if update.lon is not None:
            self.lon = update.lon
        if update.vertical_rate is not None:
            self.vertical_rate = update.vertical_rate
        if update.squawk is not None:
            self.squawk = update.squawk
        if update.is_on_ground is not None:
            self.is_on_ground = update.is_on_ground
        self.last_seen = update.timestamp
        self.message_count += 1
