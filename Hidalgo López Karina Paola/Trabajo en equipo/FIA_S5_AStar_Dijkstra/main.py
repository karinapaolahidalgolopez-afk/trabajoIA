"""
main.py
Ejecuta los experimentos A* vs Dijkstra, guarda resultados (CSV) y genera el dashboard.
Uso:  python main.py
"""
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd

from red_carretera import CIUDADES, CARRETERAS
from algoritmos import (construir_grafo, haversine, dijkstra, a_estrella,
                        verificar_admisibilidad, verificar_consistencia,
                        distancias_reales_a)

SALIDA = "resultados"
os.makedirs(SALIDA, exist_ok=True)

# Consultas (origen, destino) a evaluar
CONSULTAS = [
    ("Acapulco", "Veracruz"),
    ("Toluca", "Oaxaca"),
    ("Morelia", "Veracruz"),
    ("Querétaro", "Acapulco"),
    ("CDMX", "Oaxaca"),
    ("Pachuca", "Acapulco"),
]
CONSULTA_MAPA = ("Morelia", "Veracruz")   # la que se dibuja en el dashboard
REPETICIONES = 2000                        # para promediar el tiempo


def tiempo_promedio_us(funcion, *args):
    """Tiempo medio por ejecución (microsegundos) sobre REPETICIONES corridas."""
    tiempos = []
    for _ in range(REPETICIONES):
        t0 = time.perf_counter()
        funcion(*args)
        tiempos.append(time.perf_counter() - t0)
    return statistics.mean(tiempos) * 1e6


def main():
    grafo = construir_grafo()
    filas, detalle = [], {}

    # ------------------------------------------------------------ 1. Comparación
    for o, d in CONSULTAS:
        cam_d, c_d, n_d, ord_d, _ = dijkstra(grafo, o, d)
        cam_a, c_a, n_a, ord_a, _ = a_estrella(grafo, o, d)
        t_d = tiempo_promedio_us(dijkstra, grafo, o, d)
        t_a = tiempo_promedio_us(a_estrella, grafo, o, d)
        assert abs(c_d - c_a) < 1e-9, "A* debe igualar el costo óptimo de Dijkstra"
        detalle[(o, d)] = (cam_d, ord_d, cam_a, ord_a)
        filas.append({
            "Origen": o, "Destino": d,
            "Costo óptimo (km)": c_d,
            "Dijkstra nodos exp.": n_d, "A* nodos exp.": n_a,
            "Reducción nodos (%)": round(100 * (n_d - n_a) / n_d, 1),
            "Dijkstra tiempo (µs)": round(t_d, 1), "A* tiempo (µs)": round(t_a, 1),
            "Ruta": " → ".join(cam_a),
        })
    df = pd.DataFrame(filas)
    df.to_csv(f"{SALIDA}/comparacion_a_vs_dijkstra.csv", index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------ 2. Admisibilidad
    destinos = sorted({d for _, d in CONSULTAS})
    adm = []
    for d in destinos:
        viol_a = verificar_admisibilidad(grafo, d)
        viol_c = verificar_consistencia(grafo, d)
        adm.append({"Destino": d, "Violaciones admisibilidad": len(viol_a),
                    "Violaciones consistencia": len(viol_c)})
    df_adm = pd.DataFrame(adm)
    df_adm.to_csv(f"{SALIDA}/verificacion_heuristica.csv", index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------ 3. Heurística inflada
    pesos = [1.0, 1.25, 1.5, 2.0, 3.0]
    peso_rows = []
    for o, d in CONSULTAS:
        _, optimo, _, _, _ = dijkstra(grafo, o, d)
        for w in pesos:
            _, c, n, _, _ = a_estrella(grafo, o, d, peso=w)
            peso_rows.append({"Origen": o, "Destino": d, "Peso w": w,
                              "Costo (km)": c, "Óptimo (km)": optimo,
                              "Sobrecosto (%)": round(100 * (c - optimo) / optimo, 2),
                              "Nodos exp.": n})
    df_w = pd.DataFrame(peso_rows)
    df_w.to_csv(f"{SALIDA}/heuristica_inflada.csv", index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------ 4. Dashboard
    dashboard(grafo, df, df_w)

    # ------------------------------------------------------------ 5. Consola
    pd.set_option("display.width", 220, "display.max_columns", 20)
    print("\n=== A* vs Dijkstra ===")
    print(df.drop(columns=["Ruta"]).to_string(index=False))
    print("\n=== Rutas ===")
    for _, r in df.iterrows():
        print(f"{r['Origen']} → {r['Destino']}: {r['Ruta']}  ({r['Costo óptimo (km)']:.0f} km)")
    print("\n=== Verificación de la heurística (haversine) ===")
    print(df_adm.to_string(index=False))
    print("\n=== Heurística inflada (f = g + w·h) ===")
    print(df_w.groupby("Peso w")[["Sobrecosto (%)", "Nodos exp."]].mean().round(2))
    print(f"\nArchivos guardados en ./{SALIDA}/")


# ---------------------------------------------------------------------------
def dibujar_mapa(ax, grafo, origen, destino, camino, explorados, titulo, color):
    for a, b, _ in CARRETERAS:
        (la1, lo1), (la2, lo2) = CIUDADES[a], CIUDADES[b]
        ax.plot([lo1, lo2], [la1, la2], color="#cfd4da", lw=1, zorder=1)
    for c, (lat, lon) in CIUDADES.items():
        ax.scatter(lon, lat, s=38, color="#e9ecef", edgecolor="#868e96", zorder=2)
    for i, c in enumerate(explorados):
        lat, lon = CIUDADES[c]
        ax.scatter(lon, lat, s=90, color=color, alpha=.75, zorder=3)
    xs = [CIUDADES[c][1] for c in camino]
    ys = [CIUDADES[c][0] for c in camino]
    ax.plot(xs, ys, color="#2f9e44", lw=3, zorder=4)
    for c, (lat, lon) in CIUDADES.items():
        peso = "bold" if c in (origen, destino) else "normal"
        ax.annotate(c, (lon, lat), fontsize=6.5, xytext=(3, 3),
                    textcoords="offset points", fontweight=peso, zorder=5)
    ax.set_title(titulo, fontsize=10, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#adb5bd")


def dashboard(grafo, df, df_w):
    o, d = CONSULTA_MAPA
    from algoritmos import dijkstra as dj, a_estrella as ae
    cam_d, c_d, n_d, ord_d, _ = dj(grafo, o, d)
    cam_a, c_a, n_a, ord_a, _ = ae(grafo, o, d)

    fig = plt.figure(figsize=(17, 10.5), constrained_layout=True)
    fig.suptitle("Dashboard — A* vs Dijkstra en la red carretera del centro de México",
                 fontsize=15, fontweight="bold")
    gs = GridSpec(3, 4, figure=fig, height_ratios=[1.25, 1.25, 1])

    ax1 = fig.add_subplot(gs[0:2, 0]); ax2 = fig.add_subplot(gs[0:2, 1])
    dibujar_mapa(ax1, grafo, o, d, cam_d, ord_d,
                 f"Dijkstra: {o} → {d}\n{n_d} nodos expandidos · {c_d:.0f} km", "#f08c00")
    dibujar_mapa(ax2, grafo, o, d, cam_a, ord_a,
                 f"A* (haversine): {o} → {d}\n{n_a} nodos expandidos · {c_a:.0f} km", "#1c7ed6")

    etiquetas = [f"{a[:4]}→{b[:4]}" for a, b in zip(df["Origen"], df["Destino"])]
    x = range(len(df)); w = 0.38

    ax3 = fig.add_subplot(gs[0, 2:])
    ax3.bar([i - w/2 for i in x], df["Dijkstra nodos exp."], w, label="Dijkstra", color="#f08c00")
    ax3.bar([i + w/2 for i in x], df["A* nodos exp."], w, label="A*", color="#1c7ed6")
    ax3.set_xticks(list(x)); ax3.set_xticklabels(etiquetas, fontsize=8)
    ax3.set_title("Nodos expandidos por consulta", fontweight="bold"); ax3.legend()
    ax3.set_ylabel("nodos")

    ax4 = fig.add_subplot(gs[1, 2:])
    ax4.bar([i - w/2 for i in x], df["Dijkstra tiempo (µs)"], w, label="Dijkstra", color="#f08c00")
    ax4.bar([i + w/2 for i in x], df["A* tiempo (µs)"], w, label="A*", color="#1c7ed6")
    ax4.set_xticks(list(x)); ax4.set_xticklabels(etiquetas, fontsize=8)
    ax4.set_title("Tiempo medio de ejecución", fontweight="bold"); ax4.legend()
    ax4.set_ylabel("µs")

    # Admisibilidad: h(n) vs h*(n) hacia el destino del mapa
    ax5 = fig.add_subplot(gs[2, 0:2])
    real = distancias_reales_a(grafo, d)
    nodos = sorted(real, key=lambda n: real[n])
    ax5.plot(range(len(nodos)), [real[n] for n in nodos], "o-", color="#c92a2a",
             label="h*(n) costo real")
    ax5.plot(range(len(nodos)), [haversine(n, d) for n in nodos], "s-", color="#1c7ed6",
             label="h(n) línea recta")
    ax5.fill_between(range(len(nodos)), [haversine(n, d) for n in nodos],
                     [real[n] for n in nodos], color="#a5d8ff", alpha=.35)
    ax5.set_xticks(range(len(nodos))); ax5.set_xticklabels(nodos, rotation=60, ha="right", fontsize=7)
    ax5.set_title(f"Admisibilidad hacia {d}: h(n) ≤ h*(n) en todos los nodos", fontweight="bold")
    ax5.set_ylabel("km"); ax5.legend()

    # Heurística inflada
    ax6 = fig.add_subplot(gs[2, 2])
    g = df_w.groupby("Peso w")[["Sobrecosto (%)", "Nodos exp."]].mean()
    ax6.plot(g.index, g["Sobrecosto (%)"], "o-", color="#862e9c")
    ax6.set_title("Sobrecosto si h se infla (f=g+w·h)", fontweight="bold", fontsize=10)
    ax6.set_xlabel("w"); ax6.set_ylabel("% sobre el óptimo")

    ax7 = fig.add_subplot(gs[2, 3])
    ax7.plot(g.index, g["Nodos exp."], "o-", color="#0b7285")
    ax7.set_title("Nodos expandidos vs w", fontweight="bold", fontsize=10)
    ax7.set_xlabel("w"); ax7.set_ylabel("nodos (promedio)")

    fig.savefig(f"{SALIDA}/dashboard.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
