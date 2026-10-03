"""
Loads the trained model (from ml/train.py) and predicts travel time.

Falls back to the plain distance/speed formula (same as algorithms/eta.py)
if no trained model exists yet — so the app never crashes just because
ml/train.py hasn't been run, it just won't be using the ML prediction yet.
"""

import os
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "eta_model.joblib")

_model = None
_model_loaded = False


def _get_model():
    global _model, _model_loaded
    if not _model_loaded:
        _model_loaded = True
        if os.path.exists(MODEL_PATH):
            import joblib
            _model = joblib.load(MODEL_PATH)
    return _model


def predict_travel_time_min(distance_km, avg_speed_kmph, when=None):
    """
    Returns predicted travel time in minutes. Uses the trained model if
    available, otherwise falls back to a plain distance/speed estimate.
    """
    when = when or datetime.now()
    model = _get_model()

    if model is not None:
        features = [[distance_km, avg_speed_kmph, when.hour, when.weekday()]]
        return round(float(model.predict(features)[0]), 1)

    # Fallback — same formula algorithms/eta.py uses when there's no model.
    return round((distance_km / avg_speed_kmph) * 60, 1)
