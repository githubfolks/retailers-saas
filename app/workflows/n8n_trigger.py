import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.logger import request_logger


def trigger_n8n_workflow(
    webhook_url: str,
    event_type: str,
    event_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Trigger an n8n workflow via webhook.
    
    Args:
        webhook_url: n8n webhook URL
        event_type: Type of event (e.g., 'order_created', 'payment_completed')
        event_data: Event payload data
    
    Returns:
        Response from n8n or None on error
    """
    try:
        payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": event_data
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code not in [200, 201, 202]:
            request_logger.error(
                f"n8n webhook error: Status {response.status_code}, {response.text}"
            )
            return None
        
        request_logger.info(
            f"n8n workflow triggered: {event_type}"
        )
        
        return {
            "status": "triggered",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    except requests.exceptions.Timeout:
        request_logger.error("n8n webhook request timed out")
        return None
    except requests.exceptions.RequestException as e:
        request_logger.error(f"n8n webhook request error: {str(e)}")
        return None
    except Exception as e:
        request_logger.error(f"Error triggering n8n workflow: {str(e)}")
        return None


def trigger_order_created_event(
    tenant_id: str,
    order_id: int,
    customer_mobile: str,
    product_name: str,
    quantity: int,
    amount: float,
    webhook_url: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow for order creation event.
    """
    event_data = {
        "tenant_id": tenant_id,
        "order_id": order_id,
        "customer_mobile": customer_mobile,
        "product_name": product_name,
        "quantity": quantity,
        "amount": amount,
    }
    
    return trigger_n8n_workflow(webhook_url, "order_created", event_data)


def trigger_payment_completed_event(
    tenant_id: str,
    order_id: int,
    payment_id: str,
    customer_mobile: str,
    amount: float,
    webhook_url: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow for payment completion event.
    """
    event_data = {
        "tenant_id": tenant_id,
        "order_id": order_id,
        "payment_id": payment_id,
        "customer_mobile": customer_mobile,
        "amount": amount,
        "status": "completed",
    }
    
    return trigger_n8n_workflow(webhook_url, "payment_completed", event_data)


def trigger_payment_failed_event(
    tenant_id: str,
    order_id: int,
    customer_mobile: str,
    amount: float,
    reason: str,
    webhook_url: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow for payment failure event.
    """
    event_data = {
        "tenant_id": tenant_id,
        "order_id": order_id,
        "customer_mobile": customer_mobile,
        "amount": amount,
        "status": "failed",
        "reason": reason,
    }
    
    return trigger_n8n_workflow(webhook_url, "payment_failed", event_data)


def trigger_customer_created_event(
    tenant_id: str,
    customer_id: int,
    customer_mobile: str,
    customer_name: str,
    email: Optional[str] = None,
    webhook_url: str = None
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow for customer creation event.
    """
    event_data = {
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "customer_mobile": customer_mobile,
        "customer_name": customer_name,
        "email": email,
    }
    
    return trigger_n8n_workflow(webhook_url, "customer_created", event_data)


def trigger_conversation_started_event(
    tenant_id: str,
    customer_mobile: str,
    customer_name: str,
    webhook_url: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow for conversation start event.
    """
    event_data = {
        "tenant_id": tenant_id,
        "customer_mobile": customer_mobile,
        "customer_name": customer_name,
    }
    
    return trigger_n8n_workflow(webhook_url, "conversation_started", event_data)


def trigger_conversation_ended_event(
    tenant_id: str,
    customer_mobile: str,
    conversation_duration: int,
    webhook_url: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow for conversation end event.
    """
    event_data = {
        "tenant_id": tenant_id,
        "customer_mobile": customer_mobile,
        "conversation_duration": conversation_duration,
    }
    
    return trigger_n8n_workflow(webhook_url, "conversation_ended", event_data)


def trigger_custom_event(
    tenant_id: str,
    event_name: str,
    custom_data: Dict[str, Any],
    webhook_url: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger n8n workflow with custom event data.
    """
    event_data = {
        "tenant_id": tenant_id,
        **custom_data
    }
    
    return trigger_n8n_workflow(webhook_url, event_name, event_data)
