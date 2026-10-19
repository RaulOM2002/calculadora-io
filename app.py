import streamlit as st
from metodos import simplex
from metodos import grafico
from metodos import noroeste 
from metodos import costominimo 
from metodos import vogel 

st.set_page_config(page_title="Calculadora IO", page_icon=":material/calculate:", layout="wide")

# ---------- Estilos ----------
st.markdown(
    """
    <style>
    .titulo {text-align: center; font-size: 2.6rem; font-weight: 700; margin-bottom: 0;}
    .subtitulo {text-align: center; opacity: 0.7; margin-bottom: 2rem;}
    .pie {text-align: center; opacity: 0.6; font-size: 0.85rem; margin-top: 3rem;}
    
    [data-testid="stSidebar"] h1 {text-align: center;}

    [data-testid="InputInstructions"] {
    display: none;
    }
    
    [class*="st-key-grafico_rest"][class*="_signo"] [data-testid="stWidgetLabel"] {
    justify-content: center;
    text-align: center;
    }
    [class*="st-key-grafico_rest"][class*="_signo"] [data-testid="stRadio"] > div,
    [class*="st-key-grafico_rest"][class*="_signo"] [role="radiogroup"] {
    width: 100%;
    justify-content: center;
    }   

    /* Tarjetas clicables */
    [class*="st-key-card_"] {
        position: relative;
        min-height: 210px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    [class*="st-key-card_"]:hover {
        border-color: #1F4E79;
        transform: translateY(-3px);
    }
    [class*="st-key-card_"] [data-testid="stElementContainer"]:has(button) {
        position: absolute !important;
        top: 0; left: 0; right: 0; bottom: 0;
        width: 100% !important;
        height: 100% !important;
        z-index: 2;
    }
    [class*="st-key-card_"] [data-testid="stButton"] {
        width: 100% !important;
        height: 100% !important;
    }
    [class*="st-key-card_"] button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Datos ----------
METODOS = {
    "Inicio": {"icono": ":material/home:", "desc": ""},
    "Simplex": {"icono": ":material/table_chart:", "desc": "Resuelve problemas de programación lineal paso a paso."},
    "Método Gráfico": {"icono": ":material/show_chart:", "desc": "Visualiza la región factible y el punto óptimo."},
    "Transporte": {"icono": ":material/local_shipping:", "desc": "Esquina Noroeste, Costo Mínimo y Vogel."},
    "Asignación": {"icono": ":material/assignment_ind:", "desc": "Asigna recursos al menor costo (método húngaro)."},
}

TRANSPORTE = {
    "Esquina Noroeste": {"icono": ":material/north_west:", "desc": "Asigna comenzando por la esquina superior izquierda."},
    "Costo Mínimo": {"icono": ":material/payments:", "desc": "Prioriza las rutas de menor costo."},
    "Vogel": {"icono": ":material/balance:", "desc": "Usa penalizaciones para obtener una mejor solución inicial."},
}

TODOS = {**METODOS, **TRANSPORTE}

# Textos largos (el texto debe ir pegado al borde izquierdo, sin sangría)
DETALLES = {
    "Simplex": """
**¿Qué es?**
El método Simplex es un algoritmo que resuelve problemas de programación lineal: encontrar el mejor valor (el máximo o el mínimo) de una función, cumpliendo un conjunto de restricciones.

**¿Para qué sirve?**
Sirve para tomar decisiones óptimas cuando los recursos son limitados. Por ejemplo, decidir cuántas unidades de cada producto fabricar para obtener la mayor ganancia, o cómo mezclar ingredientes al menor costo.

**¿Cómo funciona?**
Parte de una solución factible y, en cada iteración, se mueve a una mejor, hasta que ya no se puede mejorar. El resultado final es la solución óptima.
""",

    "Método Gráfico": """
**¿Qué es?**
El método gráfico resuelve problemas de programación lineal dibujando las restricciones en un plano. La zona donde todas se cumplen a la vez se llama región factible.

**¿Para qué sirve?**
Sirve para encontrar la solución óptima de forma visual y para entender cómo se comporta el problema. Es ideal para aprender, porque se ve dónde está la mejor solución.

**¿Cómo funciona?**
Se grafica cada restricción, se identifica la región factible y se evalúa la función objetivo en cada vértice de esa región. El vértice con el mejor valor (el mayor o el menor, según el caso) es la solución óptima.
""",

    "Transporte": """
**¿Qué es?**
El problema de transporte busca la forma más barata de enviar mercancía desde varios orígenes (con una oferta limitada) hacia varios destinos (con una demanda que cubrir).

**¿Para qué sirve?**
Sirve para planear envíos y distribución: por ejemplo, decidir cuántas unidades mandar de cada bodega a cada tienda para gastar lo menos posible en transporte.

**¿Cómo se resuelve?**
Se parte de una solución inicial, que se obtiene con alguno de estos tres métodos, y luego se puede mejorar hasta llegar al óptimo:
- **Esquina Noroeste:** el más rápido, no considera los costos.
- **Costo Mínimo:** da prioridad a las rutas más baratas.
- **Vogel:** usa penalizaciones y suele dar la mejor solución inicial.

**¿Qué necesitas para usarlo?**
- La oferta de cada origen.
- La demanda de cada destino.
- El costo de enviar una unidad entre cada origen y destino.
""",

    "Esquina Noroeste": """
**¿Qué es?**
Es un método para obtener una solución inicial en un problema de transporte. Se llama así porque siempre empieza por la esquina superior izquierda (noroeste) de la tabla.

**¿Para qué sirve?**
Sirve para encontrar rápidamente una distribución factible de la mercancía, que luego se puede mejorar para llegar al óptimo.

**¿Cómo funciona?**
1. Se toma la celda de la esquina superior izquierda.
2. Se asigna la mayor cantidad posible, que es el menor valor entre la oferta y la demanda.
3. Se tacha la fila o la columna que ya quedó satisfecha.
4. Se pasa a la siguiente celda (a la derecha o hacia abajo) y se repite hasta cubrir todo.

**Ventajas y Desventajas**
- Es muy fácil y rápido de aplicar.
- No toma en cuenta los costos, por lo que casi nunca da el costo total más bajo.
""",

    "Costo Mínimo": """
**¿Qué es?**
Es un método para obtener una solución inicial en un problema de transporte, dando prioridad a las rutas con menor costo.

**¿Para qué sirve?**
Sirve para encontrar una distribución factible que ya tiene en cuenta los costos, por lo que suele ser mejor que la de la Esquina Noroeste.

**¿Cómo funciona?**
1. Se busca la celda con el costo unitario más bajo de toda la tabla.
2. Se asigna la mayor cantidad posible (el menor valor entre oferta y demanda).
3. Se tacha la fila o la columna que quedó satisfecha.
4. Se repite con la celda de menor costo que quede disponible, hasta cubrir toda la oferta y la demanda.

**Ventajas y Desventajas**
- Considera los costos, por lo que da un mejor punto de partida.
- No siempre llega a la solución óptima.
""",

    "Vogel": """
**¿Qué es?**
El método de aproximación de Vogel es una técnica para obtener la solución inicial de un problema de transporte usando penalizaciones, que miden cuánto se pierde si no se usa la ruta más barata.

**¿Para qué sirve?**
Sirve para encontrar una solución inicial muy cercana a la óptima, normalmente mejor que la de Esquina Noroeste y Costo Mínimo.

**¿Cómo funciona?**
1. En cada fila y columna se calcula la penalización: la diferencia entre los dos costos más bajos.
2. Se elige la fila o columna con la penalización más alta.
3. En esa fila o columna se asigna la mayor cantidad posible a la celda de menor costo.
4. Se tacha lo que quedó satisfecho y se repite el proceso hasta cubrir todo.

**Ventajas y Desventajas**
- Suele dar la mejor solución inicial de los tres métodos.
- Requiere más cálculos en cada paso.
""",

    "Asignación": """
**¿Qué es?**
El problema de asignación consiste en repartir tareas entre personas, máquinas o recursos, de modo que cada tarea tenga un solo responsable y el costo total sea el menor posible (o la ganancia, la mayor).

**¿Para qué sirve?**
Sirve para decidir quién hace qué: por ejemplo, asignar trabajadores a puestos, camiones a rutas o máquinas a pedidos, minimizando tiempo o costo.

**¿Cómo funciona?**
Se resuelve con el método húngaro:
1. Se resta el menor valor de cada fila y luego el de cada columna.
2. Se cubren todos los ceros con el menor número de líneas posible.
3. Si el número de líneas es igual al tamaño de la tabla, ya hay una asignación óptima. Si no, se ajusta la tabla y se repite.

**¿Qué reglas necesarias para usarlo?**
- Una tabla de costos cuadrada (igual número de tareas que de responsables).
- El costo de asignar cada responsable a cada tarea.
""",
}

# ---------- Memoria de la página actual ----------
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"


def ir_a(nombre):
    st.session_state.pagina = nombre


# ---------- Menú lateral ----------
def boton_menu(nombre):
    activo = st.session_state.pagina == nombre
    st.button(
        f"{TODOS[nombre]['icono']}  {nombre}",
        key=f"menu_{nombre}",
        on_click=ir_a,
        args=(nombre,),
        type="primary" if activo else "secondary",
        width="stretch",
    )


with st.sidebar:
    st.title(":material/calculate: Calculadora IO")
    boton_menu("Inicio")
    boton_menu("Simplex")
    boton_menu("Método Gráfico")

    # Se mantiene abierto si estás en Transporte o en alguno de sus métodos
    abierto = st.session_state.pagina == "Transporte" or st.session_state.pagina in TRANSPORTE
    with st.expander(f"{METODOS['Transporte']['icono']}  Transporte", expanded=abierto):
        for sub in TRANSPORTE:
            boton_menu(sub)

    boton_menu("Asignación")
    st.divider()


# ---------- Tarjetas clicables ----------
def tarjetas(items, prefijo):
    columnas = st.columns(len(items))
    for i, (col, nombre) in enumerate(zip(columnas, items)):
        with col:
            
            with st.container(border=True, key=f"card_{prefijo}_{i}"):
                c_icono, c_texto = st.columns([1, 5], gap="small", vertical_alignment="top")
                with c_icono:
                    st.markdown(f"### {TODOS[nombre]['icono']}")
                with c_texto:
                    st.markdown(f"### {nombre}")
                st.write(TODOS[nombre]["desc"])
                st.button("Abrir", key=f"btn_{prefijo}_{i}", on_click=ir_a, args=(nombre,))


def descripcion(nombre):
    with st.container(border=True):
        st.markdown(DETALLES.get(nombre, TODOS[nombre]["desc"]))


# ---------- Páginas ----------
def inicio():
    st.markdown('<p class="titulo">Calculadora de Investigación de Operaciones</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo">Elige un método.</p>', unsafe_allow_html=True)
    tarjetas([m for m in METODOS if m != "Inicio"], "inicio")

    # Pie de página: solo aparece en el inicio
    st.markdown(
        """
        <div class="pie">
            <p><b>Equipo</b></p>
            <p>Raúl Alejandro Orozco Mendoza</p>
            <p>Marcos Daniel de Paz Gonzalez</p>
            <p>Angie Valeska Rodriguez Alcantara</p>
            <p>Geovanni Ariel Barrios Alvarado</p>
            <p>¡Investigación de Operaciones! · Curso 2026</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pagina_transporte():
    st.button("← Volver al inicio", on_click=ir_a, args=("Inicio",))
    st.header(f"{METODOS['Transporte']['icono']} Transporte")
    descripcion("Transporte")
    st.subheader("Elige un método")
    tarjetas(list(TRANSPORTE), "transp")


def pagina_metodo(nombre):
    st.button("← Volver al inicio", on_click=ir_a, args=("Inicio",))
    st.header(f"{TODOS[nombre]['icono']} {nombre}")
    descripcion(nombre)

    if nombre == "Simplex":
        simplex.mostrar()

    elif nombre == "Método Gráfico":
        grafico.mostrar()

    elif nombre == "Esquina Noroeste":
        noroeste.mostrar()

    elif nombre == "Costo Mínimo":
        costominimo.mostrar()

    elif nombre == "Vogel":
        vogel.mostrar()

    else:
        st.info("interfaz de mi compañero")
        tab_datos, tab_proc, tab_res = st.tabs(["Datos", "Procedimiento", "Resultado"])
        with tab_datos:
            st.write("Aquí se ingresan los datos del problema.")
        with tab_proc:
            st.write("Aquí se muestran las iteraciones.")
        with tab_res:
            st.metric("Valor óptimo (Z)", "—")


# ---------- Mostrar la página elegida ----------
# Cada página va en un contenedor con key propio para que Streamlit
# lo reemplace completo al cambiar de página (reduce el error de clics rápidos)
pagina = st.session_state.pagina
with st.container(key=f"pagina_{pagina}"):
    if pagina == "Inicio":
        inicio()
    elif pagina == "Transporte":
        pagina_transporte()
    else:
        pagina_metodo(pagina)