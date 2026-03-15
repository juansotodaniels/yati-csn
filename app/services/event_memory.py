import json
import os
from typing import Any, Dict, Optional

from app.config import STATE_FILE


def ensure_state_file() -> None:
    directory = os.path.dirname(STATE_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"latest_event": None}, f, ensure_ascii=False, indent=2)


def load_state() -> Dict[str, Any]:
    ensure_state_file()

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict[str, Any]) -> None:
    ensure_state_file()

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_latest_event() -> Optional[Dict[str, Any]]:
    state = load_state()
    return state.get("latest_event")


def set_latest_event(event: Dict[str, Any]) -> None:
    state = load_state()
    state["latest_event"] = event
    save_state(state)
