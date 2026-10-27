import json, numpy as np, tensorflow as tf, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from config import *

def main():
    model = tf.keras.models.load_model(MODEL_PATH)
    test = tf.keras.utils.image_dataset_from_directory(SPLIT_DIR/"test", class_names=CLASSES,
        image_size=IMG_SIZE, batch_size=BATCH, shuffle=False)
    y = np.concatenate([l.numpy() for _, l in test]); p = model.predict(test).argmax(1)
    rep = classification_report(y, p, target_names=CLASSES, output_dict=True)
    (ART_DIR/"metrics.json").write_text(json.dumps(rep, indent=2))
    ConfusionMatrixDisplay(confusion_matrix(y, p), display_labels=CLASSES).plot(xticks_rotation=45)
    plt.tight_layout(); plt.savefig(ART_DIR/"confusion_matrix.png", dpi=150)
    print(classification_report(y, p, target_names=CLASSES))
if __name__ == "__main__": main()
