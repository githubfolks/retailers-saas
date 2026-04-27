from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.conversation import ConversationState
from app.core.database import get_session


def get_conversation(
    tenant_id: str,
    mobile: str,
    db: Optional[Session] = None
) -> Optional[ConversationState]:
    db = db or get_session()
    
    conversation = db.query(ConversationState).filter(
        ConversationState.tenant_id == tenant_id,
        ConversationState.mobile == mobile
    ).first()
    
    return conversation


def create_conversation(
    tenant_id: str,
    mobile: str,
    current_intent: Optional[str] = None,
    db: Optional[Session] = None
) -> ConversationState:
    db = db or get_session()
    
    conversation = ConversationState(
        tenant_id=tenant_id,
        mobile=mobile,
        current_intent=current_intent
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


def update_conversation_state(
    tenant_id: str,
    mobile: str,
    state_data: Dict[str, Any],
    db: Optional[Session] = None
) -> Optional[ConversationState]:
    db = db or get_session()
    
    conversation = db.query(ConversationState).filter(
        ConversationState.tenant_id == tenant_id,
        ConversationState.mobile == mobile
    ).first()
    
    if not conversation:
        return None
    
    for key, value in state_data.items():
        if hasattr(conversation, key):
            setattr(conversation, key, value)
    
    db.commit()
    db.refresh(conversation)
    
    return conversation
