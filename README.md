# Sales Demand Forecasting Dashboard

This repository now supports two deployment modes:

- `app.py`: Streamlit app (existing)
- `backend/`: FastAPI backend (for Render)
- `frontend/`: Vite frontend (for Vercel)

## 1) Push to GitHub

From project root:

```bash
git add .
git commit -m "Add Render backend and Vercel frontend deployment setup"
git push origin main
```

## 2) Deploy Backend on Render

1. Open Render dashboard and click **New +** → **Blueprint**.
2. Connect your GitHub repo.
3. Render will detect `render.yaml` and create service `sales-demand-forecast-backend`.
4. Deploy.
5. After deployment, copy backend URL, for example:

```text
https://sales-demand-forecast-backend.onrender.com
```

Check API health:

```text
https://sales-demand-forecast-backend.onrender.com/health
```

## 3) Deploy Frontend on Vercel

1. Open Vercel dashboard and click **Add New Project**.
2. Import the same GitHub repository.
3. Set **Root Directory** to `frontend`.
4. Set environment variable:

```text
VITE_API_BASE_URL=https://sales-demand-forecast-backend.onrender.com
```

5. Build command: `npm run build`
6. Output directory: `dist`
7. Deploy.

## 4) Local Run (Split Mode)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend local URL is usually `http://localhost:5173`.

## API Endpoints

- `GET /health`
- `GET /historical`
- `GET /model-info`
- `GET /forecast?days=30`