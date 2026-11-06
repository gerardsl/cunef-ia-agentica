"""Simulación determinista de la actividad de MUCDIA S.A. (empresa ficticia)."""

import math
import random
import unicodedata
from bisect import bisect_right
from collections import defaultdict
from datetime import date, timedelta
from itertools import accumulate

from . import catalogo as C
from . import textos as X

RIESGO_DEVOLUCION = {"Electrónica": .05, "Hogar": .03, "Deporte": .04, "Moda y complementos": .085,
                     "Belleza y cuidado": .02, "Gourmet": .005}
BLACK_FRIDAY = (date(2025, 11, 21), date(2025, 12, 1))
NAVIDAD_LOGIRAPIDO = (date(2025, 12, 1), date(2025, 12, 31))
CIERRE_VALENCIA = (date(2026, 2, 1), date(2026, 3, 15))
ROTURA_ANDALUCIA = (date(2026, 7, 1), date(2026, 9, 30))
ROTURA_WEB = (date(2026, 7, 15), date(2026, 9, 15))
FALLO_BATERIA = date(2026, 6, 1)
LANZAMIENTO_APP = date(2025, 9, 15)
REBAJAS = [(date(2025, 1, 7), date(2025, 2, 28)), (date(2025, 7, 1), date(2025, 8, 31)),
           (date(2026, 1, 7), date(2026, 2, 28)), (date(2026, 7, 1), date(2026, 8, 31))]


def _d(s):
    return date.fromisoformat(s)


def _ascii(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").replace(" ", "")


def _entre(d, rango):
    return rango[0] <= d <= rango[1]


class Simulador:
    def __init__(self, semilla=2026):
        self.rng = random.Random(semilla)
        self.tiendas = {t[0]: t for t in C.TIENDAS}
        self.ventas, self.lineas, self.tickets, self.resenas, self.perdidas = [], [], [], [], []
        self.n_venta = 0
        self._crear_productos()
        self._crear_clientes()
        self._preparar_pools()
        self.campanias = [dict(id=c[0], nombre=c[1], canal=c[2], cat=c[3], ini=_d(c[4]), fin=_d(c[5]),
                               presupuesto=c[6], uplift=c[7], desc=c[8], tienda=c[9]) for c in C.CAMPANIAS]

    # ------------------------------------------------------------------ maestros
    def _crear_productos(self):
        self.productos, n = [], 1
        for cat in C.CATEGORIAS:
            for nombre, sub, marca, prov, precio, pop, alta, baja in C.PRODUCTOS[cat]:
                coste = round(precio * C.RATIO_COSTE[cat] * self.rng.uniform(0.92, 1.08), 2)
                self.productos.append(dict(
                    id_producto=f"P{n:03d}", nombre=nombre, categoria=cat, subcategoria=sub, marca=marca,
                    proveedor=prov, precio_lista=precio, coste_unitario=coste, popularidad=pop,
                    fecha_alta=alta, fecha_baja=baja, calidad=self.rng.uniform(3.7, 4.6)))
                n += 1
        self.por_cat = defaultdict(list)
        for p in self.productos:
            self.por_cat[p["categoria"]].append(p)
        self.p_def = next(p for p in self.productos if p["nombre"] == C.PRODUCTO_DEFECTUOSO)
        self.p_def["calidad"] = 4.3

    def _crear_clientes(self, n=4200):
        rng, usados = self.rng, set()
        homes = list(C.REPARTO_CLIENTES)
        pesos = [C.REPARTO_CLIENTES[h] for h in homes]
        edades, pesos_edad = zip(*C.RANGOS_EDAD)
        span_old = (date(2024, 12, 31) - date(2015, 1, 1)).days
        span_new = (date(2026, 10, 15) - C.INICIO).days
        self.clientes = []
        for i in range(1, n + 1):
            home = rng.choices(homes, pesos)[0]
            ciudad, prov = rng.choice(C.CIUDADES_WEB) if home == "WEB" else C.CIUDAD_TIENDA[home]
            nombre, ap1, ap2 = rng.choice(C.NOMBRES), rng.choice(C.APELLIDOS), rng.choice(C.APELLIDOS)
            base = f"{_ascii(nombre)}.{_ascii(ap1)}".lower()
            email, k = f"{base}@{rng.choice(C.DOMINIOS)}", 2
            while email in usados:
                email, k = f"{base}{k}@{rng.choice(C.DOMINIOS)}", k + 1
            usados.add(email)
            if rng.random() < 0.85:
                alta = date(2015, 1, 1) + timedelta(days=int((rng.random() ** 0.6) * span_old))
            else:
                alta = C.INICIO + timedelta(days=rng.randint(0, span_new))
            r, ciudad_reg = rng.random(), ciudad
            if r < 0.01:
                ciudad_reg = ciudad.lower()
            elif r < 0.02:
                ciudad_reg = ciudad.upper()
            elif r < 0.03:
                ciudad_reg = ciudad + " "
            self.clientes.append(dict(
                id_cliente=f"C{i:05d}", nombre=nombre, apellidos=f"{ap1} {ap2}", email=email, ciudad=ciudad_reg,
                provincia=prov, fecha_alta=alta.isoformat(), rango_edad=rng.choices(edades, pesos_edad)[0],
                consentimiento_marketing=int(rng.random() < 0.62), home=home,
                actividad=min(rng.paretovariate(1.6), 25.0), _alta=alta, _ciudad=ciudad))

    def _preparar_pools(self):
        self.pool = {}
        for h in list(C.REPARTO_CLIENTES) + ["*"]:
            cl = [c for c in self.clientes if h == "*" or c["home"] == h]
            old = [c for c in cl if c["_alta"] < C.INICIO]
            new = sorted((c for c in cl if c["_alta"] >= C.INICIO), key=lambda c: c["_alta"])
            self.pool[h] = dict(old=old, old_cw=list(accumulate(c["actividad"] for c in old)), new=new,
                                new_alta=[c["_alta"] for c in new],
                                new_cw=list(accumulate(c["actividad"] for c in new)))

    def _elegir_cliente(self, h, dia):
        P, rng = self.pool[h], self.rng
        k = bisect_right(P["new_alta"], dia)
        w_new = P["new_cw"][k - 1] if k else 0.0
        w_old = P["old_cw"][-1] if P["old"] else 0.0
        if rng.random() * (w_old + w_new) < w_old:
            return P["old"][min(bisect_right(P["old_cw"], rng.random() * w_old), len(P["old"]) - 1)]
        return P["new"][min(bisect_right(P["new_cw"], rng.random() * w_new), k - 1)]

    # ------------------------------------------------------------------ dinámica diaria
    def _poisson(self, lam):
        if lam <= 0:
            return 0
        if lam > 30:
            return max(0, int(round(self.rng.gauss(lam, math.sqrt(lam)))))
        L, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= self.rng.random()
            if p <= L:
                return k
            k += 1

    def _lambda(self, tid, base, dia, activos):
        s, wd, fisica = dia.isoformat(), dia.weekday(), tid != "WEB"
        if fisica:
            if s in C.FESTIVOS or (tid == "T04" and _entre(dia, CIERRE_VALENCIA)):
                return 0.0
            if wd == 6 and tid not in ("T01", "T02") and dia.month != 12:
                return 0.0
            f = C.FACTOR_DIA_FISICA[wd]
        else:
            f = C.FACTOR_DIA_WEB[wd] * (0.6 if s in C.FESTIVOS else 1.0)
        f *= C.FACTOR_MES_PEDIDOS[dia.month - 1]
        anios = (dia - C.INICIO).days / 365
        f *= (1 + 0.02 * anios) if fisica else (1 + 0.20 * anios)
        if tid == "T04" and dia > CIERRE_VALENCIA[1]:
            f *= 1.15
        if _entre(dia, BLACK_FRIDAY):
            f *= 1.6
        if dia == date(2025, 11, 28):
            f *= 1.75
        if dia == date(2025, 12, 1) and not fisica:
            f *= 1.6
        if date(2025, 12, 15) <= dia <= date(2025, 12, 23):
            f *= 1.35
        if dia in (date(2025, 12, 24), date(2025, 12, 31)):
            f *= 0.6
        for c in activos:
            if c["tienda"] not in (None, tid):
                continue
            f *= c["uplift"] if c["cat"] == "Todas" else 1 + 0.25 * (c["uplift"] - 1)
        return base * f

    def _pesos_categoria(self, tid, dia, activos):
        w = []
        for cat in C.CATEGORIAS:
            x = C.PESO_CATEGORIA_BASE[cat] * C.AJUSTE_TIENDA.get(tid, {}).get(cat, 1.0)
            x *= C.ESTACIONALIDAD[cat][dia.month - 1]
            for c in activos:
                if c["cat"] == cat and c["tienda"] in (None, tid):
                    x *= c["uplift"]
            if cat == "Electrónica" and _entre(dia, BLACK_FRIDAY):
                x *= 1.3
            w.append(x)
        return w

    def _productos_dia(self, cat, dia):
        prods, pesos = [], []
        for p in self.por_cat[cat]:
            if _d(p["fecha_alta"]) > dia or (p["fecha_baja"] and _d(p["fecha_baja"]) < dia):
                continue
            w = p["popularidad"]
            if p is self.p_def and dia >= date(2026, 8, 1):
                w *= 0.45
            if p["nombre"] in ("Turrón artesano", "Pack regalo gourmet") and dia.month == 12:
                w *= 12
            if p["nombre"] == "Protector solar SPF50" and dia.month in (5, 6, 7, 8):
                w *= 2.5
            if p["subcategoria"] == "Invierno":
                w *= 2.0 if dia.month in (11, 12, 1, 2) else 0.3 if dia.month in (5, 6, 7, 8, 9) else 1.0
            prods.append(p)
            pesos.append(w)
        return prods, list(accumulate(pesos))

    def _sin_stock(self, p, tid, dia):
        if p["proveedor"] != C.PROVEEDOR_ROTURA:
            return False
        if tid in ("T05", "T06") and _entre(dia, ROTURA_ANDALUCIA):
            return True
        return tid == "WEB" and _entre(dia, ROTURA_WEB) and self.rng.random() < 0.45

    def _unidades(self, p):
        r = self.rng.random()
        if p["categoria"] == "Gourmet":
            return 1 if r < .60 else 2 if r < .85 else self.rng.randint(3, 4)
        return 1 if r < .88 else 2 if r < .98 else 3

    def _descuento(self, p, tid, dia, activos):
        cat, d = p["categoria"], 0.0
        if any(_entre(dia, r) for r in REBAJAS):
            if cat == "Moda y complementos":
                d = self.rng.choice([0.2, 0.3, 0.4])
            elif cat == "Hogar" and dia.month in (1, 2):
                d = self.rng.choice([0.15, 0.2, 0.25])
        for c in activos:
            if c["desc"] and c["cat"] in (cat, "Todas") and c["tienda"] in (None, tid):
                d = max(d, c["desc"])
        if d == 0 and self.rng.random() < 0.03:
            d = 0.05
        return d

    def _canal_online(self, dia):
        if dia < LANZAMIENTO_APP:
            return "web"
        p_app = min(0.40, 0.08 + 0.32 * (dia - LANZAMIENTO_APP).days / 400)
        return "app" if self.rng.random() < p_app else "web"

    def _riesgo(self, p, dia):
        if p is self.p_def and dia >= FALLO_BATERIA:
            return 0.22
        return RIESGO_DEVOLUCION[p["categoria"]]

    # ------------------------------------------------------------------ simulación
    def simular(self):
        dia = C.INICIO
        while dia <= C.FIN:
            activos = [c for c in self.campanias if c["ini"] <= dia <= c["fin"]]
            prod_dia = {cat: self._productos_dia(cat, dia) for cat in C.CATEGORIAS}
            for t in C.TIENDAS:
                self._tienda_dia(t, dia, activos, prod_dia)
            dia += timedelta(days=1)
        for dia, tid, cliente, p in self.perdidas:
            ciudad = self.tiendas[tid][2] if tid != "WEB" else cliente["_ciudad"]
            self._ticket(dia, cliente, None, "Falta de stock", p, ciudad)
        self.tickets.sort(key=lambda t: (t["fecha_apertura"], t["_n"]))
        for i, t in enumerate(self.tickets, 1):
            t["id_ticket"] = f"TK{i:05d}"
        self.resenas.sort(key=lambda r: (r["fecha"], r["_n"]))
        for i, r in enumerate(self.resenas, 1):
            r["id_resena"] = f"R{i:05d}"
        return self

    def _tienda_dia(self, t, dia, activos, prod_dia):
        rng, tid, fisica = self.rng, t[0], t[0] != "WEB"
        n = self._poisson(self._lambda(tid, t[8], dia, activos))
        if not n:
            return
        wcat = self._pesos_categoria(tid, dia, activos)
        for _ in range(n):
            canal = "tienda" if fisica else self._canal_online(dia)
            cliente = None
            if not fisica or rng.random() < 0.62:
                cliente = self._elegir_cliente(tid if fisica and rng.random() < 0.85 else "*", dia)
            nl = 1
            while nl < 6 and rng.random() < 0.38:
                nl += 1
            lineas, usados, perdida = [], set(), None
            for _ in range(nl):
                prods, cw = prod_dia[rng.choices(C.CATEGORIAS, weights=wcat)[0]]
                p = rng.choices(prods, cum_weights=cw)[0]
                if self._sin_stock(p, tid, dia):
                    perdida = perdida or p
                    if rng.random() >= 0.3:
                        continue
                    p = rng.choice([q for q in prods if q["proveedor"] != C.PROVEEDOR_ROTURA])
                if p["id_producto"] in usados:
                    continue
                usados.add(p["id_producto"])
                lineas.append((p, self._unidades(p), self._descuento(p, tid, dia, activos)))
            if perdida and cliente and rng.random() < 0.12:
                self.perdidas.append((dia, tid, cliente, perdida))
            if lineas:
                self._registrar_venta(dia, tid, canal, cliente, lineas, activos)

    def _registrar_venta(self, dia, tid, canal, cliente, lineas, activos):
        rng = self.rng
        self.n_venta += 1
        vid = f"V{self.n_venta:06d}"
        bruto = neto = 0.0
        for i, (p, uds, d) in enumerate(lineas, 1):
            imp = round(uds * p["precio_lista"] * (1 - d), 2)
            bruto += uds * p["precio_lista"]
            neto += imp
            self.lineas.append((vid, i, p["id_producto"], uds, p["precio_lista"], d, imp))
        r = rng.random()
        riesgo = max(self._riesgo(p, dia) for p, _, _ in lineas)
        estado = ("cancelada" if canal != "tienda" and r < 0.012 else
                  "devuelta" if r < 0.012 + riesgo else "completada")
        camp, cats = None, {p["categoria"] for p, _, _ in lineas}
        for c in activos:
            if c["tienda"] not in (None, tid) or not (c["cat"] == "Todas" or c["cat"] in cats):
                continue
            prob = 0.25 if c["tienda"] else C.PROB_ATRIBUCION[c["canal"]] * (1.0 if canal != "tienda" else 0.35)
            if rng.random() < prob:
                camp = c["id"]
                break
        if canal == "tienda":
            pago = rng.choices(["tarjeta", "efectivo", "bizum"], [70, 18, 12])[0]
        elif canal == "web":
            pago = rng.choices(["tarjeta", "paypal", "bizum"], [72, 18, 10])[0]
        else:
            pago = rng.choices(["tarjeta", "bizum", "paypal"], [60, 25, 15])[0]
        self.ventas.append(dict(
            id_venta=vid, fecha=dia.isoformat(), id_tienda=tid, canal=canal,
            id_cliente=cliente["id_cliente"] if cliente else None, id_campania=camp, metodo_pago=pago,
            importe_bruto=round(bruto, 2), descuento=round(bruto - neto, 2), importe_neto=round(neto, 2),
            estado=estado, _lineas=lineas))
        self._postventa(vid, dia, tid, canal, cliente, lineas, estado)

    def _postventa(self, vid, dia, tid, canal, cliente, lineas, estado):
        rng = self.rng
        ciudad = self.tiendas[tid][2] if tid != "WEB" else (cliente["_ciudad"] if cliente else "Online")
        if canal != "tienda" and estado != "cancelada":
            if rng.random() < (0.095 if _entre(dia, NAVIDAD_LOGIRAPIDO) else 0.022):
                self._ticket(dia + timedelta(days=rng.randint(3, 7)), cliente, vid, "Envío", lineas[0][0], ciudad)
        if estado == "devuelta" and rng.random() < 0.45:
            p = max(lineas, key=lambda x: self._riesgo(x[0], dia))[0]
            self._ticket(dia + timedelta(days=rng.randint(2, 15)), cliente, vid, "Devolución", p, ciudad)
        for p, _, _ in lineas:
            if p is self.p_def and dia >= FALLO_BATERIA and rng.random() < 0.18:
                self._ticket(dia + timedelta(days=rng.randint(5, 40)), cliente, vid, "Producto defectuoso", p, ciudad)
            elif p["categoria"] == "Electrónica" and rng.random() < 0.004:
                self._ticket(dia + timedelta(days=rng.randint(5, 40)), cliente, vid, "Producto defectuoso", p, ciudad)
        if rng.random() < 0.004:
            self._ticket(dia + timedelta(days=rng.randint(0, 10)), cliente, vid, "Facturación", lineas[0][0], ciudad)
        if rng.random() < 0.003:
            self._ticket(dia + timedelta(days=rng.randint(0, 10)), cliente, None, "Otro", None, ciudad)
        if cliente and estado != "cancelada":
            for p, _, _ in lineas:
                if rng.random() < 0.035:
                    self._resena(dia + timedelta(days=rng.randint(3, 21)), cliente, p, estado == "devuelta")

    def _ticket(self, fecha, cliente, vid, categoria, p, ciudad):
        if fecha > C.FIN:
            return
        rng = self.rng
        media = {"Envío": 20, "Devolución": 30, "Producto defectuoso": 40, "Falta de stock": 16,
                 "Facturación": 12, "Otro": 8}[categoria]
        if categoria == "Envío" and date(2025, 12, 1) <= fecha <= date(2026, 1, 10):
            media *= 2.8
        horas = round(rng.gammavariate(2.0, media / 2.0), 1)
        abierto = fecha + timedelta(hours=horas) > C.FIN + timedelta(days=1)
        satisf = None
        if not abierto and rng.random() > 0.3:
            satisf = int(min(5, max(1, round(rng.gauss(4.6 - 0.03 * horas, 0.7)))))
        prioridad = ("alta" if categoria in ("Producto defectuoso", "Envío") and rng.random() < 0.4
                     else rng.choice(["media", "media", "baja"]))
        plantilla = rng.choice(X.TICKETS[categoria])
        defectuoso = p is self.p_def and fecha >= FALLO_BATERIA
        texto = plantilla.format(
            v=vid or "-", p=p["nombre"] if p else "", c=ciudad, d=rng.randint(5, 12),
            m=rng.choice(X.MOTIVOS_DEVOLUCION),
            f=rng.choice(X.FALLOS_DEFECTUOSO if defectuoso else X.FALLOS_GENERICOS))
        self.tickets.append(dict(
            _n=len(self.tickets), fecha_apertura=fecha.isoformat(), id_cliente=cliente["id_cliente"] if cliente else None,
            id_venta=vid, id_producto=p["id_producto"] if p else None,
            canal=rng.choices(["chat", "email", "teléfono"], [45, 35, 20])[0], categoria=categoria,
            prioridad=prioridad, estado="abierto" if abierto else rng.choice(["resuelto", "cerrado"]),
            horas_resolucion=None if abierto else horas, satisfaccion=satisf, resumen=texto))

    def _resena(self, fecha, cliente, p, devuelta):
        if fecha > C.FIN:
            return
        rng = self.rng
        defecto = p is self.p_def and fecha >= date(2026, 6, 10)
        q = (1.9 if defecto else p["calidad"]) - (1.2 if devuelta else 0)
        nota = int(min(5, max(1, round(rng.gauss(q, 0.85)))))
        b = "pos" if nota >= 4 else "neu" if nota == 3 else "neg"
        partes = [rng.choice(X.APERTURA[b]).format(p=p["nombre"])]
        partes.append(rng.choice(X.DETALLE_DEFECTUOSO) if defecto and b == "neg"
                      else rng.choice(X.DETALLE[p["categoria"]][b]))
        cierre = rng.choice(X.CIERRE[b])
        if cierre:
            partes.append(cierre)
        self.resenas.append(dict(_n=len(self.resenas), fecha=fecha.isoformat(), id_producto=p["id_producto"],
                                 id_cliente=cliente["id_cliente"], puntuacion=nota,
                                 titulo=rng.choice(X.TITULOS[b]), texto=" ".join(partes)))

    # ------------------------------------------------------------------ tablas derivadas
    def segmentar_clientes(self):
        stats = defaultdict(lambda: [0, 0.0, defaultdict(int)])
        for v in self.ventas:
            if v["id_cliente"] and v["estado"] == "completada":
                s = stats[v["id_cliente"]]
                s[0] += 1
                s[1] += v["importe_neto"]
                s[2][v["canal"]] += 1
        gastos = sorted((s[1] for s in stats.values()), reverse=True)
        umbral_vip = gastos[int(len(gastos) * 0.05)] if gastos else 0
        for c in self.clientes:
            n, gasto, canales = stats.get(c["id_cliente"], [0, 0.0, {}])
            c["segmento"] = ("VIP" if gasto >= umbral_vip and n >= 3 else "Fiel" if n >= 6 else
                             "Ocasional" if n >= 2 else "Nuevo")
            c["canal_preferido"] = max(canales, key=canales.get) if canales else None
        return self

    def inventario(self):
        mensual = defaultdict(float)
        for v in self.ventas:
            if v["fecha"] < "2026-01-01":
                for p, uds, _ in v["_lineas"]:
                    mensual[(v["id_tienda"], p["id_producto"])] += uds / 12
        filas, rng = [], self.rng
        for mes in range(1, 11):
            corte = (date(2026, mes + 1, 1) if mes < 12 else date(2027, 1, 1)) - timedelta(days=1)
            for tid in self.tiendas:
                for p in self.productos:
                    if _d(p["fecha_alta"]) > corte or (p["fecha_baja"] and _d(p["fecha_baja"]) < corte):
                        continue
                    base = max(mensual.get((tid, p["id_producto"]), 0.0), 0.8)
                    stock = round(base * rng.uniform(0.9, 2.2)) + rng.randint(0, 3)
                    if p["proveedor"] == C.PROVEEDOR_ROTURA:
                        if tid in ("T05", "T06") and mes in (7, 8, 9):
                            stock = 0
                        elif tid == "WEB" and mes in (7, 8):
                            stock = rng.randint(0, 2)
                        elif tid in ("T05", "T06", "WEB") and mes == 10:
                            stock = round(base * 0.4)
                    if p is self.p_def and mes >= 7:
                        stock = round(base * 3.5)
                    if rng.random() < 0.015:
                        stock = 0
                    filas.append(dict(fecha_corte=corte.isoformat(), id_tienda=tid, id_producto=p["id_producto"],
                                      stock_unidades=stock, stock_minimo=max(2, round(base * 0.6))))
        return filas
