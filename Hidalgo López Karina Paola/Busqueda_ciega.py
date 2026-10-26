"""
Actividad 2.4 - Algoritmos de búsqueda ciega (BFS / DFS)
Fundamentos de Inteligencia Artificial - Politécnica de Atlautla

Problema: encontrar un camino de la entrada (S) a la salida (G) en un laberinto.

Modelado como problema de búsqueda:
  - Estado:      celda (fila, columna) donde está el agente.
  - Acciones:    moverse ARRIBA, ABAJO, IZQUIERDA, DERECHA (si no hay pared).
  - Modelo de transición: la celda vecina resultante.
  - Costo:       1 por movimiento.
  - Estado meta: la celda G.

Uso:  python busqueda_ciega_laberinto.py
"""
import random
import time
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

# ---------------------------------------------------------------------------
# 1. Generación del laberinto (0 = pasillo, 1 = pared)
# ---------------------------------------------------------------------------
def generar_laberinto(n=21, seed=7, huecos=0.08):
    """Laberinto n x n (n impar) con backtracking recursivo (iterativo).
    Después se abren algunas paredes ('huecos') para crear ciclos y
    múltiples caminos; así BFS y DFS no devuelven la misma solución."""
    rnd = random.Random(seed)
    m = np.ones((n, n), dtype=int)
    m[1, 1] = 0
    pila = [(1, 1)]
    while pila:
        f, c = pila[-1]
        vecinos = [(f + df, c + dc, f + df // 2, c + dc // 2)
                   for df, dc in ((-2, 0), (2, 0), (0, -2), (0, 2))
                   if 0 < f + df < n - 1 and 0 < c + dc < n - 1
                   and m[f + df, c + dc] == 1]
        if vecinos:
            nf, nc, pf, pc = rnd.choice(vecinos)
            m[pf, pc] = 0
            m[nf, nc] = 0
            pila.append((nf, nc))
        else:
            pila.pop()
    # abrir paredes internas al azar -> ciclos
    paredes = [(f, c) for f in range(1, n - 1) for c in range(1, n - 1)
               if m[f, c] == 1 and ((m[f - 1, c] == 0 and m[f + 1, c] == 0) or
                                    (m[f, c - 1] == 0 and m[f, c + 1] == 0))]
    for f, c in rnd.sample(paredes, int(len(paredes) * huecos)):
        m[f, c] = 0
    return m


# ---------------------------------------------------------------------------
# 2. Representación del grafo (lista de adyacencia)
# ---------------------------------------------------------------------------
ORDEN = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # arriba, derecha, abajo, izquierda


def construir_grafo(m):
    """Cada celda libre es un nodo; hay arista entre celdas libres adyacentes."""
    grafo = {}
    filas, cols = m.shape
    for f in range(filas):
        for c in range(cols):
            if m[f, c] == 0:
                grafo[(f, c)] = [(f + df, c + dc) for df, dc in ORDEN
                                 if 0 <= f + df < filas and 0 <= c + dc < cols
                                 and m[f + df, c + dc] == 0]
    return grafo


# ---------------------------------------------------------------------------
# 3. Algoritmos de búsqueda
# ---------------------------------------------------------------------------
def reconstruir(padres, meta):
    camino, nodo = [], meta
    while nodo is not None:
        camino.append(nodo)
        nodo = padres[nodo]
    return camino[::-1]


def bfs(grafo, inicio, meta):
    """Búsqueda en anchura: frontera FIFO (cola)."""
    t0 = time.perf_counter()
    frontera = deque([inicio])
    padres = {inicio: None}          # sirve también como conjunto de visitados
    expandidos, orden, max_front = 0, [], 1
    while frontera:
        nodo = frontera.popleft()
        expandidos += 1
        orden.append(nodo)
        if nodo == meta:
            return dict(camino=reconstruir(padres, meta), expandidos=expandidos,
                        max_frontera=max_front, orden=orden,
                        tiempo=time.perf_counter() - t0)
        for v in grafo[nodo]:
            if v not in padres:
                padres[v] = nodo
                frontera.append(v)
        max_front = max(max_front, len(frontera))
    return dict(camino=None, expandidos=expandidos, max_frontera=max_front,
                orden=orden, tiempo=time.perf_counter() - t0)


def dfs(grafo, inicio, meta):
    """Búsqueda en profundidad: frontera LIFO (pila), versión iterativa."""
    t0 = time.perf_counter()
    frontera = [inicio]
    padres = {inicio: None}
    visitados = set()
    expandidos, orden, max_front = 0, [], 1
    while frontera:
        nodo = frontera.pop()
        if nodo in visitados:
            continue
        visitados.add(nodo)
        expandidos += 1
        orden.append(nodo)
        if nodo == meta:
            return dict(camino=reconstruir(padres, meta), expandidos=expandidos,
                        max_frontera=max_front, orden=orden,
                        tiempo=time.perf_counter() - t0)
        for v in reversed(grafo[nodo]):   # reversed para explorar en el mismo orden que BFS
            if v not in visitados:
                padres[v] = nodo
                frontera.append(v)
        max_front = max(max_front, len(frontera))
    return dict(camino=None, expandidos=expandidos, max_frontera=max_front,
                orden=orden, tiempo=time.perf_counter() - t0)


# ---------------------------------------------------------------------------
# 4. Experimentos y visualización
# ---------------------------------------------------------------------------
def medir_tiempo(fn, grafo, s, g, repeticiones=200):
    """Tiempo promedio en milisegundos (promedio de varias corridas)."""
    t = 0.0
    for _ in range(repeticiones):
        t += fn(grafo, s, g)["tiempo"]
    return t / repeticiones * 1000


def dibujar(m, res, s, g, titulo, ax):
    img = m.astype(float).copy()
    cmap = ListedColormap(["white", "#2b2b3c", "#f6d365", "#e63946", "#2a9d8f"])
    img = np.where(m == 1, 1, 0)
    for (f, c) in res["orden"]:
        img[f, c] = 2        # explorados
    for (f, c) in (res["camino"] or []):
        img[f, c] = 3        # camino solución
    img[s], img[g] = 4, 4
    ax.imshow(img, cmap=cmap, vmin=0, vmax=4)
    ax.set_title(f"{titulo}\nexpandidos={res['expandidos']} | "
                 f"longitud camino={len(res['camino']) - 1}", fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    N = 21
    m = generar_laberinto(N, seed=7)
    s, g = (1, 1), (N - 2, N - 2)
    grafo = construir_grafo(m)
    aristas = sum(len(v) for v in grafo.values()) // 2
    print(f"Laberinto {N}x{N}: V={len(grafo)} nodos, E={aristas} aristas")

    r_bfs, r_dfs = bfs(grafo, s, g), dfs(grafo, s, g)
    t_bfs, t_dfs = medir_tiempo(bfs, grafo, s, g), medir_tiempo(dfs, grafo, s, g)

    print(f"{'':6}{'Tiempo(ms)':>12}{'Expandidos':>12}{'Long.camino':>13}{'Máx.frontera':>14}")
    for nom, r, t in (("BFS", r_bfs, t_bfs), ("DFS", r_dfs, t_dfs)):
        print(f"{nom:6}{t:12.3f}{r['expandidos']:12d}{len(r['camino']) - 1:13d}{r['max_frontera']:14d}")

    # --- Figura 1: laberinto resuelto con BFS y DFS
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.6))
    dibujar(m, r_bfs, s, g, "BFS (anchura)", axs[0])
    dibujar(m, r_dfs, s, g, "DFS (profundidad)", axs[1])
    plt.tight_layout(); plt.savefig("fig_laberinto.png", dpi=150, bbox_inches="tight"); plt.close()

    # --- Experimento: 40 laberintos aleatorios para comparar de forma robusta
    tamanos = [11, 21, 31, 41]
    resumen = {n: {"bfs": [], "dfs": []} for n in tamanos}
    for n in tamanos:
        for sd in range(40):
            mm = generar_laberinto(n, seed=sd)
            gg = construir_grafo(mm)
            ss, ge = (1, 1), (n - 2, n - 2)
            a, b = bfs(gg, ss, ge), dfs(gg, ss, ge)
            resumen[n]["bfs"].append((a["expandidos"], len(a["camino"]) - 1, a["max_frontera"]))
            resumen[n]["dfs"].append((b["expandidos"], len(b["camino"]) - 1, b["max_frontera"]))
    print("\nPromedio en 40 laberintos por tamaño (expandidos, long. camino, máx. frontera)")
    medias = {}
    for n in tamanos:
        mb = np.mean(resumen[n]["bfs"], axis=0); md = np.mean(resumen[n]["dfs"], axis=0)
        medias[n] = (mb, md)
        print(f"n={n:2d}  BFS={np.round(mb, 1)}  DFS={np.round(md, 1)}")

    # --- Figura 2: comparación de métricas
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    x = np.arange(len(tamanos)); w = 0.38
    for ax, idx, tit in zip(axs, (0, 1, 2),
                            ("Nodos expandidos", "Longitud del camino", "Máx. tamaño de frontera")):
        ax.bar(x - w / 2, [medias[n][0][idx] for n in tamanos], w, label="BFS", color="#6a4c93")
        ax.bar(x + w / 2, [medias[n][1][idx] for n in tamanos], w, label="DFS", color="#f4a261")
        ax.set_xticks(x); ax.set_xticklabels([f"{n}x{n}" for n in tamanos])
        ax.set_title(tit); ax.legend()
    plt.tight_layout(); plt.savefig("fig_comparacion.png", dpi=150, bbox_inches="tight"); plt.close()


if __name__ == "__main__":
    main()
    