import json, tensorflow as tf
from tensorflow.keras import layers, callbacks
from config import *

def ds(split, shuffle):
    return tf.keras.utils.image_dataset_from_directory(
        SPLIT_DIR / split, class_names=CLASSES, image_size=IMG_SIZE,
        batch_size=BATCH, shuffle=shuffle, seed=SEED).prefetch(tf.data.AUTOTUNE)

def build():
    aug = tf.keras.Sequential([layers.RandomFlip("horizontal"), layers.RandomRotation(.1),
                               layers.RandomZoom(.1)])  # active only in training
    base = tf.keras.applications.MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet")
    base.trainable = False
    x_in = tf.keras.Input(IMG_SIZE + (3,))                    # raw 0-255 pixels
    x = aug(x_in)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)  # baked in: same at inference
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(.3)(x)
    out = layers.Dense(len(CLASSES), activation="softmax")(x)
    return tf.keras.Model(x_in, out), base

def main():
    ART_DIR.mkdir(exist_ok=True)
    train, val = ds("train", True), ds("val", False)
    model, base = build()
    cb = [callbacks.ModelCheckpoint(MODEL_PATH, monitor="val_accuracy", save_best_only=True),
          callbacks.EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True)]
    model.compile(tf.keras.optimizers.Adam(1e-3), "sparse_categorical_crossentropy", ["accuracy"])
    model.fit(train, validation_data=val, epochs=15, callbacks=cb)
    base.trainable = True                                       # fine-tune top layers
    for l in base.layers[:-30]: l.trainable = False
    model.compile(tf.keras.optimizers.Adam(1e-5), "sparse_categorical_crossentropy", ["accuracy"])
    model.fit(train, validation_data=val, epochs=10, callbacks=cb)
    LABELS_PATH.write_text(json.dumps({"classes": CLASSES, "version": MODEL_VERSION}))
    print("Saved", MODEL_PATH)
if __name__ == "__main__": main()
