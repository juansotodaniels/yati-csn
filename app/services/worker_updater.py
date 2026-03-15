from typing import Dict, List

from app.config import WORKER_UPDATE_ENABLED


def update_worker_preliminary(event: Dict, intensities: List[Dict]) -> Dict:
    if not WORKER_UPDATE_ENABLED:
        return {
            "updated": False,
            "reason": "Actualización de worker deshabilitada"
        }

    return {
        "updated": True,
        "reason": "Simulación de actualización de worker",
        "event": event,
        "intensities": intensities
    }
