from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ServerProfile:
    """Perfil del servidor que se está simulando."""
    name: str               # ej. "EC2 t3.medium"
    cores: int              # número de núcleos
    ram_gb: float           # RAM en GB
    k_factor: float         # factor CPU por usuario (derivado del perfil)
    description: str        # descripción libre

    def to_dict(self):
        return {
            'name': self.name,
            'cores': self.cores,
            'ram_gb': self.ram_gb,
            'k_factor': self.k_factor,
            'description': self.description,
        }


# Perfiles predefinidos
SERVER_PROFILES = {
    'micro': ServerProfile(
        name='Micro (1 vCPU, 1GB)',
        cores=1, ram_gb=1, k_factor=2.5,
        description='Servidor mínimo. Se satura rápido con pocos usuarios.'
    ),
    'small': ServerProfile(
        name='Small (2 vCPU, 4GB)',
        cores=2, ram_gb=4, k_factor=1.2,
        description='Servidor pequeño tipo EC2 t3.small o VPS básico.'
    ),
    'medium': ServerProfile(
        name='Medium (4 vCPU, 8GB)',
        cores=4, ram_gb=8, k_factor=0.7,
        description='Servidor mediano. Maneja carga moderada sin problemas.'
    ),
    'large': ServerProfile(
        name='Large (8 vCPU, 16GB)',
        cores=8, ram_gb=16, k_factor=0.35,
        description='Servidor de producción robusto. Alta tolerancia a carga.'
    ),
    'xlarge': ServerProfile(
        name='XLarge (16 vCPU, 32GB)',
        cores=16, ram_gb=32, k_factor=0.15,
        description='Servidor de alta disponibilidad. Difícil de saturar.'
    ),
    'custom': ServerProfile(
        name='Custom', cores=4, ram_gb=8, k_factor=0.8,
        description='Perfil personalizado.'
    ),
}


@dataclass
class CPUData:
    timestamp: float
    cpu_percent: float
    users: int = 0
    mode: str = 'simulated'
    server_profile: Optional[str] = None

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'users': self.users,
            'mode': self.mode,
            'server_profile': self.server_profile,
        }


@dataclass
class IntegrationResult:
    method: str
    value: float
    n_points: int
    time_range: float
    data_points: List[CPUData] = field(default_factory=list)

    def to_dict(self):
        return {
            'method': self.method,
            'value': round(self.value, 4),
            'n_points': self.n_points,
            'time_range': round(self.time_range, 2),
            'unit': 'CPU% · seconds',
            'data_points': [d.to_dict() for d in self.data_points],
        }