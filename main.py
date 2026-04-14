import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.controllers.api import router, cpu_ticker


# ── Lifespan (inicia el ticker de background al arrancar) ─────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cpu_ticker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CPU Monitor API",
    description="Estimación de consumo CPU mediante integración numérica",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)

# ── Dashboard ─────────────────────────────────────────────────────────────────
STATIC_DIR = Path(__file__).parent / "app" / "static"

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html_path = STATIC_DIR / "dashboard.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "cpu-monitor-backend"}