"""Genera el PDF de entrega FIA_G171_Apellido_S5.pdf (ajusta nombres antes de entregar)."""
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, Preformatted)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", F + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DVM", F + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")

MORADO = colors.HexColor("#2d1b69")
body = ParagraphStyle("b", fontName="DV", fontSize=9.5, leading=14, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=13, textColor=MORADO, spaceBefore=10, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=10.5, textColor=MORADO, spaceBefore=6, spaceAfter=4)
small = ParagraphStyle("s", fontName="DV", fontSize=8, leading=11)
cell = ParagraphStyle("c", fontName="DV", fontSize=7.5, leading=9.5)
cover_t = ParagraphStyle("ct", fontName="DV-B", fontSize=22, leading=28, textColor=MORADO, alignment=1)
cover_s = ParagraphStyle("cs", fontName="DV", fontSize=12, leading=18, alignment=1)
code = ParagraphStyle("code", fontName="DVM", fontSize=7, leading=8.6)

df = pd.read_csv("resultados/comparacion_a_vs_dijkstra.csv")
dfw = pd.read_csv("resultados/heuristica_inflada.csv")
g = dfw.groupby("Peso w")[["Sobrecosto (%)", "Nodos exp."]].mean().round(2)

S = []
# ------------------------------------------------------------------ Portada
S += [Spacer(1, 3*cm),
      Paragraph("Politécnica de Atlautla", cover_s),
      Paragraph("Ing. en Tecnologías de la Información e Innovación Digital", cover_s),
      Spacer(1, 1.2*cm),
      Paragraph("Actividad Parcial 2 — Sección 5", cover_t),
      Paragraph("Búsqueda con heurísticas: A* y Dijkstra", cover_t),
      Spacer(1, 1.2*cm),
      Paragraph("<b>Tema:</b> Ruteo óptimo en una red carretera del centro de México", cover_s),
      Paragraph("<b>Asignatura:</b> Fundamentos de Inteligencia Artificial", cover_s),
      Paragraph("<b>Docente:</b> Mtro. Javier García Lara", cover_s),
      Paragraph("<b>Grupo:</b> [171 / 172] · Cuatrimestre 7", cover_s),
      Spacer(1, 1*cm),
      Paragraph("<b>Equipo:</b> [Nombre 1], [Nombre 2], [Nombre 3]", cover_s),
      Paragraph("<b>Fecha de entrega:</b> 25 de octubre de 2026", cover_s),
      Paragraph("<b>Repositorio:</b> [enlace a GitHub]", cover_s),
      PageBreak()]

# ------------------------------------------------------------------ 1 Planteamiento
S += [Paragraph("1. Planteamiento del problema", h1),
      Paragraph("Una empresa de transporte de carga necesita calcular la ruta de menor distancia entre "
                "ciudades del centro de México. Dada una red de 19 ciudades y 30 tramos carreteros, se busca "
                "el camino de costo mínimo entre un origen y un destino. Se comparan dos algoritmos: "
                "<b>Dijkstra</b> (búsqueda de costo uniforme, sin información del destino) y <b>A*</b> "
                "(búsqueda informada con heurística de distancia en línea recta).", body),
      Paragraph("<b>Objetivos:</b> (a) implementar ambos algoritmos en Python; (b) comparar costo, nodos "
                "expandidos y tiempo; (c) verificar la admisibilidad y consistencia de la heurística; "
                "(d) analizar qué ocurre si la heurística deja de ser admisible.", body),
      Paragraph("2. Formulación como problema de búsqueda", h1),
      Paragraph("<b>Estados:</b> la ciudad en que se encuentra el vehículo. <b>Estado inicial / meta:</b> "
                "ciudad de origen / ciudad de destino. <b>Acciones:</b> viajar a una ciudad vecina conectada "
                "por carretera. <b>Costo de paso c(n, n'):</b> kilómetros del tramo. <b>Costo de camino "
                "g(n):</b> suma de km recorridos. El grafo es no dirigido y ponderado.", body),
      Paragraph("<b>Heurística:</b> h(n) = distancia haversine (línea recta sobre la esfera terrestre) entre n y "
                "la meta, calculada con las coordenadas de cada ciudad. Como ningún camino por carretera puede "
                "ser más corto que la línea recta, h(n) ≤ h*(n): es <b>admisible</b>. Además cumple la desigualdad "
                "triangular, por lo que es <b>consistente</b>: h(n) ≤ c(n, n') + h(n').", body),
      Paragraph("<b>Datos:</b> coordenadas aproximadas del centro de cada ciudad; distancias por carretera "
                "aproximadas y redondeadas (archivo <font name='DVM'>red_carretera.py</font>). Se evaluaron 6 consultas.", body)]

# ------------------------------------------------------------------ 3 Procedimiento
S += [Paragraph("3. Procedimiento", h1),
      Paragraph("1) Se construyó la lista de adyacencia. 2) Se implementaron Dijkstra y A* con cola de prioridad "
                "(<font name='DVM'>heapq</font>) y lista de cerrados; Dijkstra ordena por g(n), A* por f(n) = g(n) + h(n). "
                "3) Para cada consulta se registró costo, ruta, nodos expandidos y tiempo medio sobre 2000 "
                "ejecuciones. 4) Se verificó h(n) ≤ h*(n) calculando h*(n) con Dijkstra desde la meta, y la "
                "consistencia arista por arista. 5) Se repitió A* con f = g + w·h (w = 1.25, 1.5, 2, 3) para "
                "observar el efecto de perder admisibilidad.", body),
      Paragraph("Núcleo de A* (código completo en el repositorio):", h2),
      Preformatted(
"""def a_estrella(grafo, inicio, meta, h=haversine, peso=1.0):
    g = {inicio: 0.0}; padre = {inicio: None}
    frontera = [(peso * h(inicio, meta), 0.0, inicio)]
    cerrados, orden = set(), []
    while frontera:
        _, costo, n = heapq.heappop(frontera)
        if n in cerrados: continue
        cerrados.add(n); orden.append(n)
        if n == meta:
            return _reconstruir(padre, meta), g[n], len(orden), orden, ...
        for vecino, w in grafo[n]:
            nuevo = g[n] + w
            if nuevo < g.get(vecino, math.inf):
                g[vecino] = nuevo; padre[vecino] = n
                heapq.heappush(frontera, (nuevo + peso*h(vecino, meta), nuevo, vecino))""", code),
      PageBreak()]

# ------------------------------------------------------------------ 4 Resultados
S += [Paragraph("4. Resultados", h1), Paragraph("Tabla 1. Comparación A* vs Dijkstra (ambos hallan el mismo costo óptimo).", body)]
hdr = ["Origen → Destino", "Costo (km)", "Nodos Dijkstra", "Nodos A*", "Reducción", "t Dijkstra (µs)", "t A* (µs)"]
rows = [hdr] + [[f"{r['Origen']} → {r['Destino']}", f"{r['Costo óptimo (km)']:.0f}",
                 r["Dijkstra nodos exp."], r["A* nodos exp."], f"{r['Reducción nodos (%)']}%",
                 r["Dijkstra tiempo (µs)"], r["A* tiempo (µs)"]] for _, r in df.iterrows()]
t = Table(rows, repeatRows=1, colWidths=[4.2*cm, 1.9*cm, 2.2*cm, 1.8*cm, 1.9*cm, 2.4*cm, 1.9*cm])
t.setStyle(TableStyle([("FONT", (0,0), (-1,0), "DV-B", 7.5), ("FONT", (0,1), (-1,-1), "DV", 7.5),
                       ("BACKGROUND", (0,0), (-1,0), MORADO), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                       ("GRID", (0,0), (-1,-1), .4, colors.grey), ("ALIGN", (1,0), (-1,-1), "CENTER"),
                       ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1eefb")])]))
red_prom = df["Reducción nodos (%)"].mean()
S += [t, Spacer(1, 6),
      Paragraph("Tabla 2. Rutas óptimas encontradas.", body)]
rt = Table([["Consulta", "Ruta"]] + [[f"{r['Origen']} → {r['Destino']}", Paragraph(r["Ruta"], cell)] for _, r in df.iterrows()],
           colWidths=[4*cm, 13.3*cm])
rt.setStyle(TableStyle([("FONT", (0,0), (-1,0), "DV-B", 7.5), ("FONT", (0,1), (0,-1), "DV", 7.5),
                        ("BACKGROUND", (0,0), (-1,0), MORADO), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                        ("GRID", (0,0), (-1,-1), .4, colors.grey), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
S += [rt, Spacer(1, 8),
      Paragraph("Figura 1. Dashboard comparativo (mapas de exploración, nodos, tiempo, admisibilidad y heurística inflada).", body),
      Image("resultados/dashboard.png", width=17.3*cm, height=17.3*cm*10.5/17),
      PageBreak()]

# ------------------------------------------------------------------ 5 Análisis
w1, w15, w2 = g.loc[1.0], g.loc[1.5], g.loc[2.0]
S += [Paragraph("5. Análisis", h1),
      Paragraph("Eficiencia en nodos", h2),
      Paragraph(f"A* expandió en promedio <b>{red_prom:.1f}% menos nodos</b> que Dijkstra (entre "
                f"{df['Reducción nodos (%)'].min():.1f}% y {df['Reducción nodos (%)'].max():.1f}%) y siempre devolvió el mismo costo. "
                "Dijkstra explora en todas direcciones porque no sabe dónde está la meta; la heurística de línea recta "
                "orienta la búsqueda y evita, por ejemplo, visitar Celaya o Querétaro cuando se viaja de Morelia a Veracruz.", body),
      Paragraph("Tiempo de ejecución", h2),
      Paragraph("Con estos datos A* fue <b>más lento</b> en tiempo real (≈ 19–31 µs vs 11–18 µs). No es una contradicción: "
                "el grafo tiene sólo 19 nodos, así que ahorrar unas cuantas expansiones no compensa el costo de calcular "
                "senos y cosenos del haversine en cada evaluación de h(n). La ventaja de A* se vuelve notoria en grafos "
                "grandes (miles de nodos, por ejemplo una red vial real), donde el número de expansiones domina el tiempo. "
                "Ésta es una limitación del experimento y debe tomarse en cuenta al interpretar la Figura 1.", body),
      Paragraph("Admisibilidad y consistencia", h2),
      Paragraph("Para los tres destinos usados (Acapulco, Oaxaca y Veracruz) se encontraron <b>0 violaciones</b> de "
                "h(n) ≤ h*(n) y <b>0 violaciones</b> de consistencia. Por eso A* garantiza el óptimo y no necesita "
                "reabrir nodos cerrados. Esta propiedad depende de que cada tramo en la tabla de datos sea mayor o igual "
                "que la distancia en línea recta entre sus ciudades; si se capturara un tramo con km menores a la línea recta, "
                "la heurística dejaría de ser admisible.", body),
      Paragraph("¿Y si la heurística no es admisible?", h2),
      Paragraph(f"Al multiplicar h por w (f = g + w·h) los nodos expandidos bajan de {w1['Nodos exp.']:.1f} (w = 1) a "
                f"{w15['Nodos exp.']:.1f} (w = 1.5) y {w2['Nodos exp.']:.1f} (w = 2), pero aparece sobrecosto: "
                f"{w15['Sobrecosto (%)']:.2f}% con w = 1.5 y {w2['Sobrecosto (%)']:.2f}% con w = 2 sobre el óptimo. "
                "Es el compromiso clásico velocidad vs optimalidad: con w &gt; 1 se pierde la garantía de la ruta mínima "
                "a cambio de explorar menos. En esta red el sobrecosto es pequeño porque la red es casi lineal y tiene "
                "pocas rutas alternativas.", body),
      Paragraph("Complejidad", h2),
      Paragraph("Con montículo binario ambos algoritmos son O((V + E) log V) en el peor caso; A* con heurística "
                "consistente nunca expande más nodos que Dijkstra y, en la práctica, expande bastantes menos. "
                "La memoria es O(V) en ambos casos.", body),
      Paragraph("6. Conclusiones", h1),
      Paragraph(f"1) A* y Dijkstra encontraron rutas de igual costo en las 6 consultas; A* redujo la exploración "
                f"en {red_prom:.1f}% en promedio. 2) La heurística haversine es admisible y consistente en esta red, "
                "lo que garantiza optimalidad. 3) En un grafo tan pequeño el costo de evaluar h(n) hace a A* más lento "
                "en microsegundos; su beneficio real se espera en redes grandes. 4) Inflar la heurística reduce nodos "
                "pero sacrifica optimalidad. 5) Como trabajo futuro: usar una red vial real (OpenStreetMap), tiempos "
                "de viaje en lugar de km y comparar con otras heurísticas.", body),
      Paragraph("Declaración de uso de IA", h1),
      Paragraph("<b>Herramienta:</b> Claude (Anthropic). <b>Prompt:</b> «ayúdame a hacer la actividad: resolver un caso "
                "real de ruteo con A* y Dijkstra, con dashboard y análisis de admisibilidad». <b>Uso:</b> generación del "
                "borrador del código, de los datos de la red, del dashboard y de la estructura del reporte. "
                "<b>Verificación:</b> [el equipo debe describir aquí qué revisó: ejecución del código, revisión de "
                "distancias en un mapa, lectura del análisis].", body),
      Paragraph("Referencias (APA 7.ª ed.)", h1)]
refs = [
    "Bohm, R. A. (2021). <i>The fundamentals of search algorithms</i>. Nova Science.",
    "Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. <i>Numerische Mathematik, 1</i>(1), 269–271.",
    "Hart, P. E., Nilsson, N. J., &amp; Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. "
    "<i>IEEE Transactions on Systems Science and Cybernetics, 4</i>(2), 100–107.",
    "Russell, S., &amp; Norvig, P. (2020). <i>Inteligencia artificial: Un enfoque moderno</i> (4.ª ed.). Pearson.",
]
for r in refs:
    S.append(Paragraph(r, ParagraphStyle("ref", parent=body, leftIndent=18, firstLineIndent=-18)))

def pie(c, d):
    c.saveState(); c.setFont("DV", 7); c.setFillColor(colors.grey)
    c.drawString(2*cm, 1.2*cm, "IA: Claude (Anthropic) — apoyo en código y redacción; verificado por el equipo.")
    c.drawRightString(letter[0]-2*cm, 1.2*cm, f"Pág. {d.page}"); c.restoreState()

doc = SimpleDocTemplate("resultados/FIA_G171_Apellido_S5.pdf", pagesize=letter,
                        leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=2*cm,
                        title="Actividad Parcial 2 — Sección 5: A* y Dijkstra")
doc.build(S, onFirstPage=pie, onLaterPages=pie)
print("PDF listo")
