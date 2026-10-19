from metodos import tablatransporte


def resolver(costos, oferta, demanda):
    oferta_rest = oferta.copy()
    demanda_rest = demanda.copy()
    asignaciones = [[0.0] * len(demanda) for _ in oferta]
    pasos = []

    while True:
        # celdas que todavía tienen oferta y demanda disponibles
        disponibles = [
            (costos[r][c], r, c)
            for r in range(len(oferta))
            for c in range(len(demanda))
            if oferta_rest[r] > 1e-9 and demanda_rest[c] > 1e-9
        ]
        if not disponibles:
            break

        # se toma la de menor costo (si hay empate, la primera que aparece)
        costo, i, j = min(disponibles)
        cantidad = min(oferta_rest[i], demanda_rest[j])
        asignaciones[i][j] += cantidad
        pasos.append(
            f"Origen {i + 1} → Destino {j + 1}: costo {costo:g}, asignar {cantidad:g}."
        )

        oferta_rest[i] -= cantidad
        demanda_rest[j] -= cantidad

    costo_total = sum(
        asignaciones[r][c] * costos[r][c]
        for r in range(len(oferta))
        for c in range(len(demanda))
    )

    return asignaciones, pasos, costo_total


def mostrar():
    tablatransporte.interfaz("costominimo", "Costo Mínimo", resolver)