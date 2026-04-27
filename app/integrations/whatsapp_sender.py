import requests
import json
from typing import Optional, Dict, Any
from app.core.logger import request_logger


def send_whatsapp_message(
    recipient_number: str,
    message_text: str,
    phone_number_id: str,
    whatsapp_token: str
) -> Optional[Dict[str, Any]]:
    """
    Send a WhatsApp message via Cloud API.
    
    Args:
        recipient_number: Recipient phone number with country code (e.g., 919876543210)
        message_text: Message text to send
        phone_number_id: WhatsApp phone number ID from Cloud API
        whatsapp_token: WhatsApp API token
    
    Returns:
        Response from WhatsApp API or None on error
    """
    try:
        url = f"https://graph.instagram.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_number,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code not in [200, 201]:
            error_detail = response.text
            request_logger.error(
                f"WhatsApp API error: Status {response.status_code}, {error_detail}"
            )
            return None
        
        data = response.json()
        
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
        }
    
    except requests.exceptions.Timeout:
        request_logger.error("WhatsApp API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        request_logger.error(f"WhatsApp API request error: {str(e)}")
        return None
    except Exception as e:
        request_logger.error(f"Error sending WhatsApp message: {str(e)}")
        return None


def send_template_message(
    recipient_number: str,
    template_name: str,
    template_language: str,
    parameters: Optional[list] = None,
    phone_number_id: str = None,
    whatsapp_token: str = None
) -> Optional[Dict[str, Any]]:
    """
    Send a WhatsApp template message via Cloud API.
    
    Args:
        recipient_number: Recipient phone number with country code
        template_name: WhatsApp template name
        template_language: Template language code (e.g., 'en_US')
        parameters: List of parameter values for the template
        phone_number_id: WhatsApp phone number ID
        whatsapp_token: WhatsApp API token
    
    Returns:
        Response from WhatsApp API or None on error
    """
    try:
        url = f"https://graph.instagram.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        template_body = {
            "name": template_name,
            "language": {
                "code": template_language
            }
        }
        
        if parameters:
            template_body["parameters"] = [{"type": "text", "text": param} for param in parameters]
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "template",
            "template": template_body
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code not in [200, 201]:
            error_detail = response.text
            request_logger.error(
                f"WhatsApp template API error: Status {response.status_code}, {error_detail}"
            )
            return None
        
        data = response.json()
        
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
            "template": template_name,
        }
    
    except Exception as e:
        request_logger.error(f"Error sending WhatsApp template: {str(e)}")
        return None


def send_media_message(
    recipient_number: str,
    media_url: str,
    media_type: str,
    caption: Optional[str] = None,
    phone_number_id: str = None,
    whatsapp_token: str = None
) -> Optional[Dict[str, Any]]:
    """
    Send a WhatsApp media message (image, video, audio, document).
    
    Args:
        recipient_number: Recipient phone number with country code
        media_url: URL of the media file
        media_type: Type of media ('image', 'video', 'audio', 'document')
        caption: Optional caption for the media
        phone_number_id: WhatsApp phone number ID
        whatsapp_token: WhatsApp API token
    
    Returns:
        Response from WhatsApp API or None on error
    """
    try:
        valid_types = ["image", "video", "audio", "document"]
        if media_type not in valid_types:
            request_logger.error(f"Invalid media type: {media_type}")
            return None
        
        url = f"https://graph.instagram.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        media_payload = {
            "link": media_url
        }
        
        if caption and media_type in ["image", "video"]:
            media_payload["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_number,
            "type": media_type,
            media_type: media_payload
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code not in [200, 201]:
            request_logger.error(
                f"WhatsApp media API error: Status {response.status_code}, {response.text}"
            )
            return None
        
        data = response.json()
        
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
            "media_type": media_type,
        }
    
    except Exception as e:
        request_logger.error(f"Error sending WhatsApp media: {str(e)}")
        return None
