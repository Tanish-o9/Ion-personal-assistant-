from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class UIControlElement(BaseModel):
    id: str
    element_type: str # button, input, text, link, dropdown
    label: str
    is_allowed: bool = True

class ScreenState(BaseModel):
    application: str
    window_title: str
    visible_text: str
    detected_controls: List[UIControlElement] = Field(default_factory=list)
    timestamp: str

class ComputerActionRequest(BaseModel):
    session_id: str
    application: str
    action_type: str # read_screen, click_element, type_text, scroll
    target_element_id: Optional[str] = None
    input_text: Optional[str] = None

class ComputerActionResult(BaseModel):
    success: bool
    action_type: str
    risk_level: str = "low"
    resulting_state: Optional[ScreenState] = None
    error_message: Optional[str] = None

class ComputerSession(BaseModel):
    session_id: str
    user_id: str
    application: str
    target_url_or_window: str
    permissions: List[str] = Field(default_factory=list)
    status: str = "active"
