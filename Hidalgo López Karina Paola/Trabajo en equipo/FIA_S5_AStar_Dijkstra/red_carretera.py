"""
red_carretera.py
Red carretera simplificada del centro-sur de México.

- Coordenadas (lat, lon): ubicación aproximada del centro de cada ciudad.
- Distancias por carretera (km): VALORES APROXIMADOS redondeados, tomados como
  referencia de rutas federales/autopistas habituales. Verifícalos en Google Maps
  o en la SCT/SICT si necesitas citar cifras exactas en tu reporte.
"""

# nombre: (latitud, longitud)
CIUDADES = {
    "CDMX":        (19.4326, -99.1332),
    "Toluca":      (19.2826, -99.6557),
    "Cuernavaca":  (18.9186, -99.2342),
    "Puebla":      (19.0414, -98.2063),
    "Pachuca":     (20.1011, -98.7591),
    "Tlaxcala":    (19.3182, -98.2375),
    "Tula":        (20.0540, -99.3410),
    "Cuautla":     (18.8120, -98.9540),
    "Taxco":       (18.5563, -99.6050),
    "Acapulco":    (16.8531, -99.8237),
    "Morelia":     (19.7060, -101.1950),
    "San Juan del Río": (20.3883, -99.9967),
    "Querétaro":   (20.5888, -100.3899),
    "Celaya":      (20.5235, -100.8157),
    "Tehuacán":    (18.4667, -97.3922),
    "Orizaba":     (18.8500, -97.1000),
    "Veracruz":    (19.1738, -96.1342),
    "Jalapa":      (19.5438, -96.9102),
    "Oaxaca":      (17.0732, -96.7266),
}

# (ciudad_a, ciudad_b, km por carretera aprox.)  -- grafo NO dirigido y ponderado
CARRETERAS = [
    ("CDMX", "Toluca", 66),
    ("CDMX", "Cuernavaca", 85),
    ("CDMX", "Puebla", 130),
    ("CDMX", "Pachuca", 90),
    ("CDMX", "Tlaxcala", 115),
    ("CDMX", "Tula", 75),
    ("CDMX", "Cuautla", 100),
    ("CDMX", "San Juan del Río", 170),
    ("Toluca", "Morelia", 230),
    ("Toluca", "Taxco", 105),
    ("Toluca", "Cuernavaca", 85),
    ("Cuernavaca", "Taxco", 80),
    ("Cuernavaca", "Cuautla", 50),
    ("Cuernavaca", "Acapulco", 320),
    ("Taxco", "Acapulco", 230),
    ("Puebla", "Tlaxcala", 35),
    ("Puebla", "Tehuacán", 120),
    ("Puebla", "Orizaba", 130),
    ("Puebla", "Jalapa", 190),
    ("Puebla", "Cuautla", 110),
    ("Tehuacán", "Orizaba", 75),
    ("Tehuacán", "Oaxaca", 250),
    ("Orizaba", "Veracruz", 125),
    ("Jalapa", "Veracruz", 105),
    ("Pachuca", "Tula", 75),
    ("Tula", "San Juan del Río", 100),
    ("San Juan del Río", "Querétaro", 55),
    ("Querétaro", "Celaya", 52),
    ("Celaya", "Morelia", 175),
    ("Querétaro", "Morelia", 200),
]
