from abc import ABC, abstractmethod
import math, random, time
import psutil

from app.models.cpu_data import CPUData, ServerProfile, SERVER_PROFILES


class DataSource(ABC):
    @abstractmethod
    def get_current(self, users: int = 0) -> CPUData:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class SimulatedDataSource(DataSource):
    """
    Simula CPU(t) = min(100, k * users(t)) según el perfil de servidor elegido.
    k_factor depende de los recursos del servidor simulado.
    """
    BASE_TRAFFIC = 3
    NOISE_AMP    = 2.5

    def __init__(self):
        self._start_time   = time.time()
        self._extra_users  = 0.0
        self._profile_key  = 'medium'

    def set_profile(self, profile_key: str):
        if profile_key in SERVER_PROFILES:
            self._profile_key = profile_key

    def get_profile(self) -> ServerProfile:
        return SERVER_PROFILES.get(self._profile_key, SERVER_PROFILES['medium'])

    def add_users(self, n: int):
        self._extra_users += n

    def _compute_users(self) -> int:
        t     = time.time() - self._start_time
        base  = self.BASE_TRAFFIC
        peak  = 3 * abs(math.sin(t * 0.25))
        inj   = self._extra_users
        decay = self.get_profile().k_factor
        self._extra_users = max(0.0, self._extra_users - decay)
        return int(base + peak + inj)

    def get_current(self, users: int = 0) -> CPUData:
        profile = self.get_profile()
        u       = self._compute_users() + users
        raw_cpu = profile.k_factor * u
        noise   = random.gauss(0, self.NOISE_AMP)
        cpu     = min(100.0, max(0.0, raw_cpu + noise))
        return CPUData(
            timestamp=time.time(),
            cpu_percent=round(cpu, 2),
            users=u,
            mode='simulated',
            server_profile=self._profile_key,
        )

    def get_name(self) -> str:
        return 'simulated'


class RealDataSource(DataSource):
    """
    Lee CPU real con psutil. Las peticiones sí generan carga
    real vía cpu_worker threads, así psutil lo detecta.
    """
    def get_current(self, users: int = 0) -> CPUData:
        cpu = psutil.cpu_percent(interval=None)
        return CPUData(
            timestamp=time.time(),
            cpu_percent=round(cpu, 2),
            users=0,
            mode='real',
        )

    def get_name(self) -> str:
        return 'real'