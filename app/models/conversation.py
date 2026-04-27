from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from app.core.database import Base
from datetime import datetime


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    mobile = Column(String, index=True)
    
    # State tracking
    current_state = Column(String, default="IDLE") # IDLE, AWAITING_QTY, CONFIRMING_ORDER
    current_intent = Column(String, nullable=True)
    
    # Context data
    selected_product_id = Column(Integer, nullable=True)
    selected_sku = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    context = Column(JSON, default={}) # For flexible state data
    
    # Timestamps
    last_message_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
