import streamlit as st


class SimplexCalculator:
    def __init__(self, c, A, b):
        self.num_constraints = len(b)
        self.num_variables = len(c)

        # Construcción del tableau (Restricciones + Z, Columnas: vars + holgura + RHS)
        self.tableau = []
        for i in range(self.num_constraints):
            row = list(A[i])
            slack = [0.0] * self.num_constraints
            slack[i] = 1.0
            row.extend(slack)
            row.append(float(b[i]))
            self.tableau.append(row)

        z_row = [-float(val) for val in c]
        z_row.extend([0.0] * (self.num_constraints + 1))
        self.tableau.append(z_row)

    def solve(self):
        while True:
            pivot_col = self.find_pivot_column()
            if pivot_col == -1:
                break

            pivot_row = self.find_pivot_row(pivot_col)
            if pivot_row == -1:
                return None, "El problema no tiene solución acotada."

            self.pivot(pivot_row, pivot_col)

        return self.get_solution(), "Solución óptima encontrada."

    def find_pivot_column(self):
        z_row = self.tableau[-1][:-1]
        min_val = min(z_row)
        return z_row.index(min_val) if min_val < 0 else -1

    def find_pivot_row(self, pivot_col):
        min_ratio = float('inf')
        pivot_row = -1
        for i in range(self.num_constraints):
            val = self.tableau[i][pivot_col]
            if val > 0:
                ratio = self.tableau[i][-1] / val
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i
        return pivot_row

    def pivot(self, pivot_row, pivot_col):
        pivot_element = self.tableau[pivot_row][pivot_col]
        self.tableau[pivot_row] = [x / pivot_element for x in self.tableau[pivot_row]]
        for i in range(len(self.tableau)):
            if i != pivot_row:
                factor = self.tableau[i][pivot_col]
                self.tableau[i] = [
                    val - factor * self.tableau[pivot_row][j]
                    for j, val in enumerate(self.tableau[i])
                ]

    def get_solution(self):
        res = {'Z': self.tableau[-1][-1]}
        for j in range(self.num_variables):
            col = [self.tableau[i][j] for i in range(self.num_constraints)]
            if col.count(1.0) == 1 and sum(abs(x) for x in col) == 1.0:
                res[f"X{j+1}"] = self.tableau[col.index(1.0)][-1]
            else:
                res[f"X{j+1}"] = 0.0
        return res


# --- INTERFAZ STREAMLIT ---
def mostrar():

    # Configuración inicial de dimensiones
    col_vars, col_cons = st.columns(2)
    with col_vars:
        num_vars = st.number_input("Número de Variables (X):", min_value=1, value=2, step=1, key="simplex_nvars")
    with col_cons:
        num_cons = st.number_input("Número de Restricciones:", min_value=1, value=3, step=1, key="simplex_ncons")

    st.divider()

    # 1. Inputs Función Objetivo Z
    st.subheader("Función Objetivo (Maximizar Z)")
    c_inputs = []
    cols_z = st.columns(num_vars)
    for j in range(num_vars):
        with cols_z[j]:
            val = st.number_input(f"Coeficiente X{j+1}", value=0.0, key=f"simplex_z_x{j+1}")
            c_inputs.append(val)

    # 2. Inputs Matriz A y Lado Derecho (B)
    st.subheader("Restricciones")
    a_inputs = []
    b_inputs = []

    for i in range(num_cons):
        st.markdown(f"**Restricción {i+1}**")
        cols_r = st.columns(num_vars + 2)
        
        row_a = []
        for j in range(num_vars):
            with cols_r[j]:
                val_a = st.number_input(
                    f"X{j+1}", 
                    value=0.0, 
                    key=f"simplex_r{i+1}_x{j+1}", 
                    label_visibility="collapsed"
                )
                row_a.append(val_a)
        a_inputs.append(row_a)
        
        with cols_r[num_vars]:
            st.markdown("<h4 style='text-align: center;'>≤</h4>", unsafe_allow_html=True)
            
        with cols_r[num_vars + 1]:
            val_b = st.number_input(
                "Lado Derecho", 
                value=0.0, 
                key=f"simplex_r{i+1}_b", 
                label_visibility="collapsed"
            )
            b_inputs.append(val_b)

    st.divider()

    # 3. Botón de Ejecución y Resultados
    if st.button("Calcular Simplex", type="primary", use_container_width=True):
        solver = SimplexCalculator(c_inputs, a_inputs, b_inputs)
        solucion, mensaje = solver.solve()

        if solucion:
            st.success(f"✅ {mensaje}")
            st.metric(label="Valor Óptimo (Z)", value=f"{solucion['Z']:.2f}")
            
            st.subheader("Valores de las Variables:")
            res_cols = st.columns(num_vars)
            for idx, (var_name, var_value) in enumerate(solucion.items()):
                if var_name != 'Z':
                    with res_cols[idx % num_vars]:
                        st.metric(label=var_name, value=f"{var_value:.2f}")
        else:
            st.error(f"❌ {mensaje}")