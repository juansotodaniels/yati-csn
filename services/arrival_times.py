import math
from typing import List, Dict


VP_KM_S = 6.0
VS_KM_S = 3.5
DEFAULT_ALERT_LATENCY_S = 8.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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


def hypocentral_distance_km(epicentral_km: float, depth_km: float) -> float:
    return math.sqrt(epicentral_km**2 + depth_km**2)


def estimate_arrival_times(
    event_lat: float,
    event_lon: float,
    depth_km: float,
    localities: List[Dict],
    alert_latency_s: float = DEFAULT_ALERT_LATENCY_S
) -> List[Dict]:
    results = []

    for locality in localities:
        lat_loc = float(locality["lat"])
        lon_loc = float(locality["lon"])

        epicentral_km = haversine_km(event_lat, event_lon, lat_loc, lon_loc)
        hypo_km = hypocentral_distance_km(epicentral_km, depth_km)

        t_p = hypo_km / VP_KM_S
        t_s = hypo_km / VS_KM_S
        warning_time = t_s - alert_latency_s

        results.append({
            "locality": locality["name"],
            "epicentral_distance_km": round(epicentral_km, 1),
            "hypocentral_distance_km": round(hypo_km, 1),
            "p_arrival_s": round(t_p, 1),
            "s_arrival_s": round(t_s, 1),
            "warning_time_s": round(warning_time, 1)
        })

    return results
