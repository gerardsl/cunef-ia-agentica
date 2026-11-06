"""Catálogo maestro de Almansa Market S.A. (empresa ficticia, datos 100 % sintéticos)."""

from datetime import date

INICIO = date(2025, 1, 1)
FIN = date(2026, 10, 31)

# id, nombre, ciudad, comunidad, tipo, apertura, m2, responsable, pedidos_dia_base, alquiler_mes
TIENDAS = [
    ("T01", "Almansa Madrid · Almansa", "Madrid", "Comunidad de Madrid", "fisica", "2009-03-14", 620, "Lucía Ortega", 34, 7500),
    ("T02", "Almansa Madrid · Salamanca", "Madrid", "Comunidad de Madrid", "fisica", "2012-10-05", 480, "Jorge Requena", 26, 6500),
    ("T03", "Almansa Barcelona · Gràcia", "Barcelona", "Cataluña", "fisica", "2014-04-22", 520, "Marta Puig", 28, 6500),
    ("T04", "Almansa Valencia · Ruzafa", "Valencia", "Comunitat Valenciana", "fisica", "2016-09-09", 450, "Andrés Climent", 21, 4500),
    ("T05", "Almansa Sevilla · Nervión", "Sevilla", "Andalucía", "fisica", "2017-05-18", 430, "Rocío Barrera", 21, 4000),
    ("T06", "Almansa Málaga · Centro", "Málaga", "Andalucía", "fisica", "2019-06-27", 400, "Pablo Navas", 19, 4000),
    ("T07", "Almansa Bilbao · Abando", "Bilbao", "País Vasco", "fisica", "2020-11-12", 380, "Itziar Goikoetxea", 16, 4500),
    ("T08", "Almansa Zaragoza · Delicias", "Zaragoza", "Aragón", "fisica", "2022-03-03", 350, "Sergio Lahoz", 13, 3500),
    ("WEB", "Almansa Online", "Online", "Online", "online", "2015-02-01", None, "Elena Martos", 30, 5000),
]

CATEGORIAS = ["Electrónica", "Hogar", "Deporte", "Moda y complementos", "Belleza y cuidado", "Gourmet"]

# Ratio coste/precio por categoría (margen bruto = 1 - ratio)
RATIO_COSTE = {
    "Electrónica": 0.68, "Hogar": 0.45, "Deporte": 0.50,
    "Moda y complementos": 0.42, "Belleza y cuidado": 0.38, "Gourmet": 0.60,
}

# (nombre, subcategoria, marca, proveedor, precio, popularidad, fecha_alta, fecha_baja)
PRODUCTOS = {
    "Electrónica": [
        ("Auriculares Voltix Pro X", "Audio", "Voltix", "ElectroIberia Distribución", 89.90, 2.0, "2025-02-15", None),
        ("Auriculares Voltix Lite", "Audio", "Voltix", "ElectroIberia Distribución", 39.90, 1.6, "2023-01-01", None),
        ("Auriculares deportivos Voltix Run", "Audio", "Voltix", "ElectroIberia Distribución", 59.90, 1.0, "2023-01-01", None),
        ("Altavoz Sonara Mini", "Audio", "Sonara", "ElectroIberia Distribución", 34.90, 1.4, "2023-01-01", None),
        ("Altavoz Sonara Max", "Audio", "Sonara", "ElectroIberia Distribución", 119.00, 0.7, "2023-01-01", None),
        ("Barra de sonido Sonara Cine", "Audio", "Sonara", "ElectroIberia Distribución", 179.00, 0.5, "2025-10-15", None),
        ("Smartwatch Pulsar S2", "Wearables", "Pulsar", "ElectroIberia Distribución", 149.00, 0.9, "2025-03-01", None),
        ("Pulsera de actividad Pulsar Fit", "Wearables", "Pulsar", "ElectroIberia Distribución", 49.90, 1.2, "2023-01-01", None),
        ("Cargador rápido Voltix 65W", "Accesorios", "Voltix", "ElectroIberia Distribución", 29.90, 1.5, "2023-01-01", None),
        ("Powerbank Voltix 20.000 mAh", "Accesorios", "Voltix", "ElectroIberia Distribución", 39.90, 1.3, "2023-01-01", None),
        ("Cable USB-C trenzado 2 m", "Accesorios", "Voltix", "ElectroIberia Distribución", 12.90, 2.0, "2023-01-01", None),
        ("Tablet Nébula 10\"", "Informática", "Nébula", "ElectroIberia Distribución", 229.00, 0.5, "2025-09-01", None),
        ("Funda para tablet Nébula", "Informática", "Nébula", "ElectroIberia Distribución", 24.90, 0.6, "2025-09-01", None),
        ("Teclado inalámbrico Kéntro", "Informática", "Kéntro", "ElectroIberia Distribución", 49.90, 0.8, "2023-01-01", None),
        ("Ratón ergonómico Kéntro", "Informática", "Kéntro", "ElectroIberia Distribución", 34.90, 0.9, "2023-01-01", None),
        ("Webcam Kéntro HD", "Informática", "Kéntro", "ElectroIberia Distribución", 59.90, 0.4, "2023-01-01", "2026-03-31"),
        ("Disco SSD portátil Datafy 1 TB", "Informática", "Datafy", "ElectroIberia Distribución", 99.00, 0.6, "2023-01-01", None),
        ("Lector de libros electrónicos Nébula Paper", "Informática", "Nébula", "ElectroIberia Distribución", 129.00, 0.4, "2024-05-01", None),
    ],
    "Hogar": [
        ("Juego de sábanas algodón 150", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 49.90, 1.6, "2023-01-01", None),
        ("Edredón nórdico 4 estaciones", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 89.90, 1.0, "2023-01-01", None),
        ("Pack 2 toallas de baño", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 24.90, 1.5, "2023-01-01", None),
        ("Cojín decorativo de lino", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 19.90, 1.3, "2023-01-01", None),
        ("Manta de sofá de punto", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 39.90, 1.1, "2023-01-01", None),
        ("Cortina opaca 140x260", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 34.90, 0.8, "2023-01-01", None),
        ("Alfombra de yute 160x230", "Textil hogar", "Kasa Viva", "Textiles Levante S.L.", 119.00, 0.5, "2023-01-01", None),
        ("Vela aromática Kasa Viva", "Decoración", "Kasa Viva", "Textiles Levante S.L.", 14.90, 1.2, "2023-01-01", None),
        ("Difusor de aromas", "Decoración", "Kasa Viva", "Textiles Levante S.L.", 29.90, 0.8, "2023-01-01", None),
        ("Organizador de armario", "Decoración", "Kasa Viva", "Textiles Levante S.L.", 22.90, 0.7, "2023-01-01", None),
        ("Sartén antiadherente 28 cm", "Cocina", "Nordhaus", "Menaje Atlántico", 32.90, 1.3, "2023-01-01", None),
        ("Batería de cocina 5 piezas", "Cocina", "Nordhaus", "Menaje Atlántico", 129.00, 0.5, "2023-01-01", None),
        ("Juego de cuchillos Nordhaus", "Cocina", "Nordhaus", "Menaje Atlántico", 59.90, 0.7, "2023-01-01", None),
        ("Cafetera italiana 6 tazas", "Cocina", "Nordhaus", "Menaje Atlántico", 27.90, 1.0, "2023-01-01", None),
        ("Set 6 vasos de cristal", "Cocina", "Nordhaus", "Menaje Atlántico", 18.90, 0.9, "2023-01-01", None),
        ("Lámpara de pie nórdica", "Iluminación", "Lumen&Co", "Lumen&Co Iluminación", 89.00, 0.5, "2023-01-01", None),
        ("Lámpara de escritorio LED", "Iluminación", "Lumen&Co", "Lumen&Co Iluminación", 39.90, 0.9, "2023-01-01", None),
        ("Pack 2 bombillas inteligentes", "Iluminación", "Lumen&Co", "Lumen&Co Iluminación", 24.90, 1.0, "2023-01-01", None),
    ],
    "Deporte": [
        ("Esterilla de yoga 6 mm", "Fitness", "Ritmo", "SportNorte", 29.90, 1.4, "2023-01-01", None),
        ("Mancuernas ajustables 2x10 kg", "Fitness", "Ritmo", "SportNorte", 89.90, 0.7, "2023-01-01", None),
        ("Set de bandas elásticas", "Fitness", "Ritmo", "SportNorte", 19.90, 1.2, "2023-01-01", None),
        ("Comba de velocidad", "Fitness", "Ritmo", "SportNorte", 12.90, 1.0, "2023-01-01", None),
        ("Rodillo de masaje", "Fitness", "Ritmo", "SportNorte", 24.90, 0.9, "2023-01-01", None),
        ("Pelota de pilates", "Fitness", "Ritmo", "SportNorte", 16.90, 0.7, "2023-01-01", None),
        ("Kettlebell 12 kg", "Fitness", "Ritmo", "SportNorte", 39.90, 0.6, "2026-01-05", None),
        ("Zapatillas running Ritmo Air", "Running", "Ritmo", "SportNorte", 79.90, 1.1, "2023-01-01", None),
        ("Camiseta técnica de running", "Running", "Ritmo", "SportNorte", 19.90, 1.4, "2023-01-01", None),
        ("Mallas de running", "Running", "Ritmo", "SportNorte", 29.90, 1.0, "2023-01-01", None),
        ("Gorra de running", "Running", "Ritmo", "SportNorte", 14.90, 0.8, "2023-01-01", None),
        ("Botella térmica 750 ml", "Outdoor", "Cumbre", "SportNorte", 22.90, 1.5, "2023-01-01", None),
        ("Mochila de trekking 30 L", "Outdoor", "Cumbre", "SportNorte", 69.90, 0.7, "2023-01-01", None),
        ("Bastones de trekking", "Outdoor", "Cumbre", "SportNorte", 49.90, 0.5, "2023-01-01", None),
        ("Chaqueta cortavientos", "Outdoor", "Cumbre", "SportNorte", 59.90, 0.8, "2023-01-01", None),
        ("Linterna frontal", "Outdoor", "Cumbre", "SportNorte", 24.90, 0.7, "2023-01-01", None),
        ("Tienda de campaña 2 plazas", "Outdoor", "Cumbre", "SportNorte", 129.00, 0.3, "2023-01-01", None),
        ("Saco de dormir", "Outdoor", "Cumbre", "SportNorte", 79.00, 0.4, "2023-01-01", None),
    ],
    "Moda y complementos": [
        ("Mochila urbana Altamar", "Bolsos y mochilas", "Altamar", "Altamar Textil", 49.90, 1.3, "2023-01-01", None),
        ("Bolso bandolera Bruma", "Bolsos y mochilas", "Bruma", "Altamar Textil", 39.90, 1.0, "2023-01-01", None),
        ("Riñonera Altamar", "Bolsos y mochilas", "Altamar", "Altamar Textil", 24.90, 0.8, "2023-01-01", None),
        ("Maleta de cabina", "Bolsos y mochilas", "Altamar", "Altamar Textil", 99.00, 0.5, "2023-01-01", None),
        ("Neceser de viaje", "Bolsos y mochilas", "Bruma", "Altamar Textil", 19.90, 0.8, "2023-01-01", None),
        ("Gafas de sol polarizadas", "Complementos", "Bruma", "Altamar Textil", 59.90, 1.0, "2023-01-01", None),
        ("Cartera de piel", "Complementos", "Altamar", "Altamar Textil", 34.90, 0.9, "2023-01-01", None),
        ("Cinturón de piel", "Complementos", "Altamar", "Altamar Textil", 29.90, 0.8, "2023-01-01", None),
        ("Reloj analógico Altamar", "Complementos", "Altamar", "Altamar Textil", 79.90, 0.5, "2023-01-01", None),
        ("Paraguas plegable", "Complementos", "Altamar", "Altamar Textil", 19.90, 1.0, "2023-01-01", None),
        ("Bufanda de lana merino", "Invierno", "Bruma", "Altamar Textil", 29.90, 0.9, "2023-01-01", None),
        ("Gorro de punto", "Invierno", "Bruma", "Altamar Textil", 16.90, 0.9, "2023-01-01", None),
        ("Guantes táctiles", "Invierno", "Bruma", "Altamar Textil", 19.90, 0.7, "2023-01-01", None),
        ("Pañuelo de seda", "Complementos", "Bruma", "Altamar Textil", 34.90, 0.5, "2023-01-01", None),
        ("Sudadera básica", "Ropa", "Altamar", "Altamar Textil", 34.90, 1.1, "2023-01-01", None),
        ("Camiseta de algodón orgánico", "Ropa", "Altamar", "Altamar Textil", 19.90, 1.4, "2023-01-01", None),
        ("Pack 5 pares de calcetines", "Ropa", "Altamar", "Altamar Textil", 14.90, 1.2, "2023-01-01", None),
        ("Zapatillas de lona", "Ropa", "Altamar", "Altamar Textil", 44.90, 0.9, "2023-01-01", None),
    ],
    "Belleza y cuidado": [
        ("Crema facial hidratante", "Cuidado facial", "Aura", "BelleCos Lab", 24.90, 1.4, "2023-01-01", None),
        ("Sérum de vitamina C", "Cuidado facial", "Aura", "BelleCos Lab", 29.90, 1.1, "2023-01-01", None),
        ("Contorno de ojos", "Cuidado facial", "Aura", "BelleCos Lab", 21.90, 0.7, "2023-01-01", None),
        ("Bruma facial hidratante", "Cuidado facial", "Aura", "BelleCos Lab", 12.90, 0.8, "2026-04-01", None),
        ("Protector solar SPF50", "Cuidado facial", "Aura", "BelleCos Lab", 19.90, 1.3, "2023-01-01", None),
        ("Champú sólido", "Cuidado corporal", "Verdea", "BelleCos Lab", 9.90, 1.2, "2023-01-01", None),
        ("Gel de ducha natural", "Cuidado corporal", "Verdea", "BelleCos Lab", 7.90, 1.4, "2023-01-01", None),
        ("Desodorante natural", "Cuidado corporal", "Verdea", "BelleCos Lab", 6.90, 1.1, "2023-01-01", None),
        ("Crema de manos", "Cuidado corporal", "Verdea", "BelleCos Lab", 5.90, 1.0, "2023-01-01", None),
        ("Aceite corporal", "Cuidado corporal", "Verdea", "BelleCos Lab", 16.90, 0.7, "2023-01-01", None),
        ("Pack 3 bálsamos labiales", "Cuidado corporal", "Verdea", "BelleCos Lab", 8.90, 0.9, "2023-01-01", None),
        ("Mascarilla capilar", "Cabello", "Verdea", "BelleCos Lab", 14.90, 0.8, "2023-01-01", None),
        ("Secador iónico Aura", "Cabello", "Aura", "BelleCos Lab", 59.90, 0.6, "2023-01-01", None),
        ("Plancha de pelo Aura", "Cabello", "Aura", "BelleCos Lab", 44.90, 0.6, "2023-01-01", None),
        ("Cepillo dental eléctrico", "Electro-belleza", "Aura", "BelleCos Lab", 49.90, 0.7, "2023-01-01", None),
        ("Afeitadora eléctrica", "Electro-belleza", "Aura", "BelleCos Lab", 79.90, 0.5, "2023-01-01", None),
        ("Kit de manicura", "Electro-belleza", "Aura", "BelleCos Lab", 19.90, 0.6, "2023-01-01", None),
        ("Perfume Agua Almansa 100 ml", "Perfumería", "Almansa Selección", "BelleCos Lab", 39.90, 0.9, "2023-01-01", None),
    ],
    "Gourmet": [
        ("Aceite de oliva virgen extra 1 L", "Despensa", "Oliva Real", "Gourmet del Sur", 12.90, 1.8, "2023-01-01", None),
        ("AOVE premium 500 ml", "Despensa", "Oliva Real", "Gourmet del Sur", 14.90, 1.0, "2023-01-01", None),
        ("Vinagre de Jerez", "Despensa", "Gourmet del Sur", "Gourmet del Sur", 6.90, 0.6, "2023-01-01", None),
        ("Pimentón de la Vera", "Despensa", "Gourmet del Sur", "Gourmet del Sur", 3.90, 0.7, "2023-01-01", None),
        ("Conservas de atún en aceite", "Despensa", "Gourmet del Sur", "Gourmet del Sur", 7.90, 1.1, "2023-01-01", None),
        ("Miel de romero", "Despensa", "Gourmet del Sur", "Gourmet del Sur", 8.90, 0.8, "2023-01-01", None),
        ("Mermelada de naranja amarga", "Despensa", "Gourmet del Sur", "Gourmet del Sur", 5.90, 0.6, "2023-01-01", None),
        ("Café en grano 1 kg", "Café y té", "Almansa Selección", "Gourmet del Sur", 19.90, 1.3, "2023-01-01", None),
        ("Café molido 250 g", "Café y té", "Almansa Selección", "Gourmet del Sur", 6.90, 1.6, "2023-01-01", None),
        ("Té verde matcha", "Café y té", "Almansa Selección", "Gourmet del Sur", 18.90, 0.6, "2026-02-01", None),
        ("Chocolate negro 85 %", "Dulces", "Almansa Selección", "Gourmet del Sur", 3.90, 1.5, "2023-01-01", None),
        ("Galletas artesanas", "Dulces", "Almansa Selección", "Gourmet del Sur", 4.90, 1.1, "2023-01-01", None),
        ("Turrón artesano", "Dulces", "Almansa Selección", "Gourmet del Sur", 9.90, 0.2, "2023-01-01", None),
        ("Frutos secos premium", "Dulces", "Almansa Selección", "Gourmet del Sur", 9.90, 0.9, "2023-01-01", None),
        ("Jamón ibérico loncheado 100 g", "Charcutería y quesos", "Gourmet del Sur", "Gourmet del Sur", 14.90, 1.0, "2023-01-01", None),
        ("Queso manchego curado", "Charcutería y quesos", "Gourmet del Sur", "Gourmet del Sur", 16.90, 0.8, "2023-01-01", None),
        ("Vino tinto crianza", "Bodega", "Gourmet del Sur", "Gourmet del Sur", 12.90, 0.9, "2023-01-01", None),
        ("Pack regalo gourmet", "Regalo", "Almansa Selección", "Gourmet del Sur", 49.90, 0.2, "2023-01-01", None),
    ],
}

PRODUCTO_DEFECTUOSO = "Auriculares Voltix Pro X"
PROVEEDOR_ROTURA = "Textiles Levante S.L."

# Peso relativo de cada categoría por tienda (se normaliza)
PESO_CATEGORIA_BASE = {"Electrónica": .24, "Hogar": .20, "Deporte": .16,
                       "Moda y complementos": .15, "Belleza y cuidado": .13, "Gourmet": .12}
AJUSTE_TIENDA = {
    "WEB": {"Electrónica": 1.3, "Gourmet": 0.6},
    "T03": {"Moda y complementos": 1.2},
    "T06": {"Belleza y cuidado": 1.15},
    "T07": {"Deporte": 1.25},
    "T05": {"Hogar": 1.1},
}

# Estacionalidad por categoría (enero..diciembre)
ESTACIONALIDAD = {
    "Electrónica": [0.9, 0.8, 0.9, 0.9, 0.9, 0.9, 1.0, 0.8, 1.1, 1.0, 1.5, 1.7],
    "Hogar": [1.2, 1.0, 1.0, 1.1, 1.0, 0.9, 0.9, 0.8, 1.1, 1.1, 1.0, 1.2],
    "Deporte": [1.5, 1.1, 1.0, 1.1, 1.2, 1.2, 1.0, 0.8, 1.1, 0.9, 0.9, 1.0],
    "Moda y complementos": [1.3, 1.0, 0.9, 1.0, 1.0, 1.0, 1.2, 1.0, 1.1, 1.1, 1.1, 1.4],
    "Belleza y cuidado": [0.9, 1.0, 0.9, 1.0, 1.1, 1.3, 1.3, 1.1, 0.9, 0.9, 1.0, 1.5],
    "Gourmet": [0.8, 0.8, 0.9, 0.9, 0.9, 0.8, 0.8, 0.8, 0.9, 1.0, 1.1, 2.2],
}
FACTOR_MES_PEDIDOS = [1.05, 0.90, 0.95, 1.0, 1.0, 1.0, 1.05, 0.85, 1.0, 1.0, 1.15, 1.40]
FACTOR_DIA_FISICA = [0.85, 0.85, 0.90, 0.95, 1.15, 1.45, 0.70]  # lunes..domingo
FACTOR_DIA_WEB = [1.10, 1.0, 1.0, 0.95, 0.95, 0.85, 1.15]

FESTIVOS = {
    "2025-01-01", "2025-01-06", "2025-04-18", "2025-05-01", "2025-08-15", "2025-10-13",
    "2025-11-01", "2025-12-08", "2025-12-25", "2026-01-01", "2026-01-06", "2026-04-03",
    "2026-05-01", "2026-08-15", "2026-10-12", "2026-12-08",
}

# id, nombre, canal, categoria_objetivo, inicio, fin, presupuesto, uplift, descuento, tienda (None = todas)
CAMPANIAS = [
    ("CMP01", "Rebajas de invierno 2025", "Redes sociales", "Moda y complementos", "2025-01-07", "2025-02-15", 9000, 1.25, 0.0, None),
    ("CMP02", "Propósitos fitness 2025", "Buscadores", "Deporte", "2025-01-02", "2025-01-31", 6000, 1.35, 0.10, None),
    ("CMP03", "San Valentín 2025", "Email", "Belleza y cuidado", "2025-02-03", "2025-02-14", 2500, 1.30, 0.10, None),
    ("CMP04", "Día del Padre 2025", "Redes sociales", "Electrónica", "2025-03-03", "2025-03-19", 5000, 1.30, 0.10, None),
    ("CMP05", "Primavera en casa 2025", "Influencers", "Hogar", "2025-04-01", "2025-04-30", 12000, 1.45, 0.10, None),
    ("CMP06", "Día de la Madre 2025", "Email", "Belleza y cuidado", "2025-04-21", "2025-05-04", 3000, 1.35, 0.10, None),
    ("CMP07", "Operación verano 2025", "Buscadores", "Deporte", "2025-05-15", "2025-06-30", 8000, 1.30, 0.0, None),
    ("CMP08", "Almansa Days 2025", "Redes sociales", "Electrónica", "2025-07-08", "2025-07-11", 10000, 2.20, 0.15, None),
    ("CMP09", "Rebajas de verano 2025", "Email", "Moda y complementos", "2025-07-01", "2025-08-31", 4000, 1.15, 0.0, None),
    ("CMP10", "Vuelta al cole 2025", "Buscadores", "Electrónica", "2025-08-25", "2025-09-21", 9000, 1.35, 0.05, None),
    ("CMP11", "Lanzamiento app Almansa", "Influencers", "Todas", "2025-09-15", "2025-10-15", 15000, 1.10, 0.0, None),
    ("CMP12", "Otoño gourmet 2025", "Email", "Gourmet", "2025-10-01", "2025-10-31", 2000, 1.30, 0.05, None),
    ("CMP13", "Black Friday 2025", "Redes sociales", "Electrónica", "2025-11-21", "2025-12-01", 20000, 2.00, 0.25, None),
    ("CMP14", "Navidad 2025 (campaña de marca)", "Exterior", "Gourmet", "2025-12-01", "2025-12-24", 25000, 1.10, 0.0, None),
    ("CMP15", "Regalos de Navidad 2025", "Email", "Belleza y cuidado", "2025-12-05", "2025-12-24", 4000, 1.25, 0.10, None),
    ("CMP16", "Rebajas de invierno 2026", "Redes sociales", "Moda y complementos", "2026-01-07", "2026-02-15", 9500, 1.25, 0.0, None),
    ("CMP17", "Propósitos fitness 2026", "Buscadores", "Deporte", "2026-01-02", "2026-01-31", 6500, 1.35, 0.10, None),
    ("CMP18", "Día del Padre 2026", "Redes sociales", "Electrónica", "2026-03-02", "2026-03-19", 5500, 1.30, 0.10, None),
    ("CMP19", "Reapertura Valencia", "Exterior", "Todas", "2026-03-16", "2026-04-15", 7000, 1.20, 0.10, "T04"),
    ("CMP20", "Primavera en casa 2026", "Influencers", "Hogar", "2026-04-01", "2026-04-30", 13000, 1.45, 0.10, None),
    ("CMP21", "Día de la Madre 2026", "Email", "Belleza y cuidado", "2026-04-20", "2026-05-03", 3200, 1.35, 0.10, None),
    ("CMP22", "Operación verano 2026", "Buscadores", "Deporte", "2026-05-15", "2026-06-30", 8500, 1.30, 0.0, None),
    ("CMP23", "Influencers Hogar verano 2026", "Influencers", "Hogar", "2026-07-01", "2026-08-15", 45000, 1.12, 0.15, None),
    ("CMP24", "Almansa Days 2026", "Redes sociales", "Electrónica", "2026-07-07", "2026-07-10", 11000, 2.20, 0.15, None),
    ("CMP25", "Vuelta al cole 2026", "Buscadores", "Electrónica", "2026-08-24", "2026-09-20", 9500, 1.35, 0.05, None),
    ("CMP26", "Otoño gourmet 2026", "Email", "Gourmet", "2026-10-01", "2026-10-31", 2200, 1.30, 0.05, None),
]
PROB_ATRIBUCION = {"Redes sociales": 0.35, "Buscadores": 0.40, "Email": 0.45, "Influencers": 0.30, "Exterior": 0.04}
IMPRESIONES_POR_EURO = {"Redes sociales": 160, "Buscadores": 45, "Email": 900, "Influencers": 220, "Exterior": 1200}
CTR = {"Redes sociales": 0.012, "Buscadores": 0.045, "Email": 0.03, "Influencers": 0.008, "Exterior": 0.0005}

NOMBRES = [
    "Lucía", "Sofía", "Martina", "María", "Julia", "Paula", "Valeria", "Emma", "Daniela", "Carla", "Alba", "Noa",
    "Sara", "Carmen", "Laura", "Ana", "Marta", "Elena", "Irene", "Claudia", "Nerea", "Andrea", "Cristina", "Raquel",
    "Hugo", "Martín", "Lucas", "Mateo", "Leo", "Daniel", "Alejandro", "Pablo", "Manuel", "Álvaro", "Adrián", "David",
    "Mario", "Diego", "Javier", "Sergio", "Jorge", "Carlos", "Antonio", "José", "Francisco", "Juan", "Miguel", "Rubén",
    "Iván", "Óscar", "Raúl", "Alberto", "Íker", "Unai", "Pau", "Jordi", "Nuria", "Montse", "Ainhoa", "Iratxe",
]
APELLIDOS = [
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez", "Gómez", "Martín",
    "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Molina",
    "Morales", "Suárez", "Ortega", "Delgado", "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Núñez", "Iglesias",
    "Medina", "Garrido", "Cortés", "Castillo", "Santos", "Lozano", "Guerrero", "Cano", "Prieto", "Méndez", "Cruz",
    "Calvo", "Gallego", "Vidal", "León", "Márquez", "Herrera", "Peña", "Flores", "Cabrera", "Campos", "Vega",
    "Fuentes", "Carrasco", "Diez", "Caballero", "Reyes", "Nieto", "Aguilar", "Pascual", "Santana", "Herrero",
    "Montero", "Lorenzo", "Hidalgo", "Giménez", "Ibáñez", "Ferrer", "Duran",
]
CIUDAD_TIENDA = {
    "T01": ("Madrid", "Madrid"), "T02": ("Madrid", "Madrid"), "T03": ("Barcelona", "Barcelona"),
    "T04": ("Valencia", "Valencia"), "T05": ("Sevilla", "Sevilla"), "T06": ("Málaga", "Málaga"),
    "T07": ("Bilbao", "Bizkaia"), "T08": ("Zaragoza", "Zaragoza"),
}
CIUDADES_WEB = [
    ("Murcia", "Murcia"), ("Valladolid", "Valladolid"), ("Alicante", "Alicante"), ("Granada", "Granada"),
    ("Córdoba", "Córdoba"), ("Palma", "Illes Balears"), ("Las Palmas de Gran Canaria", "Las Palmas"),
    ("A Coruña", "A Coruña"), ("Vigo", "Pontevedra"), ("Gijón", "Asturias"), ("Oviedo", "Asturias"),
    ("Santander", "Cantabria"), ("Pamplona", "Navarra"), ("Salamanca", "Salamanca"), ("Toledo", "Toledo"),
    ("Cádiz", "Cádiz"), ("Burgos", "Burgos"), ("León", "León"), ("Badajoz", "Badajoz"),
    ("Tarragona", "Tarragona"), ("Girona", "Girona"), ("Castellón de la Plana", "Castellón"),
    ("Getafe", "Madrid"), ("Alcalá de Henares", "Madrid"), ("Sabadell", "Barcelona"),
]
REPARTO_CLIENTES = {"T01": .17, "T02": .13, "T03": .13, "T04": .10, "T05": .09, "T06": .08, "T07": .07, "T08": .06, "WEB": .17}
RANGOS_EDAD = [("18-24", .10), ("25-34", .22), ("35-44", .25), ("45-54", .21), ("55-64", .13), ("65+", .09)]
DOMINIOS = ["example.com", "example.org", "example.net"]
