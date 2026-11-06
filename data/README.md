# Datos de Almansa Market S.A.

**Almansa Market S.A. es una empresa inventada y todos sus datos son sintéticos.** Los genera
[`generar_datos.py`](generar_datos.py) con una semilla fija, así que todo el mundo tiene exactamente los mismos
datos. Los nombres y los emails (dominios `example.*`) son ficticios.

- **Periodo:** del 1 de enero de 2025 al 31 de octubre de 2026.
- **Negocio:** 8 tiendas físicas (Madrid ×2, Barcelona, Valencia, Sevilla, Málaga, Bilbao y Zaragoza) y la tienda
  online (web y, desde septiembre de 2025, app).
- **Catálogo:** 108 productos en 6 categorías: Electrónica, Hogar, Deporte, Moda y complementos, Belleza y cuidado,
  Gourmet.

## Ficheros

| Fichero | Contenido |
|---|---|
| `almansa.db` | Base de datos SQLite con todas las tablas, las vistas, el diccionario y el buscador de documentos |
| `csv/` | Copias en CSV de las tablas (salvo `ventas` y `lineas_venta`, que están agregadas en `ventas_mensuales.csv`) |
| `docs/` | 13 documentos internos en Markdown (políticas, actas, contratos, informes, FAQ) |
| `generar_datos.py` y `generador/` | El generador. Para regenerar todo: `python data/generar_datos.py` |

## Tablas

| Tabla | Filas | Qué contiene |
|---|---:|---|
| `tiendas` | 9 | Tiendas físicas `T01`-`T08` y el canal online `WEB` |
| `productos` | 108 | Catálogo con precio de venta, coste, proveedor y fechas de alta y baja |
| `clientes` | 4.200 | Clientes identificados (tarjeta Almansa+ o compra online), segmento y consentimiento de marketing |
| `campanias` | 26 | Campañas de marketing con presupuesto, impresiones, clics, conversiones e ingresos atribuidos |
| `ventas` | 147.115 | Cabecera de cada pedido: fecha, tienda, canal, cliente, campaña, importes y estado |
| `lineas_venta` | 234.533 | Productos de cada pedido: unidades, precio, descuento e importe |
| `inventario` | 9.621 | Foto del stock a fin de mes (enero-octubre de 2026) por tienda y producto |
| `tickets_soporte` | 5.998 | Incidencias de atención al cliente: categoría, prioridad, horas de resolución y satisfacción |
| `resenas` | 5.432 | Reseñas de clientes en la web (de 1 a 5 estrellas) |
| `finanzas_mensuales` | 22 | Cuenta de resultados mensual simplificada (ingresos, costes, EBITDA) |
| `objetivos_2026` | 36 | Objetivo de ventas por tienda y trimestre de 2026 |
| `diccionario` | — | Descripción de tablas y columnas (lo que ves con `almansa.esquema()`) |
| `documentos` | — | Buscador de texto completo (SQLite FTS5) sobre `docs/` |
| `documentos_meta` | 13 | Título, fecha, versión y estado (vigente u obsoleto) de cada documento |

**Vistas recomendadas** (ahorran *joins*):

- `v_ventas_lineas`: cada línea de venta con fecha, `anio`, `mes` (`'2026-07'`), `trimestre` (`'2026-T3'`),
  tienda, comunidad, canal, producto, categoría, proveedor, importe y coste.
- `v_ventas_mensuales`: ventas **completadas** agregadas por mes, trimestre, tienda, canal y categoría (pedidos,
  unidades, ingresos netos y coste).

## Antes de sacar conclusiones

Como en cualquier empresa real, los datos tienen sus particularidades. Todas están en el diccionario
(`print(almansa.esquema())`); un buen agente (y un buen analista) las lee antes de calcular:

- **Ventas reales:** la tabla `ventas` incluye pedidos devueltos y cancelados. Filtra `estado = 'completada'`.
- **Importes:** en euros, con IVA incluido. `descuento_pct` está en tanto por uno (0,25 = 25 %).
- **Clientes anónimos:** `id_cliente` es `NULL` en las compras en tienda sin tarjeta.
- **Ciudades:** hay variantes de escritura (mayúsculas, espacios). Normaliza con `TRIM` y `LOWER` antes de agrupar.
- **Costes:** dos productos no tienen el coste informado (`NULL`).
- **Encuestas:** `satisfaccion` es `NULL` si el cliente no respondió.
- **Marketing y RGPD:** sin `consentimiento_marketing = 1` no se puede enviar publicidad a un cliente.
- **Documentos:** no todos están vigentes. Comprueba la fecha y el estado antes de citar una política.

## Ejemplos

```python
import almansa

almansa.consultar("""
    SELECT trimestre, ROUND(SUM(ingresos_netos)) AS ventas_eur
    FROM v_ventas_mensuales
    GROUP BY trimestre ORDER BY trimestre
""")

almansa.buscar_documentos("plazo de devolución")
```
