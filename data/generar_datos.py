"""Genera el dataset sintético de Almansa Market S.A. (empresa ficticia, datos 100 % sintéticos).

Uso:   python data/generar_datos.py
Crea:  data/almansa.db  (SQLite: tablas, vistas, diccionario y buscador de documentos)
       data/csv/*.csv    (copias en CSV de las tablas principales)
Es determinista: la misma semilla produce siempre los mismos datos.
"""

import csv
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from generador import catalogo as C  # noqa: E402
from generador.simulacion import Simulador  # noqa: E402

DB = DIR / "almansa.db"
CSV_DIR = DIR / "csv"
DOCS_DIR = DIR / "docs"
PRODUCTOS_SIN_COSTE = ("Pañuelo de seda", "Pelota de pilates")

ESQUEMA = """
CREATE TABLE tiendas (id_tienda TEXT PRIMARY KEY, nombre TEXT, ciudad TEXT, comunidad TEXT, tipo TEXT,
    fecha_apertura TEXT, superficie_m2 INTEGER, responsable TEXT);
CREATE TABLE productos (id_producto TEXT PRIMARY KEY, nombre TEXT, categoria TEXT, subcategoria TEXT, marca TEXT,
    proveedor TEXT, precio_lista REAL, coste_unitario REAL, fecha_alta TEXT, fecha_baja TEXT, activo INTEGER);
CREATE TABLE clientes (id_cliente TEXT PRIMARY KEY, nombre TEXT, apellidos TEXT, email TEXT, ciudad TEXT,
    provincia TEXT, fecha_alta TEXT, rango_edad TEXT, segmento TEXT, canal_preferido TEXT,
    consentimiento_marketing INTEGER);
CREATE TABLE campanias (id_campania TEXT PRIMARY KEY, nombre TEXT, canal TEXT, categoria_objetivo TEXT,
    fecha_inicio TEXT, fecha_fin TEXT, ambito TEXT, presupuesto_eur REAL, impresiones INTEGER, clics INTEGER,
    conversiones INTEGER, ingresos_atribuidos_eur REAL);
CREATE TABLE ventas (id_venta TEXT PRIMARY KEY, fecha TEXT, id_tienda TEXT, canal TEXT, id_cliente TEXT,
    id_campania TEXT, metodo_pago TEXT, importe_bruto REAL, descuento REAL, importe_neto REAL, estado TEXT)
    WITHOUT ROWID;
CREATE TABLE lineas_venta (id_venta TEXT, num_linea INTEGER, id_producto TEXT, unidades INTEGER,
    precio_unitario REAL, descuento_pct REAL, importe_linea REAL, PRIMARY KEY (id_venta, num_linea)) WITHOUT ROWID;
CREATE TABLE inventario (fecha_corte TEXT, id_tienda TEXT, id_producto TEXT, stock_unidades INTEGER,
    stock_minimo INTEGER, PRIMARY KEY (fecha_corte, id_tienda, id_producto)) WITHOUT ROWID;
CREATE TABLE tickets_soporte (id_ticket TEXT PRIMARY KEY, fecha_apertura TEXT, id_cliente TEXT, id_venta TEXT,
    id_producto TEXT, canal TEXT, categoria TEXT, prioridad TEXT, estado TEXT, horas_resolucion REAL,
    satisfaccion INTEGER, resumen TEXT);
CREATE TABLE resenas (id_resena TEXT PRIMARY KEY, fecha TEXT, id_producto TEXT, id_cliente TEXT,
    puntuacion INTEGER, titulo TEXT, texto TEXT);
CREATE TABLE finanzas_mensuales (mes TEXT PRIMARY KEY, ingresos_netos REAL, coste_mercancia REAL,
    margen_bruto REAL, gasto_marketing REAL, gasto_personal REAL, gasto_alquileres REAL, gasto_logistica REAL,
    otros_gastos REAL, ebitda REAL);
CREATE TABLE objetivos_2026 (id_tienda TEXT, trimestre TEXT, objetivo_ventas_eur REAL,
    PRIMARY KEY (id_tienda, trimestre));
CREATE TABLE diccionario (tabla TEXT, columna TEXT, descripcion TEXT);
CREATE TABLE documentos_meta (doc TEXT PRIMARY KEY, titulo TEXT, fecha TEXT, version TEXT, estado TEXT);
CREATE VIRTUAL TABLE documentos USING fts5(doc UNINDEXED, titulo, seccion, texto,
    tokenize='unicode61 remove_diacritics 2');
CREATE INDEX ix_ventas_fecha ON ventas(fecha);
CREATE INDEX ix_ventas_tienda ON ventas(id_tienda);
CREATE INDEX ix_ventas_cliente ON ventas(id_cliente);
CREATE INDEX ix_lineas_producto ON lineas_venta(id_producto);
CREATE INDEX ix_tickets_fecha ON tickets_soporte(fecha_apertura);
CREATE INDEX ix_resenas_producto ON resenas(id_producto);
CREATE VIEW v_ventas_lineas AS
SELECT v.id_venta, v.fecha, substr(v.fecha, 1, 4) AS anio, substr(v.fecha, 1, 7) AS mes,
       substr(v.fecha, 1, 4) || '-T' || ((CAST(substr(v.fecha, 6, 2) AS INTEGER) + 2) / 3) AS trimestre,
       v.id_tienda, t.nombre AS tienda, t.comunidad, v.canal, v.id_cliente, v.id_campania, v.metodo_pago, v.estado,
       l.num_linea, l.id_producto, p.nombre AS producto, p.categoria, p.subcategoria, p.marca, p.proveedor,
       l.unidades, l.precio_unitario, l.descuento_pct, l.importe_linea,
       ROUND(l.unidades * p.coste_unitario, 2) AS coste_linea
FROM lineas_venta l JOIN ventas v ON v.id_venta = l.id_venta
JOIN productos p ON p.id_producto = l.id_producto JOIN tiendas t ON t.id_tienda = v.id_tienda;
CREATE VIEW v_ventas_mensuales AS
SELECT mes, trimestre, id_tienda, tienda, comunidad, canal, categoria,
       COUNT(DISTINCT id_venta) AS pedidos, SUM(unidades) AS unidades,
       ROUND(SUM(importe_linea), 2) AS ingresos_netos, ROUND(SUM(coste_linea), 2) AS coste
FROM v_ventas_lineas WHERE estado = 'completada'
GROUP BY mes, trimestre, id_tienda, tienda, comunidad, canal, categoria;
"""

DICCIONARIO = [
    ("tiendas", "*", "Tiendas físicas (T01-T08) y canal online (WEB)."),
    ("tiendas", "tipo", "'fisica' u 'online'."),
    ("productos", "*", "Catálogo: 108 productos en 6 categorías."),
    ("productos", "precio_lista", "Precio de venta al público con IVA, en euros."),
    ("productos", "coste_unitario", "Coste de compra en euros. ATENCIÓN: 2 productos tienen el coste sin informar (NULL)."),
    ("productos", "fecha_baja", "Fecha de descatalogación (NULL si sigue activo)."),
    ("clientes", "*", "Clientes identificados (tarjeta Almansa+ o compra online). Datos sintéticos: emails en dominios example.*."),
    ("clientes", "ciudad", "ATENCIÓN: hay variantes de escritura (mayúsculas, espacios). Normaliza con TRIM/LOWER antes de agrupar."),
    ("clientes", "segmento", "VIP (top 5 % de gasto), Fiel (6+ pedidos), Ocasional (2-5), Nuevo (0-1)."),
    ("clientes", "consentimiento_marketing", "1 si aceptó comunicaciones comerciales (RGPD). Sin consentimiento NO se le puede enviar marketing."),
    ("campanias", "*", "Campañas de marketing. ingresos_atribuidos_eur = suma de importe_neto de pedidos completados atribuidos."),
    ("campanias", "ambito", "'Todas' o el id de la tienda si es una campaña local."),
    ("ventas", "*", "Cabecera de pedido (un registro por ticket o pedido online)."),
    ("ventas", "canal", "'tienda', 'web' o 'app' (la app existe desde el 15/09/2025)."),
    ("ventas", "id_cliente", "NULL en compras anónimas en tienda."),
    ("ventas", "importe_neto", "Importe pagado tras descuentos, en euros (IVA incluido)."),
    ("ventas", "estado", "'completada', 'devuelta' o 'cancelada'. Para medir ventas reales filtra estado = 'completada'."),
    ("lineas_venta", "*", "Líneas de cada pedido (producto, unidades, precio y descuento)."),
    ("lineas_venta", "descuento_pct", "Descuento aplicado en tanto por uno (0.25 = 25 %)."),
    ("inventario", "*", "Foto del stock a fin de mes (enero-octubre 2026) por tienda y producto."),
    ("inventario", "stock_unidades", "0 = rotura de stock."),
    ("tickets_soporte", "*", "Incidencias de atención al cliente."),
    ("tickets_soporte", "satisfaccion", "Encuesta de 1 a 5 (NULL si el cliente no respondió o el ticket sigue abierto)."),
    ("resenas", "*", "Reseñas publicadas por clientes en la web (puntuación de 1 a 5)."),
    ("finanzas_mensuales", "*", "Cuenta de resultados mensual simplificada en euros (ventas completadas)."),
    ("objetivos_2026", "*", "Objetivo de ventas netas por tienda y trimestre de 2026 (formato '2026-T1')."),
    ("v_ventas_lineas", "*", "VISTA recomendada: líneas de venta con fecha, mes, trimestre, tienda, producto y categoría ya unidos."),
    ("v_ventas_mensuales", "*", "VISTA recomendada: ventas completadas agregadas por mes, tienda, canal y categoría."),
    ("documentos", "*", "Buscador de texto completo (FTS5) sobre los documentos internos de data/docs."),
]


def _prorrateo_mensual(campanias):
    gasto = defaultdict(float)
    for c in campanias:
        dias = (c["fin"] - c["ini"]).days + 1
        d = c["ini"]
        while d <= c["fin"]:
            gasto[d.strftime("%Y-%m")] += c["presupuesto"] / dias
            d += timedelta(days=1)
    return gasto


def _finanzas(sim):
    coste_real = {p["id_producto"]: p["coste_unitario"] for p in sim.productos}
    ingresos, cogs, envios = defaultdict(float), defaultdict(float), defaultdict(int)
    for v in sim.ventas:
        mes = v["fecha"][:7]
        if v["canal"] != "tienda" and v["estado"] != "cancelada":
            envios[mes] += 1
        if v["estado"] != "completada":
            continue
        ingresos[mes] += v["importe_neto"]
        for p, uds, _ in v["_lineas"]:
            cogs[mes] += uds * coste_real[p["id_producto"]]
    marketing = _prorrateo_mensual(sim.campanias)
    alquileres = sum(t[9] for t in C.TIENDAS)
    filas = []
    for mes in sorted(ingresos):
        personal = (8 * 7800 + 20000) * (1.12 if mes.endswith("-12") else 1.0)
        mk = marketing.get(mes, 0.0) + 2500
        logistica = 4.9 * envios[mes] + 1500
        otros = 0.02 * ingresos[mes] + 2000
        margen = ingresos[mes] - cogs[mes]
        ebitda = margen - personal - mk - alquileres - logistica - otros
        filas.append(dict(mes=mes, ingresos_netos=round(ingresos[mes], 2), coste_mercancia=round(cogs[mes], 2),
                          margen_bruto=round(margen, 2), gasto_marketing=round(mk, 2), gasto_personal=round(personal, 2),
                          gasto_alquileres=float(alquileres), gasto_logistica=round(logistica, 2),
                          otros_gastos=round(otros, 2), ebitda=round(ebitda, 2)))
    return filas


def _campanias(sim):
    conv, ingr = defaultdict(int), defaultdict(float)
    for v in sim.ventas:
        if v["id_campania"]:
            conv[v["id_campania"]] += 1
            if v["estado"] == "completada":
                ingr[v["id_campania"]] += v["importe_neto"]
    filas = []
    for c in sim.campanias:
        imp = int(c["presupuesto"] * C.IMPRESIONES_POR_EURO[c["canal"]] * sim.rng.uniform(0.85, 1.15))
        filas.append(dict(id_campania=c["id"], nombre=c["nombre"], canal=c["canal"], categoria_objetivo=c["cat"],
                          fecha_inicio=c["ini"].isoformat(), fecha_fin=c["fin"].isoformat(),
                          ambito=c["tienda"] or "Todas", presupuesto_eur=float(c["presupuesto"]), impresiones=imp,
                          clics=int(imp * C.CTR[c["canal"]] * sim.rng.uniform(0.8, 1.2)),
                          conversiones=conv[c["id"]], ingresos_atribuidos_eur=round(ingr[c["id"]], 2)))
    return filas


def _objetivos(sim):
    trimestral = defaultdict(float)
    for v in sim.ventas:
        if v["estado"] == "completada" and v["fecha"].startswith("2025"):
            trimestral[(v["id_tienda"], (int(v["fecha"][5:7]) + 2) // 3)] += v["importe_neto"]
    filas = []
    for t in C.TIENDAS:
        for q in range(1, 5):
            f = 1.18 if t[0] == "WEB" else 1.06
            if t[0] == "T04":
                f = {1: 0.55, 2: 1.10}.get(q, 1.06)
            filas.append(dict(id_tienda=t[0], trimestre=f"2026-T{q}",
                              objetivo_ventas_eur=round(trimestral[(t[0], q)] * f, -2)))
    return filas


def _documentos():
    meta, trozos = [], []
    for ruta in sorted(DOCS_DIR.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        titulo = next((l[2:].strip() for l in texto.splitlines() if l.startswith("# ")), ruta.stem)
        campo = lambda k: (re.search(rf"\*\*{k}:\*\*\s*(.+)", texto) or [None, ""])[1].strip()  # noqa: E731
        meta.append(dict(doc=ruta.name, titulo=titulo, fecha=campo("Fecha"), version=campo("Versión"),
                         estado=campo("Estado")))
        seccion, buffer = "Introducción", []
        for linea in texto.splitlines():
            if linea.startswith("## "):
                if "".join(buffer).strip():
                    trozos.append((ruta.name, titulo, seccion, "\n".join(buffer).strip()))
                seccion, buffer = linea[3:].strip(), []
            elif not linea.startswith("# "):
                buffer.append(linea)
        if "".join(buffer).strip():
            trozos.append((ruta.name, titulo, seccion, "\n".join(buffer).strip()))
    return meta, trozos


def _insertar(con, tabla, filas):
    if not filas:
        return
    cols = [k for k in filas[0] if not k.startswith("_")]
    con.executemany(f"INSERT INTO {tabla} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                    [[f.get(k) for k in cols] for f in filas])


def _exportar_csv(con):
    CSV_DIR.mkdir(exist_ok=True)
    for tabla in ["tiendas", "productos", "clientes", "campanias", "inventario", "tickets_soporte", "resenas",
                  "finanzas_mensuales", "objetivos_2026", "v_ventas_mensuales"]:
        cur = con.execute(f"SELECT * FROM {tabla}")
        nombre = "ventas_mensuales" if tabla == "v_ventas_mensuales" else tabla
        with open(CSV_DIR / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([d[0] for d in cur.description])
            w.writerows(cur)


def generar():
    sim = Simulador().simular().segmentar_clientes()
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(ESQUEMA)
    _insertar(con, "tiendas", [dict(id_tienda=t[0], nombre=t[1], ciudad=t[2], comunidad=t[3], tipo=t[4],
                                    fecha_apertura=t[5], superficie_m2=t[6], responsable=t[7]) for t in C.TIENDAS])
    _insertar(con, "productos", [dict(
        id_producto=p["id_producto"], nombre=p["nombre"], categoria=p["categoria"], subcategoria=p["subcategoria"],
        marca=p["marca"], proveedor=p["proveedor"], precio_lista=p["precio_lista"],
        coste_unitario=None if p["nombre"] in PRODUCTOS_SIN_COSTE else p["coste_unitario"],
        fecha_alta=p["fecha_alta"], fecha_baja=p["fecha_baja"], activo=0 if p["fecha_baja"] else 1)
        for p in sim.productos])
    _insertar(con, "clientes", [{k: c[k] for k in ("id_cliente", "nombre", "apellidos", "email", "ciudad", "provincia",
                                                   "fecha_alta", "rango_edad", "segmento", "canal_preferido",
                                                   "consentimiento_marketing")} for c in sim.clientes])
    _insertar(con, "campanias", _campanias(sim))
    _insertar(con, "ventas", sim.ventas)
    con.executemany("INSERT INTO lineas_venta VALUES (?,?,?,?,?,?,?)", sim.lineas)
    _insertar(con, "inventario", sim.inventario())
    _insertar(con, "tickets_soporte", sim.tickets)
    _insertar(con, "resenas", sim.resenas)
    _insertar(con, "finanzas_mensuales", _finanzas(sim))
    _insertar(con, "objetivos_2026", _objetivos(sim))
    con.executemany("INSERT INTO diccionario VALUES (?,?,?)", DICCIONARIO)
    meta, trozos = _documentos()
    _insertar(con, "documentos_meta", meta)
    con.executemany("INSERT INTO documentos (doc, titulo, seccion, texto) VALUES (?,?,?,?)", trozos)
    con.commit()
    _exportar_csv(con)
    con.execute("VACUUM")
    con.close()
    return sim


def comprobar():
    con = sqlite3.connect(DB)
    q = lambda sql: con.execute(sql).fetchall()  # noqa: E731
    print("Pedidos:", q("SELECT COUNT(*) FROM ventas")[0][0], "| líneas:", q("SELECT COUNT(*) FROM lineas_venta")[0][0],
          "| clientes:", q("SELECT COUNT(*) FROM clientes")[0][0], "| tickets:", q("SELECT COUNT(*) FROM tickets_soporte")[0][0],
          "| reseñas:", q("SELECT COUNT(*) FROM resenas")[0][0], "| trozos doc:", q("SELECT COUNT(*) FROM documentos")[0][0])
    for anio, ing, eb in q("SELECT substr(mes,1,4), ROUND(SUM(ingresos_netos)), ROUND(SUM(ebitda)) FROM finanzas_mensuales GROUP BY 1"):
        print(f"  {anio}: ingresos {ing:,.0f} €  EBITDA {eb:,.0f} € ({eb / ing:.1%})")
    print("  EBITDA jul-2026:", q("SELECT ebitda FROM finanzas_mensuales WHERE mes='2026-07'")[0][0])
    h = dict(q("SELECT trimestre, SUM(ingresos_netos) FROM v_ventas_mensuales WHERE categoria='Hogar' "
               "AND comunidad='Andalucía' AND trimestre IN ('2025-T3','2026-T3') GROUP BY 1"))
    print(f"  Hogar Andalucía T3: {h['2025-T3']:,.0f} -> {h['2026-T3']:,.0f} ({h['2026-T3'] / h['2025-T3'] - 1:+.1%})")
    for cid, nombre, pres, ingr in q("SELECT id_campania, nombre, presupuesto_eur, ingresos_atribuidos_eur FROM campanias "
                                     "WHERE id_campania IN ('CMP13','CMP14','CMP20','CMP23')"):
        print(f"  {cid} {nombre}: ROAS {ingr / pres:.2f}x")
    for periodo, nota, n in q("SELECT CASE WHEN r.fecha >= '2026-06-10' THEN 'después' ELSE 'antes' END, "
                              "ROUND(AVG(puntuacion),2), COUNT(*) FROM resenas r JOIN productos p USING(id_producto) "
                              "WHERE p.nombre='Auriculares Voltix Pro X' GROUP BY 1"):
        print(f"  Voltix Pro X {periodo}: nota media {nota} ({n} reseñas)")
    t4 = dict(q("SELECT trimestre, SUM(ingresos_netos) FROM v_ventas_mensuales WHERE id_tienda='T04' "
                "AND trimestre IN ('2025-T1','2026-T1','2025-T2','2026-T2') GROUP BY 1"))
    print("  Valencia T1/T2:", {k: round(v) for k, v in t4.items()})
    print("  Cuota app oct-2026:", q("SELECT ROUND(AVG(canal='app'),3) FROM ventas WHERE fecha LIKE '2026-10%' AND id_tienda='WEB'")[0][0])
    print("  Tickets envío dic-2025 vs nov-2025:",
          q("SELECT SUM(fecha_apertura LIKE '2025-12%'), SUM(fecha_apertura LIKE '2025-11%') FROM tickets_soporte WHERE categoria='Envío'")[0])
    con.close()


if __name__ == "__main__":
    generar()
    comprobar()
