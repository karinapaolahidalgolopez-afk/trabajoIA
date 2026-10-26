"""
algoritmos.py
Implementación de Dijkstra y A* desde cero (heapq) con métricas de desempeño.
"""
import heapq
import math
import time

from red_carretera import CIUDADES, CARRETERAS


# ----------------------------------------------------------------------------
# Grafo y heurística
# ----------------------------------------------------------------------------
def construir_grafo():
    """Lista de adyacencia: {ciudad: [(vecino, km), ...]} (no dirigido)."""
    grafo = {c: [] for c in CIUDADES}
    for a, b, km in CARRETERAS:
        grafo[a].append((b, km))
        grafo[b].append((a, km))
    return grafo


def haversine(a, b):
    """Distancia en línea recta (km) entre dos ciudades. Heurística h(n)."""
    lat1, lon1 = map(math.radians, CIUDADES[a])
    lat2, lon2 = map(math.radians, CIUDADES[b])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    x = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(x))


# ----------------------------------------------------------------------------
# Algoritmos
# ----------------------------------------------------------------------------
def _reconstruir(padre, meta):
    camino, n = [], meta
    while n is not None:
        camino.append(n)
        n = padre[n]
    return camino[::-1]


def dijkstra(grafo, inicio, meta):
    """
    Dijkstra: expande siempre el nodo con menor g(n). Equivale a A* con h = 0.
    Devuelve (camino, costo, nodos_expandidos, orden_expansion, tiempo_s).
    """
    t0 = time.perf_counter()
    g = {inicio: 0.0}
    padre = {inicio: None}
    frontera = [(0.0, inicio)]
    cerrados, orden = set(), []

    while frontera:
        costo, n = heapq.heappop(frontera)
        if n in cerrados:
            continue
        cerrados.add(n)
        orden.append(n)
        if n == meta:
            return _reconstruir(padre, meta), costo, len(orden), orden, time.perf_counter() - t0
        for vecino, w in grafo[n]:
            nuevo = costo + w
            if nuevo < g.get(vecino, math.inf):
                g[vecino] = nuevo
                padre[vecino] = n
                heapq.heappush(frontera, (nuevo, vecino))
    return None, math.inf, len(orden), orden, time.perf_counter() - t0


def a_estrella(grafo, inicio, meta, h=haversine, peso=1.0):
    """
    A*: expande el nodo con menor f(n) = g(n) + peso * h(n).
    peso = 1  -> A* clásico (óptimo si h es admisible y consistente).
    peso > 1  -> heurística 'inflada' (puede perder admisibilidad / optimalidad).
    Devuelve (camino, costo, nodos_expandidos, orden_expansion, tiempo_s).
    """
    t0 = time.perf_counter()
    g = {inicio: 0.0}
    padre = {inicio: None}
    frontera = [(peso * h(inicio, meta), 0.0, inicio)]
    cerrados, orden = set(), []

    while frontera:
        _, costo, n = heapq.heappop(frontera)
        if n in cerrados:
            continue
        cerrados.add(n)
        orden.append(n)
        if n == meta:
            return _reconstruir(padre, meta), g[n], len(orden), orden, time.perf_counter() - t0
        for vecino, w in grafo[n]:
            nuevo = g[n] + w
            if nuevo < g.get(vecino, math.inf):
                g[vecino] = nuevo
                padre[vecino] = n
                heapq.heappush(frontera, (nuevo + peso * h(vecino, meta), nuevo, vecino))
    return None, math.inf, len(orden), orden, time.perf_counter() - t0


# ----------------------------------------------------------------------------
# Verificación formal de la heurística
# ----------------------------------------------------------------------------
def distancias_reales_a(grafo, meta):
    """h*(n): costo óptimo real de cada nodo a la meta (Dijkstra desde la meta)."""
    dist = {meta: 0.0}
    cola = [(0.0, meta)]
    while cola:
        d, n = heapq.heappop(cola)
        if d > dist.get(n, math.inf):
            continue
        for v, w in grafo[n]:
            if d + w < dist.get(v, math.inf):
                dist[v] = d + w
                heapq.heappush(cola, (d + w, v))
    return dist


def verificar_admisibilidad(grafo, meta, h=haversine):
    """Admisible: h(n) <= h*(n) para todo n. Devuelve lista de violaciones."""
    real = distancias_reales_a(grafo, meta)
    return [(n, h(n, meta), real[n]) for n in grafo if h(n, meta) > real[n] + 1e-9]


def verificar_consistencia(grafo, meta, h=haversine):
    """Consistente: h(n) <= c(n,n') + h(n') para toda arista. Devuelve violaciones."""
    malas = []
    for n, vecinos in grafo.items():
        for v, w in vecinos:
            if h(n, meta) > w + h(v, meta) + 1e-9:
                malas.append((n, v, h(n, meta), w + h(v, meta)))
    return malas
