"""Zero-shot waste classifier: CLIP (pretrained, no training needed). Weights download on first use and are cached."""
import json, logging, os
from pathlib import Path
log = logging.getLogger('ecosort')

CACHE = os.getenv("MODEL_CACHE_DIR", str(Path(__file__).resolve().parents[1] / "model_cache"))
MODEL_NAME = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
MODEL_VERSION = "clip-zeroshot-v1"
CATEGORY_IDS = ["wet", "dry", "plastic", "metal", "reusable", "non_recyclable"]
MIN_SCORE = 0.30  # below this the photo is treated as unclear (no guess is returned)

PROMPTS = {
    "wet": ["a photo of food waste", "a photo of vegetable peels and fruit scraps", "a photo of leftover cooked food", "a photo of rotting organic kitchen waste"],
    "dry": ["a photo of clean waste paper", "a photo of a cardboard box", "a photo of newspaper and dry paper packaging", "a photo of dry carton packaging"],
    "plastic": ["a photo of a plastic bottle", "a photo of a plastic bag", "a photo of a plastic wrapper", "a photo of a plastic container"],
    "metal": ["a photo of an aluminium can", "a photo of a steel tin can", "a photo of a metal object", "a photo of scrap metal"],
    "reusable": ["a photo of clothes that can be reused", "a photo of a usable household object in good condition", "a photo of an intact glass jar", "a photo of a usable toy, shoe or utensil"],
    "non_recyclable": ["a photo of sanitary waste or a used diaper", "a photo of dirty contaminated food packaging", "a photo of used tissues and cigarette butts", "a photo of broken ceramic and mixed unrecyclable trash"],
}

def decide(scores):
    """Return a category id, or None if the photo is unclear. Overlap rules:
    - reusable only wins if no recyclable material class is close (a plastic bottle is plastic, not reusable);
    - dry/plastic items that look contaminated go to non_recyclable."""
    best = max(scores, key=scores.get)
    if scores[best] < MIN_SCORE:
        return None
    if best == "reusable":
        mat = max(("plastic", "metal", "dry"), key=scores.get)
        if scores[mat] >= 0.6 * scores["reusable"]:
            best = mat
    if best in ("dry", "plastic") and scores["non_recyclable"] >= 0.7 * scores[best]:
        best = "non_recyclable"
    return best

class Classifier:
    version = MODEL_VERSION
    def __init__(self):
        import torch
        from transformers import CLIPModel, CLIPProcessor
        self.torch = torch
        self.model = CLIPModel.from_pretrained(MODEL_NAME, cache_dir=CACHE).eval()
        self.proc = CLIPProcessor.from_pretrained(MODEL_NAME, cache_dir=CACHE)
        self.texts = [p for c in CATEGORY_IDS for p in PROMPTS[c]]
        self.owner = [c for c in CATEGORY_IDS for _ in PROMPTS[c]]

    def scores(self, img):
        with self.torch.no_grad():
            out = self.model(**self.proc(text=self.texts, images=img, return_tensors="pt", padding=True))
        probs = out.logits_per_image.softmax(-1)[0].tolist()
        s = {c: 0.0 for c in CATEGORY_IDS}
        for c, p in zip(self.owner, probs): s[c] += p
        return s


ART = Path(os.getenv("ART_DIR", Path(__file__).resolve().parents[2] / "ml" / "artifacts"))
H5 = ART / "ecodetect_model.h5"
LABELS = ART / "labels.json"   # JSON list of the model's output class ids, in output order

class KerasClassifier:
    """Your EfficientNetB0 .h5 (124x124 RGB, raw 0-255 input, 6 softmax outputs). Needs TensorFlow >= 2.16 (Keras 3)."""
    version = "ecodetect-effnetb0-v1"
    def __init__(self, labels):
        import tensorflow as tf
        self.labels = labels
        self.model = tf.keras.models.load_model(H5, compile=False)
        self.size = tuple(self.model.input_shape[1:3])
    def scores(self, img):
        import numpy as np
        p = self.model.predict(np.asarray(img.resize(self.size), dtype="float32")[None], verbose=0)[0]
        s = {c: 0.0 for c in CATEGORY_IDS}
        for c, v in zip(self.labels, p): s[c] += float(v)
        return s

def load_classifier():
    """Use the .h5 only if labels.json declares its six classes as our category ids; otherwise use CLIP (never guess the mapping)."""
    if H5.exists():
        try:
            labels = json.loads(LABELS.read_text())
            if isinstance(labels, dict): labels = labels["classes"]
            if len(labels) == 6 and set(labels) == set(CATEGORY_IDS): return KerasClassifier(labels)
            log.warning("labels.json does not match the six category ids; using CLIP")
        except Exception:
            log.warning("ecodetect_model.h5 not used (labels.json missing/invalid or TensorFlow load failed); using CLIP", exc_info=True)
    return Classifier()
