import numpy as np
import matplotlib.pyplot as plt

# Tiempo total y número de puntos (según tu ejecución)
t = np.linspace(0, 299.81, 300)

# Simulación de CPU basada en tu gráfica (valores bajos con variaciones)
cpu = 5 + 3*np.sin(0.1*t) + 2*np.sin(0.3*t)
cpu = np.clip(cpu, 0, 10)  # limitar entre 0% y 10%

# =========================
# GRÁFICA 1: ÁREA BAJO LA CURVA
# =========================
plt.figure()
plt.plot(t, cpu)
plt.fill_between(t, cpu)
plt.title("Área bajo la curva de CPU(t)")
plt.xlabel("Tiempo (s)")
plt.ylabel("CPU (%)")
plt.savefig("area_cpu.png")

# =========================
# RESULTADOS REALES (los tuyos)
# =========================
trapecio = 1611.68
simpson = 1599.22

# =========================
# GRÁFICA 2: COMPARACIÓN
# =========================
plt.figure()
plt.bar(["Trapecio", "Simpson"], [trapecio, simpson])
plt.title("Comparación de métodos de integración")
plt.ylabel("Consumo acumulado (CPU·seg)")
plt.savefig("comparacion.png")

print("Gráficas generadas correctamente.")