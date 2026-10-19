import pandas as pd
import streamlit as st

# Este archivo lo usan los tres métodos de transporte (noroeste, costo mínimo
# y vogel). Aquí está la tabla de datos, los botones y la forma de mostrar el
# resultado. Cada método solo aporta su función resolver().


def _matriz_vacia(filas, columnas):
    return pd.DataFrame(
        0,
        index=[f"Origen {i + 1}" for i in range(filas)],
        columns=[f"Destino {j + 1}" for j in range(columnas)],
    )


def borrar_resultados():
    for clave in list(st.session_state.keys()):
        if clave.startswith("transp_sol_"):
            del st.session_state[clave]


def _reiniciar(filas, columnas):
    st.session_state.transp_filas = filas
    st.session_state.transp_cols = columnas
    st.session_state.transp_costos = _matriz_vacia(filas, columnas)
    st.session_state.transp_oferta = [0] * filas
    st.session_state.transp_demanda = [0] * columnas
    # la versión cambia la key del editor para que no regresen los valores viejos
    st.session_state.transp_version = st.session_state.get("transp_version", 0) + 1
    borrar_resultados()


def _dibujar_tabla():
    with st.container(border=True):
        st.markdown("**Tamaño de la tabla**")
        a, b, c = st.columns(3)
        with a:
            n_filas = st.number_input(
                "Número de orígenes:",
                min_value=1,
                max_value=10,
                value=st.session_state.transp_filas,
                step=1,
                key="transp_n_filas",
            )
        with b:
            n_cols = st.number_input(
                "Número de destinos:",
                min_value=1,
                max_value=10,
                value=st.session_state.transp_cols,
                step=1,
                key="transp_n_cols",
            )
        with c:
            st.write("")
            st.write("")
            if st.button("Crear tabla", type="primary", width="stretch", key="transp_crear"):
                _reiniciar(int(n_filas), int(n_cols))

    filas = st.session_state.transp_filas
    cols = st.session_state.transp_cols

    st.markdown("#### Matriz de costos, oferta y demanda")

    tabla = st.session_state.transp_costos.copy()
    tabla["Oferta"] = st.session_state.transp_oferta
    tabla.loc["Demanda"] = list(st.session_state.transp_demanda) + [None]

    configuracion = {"Oferta": st.column_config.NumberColumn("Oferta", min_value=0, step=1)}
    for j in range(cols):
        nombre = f"Destino {j + 1}"
        configuracion[nombre] = st.column_config.NumberColumn(nombre, min_value=0, step=1)

    editada = st.data_editor(
        tabla,
        key=f"transp_editor_{filas}_{cols}_{st.session_state.transp_version}",
        width="stretch",
        num_rows="fixed",
        column_config=configuracion,
    )

    # guardar lo que el usuario escribió en la tabla
    try:
        st.session_state.transp_costos = editada.iloc[:filas, :cols].copy()
        st.session_state.transp_oferta = editada.iloc[:filas]["Oferta"].tolist()
        st.session_state.transp_demanda = editada.iloc[filas, :cols].tolist()
    except Exception:
        pass


def _leer_datos():
    try:
        costos = st.session_state.transp_costos.astype(float).values
        oferta = [float(v) for v in st.session_state.transp_oferta]
        demanda = [float(v) for v in st.session_state.transp_demanda]
    except (ValueError, TypeError):
        st.error("Revisa que todos los campos tengan números válidos.")
        return None

    if pd.isna(costos).any() or pd.isna(oferta).any() or pd.isna(demanda).any():
        st.error("Revisa que todos los campos tengan números válidos.")
        return None

    if any(v < 0 for v in oferta + demanda) or (costos < 0).any():
        st.error("Ingresa únicamente valores positivos o cero.")
        return None

    if abs(sum(oferta) - sum(demanda)) > 1e-9:
        st.error(
            f"La oferta total ({sum(oferta):g}) debe ser igual "
            f"a la demanda total ({sum(demanda):g})."
        )
        return None

    return costos, oferta, demanda


def _mostrar_resultado(titulo, asignaciones, pasos, costo_total):
    filas = len(asignaciones)
    cols = len(asignaciones[0])

    st.markdown(f"#### Resultado: {titulo}")

    tabla = pd.DataFrame(
        asignaciones,
        index=[f"Origen {i + 1}" for i in range(filas)],
        columns=[f"Destino {j + 1}" for j in range(cols)],
    )
    st.dataframe(tabla, width="stretch")
    st.success(f"Costo total de transporte: {costo_total:,.2f}")

    with st.expander("Ver pasos del procedimiento"):
        for numero, paso in enumerate(pasos, 1):
            st.write(f"{numero}. {paso}")


def interfaz(clave, titulo, resolver):
    """
    clave:    nombre corto del método ("noroeste", "costominimo", "vogel")
    titulo:   nombre que se muestra ("Esquina Noroeste", etc.)
    resolver: función del método, recibe (costos, oferta, demanda) y devuelve
              (asignaciones, pasos, costo_total)
    """
    if "transp_filas" not in st.session_state:
        _reiniciar(2, 2)

    _dibujar_tabla()

    st.write("")
    izquierda, derecha = st.columns(2)
    with izquierda:
        calcular = st.button(
            f"Calcular {titulo}",
            type="primary",
            width="stretch",
            key=f"{clave}_calcular",
        )
    with derecha:
        limpiar = st.button("Limpiar datos", width="stretch", key=f"{clave}_limpiar")

    if limpiar:
        _reiniciar(st.session_state.transp_filas, st.session_state.transp_cols)
        st.rerun()

    if calcular:
        datos = _leer_datos()
        if datos is not None:
            costos, oferta, demanda = datos
            st.session_state[f"transp_sol_{clave}"] = resolver(costos, oferta, demanda)

    solucion = st.session_state.get(f"transp_sol_{clave}")
    if solucion is not None:
        _mostrar_resultado(titulo, *solucion)