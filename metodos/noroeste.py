from metodos import tablatransporte


def resolver(costos, oferta, demanda):
    oferta_rest = oferta.copy()
    demanda_rest = demanda.copy()
    asignaciones = [[0.0] * len(demanda) for _ in oferta]
    pasos = []

    # se empieza en la esquina de arriba a la izquierda
    i = 0
    j = 0
    while i < len(oferta) and j < len(demanda):
        cantidad = min(oferta_rest[i], demanda_rest[j])
        asignaciones[i][j] = cantidad
        pasos.append(f"Origen {i + 1} → Destino {j + 1}: asignar {cantidad:g}.")

        oferta_rest[i] -= cantidad
        demanda_rest[j] -= cantidad

        # si se agotó la fila bajamos, si se completó la columna avanzamos
        if abs(oferta_rest[i]) < 1e-9:
            i += 1
        if abs(demanda_rest[j]) < 1e-9:
            j += 1

    costo_total = sum(
        asignaciones[r][c] * costos[r][c]
        for r in range(len(oferta))
        for c in range(len(demanda))
    )

    return asignaciones, pasos, costo_total


def mostrar():
    tablatransporte.interfaz("noroeste", "Esquina Noroeste", resolver)