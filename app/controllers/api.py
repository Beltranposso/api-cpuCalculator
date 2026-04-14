import asyncio, json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.state import AppState
from app.services.integrator import IntegratorService

router = APIRouter()
state  = AppState()


# ── WebSocket manager ──────────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def broadcast(self, data: dict):
        dead = set()
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        self.active -= dead


manager = ConnectionManager()


async def cpu_ticker():
    while True:
        point = state.tick()
        await manager.broadcast({'type': 'cpu_update', 'data': point.to_dict()})
        await asyncio.sleep(1)


# ── Schemas ────────────────────────────────────────────────────────────────────
class SimulatePayload(BaseModel):
    name: str
    num_requests: int

class ModePayload(BaseModel):
    mode: str

class ProfilePayload(BaseModel):
    profile: str


# ── REST Endpoints ─────────────────────────────────────────────────────────────
@router.post('/simulate-load')
async def simulate_load(payload: SimulatePayload):
    if state.mode == 'simulated':
        state.add_simulation_load(payload.num_requests)
        profile = state.get_profile()
        msg = (
            f"{payload.num_requests} peticiones de '{payload.name}' procesadas. "
            f"Simulando en '{profile['name']}' (k={profile['k_factor']})."
        )
    else:
        # Modo real: genera carga CPU genuina
        state.add_real_load(payload.num_requests)
        msg = (
            f"{payload.num_requests} peticiones de '{payload.name}' generando "
            f"carga REAL en el servidor. Observa el CPU subir."
        )

    return {
        'status': 'ok',
        'message': msg,
        'mode': state.mode,
        'total_requests': state.total_requests,
    }


@router.get('/metrics')
async def get_metrics():
    buffer = state.get_buffer()
    if len(buffer) < 2:
        return {'mode': state.mode, 'points': [p.to_dict() for p in buffer], 'integration': None}

    trap = IntegratorService.trapezoid(buffer)
    simp = IntegratorService.simpson(buffer)
    return {
        'mode': state.mode,
        'points': [p.to_dict() for p in buffer],
        'integration': {
            'trapezoid': trap.to_dict(),
            'simpson':   simp.to_dict(),
        },
    }


@router.get('/mode')
async def get_mode():
    return {'mode': state.mode}


@router.post('/mode')
async def set_mode(payload: ModePayload):
    if payload.mode not in ('simulated', 'real'):
        return {'error': 'Modo inválido'}
    state.set_mode(payload.mode)
    await manager.broadcast({'type': 'mode_change', 'mode': payload.mode})
    return {'status': 'ok', 'mode': state.mode}


@router.get('/profiles')
async def get_profiles():
    return {
        'profiles': state.get_all_profiles(),
        'active': state.get_profile(),
    }


@router.post('/profiles')
async def set_profile(payload: ProfilePayload):
    state.set_profile(payload.profile)
    profile = state.get_profile()
    await manager.broadcast({'type': 'profile_change', 'profile': profile})
    return {'status': 'ok', 'profile': profile}


@router.post('/clear')
async def clear_buffer():
    state.clear_buffer()
    return {'status': 'ok'}


# ── WebSocket ──────────────────────────────────────────────────────────────────
@router.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    await ws.send_json({
        'type': 'init',
        'mode': state.mode,
        'profile': state.get_profile(),
        'buffer': [p.to_dict() for p in state.get_buffer()],
    })
    try:
        while True:
            msg = await ws.receive_text()
            try:
                data = json.loads(msg)
                if data.get('action') == 'ping':
                    await ws.send_json({'type': 'pong'})
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(ws)