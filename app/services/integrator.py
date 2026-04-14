from typing import List, Tuple
from app.models.cpu_data import CPUData, IntegrationResult


class IntegratorService:
    """
    Servicio de integración numérica.
    Implementa métodos del Trapecio y Simpson 1/3 compuesto.
    """

    @staticmethod
    def trapezoid(data: List[CPUData]) -> IntegrationResult:
        """
        Método del Trapecio Compuesto:
            ∫f(x)dx ≈ (h/2)[f(x0) + 2f(x1) + ... + 2f(xn-1) + f(xn)]
        donde h = (b-a)/n
        """
        if len(data) < 2:
            return IntegrationResult("trapezoid", 0.0, len(data), 0.0, data)

        total = 0.0
        for i in range(1, len(data)):
            dt = data[i].timestamp - data[i - 1].timestamp
            total += (data[i].cpu_percent + data[i - 1].cpu_percent) * dt / 2.0

        time_range = data[-1].timestamp - data[0].timestamp
        return IntegrationResult(
            method="trapezoid",
            value=total,
            n_points=len(data),
            time_range=time_range,
            data_points=data,
        )

    @staticmethod
    def simpson(data: List[CPUData]) -> IntegrationResult:
        """
        Método de Simpson 1/3 Compuesto:
            ∫f(x)dx ≈ (h/3)[f(x0) + 4f(x1) + 2f(x2) + 4f(x3) + ... + f(xn)]
        Requiere n par. Si n es impar, el último intervalo usa el Trapecio.
        """
        n = len(data)
        if n < 3:
            return IntegratorService.trapezoid(data)

        # Asegurar n par para Simpson puro
        use_data = data if (n - 1) % 2 == 0 else data[:-1]
        leftover = data[len(use_data):] if len(use_data) < n else []

        # Asumimos timestamps equiespaciados aprox; calculamos h promedio
        n_intervals = len(use_data) - 1
        if n_intervals < 2:
            return IntegratorService.trapezoid(data)

        total = 0.0
        for i in range(0, n_intervals - 1, 2):
            h = (use_data[i + 2].timestamp - use_data[i].timestamp) / 2.0
            total += (h / 3.0) * (
                use_data[i].cpu_percent
                + 4 * use_data[i + 1].cpu_percent
                + use_data[i + 2].cpu_percent
            )

        # Si sobró un punto (n original era par de intervalos impares), añadir con trapecio
        if leftover:
            dt = leftover[0].timestamp - use_data[-1].timestamp
            total += (use_data[-1].cpu_percent + leftover[0].cpu_percent) * dt / 2.0

        time_range = data[-1].timestamp - data[0].timestamp
        return IntegrationResult(
            method="simpson",
            value=total,
            n_points=len(data),
            time_range=time_range,
            data_points=data,
        )

    @staticmethod
    def compute(data: List[CPUData], method: str = "simpson") -> IntegrationResult:
        """Dispatcher principal."""
        if method == "trapezoid":
            return IntegratorService.trapezoid(data)
        return IntegratorService.simpson(data)