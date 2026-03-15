from fastapi import APIRouter
from app.models.schemas import SeismicEvent, PreliminaryEventResponse
from app.services.event_memory import get_latest_event, set_latest_event
from app.services.intensity_engine import (
    estimate_intensities,
    get_localities_for_processing,
)
from app.services.arrival_times import estimate_arrival_times
from app.services.sms_service import send_prealert_sms
from app.services.worker_updater import update_worker_preliminary
from app.services.csn_monitor import (
    start_csn_confirmation_monitor,
    process_csn_event,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "YATI"}


@router.get("/event/latest")
def event_latest():
    latest = get_latest_event()

    if latest is None:
        return {
            "status": "ok",
            "latest_event": None
        }

    intensities = latest.get("intensities", [])
    top_with_arrivals = latest.get("top_with_arrivals", [])

    return {
        "status": "ok",
        "latest_event": {
            "event": latest.get("event"),
            "status": latest.get("status"),
            "top_intensities": intensities[:20],
            "top_with_arrivals": top_with_arrivals[:20],
            "total_localities": len(intensities)
        }
    }


@router.get("/event/latest/full")
def event_latest_full():
    latest = get_latest_event()
    return {
        "status": "ok",
        "latest_event": latest
    }


@router.post("/event/preliminary", response_model=PreliminaryEventResponse)
def event_preliminary(event: SeismicEvent):
    event_dict = event.model_dump()

    intensities = estimate_intensities(
        latitude=event.latitude,
        longitude=event.longitude,
        depth_km=event.depth_km,
        magnitude=event.magnitude
    )

    localities = get_localities_for_processing()

    arrivals = estimate_arrival_times(
        event_lat=event.latitude,
        event_lon=event.longitude,
        depth_km=event.depth_km,
        localities=localities
    )

    arrival_map = {item["locality"]: item for item in arrivals}

    top_combined = []
    for item in intensities[:20]:
        locality = item["locality"]
        top_combined.append({
            "locality": locality,
            "intensity": item["intensity"],
            "arrival": arrival_map.get(locality)
        })

    set_latest_event({
        "event": event_dict,
        "intensities": intensities,
        "top_with_arrivals": top_combined,
        "status": "PRE"
    })

    sms_result = send_prealert_sms(event_dict, intensities)
    worker_result = update_worker_preliminary(event_dict, intensities)
    csn_result = start_csn_confirmation_monitor(event_dict)

    return {
        "status": "ok",
        "message": "Evento preliminar procesado",
        "event": event_dict,
        "intensities": intensities,
        "metadata": {
            "top_with_arrivals": top_combined,
            "sms": sms_result,
            "worker": worker_result,
            "csn_monitor": csn_result
        }
    }


@router.post("/event/confirm")
def event_confirm(event: SeismicEvent):
    event_dict = event.model_dump()

    result = process_csn_event(event_dict)

    if not result["matched"]:
        return {
            "status": "ignored",
            "reason": result["reason"]
        }

    return {
        "status": "ok",
        "message": "Evento confirmado por CSN",
        "event": result["event"]
    }


@router.get("/")
def root():
    return {
        "message": "YATI operativo",
        "docs": "/docs"
    }
