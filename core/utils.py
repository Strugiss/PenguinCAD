"""PenguinCAD core - utility (estratte da penguincad.py)."""
import json
import numpy as np

# --- UTILITY: NumpyEncoder ---
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.ndarray, np.integer, np.floating)):
            return obj.tolist()
        return super().default(obj)
