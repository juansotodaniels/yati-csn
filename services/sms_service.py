from typing import List, Dict

from app.config import SMS_ENABLED


def build_prealert_message(event: Dict, intensities: List[Dict]) -> str:
    top = intensities[:3]
    intensity_text = ", ".join(f"{item['locality']}({item['intensity']})" for item in top)

    return (
        f"YATI PRE M{event['magnitude']:.1f} | "
        f"{event['origin_time']} | "
        f"{event.get('place') or 'Preliminar'} | "
        f"{intensity_text} | "
        f"Fuente {event['source']}"
    )


def send_prealert_sms(event: Dict, intensities: List[Dict]) -> Dict:
    message = build_prealert_message(event, intensities)

    if not SMS_ENABLED:
        return {
            "sent": False,
            "reason": "SMS deshabilitado en configuración",
            "message": message
        }

    return {
        "sent": True,
        "reason": "Simulación de envío",
        "message": message
    }
