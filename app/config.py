import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "YATI")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MIN_EVENT_MAGNITUDE = float(os.getenv("MIN_EVENT_MAGNITUDE", "4.0"))

STATE_FILE = os.getenv("STATE_FILE", "state/events.json")
MODEL_PATH = os.getenv("MODEL_PATH", "models/Sismos_RF_joblib_Ene_2026.pkl")

SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"
WORKER_UPDATE_ENABLED = os.getenv("WORKER_UPDATE_ENABLED", "false").lower() == "true"
CSN_MONITOR_ENABLED = os.getenv("CSN_MONITOR_ENABLED", "false").lower() == "true"
