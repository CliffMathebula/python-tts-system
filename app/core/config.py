import os
import torch
import sys

# --- DIRECTORY SETUP ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMP_DIR = os.path.join(BASE_DIR, "temp_audio")
SPEAKER_DIR = os.path.join(BASE_DIR, "speakers")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(SPEAKER_DIR, exist_ok=True)

# --- HARDWARE DETECTION ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- TRANSFORMERS COMPATIBILITY PATCH ---
try:
    import transformers.pytorch_utils
    if not hasattr(transformers.pytorch_utils, "isin_mps_friendly"):
        # We use *args and **kwargs to catch 'elements' and 'test_elements'
        def isin_mps_friendly(*args, **kwargs):
            # Internal logic: just use torch.isin if available, 
            # or return a dummy/False if logic isn't critical for CPU/CUDA
            return torch.isin(kwargs.get('elements'), kwargs.get('test_elements'))
            
        transformers.pytorch_utils.isin_mps_friendly = isin_mps_friendly
        print("🛠️ Robust Transformers v5.0 patch applied (Keyword args supported).")
except ImportError:
    pass