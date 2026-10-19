from metodos import tablatransporte


def _penalizacion(valores):
    # diferencia entre los dos costos más bajos
    valores = sorted(valores)
    if len(valores) >= 2:
        return valores[1] - valores[0]
    return valores[0]


def resolver(costos, oferta, demanda):
    oferta_rest = oferta.copy()
    demanda_rest = demanda.copy()
    asignaciones = [[0.0] * len(demanda) for _ in oferta]
    pasos = []

    while True:
        filas = [r for r in range(len(oferta)) if oferta_rest[r] > 1e-9]
        columnas = [c for c in range(len(demanda)) if demanda_rest[c] > 1e-9]
        if not filas or not columnas:
            break

        # penalización de cada fila y de cada columna que siguen activas
        penalizaciones = []
        for r in filas:
            valor = _penalizacion([costos[r][c] for c in columnas])
            penalizaciones.append((valor, "fila", r))
        for c in columnas:
            valor = _penalizacion([costos[r][c] for r in filas])
            penalizaciones.append((valor, "columna", c))

        # se elige la mayor penalización (si hay empate, la primera)
        mayor, tipo, indice = max(penalizaciones, key=lambda p: p[0])

        # dentro de esa fila o columna, se usa la celda de menor costo
        if tipo == "fila":
            i = indice
            j = min(columnas, key=lambda c: costos[i][c])
        else:
            j = indice
            i = min(filas, key=lambda r: costos[r][j])

        cantidad = min(oferta_rest[i], demanda_rest[j])
        asignaciones[i][j] += cantidad
        pasos.append(
            f"Origen {i + 1} → Destino {j + 1}: asignar {cantidad:g} "
            f"(mayor penalización {mayor:g}, {tipo} {indice + 1})."
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
    tablatransporte.interfaz("vogel", "Vogel", resolver)