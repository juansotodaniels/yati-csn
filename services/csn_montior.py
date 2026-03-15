import math
from typing import Dict, Optional
from datetime import datetime

from app.services.event_memory import get_latest_event, set_latest_event
from app.services.intensity_engine import estimate_intensities


TIME_THRESHOLD_S = 60
DIST_THRESHOLD_KM = 50
MAG_THRESHOLD = 1.0


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


def time_difference_seconds(t1: str, t2: str) -> float:
    dt1 = datetime.fromisoformat(t1.replace("Z", ""))
    dt2 = datetime.fromisoformat(t2.replace("Z", ""))

    return abs((dt1 - dt2).total_seconds())


def is_same_event(pre_event: Dict, csn_event: Dict) -> bool:

    time_diff = time_difference_seconds(
        pre_event["origin_time"],
        csn_event["origin_time"]
    )

    if time_diff > TIME_THRESHOLD_S:
        return False

    dist = haversine_km(
        pre_event["latitude"],
        pre_event["longitude"],
        csn_event["latitude"],
        csn_event["longitude"]
    )

    if dist > DIST_THRESHOLD_KM:
        return False

    mag_diff = abs(pre_event["magnitude"] - csn_event["magnitude"])

    if mag_diff > MAG_THRESHOLD:
        return False

    return True


def process_csn_event(csn_event: Dict) -> Dict:

    latest = get_latest_event()

    if latest is None:
        return {
            "matched": False,
            "reason": "no PRE event stored"
        }

    pre_event = latest["event"]

    if not is_same_event(pre_event, csn_event):
        return {
            "matched": False,
            "reason": "events do not match"
        }

    intensities = estimate_intensities(
        latitude=csn_event["latitude"],
        longitude=csn_event["longitude"],
        depth_km=csn_event["depth_km"],
        magnitude=csn_event["magnitude"]
    )

    updated_event = {
        "event": csn_event,
        "intensities": intensities,
        "status": "CONF"
    }

    set_latest_event(updated_event)

    return {
        "matched": True,
        "status": "CONF",
        "event": csn_event
    }


def start_csn_confirmation_monitor(event: Dict) -> Dict:
    """
    Placeholder para futuro monitoreo automático de CSN.
    """
    return {
        "started": False,
        "reason": "CSN monitor not implemented yet"
    }
