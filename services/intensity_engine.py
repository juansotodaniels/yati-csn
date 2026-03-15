import joblib
import math
import os
import pandas as pd
from typing import List, Dict

from app.config import MODEL_PATH

model = None
localities_df = None

LOCALITIES_FILE = "data/Localidades_Enero_2026_con_coords.csv"


def load_model():
    global model

    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Modelo no encontrado: {MODEL_PATH}")

        model = joblib.load(MODEL_PATH)
        print(f"Modelo cargado: {MODEL_PATH}")

    return model


def load_localities():
    global localities_df

    if localities_df is None:
        if not os.path.exists(LOCALITIES_FILE):
            raise FileNotFoundError(
                f"Archivo de localidades no encontrado: {LOCALITIES_FILE}"
            )

        try:
            localities_df = pd.read_csv(LOCALITIES_FILE)
        except Exception:
            localities_df = pd.read_csv(LOCALITIES_FILE, sep=";")

        print("Columnas CSV:", list(localities_df.columns))
        print(f"Localidades cargadas: {len(localities_df)}")

        required = ["Localidad", "Latitud", "Longitud"]
        for col in required:
            if col not in localities_df.columns:
                raise KeyError(
                    f"No se encontró la columna '{col}' en el CSV. Columnas disponibles: {list(localities_df.columns)}"
                )

        localities_df["Latitud"] = (
            localities_df["Latitud"].astype(str).str.replace(",", ".", regex=False)
        )
        localities_df["Longitud"] = (
            localities_df["Longitud"].astype(str).str.replace(",", ".", regex=False)
        )

        localities_df["Latitud"] = pd.to_numeric(
            localities_df["Latitud"], errors="coerce"
        )
        localities_df["Longitud"] = pd.to_numeric(
            localities_df["Longitud"], errors="coerce"
        )

        localities_df = localities_df.dropna(
            subset=["Latitud", "Longitud", "Localidad"]
        ).copy()

        print(f"Localidades válidas tras limpieza: {len(localities_df)}")

    return localities_df


def get_localities_for_processing() -> List[Dict]:
    df = load_localities()

    localities = []
    for _, row in df.iterrows():
        localities.append({
            "name": str(row["Localidad"]),
            "lat": float(row["Latitud"]),
            "lon": float(row["Longitud"])
        })

    return localities


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


def estimate_intensities(
    latitude: float,
    longitude: float,
    depth_km: float,
    magnitude: float
) -> List[Dict]:
    model = load_model()
    df = load_localities()

    X = []
    locality_names = []

    for _, row in df.iterrows():
        lat_loc = float(row["Latitud"])
        lon_loc = float(row["Longitud"])

        distancia = haversine_km(latitude, longitude, lat_loc, lon_loc)

        features = [
            float(latitude),   # Latitud_sismo
            float(longitude),  # Longitud_sismo
            float(depth_km),   # Profundidad
            float(magnitude),  # magnitud
            lat_loc,           # Latitud_localidad
            lon_loc,           # Longitud_localidad
            float(distancia)   # distancia_epicentro
        ]

        X.append(features)
        locality_names.append(str(row["Localidad"]))

    print(f"Cantidad de filas para predicción: {len(X)}")
    if len(X) > 0:
        print("Primera fila X:", X[0])

    predictions = model.predict(X)
    print(f"Cantidad de predicciones: {len(predictions)}")

    intensities = []

    for locality, value in zip(locality_names, predictions):
        intensities.append({
            "locality": locality,
            "intensity": round(float(value), 2)
        })

    intensities.sort(key=lambda x: x["intensity"], reverse=True)

    return intensities
