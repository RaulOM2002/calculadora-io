import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ---------- CONFIGURACIÓN ----------

TOLERANCIA = 1e-8

# Colores de la gráfica (antes estaban en estilo.py)
BLANCO = "#FFFFFF"
AZUL_MARINO = "#0B1F3A"
AZUL_SECUNDARIO = "#102A4C"
AZUL_BOTON = "#164A7A"

COLOR_GRAFICA_FONDO = AZUL_MARINO
COLOR_GRAFICA_PANEL = AZUL_SECUNDARIO
COLOR_GRAFICA_TEXTO = BLANCO
COLOR_GRAFICA_REJILLA = "#5079A3"
COLOR_GRAFICA_REGION = AZUL_BOTON
COLOR_GRAFICA_OPTIMO = BLANCO
COLOR_GRAFICA_LINEA = BLANCO


def color_restriccion(indice):
    if indice == 0:
        return BLANCO
    if indice == 1:
        return "#FFD54F"
    return COLOR_GRAFICA_LINEA


# ---------- LÓGICA DEL MÉTODO ----------

def convertir_numero(texto):
    texto = texto.strip()
    texto = texto.replace(",", ".")
    numero = float(texto)

    if not math.isfinite(numero):
        raise ValueError

    return numero


def cumple_restriccion(x, y, restriccion):
    lado_izquierdo = restriccion["x1"] * x + restriccion["x2"] * y
    resultado = restriccion["resultado"]
    signo = restriccion["signo"]

    if signo == "<=":
        return lado_izquierdo <= resultado + TOLERANCIA
    elif signo == ">=":
        return lado_izquierdo >= resultado - TOLERANCIA
    elif signo == "=":
        return abs(lado_izquierdo - resultado) <= TOLERANCIA

    return False


def es_factible(x, y, restricciones_datos):
    if x < -TOLERANCIA:
        return False

    if y < -TOLERANCIA:
        return False

    for restriccion in restricciones_datos:
        if not cumple_restriccion(x, y, restriccion):
            return False

    return True


def interseccion(r1, r2):
    a1 = r1["x1"]
    b1 = r1["x2"]
    c1 = r1["resultado"]

    a2 = r2["x1"]
    b2 = r2["x2"]
    c2 = r2["resultado"]

    determinante = a1 * b2 - a2 * b1

    if abs(determinante) < TOLERANCIA:
        return None

    x = (c1 * b2 - c2 * b1) / determinante
    y = (a1 * c2 - a2 * c1) / determinante

    return (x, y)


def agregar_punto_unico(lista, punto):
    x, y = punto

    if abs(x) < TOLERANCIA:
        x = 0.0

    if abs(y) < TOLERANCIA:
        y = 0.0

    for px, py in lista:
        if abs(px - x) < 1e-6 and abs(py - y) < 1e-6:
            return

    lista.append((x, y))


def encontrar_puntos_candidatos(restricciones_datos):
    candidatos = []

    agregar_punto_unico(candidatos, (0, 0))

    for r in restricciones_datos:
        a = r["x1"]
        b = r["x2"]
        c = r["resultado"]

        if abs(b) > TOLERANCIA:
            y = c / b
            agregar_punto_unico(candidatos, (0, y))

        if abs(a) > TOLERANCIA:
            x = c / a
            agregar_punto_unico(candidatos, (x, 0))

    cantidad = len(restricciones_datos)

    for i in range(cantidad):
        for j in range(i + 1, cantidad):
            punto = interseccion(restricciones_datos[i], restricciones_datos[j])

            if punto is not None:
                agregar_punto_unico(candidatos, punto)

    return candidatos


def encontrar_vertices(restricciones_datos):
    candidatos = encontrar_puntos_candidatos(restricciones_datos)
    vertices = []

    for punto in candidatos:
        x, y = punto

        if es_factible(x, y, restricciones_datos):
            agregar_punto_unico(vertices, punto)

    return (candidatos, vertices)


def direccion_factible(dx, dy, restricciones_datos):
    if dx < -TOLERANCIA:
        return False

    if dy < -TOLERANCIA:
        return False

    for r in restricciones_datos:
        valor = r["x1"] * dx + r["x2"] * dy

        if r["signo"] == "<=":
            if valor > TOLERANCIA:
                return False

        elif r["signo"] == ">=":
            if valor < -TOLERANCIA:
                return False

        elif r["signo"] == "=":
            if abs(valor) > TOLERANCIA:
                return False

    return True


def problema_no_acotado(tipo, obj_x1, obj_x2, restricciones_datos):
    direcciones = [(1, 0), (0, 1)]

    for r in restricciones_datos:
        a = r["x1"]
        b = r["x2"]

        direcciones.append((b, -a))
        direcciones.append((-b, a))

    for dx, dy in direcciones:
        norma = math.hypot(dx, dy)

        if norma < TOLERANCIA:
            continue

        dx = dx / norma
        dy = dy / norma

        if not direccion_factible(dx, dy, restricciones_datos):
            continue

        cambio_z = obj_x1 * dx + obj_x2 * dy

        if tipo == "Maximizar":
            if cambio_z > TOLERANCIA:
                return True
        else:
            if cambio_z < -TOLERANCIA:
                return True

    return False


def formato(numero):
    if abs(numero) < 1e-8:
        numero = 0

    if abs(numero - round(numero)) < 1e-8:
        return str(int(round(numero)))

    return f"{numero:.4f}".rstrip("0").rstrip(".")


def crear_procedimiento(
    tipo,
    obj_x1,
    obj_x2,
    restricciones_datos,
    candidatos,
    vertices,
    no_acotado,
):
    texto = ""

    texto += "PASO 1 - PROBLEMA INGRESADO\n\n"
    texto += f"{tipo}:\n\n"
    texto += f"Z = {formato(obj_x1)}X1 + {formato(obj_x2)}X2\n\n"
    texto += "Sujeto a:\n\n"

    for i, r in enumerate(restricciones_datos):
        texto += (
            f"R{i + 1}: "
            f"{formato(r['x1'])}X1 + "
            f"{formato(r['x2'])}X2 "
            f"{r['signo']} "
            f"{formato(r['resultado'])}\n"
        )

    texto += "\nX1 >= 0\n"
    texto += "X2 >= 0\n\n"

    texto += "PASO 2 - INTERSECCIONES CON LOS EJES\n\n"

    for i, r in enumerate(restricciones_datos):
        a = r["x1"]
        b = r["x2"]
        c = r["resultado"]

        texto += f"Restricción {i + 1}:\n"
        texto += f"{formato(a)}X1 + {formato(b)}X2 = {formato(c)}\n"

        if abs(b) > TOLERANCIA:
            y = c / b
            texto += f"Si X1 = 0 -> X2 = {formato(y)}\n"
            texto += f"Punto: (0, {formato(y)})\n"
        else:
            texto += "No corta el eje X2.\n"

        if abs(a) > TOLERANCIA:
            x = c / a
            texto += f"Si X2 = 0 -> X1 = {formato(x)}\n"
            texto += f"Punto: ({formato(x)}, 0)\n"
        else:
            texto += "No corta el eje X1.\n"

        texto += "\n"

    texto += "PASO 3 - INTERSECCIONES ENTRE RESTRICCIONES\n\n"

    cantidad = len(restricciones_datos)

    for i in range(cantidad):
        for j in range(i + 1, cantidad):
            punto = interseccion(restricciones_datos[i], restricciones_datos[j])

            if punto is None:
                texto += f"R{i + 1} con R{j + 1}: rectas paralelas.\n"
            else:
                x, y = punto
                texto += f"R{i + 1} con R{j + 1}: ({formato(x)}, {formato(y)})\n"

    texto += "\nPASO 4 - COMPROBACIÓN DE PUNTOS\n\n"

    for x, y in candidatos:
        if es_factible(x, y, restricciones_datos):
            estado = "FACTIBLE"
        else:
            estado = "NO FACTIBLE"

        texto += f"({formato(x)}, {formato(y)}) -> {estado}\n"

    texto += "\nPASO 5 - VÉRTICES DE LA REGIÓN FACTIBLE\n\n"

    if not vertices:
        texto += "No se encontraron puntos factibles.\n\n"
        texto += "EL PROBLEMA NO TIENE SOLUCIÓN FACTIBLE.\n"
        return texto

    for i, punto in enumerate(vertices, start=1):
        x, y = punto
        texto += f"V{i} = ({formato(x)}, {formato(y)})\n"

    texto += "\nPASO 6 - EVALUAR LA FUNCIÓN OBJETIVO\n\n"

    resultados = []

    for x, y in vertices:
        z = obj_x1 * x + obj_x2 * y
        resultados.append((x, y, z))

        texto += (
            f"Z({formato(x)}, {formato(y)}) = "
            f"{formato(obj_x1)}({formato(x)}) + "
            f"{formato(obj_x2)}({formato(y)}) = "
            f"{formato(z)}\n"
        )

    texto += "\nPASO 7 - SOLUCIÓN\n\n"

    if no_acotado:
        texto += "El problema es NO ACOTADO.\n\n"
        texto += "La función objetivo puede seguir mejorando indefinidamente."
        return texto

    if tipo == "Maximizar":
        mejor_z = max(resultado[2] for resultado in resultados)
    else:
        mejor_z = min(resultado[2] for resultado in resultados)

    optimos = [
        resultado
        for resultado in resultados
        if abs(resultado[2] - mejor_z) < 1e-7
    ]

    if len(optimos) > 1:
        texto += "Existen múltiples soluciones óptimas.\n\n"

    x, y, z = optimos[0]

    texto += f"X1 = {formato(x)}\n"
    texto += f"X2 = {formato(y)}\n"

    if tipo == "Maximizar":
        texto += f"Z máximo = {formato(z)}\n"
    else:
        texto += f"Z mínimo = {formato(z)}\n"

    return texto


def obtener_limites_iniciales(candidatos):
    valores_x = [0, 10]
    valores_y = [0, 10]

    for x, y in candidatos:
        if math.isfinite(x) and x >= 0:
            valores_x.append(x)

        if math.isfinite(y) and y >= 0:
            valores_y.append(y)

    max_x = min(max(max(valores_x) * 1.20, 10), 100000)
    max_y = min(max(max(valores_y) * 1.20, 10), 100000)

    return (0, max_x, 0, max_y)


# ---------- GRÁFICA INTERACTIVA ----------

def crear_grafica(restricciones_datos, vertices, candidatos, mejor_punto=None):
    figura = go.Figure()

    limites = obtener_limites_iniciales(candidatos)
    max_x = limites[1]
    max_y = limites[3]

    # Región factible
    if len(vertices) >= 3:
        centro_x = sum(p[0] for p in vertices) / len(vertices)
        centro_y = sum(p[1] for p in vertices) / len(vertices)

        ordenados = sorted(
            vertices,
            key=lambda p: math.atan2(p[1] - centro_y, p[0] - centro_x),
        )

        region_x = [p[0] for p in ordenados]
        region_y = [p[1] for p in ordenados]

        region_x.append(region_x[0])
        region_y.append(region_y[0])

        figura.add_trace(go.Scatter(
            x=region_x,
            y=region_y,
            fill="toself",
            fillcolor=COLOR_GRAFICA_REGION,
            opacity=0.35,
            line=dict(width=0),
            name="Región factible",
        ))

    # Rectas de las restricciones
    for i, r in enumerate(restricciones_datos):
        a = r["x1"]
        b = r["x2"]
        c = r["resultado"]

        color = color_restriccion(i)

        if abs(b) > TOLERANCIA:
            x_linea = np.linspace(0, max_x, 500)
            y_linea = (c - a * x_linea) / b

            figura.add_trace(go.Scatter(
                x=x_linea,
                y=y_linea,
                mode="lines",
                line=dict(color=color, width=2),
                name=f"R{i + 1}",
            ))

        elif abs(a) > TOLERANCIA:
            x_vertical = c / a

            figura.add_trace(go.Scatter(
                x=[x_vertical, x_vertical],
                y=[0, max_y],
                mode="lines",
                line=dict(color=color, width=2),
                name=f"R{i + 1}",
            ))

    # Vértices
    if vertices:
        figura.add_trace(go.Scatter(
            x=[p[0] for p in vertices],
            y=[p[1] for p in vertices],
            mode="markers+text",
            text=[
                f"V{i + 1} ({formato(x)}, {formato(y)})"
                for i, (x, y) in enumerate(vertices)
            ],
            textposition="top right",
            marker=dict(size=9, color=COLOR_GRAFICA_OPTIMO),
            name="Vértices",
        ))

    # Solución óptima
    if mejor_punto is not None:
        x, y = mejor_punto

        figura.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(size=16, symbol="star", color=COLOR_GRAFICA_OPTIMO),
            name="Solución óptima",
        ))

    # Diseño y controles
    figura.update_layout(
        title="Método Gráfico",
        paper_bgcolor=COLOR_GRAFICA_FONDO,
        plot_bgcolor=COLOR_GRAFICA_PANEL,
        font=dict(color=COLOR_GRAFICA_TEXTO),
        xaxis_title="X1",
        yaxis_title="X2",
        legend=dict(
            bgcolor=COLOR_GRAFICA_PANEL,
            bordercolor=COLOR_GRAFICA_REJILLA,
            borderwidth=1,
        ),
        margin=dict(l=40, r=20, t=55, b=40),
        height=550,
        dragmode="pan",
        xaxis=dict(
            range=[0, max_x],
            zeroline=True,
            zerolinecolor=COLOR_GRAFICA_REJILLA,
            gridcolor=COLOR_GRAFICA_REJILLA,
            fixedrange=False,
        ),
        yaxis=dict(
            range=[0, max_y],
            zeroline=True,
            zerolinecolor=COLOR_GRAFICA_REJILLA,
            gridcolor=COLOR_GRAFICA_REJILLA,
            fixedrange=False,
            scaleanchor="x",
            scaleratio=1,
        ),
    )

    return figura


# ---------- LECTURA DE DATOS DE LA INTERFAZ ----------

def obtener_datos():
    tipo = st.session_state.get("grafico_tipo", "Maximizar")

    try:
        texto_obj_x1 = st.session_state.get("grafico_obj_x1", "").strip()
        obj_x1 = 0 if texto_obj_x1 == "" else convertir_numero(texto_obj_x1)
    except ValueError:
        st.error("El coeficiente de X1 de la función objetivo debe ser un número.")
        return None

    try:
        texto_obj_x2 = st.session_state.get("grafico_obj_x2", "").strip()
        obj_x2 = 0 if texto_obj_x2 == "" else convertir_numero(texto_obj_x2)
    except ValueError:
        st.error("El coeficiente de X2 de la función objetivo debe ser un número.")
        return None

    if abs(obj_x1) < TOLERANCIA and abs(obj_x2) < TOLERANCIA:
        st.error("La función objetivo no puede tener X1 y X2 iguales a 0.")
        return None

    datos_restricciones = []

    for i in range(st.session_state.grafico_cant):
        numero = i + 1
        texto_x1 = st.session_state.get(f"grafico_rest{i}_x1", "").strip()
        texto_x2 = st.session_state.get(f"grafico_rest{i}_x2", "").strip()
        texto_resultado = st.session_state.get(f"grafico_rest{i}_resultado", "").strip()
        signo = st.session_state.get(f"grafico_rest{i}_signo", "<=")

        try:
            x1 = 0 if texto_x1 == "" else convertir_numero(texto_x1)
        except ValueError:
            st.error(f"X1 de la restricción {numero} debe ser un número.")
            return None

        try:
            x2 = 0 if texto_x2 == "" else convertir_numero(texto_x2)
        except ValueError:
            st.error(f"X2 de la restricción {numero} debe ser un número.")
            return None

        if texto_resultado == "":
            st.error(f"Debes ingresar el resultado de la restricción {numero}.")
            return None

        try:
            resultado = convertir_numero(texto_resultado)
        except ValueError:
            st.error(f"El resultado de la restricción {numero} debe ser un número.")
            return None

        if abs(x1) < TOLERANCIA and abs(x2) < TOLERANCIA:
            st.error(f"La restricción {numero} no puede tener X1 y X2 iguales a 0.")
            return None

        datos_restricciones.append({
            "x1": x1,
            "x2": x2,
            "signo": signo,
            "resultado": resultado,
        })

    return tipo, obj_x1, obj_x2, datos_restricciones


def graficar():
    datos = obtener_datos()

    if datos is None:
        return

    tipo, obj_x1, obj_x2, restricciones_datos = datos
    candidatos, vertices = encontrar_vertices(restricciones_datos)

    if not vertices:
        procedimiento = crear_procedimiento(
            tipo, obj_x1, obj_x2, restricciones_datos,
            candidatos, vertices, False,
        )
        st.session_state.grafico_res_actual = {
            "procedimiento": procedimiento,
            "restricciones": restricciones_datos,
            "vertices": vertices,
            "candidatos": candidatos,
            "mejor_punto": None,
        }
        st.warning("El problema no tiene una región factible.")
        return

    no_acotado = problema_no_acotado(tipo, obj_x1, obj_x2, restricciones_datos)

    resultados = []
    for x, y in vertices:
        z = obj_x1 * x + obj_x2 * y
        resultados.append((x, y, z))

    mejor_punto = None
    if not no_acotado:
        if tipo == "Maximizar":
            mejor = max(resultados, key=lambda dato: dato[2])
        else:
            mejor = min(resultados, key=lambda dato: dato[2])
        mejor_punto = (mejor[0], mejor[1])

    procedimiento = crear_procedimiento(
        tipo, obj_x1, obj_x2, restricciones_datos,
        candidatos, vertices, no_acotado,
    )

    st.session_state.grafico_res_actual = {
        "procedimiento": procedimiento,
        "restricciones": restricciones_datos,
        "vertices": vertices,
        "candidatos": candidatos,
        "mejor_punto": mejor_punto,
    }


# ---------- INTERFAZ (la llama app.py) ----------

def mostrar():
    # Estado inicial
    if "grafico_cant" not in st.session_state:
        st.session_state.grafico_cant = 2
    if "grafico_res_actual" not in st.session_state:
        st.session_state.grafico_res_actual = None

    # Objetivo
    st.subheader("Objetivo:")
    st.radio(
        "Tipo de objetivo",
        ["Maximizar", "Minimizar"],
        key="grafico_tipo",
        horizontal=True,
    )

    # Función objetivo
    st.subheader("Función Objetivo:")
    col1, col2, col3, col4 = st.columns([1, 0.35, 1, 0.35])
    with col1:
        st.text_input("Coeficiente de X1", key="grafico_obj_x1", placeholder="0")
    with col2:
        st.markdown("<div style='padding-top: 35px'>X1 +</div>", unsafe_allow_html=True)
    with col3:
        st.text_input("Coeficiente de X2", key="grafico_obj_x2", placeholder="0")
    with col4:
        st.markdown("<div style='padding-top: 35px'>X2</div>", unsafe_allow_html=True)

    # Restricciones
    st.subheader("Restricciones")

    for i in range(st.session_state.grafico_cant):
        st.markdown(f"**Restricción {i + 1}:**")
        c1, c2, c3, c4, c5 = st.columns([1, 0.35, 1, 0.55, 1])
        with c1:
            st.text_input(f"Coeficiente X1 (R{i + 1})", key=f"grafico_rest{i}_x1", placeholder="0")
        with c2:
            st.markdown("<div style='padding-top: 35px'>X1 +</div>", unsafe_allow_html=True)
        with c3:
            st.text_input(f"Coeficiente X2 (R{i + 1})", key=f"grafico_rest{i}_x2", placeholder="0")
        with c4:
            st.radio(f"Signo (R{i + 1})", ["<=", ">=", "="], key=f"grafico_rest{i}_signo", horizontal=True)
        with c5:
            st.text_input(f"Resultado (R{i + 1})", key=f"grafico_rest{i}_resultado", placeholder="Resultado")

    # Reglas de no negatividad
    st.markdown("### Restricciones de no negatividad")

    col_x1, col_x2, col_xn = st.columns(3)
    with col_x1:
        st.markdown("**X1 ≥ 0**")
    with col_x2:
        st.markdown("**X2 ≥ 0**")
    with col_xn:
        st.markdown("**Xn ≥ 0**")

    # Botones + y -
    col_agregar, col_quitar, col_vacio = st.columns([1, 1, 4])
    with col_agregar:
        if st.button("+ Agregar restricción", key="grafico_btn_mas", width="stretch"):
            st.session_state.grafico_cant += 1
            st.rerun()
    with col_quitar:
        if st.button("- Quitar restricción", key="grafico_btn_menos", width="stretch"):
            if st.session_state.grafico_cant <= 1:
                st.warning("Debe existir al menos una restricción.")
            else:
                ultimo = st.session_state.grafico_cant - 1
                for sufijo in ("x1", "x2", "signo", "resultado"):
                    st.session_state.pop(f"grafico_rest{ultimo}_{sufijo}", None)
                st.session_state.grafico_cant -= 1
                st.rerun()

    # Botones principales
    col_resolver, col_limpiar = st.columns(2)
    with col_resolver:
        if st.button("Resolver y Graficar", key="grafico_btn_resolver", type="primary", width="stretch"):
            graficar()
    with col_limpiar:
        if st.button("Limpiar", key="grafico_btn_limpiar", width="stretch"):
            st.session_state.grafico_pend = True
            st.rerun()

    # Limpieza pendiente
    if st.session_state.get("grafico_pend", False):
        for clave in list(st.session_state.keys()):
            if clave.startswith("grafico_rest") or clave in (
                "grafico_tipo",
                "grafico_obj_x1",
                "grafico_obj_x2",
            ):
                del st.session_state[clave]
        st.session_state.grafico_cant = 2
        st.session_state.grafico_res_actual = None
        st.session_state.grafico_pend = False
        st.rerun()

    # Resultado
    if st.session_state.grafico_res_actual is not None:
        resultado = st.session_state.grafico_res_actual

        st.divider()
        st.subheader("Resultado - Método Gráfico")

        col_texto, col_grafica = st.columns([1, 1])

        with col_texto:
            st.markdown("**Procedimiento paso a paso**")
            st.text_area(
                "Procedimiento",
                value=resultado["procedimiento"],
                height=600,
                disabled=True,
                label_visibility="collapsed",
                key="grafico_area_proc",
            )

        with col_grafica:
            figura = crear_grafica(
                resultado["restricciones"],
                resultado["vertices"],
                resultado["candidatos"],
                resultado["mejor_punto"],
            )

            st.plotly_chart(
                figura,
                width="stretch",
                key="grafico_plot",
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "scrollZoom": True,
                    "modeBarButtons": [
                        ["pan2d", "zoomIn2d", "zoomOut2d", "resetScale2d"]
                    ],
                },
            )