"""Plantillas de texto para reseñas y tickets de soporte (sintéticos)."""

TITULOS = {
    "pos": ["Muy contento", "Recomendable", "Calidad excelente", "Tal y como se describe", "Repetiré",
            "Gran compra", "Me encanta", "Mejor de lo esperado", "Perfecto para regalar"],
    "neu": ["Correcto sin más", "Cumple", "Bien, pero mejorable", "Aceptable", "Ni fu ni fa"],
    "neg": ["Decepcionado", "No lo recomiendo", "Mala calidad", "Lo he devuelto", "No vale lo que cuesta"],
}

APERTURA = {
    "pos": ["{p} cumple de sobra.", "Compré {p} y estoy encantada.", "Llevo unas semanas usando {p} y va genial.",
            "{p} ha sido todo un acierto.", "Segunda vez que compro {p} y sigue sin fallar."],
    "neu": ["{p} está bien, aunque esperaba algo más.", "{p} cumple su función sin destacar.",
            "Por el precio, {p} es correcto.", "{p} no está mal, pero hay opciones mejores."],
    "neg": ["{p} me ha decepcionado bastante.", "No volvería a comprar {p}.",
            "{p} no está a la altura de lo que promete.", "Tuve que devolver {p}."],
}

DETALLE = {
    "Electrónica": {
        "pos": ["La batería dura bastante y la conexión es estable.", "El sonido es muy limpio para lo que cuesta.",
                "Se configura en dos minutos con el móvil."],
        "neu": ["La app es algo lenta.", "El cable que trae es demasiado corto."],
        "neg": ["Dejó de funcionar a las pocas semanas.", "La conexión Bluetooth se corta continuamente."],
    },
    "Hogar": {
        "pos": ["El tejido es suave y ha aguantado bien los lavados.", "Queda precioso en el salón.",
                "Muy buena calidad de acabados."],
        "neu": ["El color es algo distinto al de la foto.", "Las medidas son algo justas."],
        "neg": ["Se deshilachó tras el primer lavado.", "Llegó con una mancha y el embalaje roto."],
    },
    "Deporte": {
        "pos": ["Lo uso a diario en el gimnasio y aguanta perfecto.", "Muy cómodo para correr.",
                "Ligero y resistente, ideal para la montaña."],
        "neu": ["La talla viene un poco pequeña.", "El material es algo básico."],
        "neg": ["Se rompió en la segunda salida.", "Muy incómodo tras una hora de uso."],
    },
    "Moda y complementos": {
        "pos": ["Buen material y muy bonito.", "Combina con todo.", "Las costuras están muy bien rematadas."],
        "neu": ["El tono es más oscuro de lo que parece.", "Bonito, pero algo pequeño."],
        "neg": ["Se descosió enseguida.", "La piel parece sintética."],
    },
    "Belleza y cuidado": {
        "pos": ["Se absorbe rápido y huele genial.", "Noto la piel mucho más hidratada.", "Ingredientes muy naturales."],
        "neu": ["El olor es demasiado intenso para mí.", "Dura poco el envase."],
        "neg": ["Me provocó rojeces.", "No noto ninguna diferencia."],
    },
    "Gourmet": {
        "pos": ["Sabor espectacular, se nota la calidad.", "Ideal para regalar.", "Producto muy auténtico."],
        "neu": ["Bueno, pero algo caro.", "Esperaba un sabor más intenso."],
        "neg": ["Llegó con el envase dañado.", "El sabor no tiene nada que ver con el de antes."],
    },
}

DETALLE_DEFECTUOSO = [
    "La batería no llega ni a dos horas de uso.",
    "Se desconectan solos y la batería se agota enseguida.",
    "Desde la última actualización la batería dura la mitad.",
    "La carga no pasa del 60 % y se calientan.",
    "Uno de los auriculares deja de sonar cuando baja la batería.",
]

CIERRE = {
    "pos": ["Lo recomiendo.", "Buena relación calidad-precio.", "El envío llegó antes de lo previsto.", "", ""],
    "neu": ["", "Para salir del paso está bien.", "Quizá pruebe otra marca la próxima vez."],
    "neg": ["", "Atención al cliente tardó días en responder.", "Esperaba más de Almansa."],
}

TICKETS = {
    "Envío": [
        "Pedido {v} sin entregar tras {d} días. El seguimiento de LogiRápido no se actualiza.",
        "El cliente pregunta por el retraso del pedido {v}; el transportista indica incidencia en almacén.",
        "Entrega fallida del pedido {v}: el repartidor no dejó aviso.",
        "Pedido {v} entregado incompleto: falta {p}.",
        "Pedido {v} entregado en una dirección equivocada.",
    ],
    "Devolución": [
        "Solicita la devolución de {p} (pedido {v}): {m}.",
        "Quiere devolver {p} del pedido {v} y pregunta por el reembolso: {m}.",
        "Devolución de {p} (pedido {v}) pendiente de recogida: {m}.",
    ],
    "Producto defectuoso": [
        "{p} del pedido {v} presenta fallos: {f}.",
        "El cliente reclama por {p} (pedido {v}): {f}.",
        "{p} defectuoso, solicita sustitución (pedido {v}): {f}.",
    ],
    "Falta de stock": [
        "El cliente no encuentra {p} en la tienda de {c} y pregunta cuándo habrá reposición.",
        "Pregunta por la reposición de {p}; lleva semanas agotado en {c}.",
        "Quiere comprar {p} pero aparece como agotado; amenaza con irse a la competencia.",
    ],
    "Facturación": [
        "Solicita factura con datos de empresa para el pedido {v}.",
        "Cobro duplicado en el pedido {v}.",
        "El descuento de la campaña no se aplicó en el pedido {v}.",
    ],
    "Otro": [
        "Consulta sobre el horario de la tienda de {c}.",
        "Pregunta por las ventajas de la tarjeta Almansa+.",
        "Sugiere ampliar el catálogo de productos gourmet.",
        "Pide darse de baja de las comunicaciones comerciales y saber qué datos personales se guardan.",
    ],
}

MOTIVOS_DEVOLUCION = ["no es lo que esperaba", "la talla o medida no es correcta", "llegó dañado",
                      "ha encontrado mejor precio", "era un regalo duplicado"]
FALLOS_GENERICOS = ["no enciende", "llegó con un golpe", "falla a los pocos días de uso", "hace un ruido extraño"]
FALLOS_DEFECTUOSO = ["la batería se agota en menos de dos horas", "se desconecta del móvil constantemente",
                     "no carga tras actualizar el firmware", "se calienta mucho al cargar"]
