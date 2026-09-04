"""
Phase 74: Localization & Internationalization Architecture
"""

from datetime import datetime, timezone
import zoneinfo
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LocalizedMessageCatalog(BaseModel):
    messages: Dict[str, Dict[str, str]] = Field(
        default_factory=lambda: {
            "en": {
                "welcome": "Welcome to JARVIS 4.0",
                "error_unauthorized": "Access denied: Unauthorized action.",
                "error_budget_exceeded": "Resource budget exceeded.",
                "status_ready": "JARVIS Platform Ready",
            },
            "hi": {
                "welcome": "जार्विस 4.0 में आपका स्वागत है",
                "error_unauthorized": "पहुंच से वंचित: अनधिकृत कार्रवाई।",
                "error_budget_exceeded": "संसाधन बजट पार हो गया।",
                "status_ready": "जार्विस प्लेटफॉर्म तैयार है",
            },
            "es": {
                "welcome": "Bienvenido a JARVIS 4.0",
                "error_unauthorized": "Acceso denegado: Acción no autorizada.",
                "error_budget_exceeded": "Presupuesto de recursos excedido.",
                "status_ready": "Plataforma JARVIS Lista",
            },
        }
    )

class LocalizationManager:
    """Manages internationalization, translations, error localization, and UTF-8 formatting."""
    def __init__(self):
        self.catalog = LocalizedMessageCatalog()

    def get_message(self, key: str, lang: str = "en") -> str:
        lang_dict = self.catalog.messages.get(lang, self.catalog.messages["en"])
        return lang_dict.get(key, self.catalog.messages["en"].get(key, key))

    def format_currency(self, amount: float, currency_code: str = "USD", locale: str = "en_US") -> str:
        symbol = "$" if currency_code == "USD" else ("₹" if currency_code == "INR" else "€")
        return f"{symbol}{amount:,.2f}"

    def format_timezone_datetime(self, utc_dt_iso: str, target_tz_name: str = "UTC") -> str:
        try:
            dt = datetime.fromisoformat(utc_dt_iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            tz = zoneinfo.ZoneInfo(target_tz_name)
            local_dt = dt.astimezone(tz)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception:
            return utc_dt_iso

default_localization_manager = LocalizationManager()
