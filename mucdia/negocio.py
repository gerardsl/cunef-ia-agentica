"""Funciones de negocio de MUCDIA reutilizables como herramientas de agentes.

Todas devuelven texto compacto (CSV) pensado para que lo lea un modelo. Las fechas van en formato AAAA-MM-DD.
Solo cuentan los pedidos con estado 'completada' (las devoluciones y cancelaciones no son ventas).
"""

import re
from typing import Annotated

from .datos import a_texto, buscar_documentos, consultar

_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")

Desde = Annotated[str, "Fecha inicial en formato AAAA-MM-DD (incluida)"]
Hasta = Annotated[str, "Fecha final en formato AAAA-MM-DD (incluida)"]
Categoria = Annotated[str | None, "Categoría: Electrónica, Hogar, Deporte, Moda y complementos, Belleza y cuidado o Gourmet (opcional)"]
Tienda = Annotated[str | None, "Tienda: T01-T08 (físicas) o WEB (online) (opcional)"]


def _fechas(desde: str, hasta: str) -> str | None:
    if not (_FECHA.match(str(desde)) and _FECHA.match(str(hasta))):
        return "ERROR: las fechas deben tener el formato AAAA-MM-DD (por ejemplo 2026-07-01)."
    if desde > hasta:
        return "ERROR: 'desde' es posterior a 'hasta'."
    if hasta < "2025-01-01" or desde > "2026-10-31":
        return "AVISO: solo hay datos entre 2025-01-01 y 2026-10-31."
    return None


def ventas_por_categoria(desde: Desde, hasta: Hasta) -> str:
    """Ventas netas (€), pedidos y unidades por categoría de producto entre dos fechas (incluidas)."""
    if error := _fechas(desde, hasta):
        return error
    df = consultar(
        "SELECT categoria, ROUND(SUM(importe_linea), 2) AS ventas_netas_eur, COUNT(DISTINCT id_venta) AS pedidos, "
        "SUM(unidades) AS unidades FROM v_ventas_lineas WHERE estado = 'completada' AND fecha BETWEEN ? AND ? "
        "GROUP BY categoria ORDER BY ventas_netas_eur DESC", (desde, hasta))
    return a_texto(df)


def ventas_por_tienda(desde: Desde, hasta: Hasta, categoria: Categoria = None) -> str:
    """Ventas netas (€) por tienda (T01-T08 físicas, WEB = online) entre dos fechas, opcionalmente de una categoría."""
    if error := _fechas(desde, hasta):
        return error
    filtro, params = "", [desde, hasta]
    if categoria:
        filtro, params = " AND lower(categoria) = lower(?)", params + [categoria]
    df = consultar(
        "SELECT id_tienda, tienda, comunidad, ROUND(SUM(importe_linea), 2) AS ventas_netas_eur, "
        "COUNT(DISTINCT id_venta) AS pedidos FROM v_ventas_lineas WHERE estado = 'completada' "
        f"AND fecha BETWEEN ? AND ?{filtro} GROUP BY id_tienda, tienda, comunidad ORDER BY ventas_netas_eur DESC",
        tuple(params))
    return a_texto(df)


def ventas_mensuales(anio: Annotated[int, "Año: 2025 o 2026"], categoria: Categoria = None, id_tienda: Tienda = None) -> str:
    """Serie mensual de ventas netas (€) de un año, opcionalmente filtrada por categoría y/o tienda."""
    filtro, params = "", [f"{int(anio)}-%"]
    if categoria:
        filtro, params = filtro + " AND lower(categoria) = lower(?)", params + [categoria]
    if id_tienda:
        filtro, params = filtro + " AND id_tienda = ?", params + [id_tienda.upper()]
    df = consultar(f"SELECT mes, ROUND(SUM(ingresos_netos), 2) AS ventas_netas_eur, SUM(pedidos) AS pedidos "
                   f"FROM v_ventas_mensuales WHERE mes LIKE ?{filtro} GROUP BY mes ORDER BY mes", tuple(params))
    return a_texto(df)


def top_productos(desde: Desde, hasta: Hasta, n: Annotated[int, "Número de productos"] = 5, categoria: Categoria = None) -> str:
    """Los n productos con más ventas netas (€) entre dos fechas, opcionalmente de una categoría."""
    if error := _fechas(desde, hasta):
        return error
    filtro, params = "", [desde, hasta]
    if categoria:
        filtro, params = " AND lower(categoria) = lower(?)", params + [categoria]
    df = consultar(
        "SELECT producto, categoria, ROUND(SUM(importe_linea), 2) AS ventas_netas_eur, SUM(unidades) AS unidades "
        f"FROM v_ventas_lineas WHERE estado = 'completada' AND fecha BETWEEN ? AND ?{filtro} "
        "GROUP BY producto, categoria ORDER BY ventas_netas_eur DESC LIMIT ?", tuple(params + [int(n)]))
    return a_texto(df)


def roturas_de_stock(mes: Annotated[str, "Mes en formato AAAA-MM (2026-01 a 2026-10)"], id_tienda: Tienda = None) -> str:
    """Productos sin stock (roturas) en la foto de inventario de fin de mes. mes en formato AAAA-MM (solo 2026-01 a 2026-10)."""
    filtro, params = "", [f"{mes}%"]
    if id_tienda:
        filtro, params = " AND i.id_tienda = ?", params + [id_tienda.upper()]
    df = consultar(
        "SELECT i.fecha_corte, i.id_tienda, p.nombre AS producto, p.categoria, p.proveedor FROM inventario i "
        f"JOIN productos p USING (id_producto) WHERE i.fecha_corte LIKE ? AND i.stock_unidades = 0{filtro} "
        "ORDER BY i.id_tienda, p.categoria", tuple(params))
    return a_texto(df, limite=60)


def campanias(anio: Annotated[int | None, "Año de inicio de la campaña (opcional)"] = None) -> str:
    """Campañas de marketing con presupuesto, ventas atribuidas y ROAS (ventas atribuidas / presupuesto)."""
    filtro, params = ("WHERE fecha_inicio LIKE ?", (f"{int(anio)}-%",)) if anio else ("", ())
    df = consultar(
        "SELECT id_campania, nombre, canal, categoria_objetivo, fecha_inicio, fecha_fin, presupuesto_eur, "
        "ingresos_atribuidos_eur, ROUND(ingresos_atribuidos_eur / presupuesto_eur, 2) AS roas "
        f"FROM campanias {filtro} ORDER BY fecha_inicio", params)
    return a_texto(df)


def tickets_por_categoria(desde: Desde, hasta: Hasta) -> str:
    """Tickets de atención al cliente por categoría: número, horas medias de resolución y satisfacción media (1-5)."""
    if error := _fechas(desde, hasta):
        return error
    df = consultar(
        "SELECT categoria, COUNT(*) AS tickets, ROUND(AVG(horas_resolucion), 1) AS horas_medias, "
        "ROUND(AVG(satisfaccion), 2) AS satisfaccion_media FROM tickets_soporte "
        "WHERE fecha_apertura BETWEEN ? AND ? GROUP BY categoria ORDER BY tickets DESC", (desde, hasta))
    return a_texto(df)


def valoraciones_producto(producto: Annotated[str, "Nombre o parte del nombre del producto"], desde: Desde = "2025-01-01", hasta: Hasta = "2026-10-31") -> str:
    """Nota media, número de reseñas y tres reseñas recientes de un producto (búsqueda por nombre parcial)."""
    if error := _fechas(desde, hasta):
        return error
    df = consultar(
        "SELECT p.nombre AS producto, ROUND(AVG(r.puntuacion), 2) AS nota_media, COUNT(*) AS resenas "
        "FROM resenas r JOIN productos p USING (id_producto) WHERE lower(p.nombre) LIKE lower(?) "
        "AND r.fecha BETWEEN ? AND ? GROUP BY p.nombre", (f"%{producto}%", desde, hasta))
    if df.empty:
        return f"No hay reseñas de productos que contengan '{producto}' en ese periodo."
    ejemplos = consultar(
        "SELECT r.fecha, r.puntuacion, r.titulo, r.texto FROM resenas r JOIN productos p USING (id_producto) "
        "WHERE lower(p.nombre) LIKE lower(?) AND r.fecha BETWEEN ? AND ? ORDER BY r.fecha DESC LIMIT 3",
        (f"%{producto}%", desde, hasta))
    return a_texto(df) + "\n\nReseñas recientes:\n" + a_texto(ejemplos)


def objetivos_vs_real(trimestre: Annotated[str, "Trimestre de 2026 en formato 2026-T1 ... 2026-T4"]) -> str:
    """Compara ventas reales con el objetivo de 2026 por tienda. trimestre en formato '2026-T1'..'2026-T4'."""
    df = consultar(
        "SELECT o.id_tienda, o.objetivo_ventas_eur, ROUND(COALESCE(SUM(m.ingresos_netos), 0), 2) AS ventas_reales_eur, "
        "ROUND(100.0 * COALESCE(SUM(m.ingresos_netos), 0) / o.objetivo_ventas_eur - 100, 1) AS desviacion_pct "
        "FROM objetivos_2026 o LEFT JOIN v_ventas_mensuales m ON m.id_tienda = o.id_tienda AND m.trimestre = o.trimestre "
        "WHERE o.trimestre = ? GROUP BY o.id_tienda, o.objetivo_ventas_eur ORDER BY desviacion_pct", (trimestre,))
    return a_texto(df)


def buscar_en_documentos(consulta: Annotated[str, "Palabras clave de lo que buscas"]) -> str:
    """Busca en los documentos internos (políticas, actas, contratos, informes) y devuelve los fragmentos más relevantes con su fuente."""
    resultados = buscar_documentos(consulta, k=4)
    if not resultados:
        return "No se encontraron documentos relevantes. Prueba con otras palabras clave."
    return "\n\n".join(f"[{r['doc']} · {r['seccion']}] (estado: {r['estado']}; fecha: {r['fecha']})\n{r['texto']}"
                       for r in resultados)


HERRAMIENTAS_ANALISIS = [ventas_por_categoria, ventas_por_tienda, ventas_mensuales, top_productos,
                         roturas_de_stock, campanias, tickets_por_categoria, valoraciones_producto, objetivos_vs_real]
