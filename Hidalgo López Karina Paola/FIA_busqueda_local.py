"""
Actividad 2.3 - Búsqueda Local
Problema: Ruta mínima (TSP) para un repartidor que visita N puntos y regresa al origen.
Algoritmos: Hill Climbing (con reinicios opcionales) y Simulated Annealing.

Requisitos: pip install numpy matplotlib pandas
"""
import math
import random
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# 1. DATOS DEL PROBLEMA
# ------------------------------------------------------------------
N_CIUDADES = 30
SEMILLA_PROBLEMA = 42

rng = np.random.default_rng(SEMILLA_PROBLEMA)
COORDS = rng.uniform(0, 100, size=(N_CIUDADES, 2))  # puntos en un plano 100x100 km
DIST = np.linalg.norm(COORDS[:, None, :] - COORDS[None, :, :], axis=2)


# ------------------------------------------------------------------
# 2. FUNCIÓN OBJETIVO Y VECINDARIO
# ------------------------------------------------------------------
def costo(ruta):
    """Función objetivo: distancia total del ciclo (minimizar)."""
    return sum(DIST[ruta[i], ruta[(i + 1) % len(ruta)]] for i in range(len(ruta)))


def vecino(ruta):
    """Operador de vecindad 2-opt: invierte un segmento de la ruta."""
    i, j = sorted(random.sample(range(len(ruta)), 2))
    return ruta[:i] + ruta[i:j + 1][::-1] + ruta[j + 1:]


def ruta_inicial():
    r = list(range(N_CIUDADES))
    random.shuffle(r)
    return r


# ------------------------------------------------------------------
# 3. HILL CLIMBING (ascenso/descenso de colina)
# ------------------------------------------------------------------
def hill_climbing(iteraciones=20000, seed=0):
    random.seed(seed)
    actual = ruta_inicial()
    c_actual = costo(actual)
    historial = [c_actual]
    for _ in range(iteraciones):
        cand = vecino(actual)
        c_cand = costo(cand)
        if c_cand < c_actual:          # solo acepta mejoras
            actual, c_actual = cand, c_cand
        historial.append(c_actual)
    return actual, c_actual, historial


# ------------------------------------------------------------------
# 4. SIMULATED ANNEALING (recocido simulado)
# ------------------------------------------------------------------
def simulated_annealing(iteraciones=20000, T0=10.0, alfa=0.9999, T_min=1e-3, seed=0):
    """
    T0   : temperatura inicial
    alfa : factor de enfriamiento geométrico (T <- alfa * T)
    """
    random.seed(seed)
    actual = ruta_inicial()
    c_actual = costo(actual)
    mejor, c_mejor = actual[:], c_actual
    T = T0
    historial = [c_actual]
    historial_mejor = [c_mejor]
    for _ in range(iteraciones):
        cand = vecino(actual)
        c_cand = costo(cand)
        delta = c_cand - c_actual
        # acepta mejoras siempre; empeoramientos con prob. exp(-delta/T)
        if delta < 0 or random.random() < math.exp(-delta / T):
            actual, c_actual = cand, c_cand
            if c_actual < c_mejor:
                mejor, c_mejor = actual[:], c_actual
        T = max(T * alfa, T_min)
        historial.append(c_actual)
        historial_mejor.append(c_mejor)
    return mejor, c_mejor, historial, historial_mejor


# ------------------------------------------------------------------
# 5. EXPERIMENTOS (varias corridas para comparar con rigor)
# ------------------------------------------------------------------
if __name__ == "__main__":
    ITER = 20000
    CORRIDAS = 10

    res_hc, res_sa = [], []
    mejor_hc = mejor_sa = None
    for s in range(CORRIDAS):
        t = time.perf_counter()
        r, c, h = hill_climbing(ITER, seed=s)
        t_hc = time.perf_counter() - t
        res_hc.append((c, t_hc))
        if mejor_hc is None or c < mejor_hc[1]:
            mejor_hc = (r, c, h)

        t = time.perf_counter()
        r, c, h, hm = simulated_annealing(ITER, T0=10, alfa=0.9999, seed=s)
        t_sa = time.perf_counter() - t
        res_sa.append((c, t_sa))
        if mejor_sa is None or c < mejor_sa[1]:
            mejor_sa = (r, c, h, hm)

    tabla = pd.DataFrame({
        "Algoritmo": ["Hill Climbing", "Simulated Annealing"],
        "Mejor costo": [min(c for c, _ in res_hc), min(c for c, _ in res_sa)],
        "Costo promedio": [np.mean([c for c, _ in res_hc]), np.mean([c for c, _ in res_sa])],
        "Desv. estándar": [np.std([c for c, _ in res_hc]), np.std([c for c, _ in res_sa])],
        "Tiempo prom. (s)": [np.mean([t for _, t in res_hc]), np.mean([t for _, t in res_sa])],
    }).round(2)
    print(tabla.to_string(index=False))
    tabla.to_csv("resultados_comparacion.csv", index=False)

    # --- Gráfica de convergencia ---
    plt.figure(figsize=(9, 5))
    plt.plot(mejor_hc[2], label="Hill Climbing", color="tab:red")
    plt.plot(mejor_sa[2], label="SA (solución actual)", color="tab:blue", alpha=0.35)
    plt.plot(mejor_sa[3], label="SA (mejor encontrada)", color="tab:blue")
    plt.xlabel("Iteración")
    plt.ylabel("Distancia total de la ruta")
    plt.title("Convergencia: Hill Climbing vs Simulated Annealing")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("convergencia.png", dpi=150)

    # --- Rutas finales ---
    fig, ejes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, (nombre, ruta, c) in zip(
        ejes, [("Hill Climbing", mejor_hc[0], mejor_hc[1]), ("Simulated Annealing", mejor_sa[0], mejor_sa[1])]
    ):
        cerrada = ruta + [ruta[0]]
        ax.plot(COORDS[cerrada, 0], COORDS[cerrada, 1], "-o", markersize=4)
        ax.set_title(f"{nombre} — costo = {c:.1f}")
        ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig("rutas_finales.png", dpi=150)

    # --- Sensibilidad de parámetros de SA (T0 y alfa) ---
    filas = []
    for T0 in (1, 10, 50):
        for alfa in (0.999, 0.9995, 0.9999):
            costos = [simulated_annealing(ITER, T0=T0, alfa=alfa, seed=s)[1] for s in range(5)]
            filas.append({"T0": T0, "alfa": alfa, "costo promedio": round(np.mean(costos), 2)})
    sens = pd.DataFrame(filas)
    print("\nSensibilidad de parámetros en SA:")
    print(sens.to_string(index=False))
    sens.to_csv("sensibilidad_sa.csv", index=False)
