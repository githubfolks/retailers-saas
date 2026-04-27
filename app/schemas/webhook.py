from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class TextMessage(BaseModel):
    body: str


class MessageData(BaseModel):
    from_: str = None
    id: str
    timestamp: str
    type: str
    text: Optional[TextMessage] = None


class Contact(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    wa_id: str


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class MessageValue(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[MessageData]] = None
    statuses: Optional[List[Dict[str, Any]]] = None


class Change(BaseModel):
    field: str
    value: MessageValue


class Entry(BaseModel):
    id: str
    changes: List[Change]


class WebhookPayload(BaseModel):
    object: str
    entry: List[Entry]
