# Model card: EcoSort AI
- Architecture: MobileNetV2 (ImageNet pretrained) + global average pooling + dropout + 6-unit softmax. Preprocessing is part of the saved model.
- Classes (fixed order): cardboard, glass, metal, paper, plastic, trash.
- Data: six-class TrashNet. Verify source and licence before use. Split 70/15/15 with duplicates removed before splitting.
- Intended use: classroom demonstration of waste segregation guidance.
- Limitations: closed six-class model; it will assign unrelated objects to one of the classes. Low-confidence results are flagged (default threshold 0.60, configurable). Not tested on in-the-wild images unless you do so.
- Evaluation: NOT YET MEASURED. After running `ml/evaluate.py`, copy the real figures from `ml/artifacts/metrics.json` and `confusion_matrix.png` here. Do not publish numbers that were not produced by that script.
- Privacy: uploaded images are not stored; only scan id, time, category, confidence and model version are saved.
