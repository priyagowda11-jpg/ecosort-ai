from pathlib import Path
ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"          # RAW_DIR/<class>/*.jpg
SPLIT_DIR = ROOT / "data" / "split"      # train/ val/ test/
ART_DIR = ROOT / "artifacts"
MODEL_PATH = ART_DIR / "ecosort_mobilenetv2.keras"
LABELS_PATH = ART_DIR / "labels.json"
CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]  # index order = output order
IMG_SIZE = (224, 224)
BATCH = 32
SEED = 42
MODEL_VERSION = "mnv2-trashnet-v1"
