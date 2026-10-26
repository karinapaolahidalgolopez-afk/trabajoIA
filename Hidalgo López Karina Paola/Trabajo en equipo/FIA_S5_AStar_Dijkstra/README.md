# Actividad Parcial 2 · Sección 5 — A* vs Dijkstra

**Asignatura:** Fundamentos de Inteligencia Artificial · Politécnica de Atlautla
**Docente:** Mtro. Javier García Lara · **Equipo:** _(nombres de los integrantes)_

## Caso de estudio
Ruteo sobre una red carretera simplificada del centro de México (19 ciudades, 30 tramos).
Se compara **Dijkstra** contra **A\*** con heurística de distancia en línea recta (haversine)
en 6 consultas origen-destino.

## Estructura
```
red_carretera.py   # ciudades (lat/lon) y tramos (km aproximados)
algoritmos.py      # Dijkstra, A*, haversine, verificación de admisibilidad/consistencia
main.py            # experimentos + CSV + dashboard
resultados/        # dashboard.png y archivos CSV generados
```

## Cómo ejecutarlo
```bash
pip install -r requirements.txt
python main.py
```
Genera en `resultados/`: `dashboard.png`, `comparacion_a_vs_dijkstra.csv`,
`verificacion_heuristica.csv`, `heuristica_inflada.csv`.

## Notas
- Las distancias por carretera son **aproximadas** (redondeadas); sirven para comparar algoritmos.
- A* sólo es óptimo si h es admisible; `main.py` lo verifica contra el costo real h*(n).
- Declaración de uso de IA: ver pie del PDF de entrega.
