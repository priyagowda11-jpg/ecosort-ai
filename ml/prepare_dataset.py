"""Verify classes, drop corrupt/duplicate images, split 70/15/15 BEFORE augmentation."""
import hashlib, random, shutil
from PIL import Image
from config import *

def main():
    found = sorted(p.name for p in RAW_DIR.iterdir() if p.is_dir()) if RAW_DIR.exists() else []
    if found != CLASSES:
        raise SystemExit(f"Expected folders {CLASSES} in {RAW_DIR}, found {found}")
    random.seed(SEED); seen = set()
    if SPLIT_DIR.exists(): shutil.rmtree(SPLIT_DIR)
    for cls in CLASSES:
        good = []
        for f in sorted((RAW_DIR / cls).iterdir()):
            try:
                with Image.open(f) as im: im.verify()
            except Exception:
                print("corrupt, skipped:", f.name); continue
            h = hashlib.md5(f.read_bytes()).hexdigest()
            if h in seen: print("duplicate, skipped:", f.name); continue
            seen.add(h); good.append(f)
        random.shuffle(good); n = len(good)
        cuts = {"train": good[:int(.7*n)], "val": good[int(.7*n):int(.85*n)], "test": good[int(.85*n):]}
        for split, files in cuts.items():
            d = SPLIT_DIR / split / cls; d.mkdir(parents=True)
            for f in files: shutil.copy2(f, d / f.name)
        print(cls, {k: len(v) for k, v in cuts.items()})
if __name__ == "__main__": main()
