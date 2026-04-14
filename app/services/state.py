import threading
from collections import deque
from typing import Deque, List

from app.datasources.sources import DataSource, SimulatedDataSource, RealDataSource
from app.models.cpu_data import CPUData, SERVER_PROFILES

MAX_BUFFER = 300


class AppState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init()
        return cls._instance

    def _init(self):
        self._simulated_source = SimulatedDataSource()
        self._real_source      = RealDataSource()
        self._active: DataSource = self._simulated_source
        self._buffer: Deque[CPUData] = deque(maxlen=MAX_BUFFER)
        self._total_requests   = 0
        self._pending_users    = 0
        self._lock = threading.Lock()

    # ── Mode ──────────────────────────────────────────────────────────────────
    @property
    def mode(self) -> str:
        return self._active.get_name()

    def set_mode(self, mode: str):
        with self._lock:
            self._active = self._real_source if mode == 'real' else self._simulated_source

    # ── Server profile (solo simulación) ──────────────────────────────────────
    def set_profile(self, profile_key: str):
        self._simulated_source.set_profile(profile_key)

    def get_profile(self):
        return self._simulated_source.get_profile().to_dict()

    def get_all_profiles(self):
        return {k: v.to_dict() for k, v in SERVER_PROFILES.items()}

    # ── Load injection ────────────────────────────────────────────────────────
    def add_simulation_load(self, num_requests: int):
        """Modo simulado: convierte peticiones en usuarios."""
        users = max(1, num_requests // 10)
        with self._lock:
            self._simulated_source.add_users(users)
            self._total_requests += num_requests
            self._pending_users  += users

    def add_real_load(self, num_requests: int):
        """Modo real: lanza trabajo computacional real en threads."""
        from app.services.cpu_worker import fire_real_load
        with self._lock:
            self._total_requests += num_requests
        fire_real_load(num_requests)

    # ── Tick ──────────────────────────────────────────────────────────────────
    def tick(self) -> CPUData:
        data = self._active.get_current()
        with self._lock:
            self._buffer.append(data)
            if self._pending_users > 0:
                self._pending_users = max(0, self._pending_users - 1)
        return data

    def get_buffer(self) -> List[CPUData]:
        with self._lock:
            return list(self._buffer)

    def clear_buffer(self):
        with self._lock:
            self._buffer.clear()

    @property
    def total_requests(self) -> int:
        return self._total_requests

    @property
    def pending_users(self) -> int:
        return self._pending_users