import networkx as nx
import matplotlib.pyplot as plt

def generar_espacio_almacen():
    """
    Genera el espacio de búsqueda para el Problema 1: 
    Robot en almacén usando un grafo no dirigido y ponderado.
    """
    # Crear grafo vacío
    G = nx.Graph()
    
    # Añadir estados (nodos) y acciones/costes (aristas)
    # Formato: (NodoOrigen, NodoDestino, coste_distancia)
    conexiones = [
        ('A', 'B', 2), ('A', 'C', 5),
        ('B', 'D', 4), ('C', 'D', 1),
        ('C', 'E', 6), ('D', 'F', 3),
        ('E', 'F', 2), ('F', 'Meta', 1)
    ]
    
    G.add_weighted_edges_from(conexiones)
    return G

def visualizar_grafo(G):
    """
    Dibuja el diagrama del grafo para la entrega.
    """
    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Espacio de Búsqueda: Ruta del Robot en Almacén")
    plt.show()

# Ejecución
grafo_almacen = generar_espacio_almacen()
visualizar_grafo(grafo_almacen)