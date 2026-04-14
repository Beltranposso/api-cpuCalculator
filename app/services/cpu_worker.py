"""
Genera carga CPU real ejecutando trabajo computacional en threads.
Cada 'petición' lanza N iteraciones de trabajo pesado que psutil puede detectar.
"""
import threading
import math
import time


def _heavy_work(duration: float):
    """Trabajo CPU-intensivo: cálculos matemáticos en loop."""
    end = time.time() + duration
    x = 1.0
    while time.time() < end:
        # Operaciones que realmente queman CPU
        for _ in range(5000):
            x = math.sqrt(x * 1.0001 + 1) * math.sin(x) + math.log(abs(x) + 1)


def fire_real_load(num_requests: int):
    """
    Lanza threads de trabajo real proporcional al número de peticiones.
    - Pocas peticiones  → pocos threads cortos
    - Muchas peticiones → más threads o más duración
    """
    # Escala: cada 50 peticiones = 1 thread de ~1.5s de trabajo
    num_threads = max(1, min(num_requests // 50, 8))   # cap 8 threads
    duration    = min(0.5 + (num_requests / 500), 3.0) # 0.5s a 3s

    for _ in range(num_threads):
        t = threading.Thread(target=_heavy_work, args=(duration,), daemon=True)
        t.start()