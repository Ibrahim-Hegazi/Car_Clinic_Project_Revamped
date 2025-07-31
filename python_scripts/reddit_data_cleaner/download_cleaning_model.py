# This code should be runned once manually; later on when you run the cleaner, the cleaner should check if the model is downloaded, if not download then execute this script automatically

import os
from pathlib import Path
import requests

# ------------------------------
# 1. Configurations
# ------------------------------
MODEL_REPO = "TheBloke/deepseek-coder-6.7B-instruct-GGUF"
GGUF_FILENAME = "deepseek-coder-6.7b-instruct.Q5_K_M.gguf"
DOWNLOAD_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{GGUF_FILENAME}"

# ------------------------------
# 2. Get root of project (go 2 levels up from this script)
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # reddit_data_cleaner → python_scripts → Car_Clinic_Project

# ------------------------------
# 3. Final model save path
# ------------------------------
MODEL_PATH = PROJECT_ROOT / "models" / "TheDataCleaningModel"
GGUF_FILEPATH = MODEL_PATH / GGUF_FILENAME

# ------------------------------
# 4. Create the save directory if not exists
# ------------------------------
MODEL_PATH.mkdir(parents=True, exist_ok=True)

# ------------------------------
# 5. Check if file already exists
# ------------------------------
if GGUF_FILEPATH.exists():
    print(f"✅ Model already downloaded at {GGUF_FILEPATH}")
else:
    # ------------------------------
    # 6. Download the file
    # ------------------------------
    print(f"🔄 Downloading GGUF model from: {DOWNLOAD_URL}")
    try:
        with requests.get(DOWNLOAD_URL, stream=True) as r:
            r.raise_for_status()
            with open(GGUF_FILEPATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Download complete. Model saved at {GGUF_FILEPATH}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
