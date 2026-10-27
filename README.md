# EcoSort AI (core: ML + API)
Python 3.10-3.12. Windows PowerShell: `py -m venv .venv; .\.venv\Scripts\Activate.ps1`  (macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`)
1. `pip install -r backend/requirements.txt scikit-learn matplotlib`
2. Put the six-class TrashNet folders in `ml/data/raw/<class>/` (verify source and licence yourself).
3. `cd ml; python prepare_dataset.py; python train.py; python evaluate.py`
   Outputs in `ml/artifacts/`: model, labels.json, metrics.json, confusion_matrix.png.
4. `cd backend; uvicorn app.main:app --reload`, then open http://localhost:8000/docs and POST an image to /api/predict.
Frontend: see frontend/SETUP.txt (Node 18+). Set CORS_ORIGINS on the backend to the frontend origin.
Without a trained model, /api/predict returns 503 with instructions (no fake predictions).

## Deployment
- Local with Docker: train first (artifacts must exist in `ml/artifacts/`), then `docker compose up --build`; app at http://localhost:8080, API at http://localhost:8000/api/health.
- Online: build the frontend with `VITE_API_URL=https://<your-api> npm run build` and host `frontend/dist` on any static host (HashRouter needs no rewrite rules). Host the backend on a Python/Docker host; set `CORS_ORIGINS` to the frontend origin, mount the model files, and use a persistent disk for SQLite (or the DB will reset on redeploy).
- Expect slow cold starts (TensorFlow load) and high memory use on free tiers. Health check: `GET /api/health` (`model_ready` must be true).
- No live URL exists; none has been deployed or verified.
