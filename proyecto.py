import streamlit as st
import pyodbc

st.set_page_config(page_title="StreamUCV Admin", layout="centered")

# estados para manejar la navegacion
if "conectado" not in st.session_state:
    st.session_state.conectado = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "menu"
if "opcion_seleccionada" not in st.session_state:
    st.session_state.opcion_seleccionada = None


def conectar(server, database, username, password, driver):
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    return pyodbc.connect(conn_str)


# muestra las tablas con el nombre la de las columnas tipo sql
def mostrar_tabla_con_encabezados(cursor, query, titulo):
    cursor.execute(query)
    datos = cursor.fetchall()

    columnas = [column[0] for column in cursor.description]
    st.subheader(titulo)

    st.table([columnas] + [list(fila) for fila in datos])


if not st.session_state.conectado:
    st.title("🗄️ Administración de Base de Datos - StreamUCV")
    st.header("⚙️ Establecer conexión")
    server = st.text_input("Servidor")
    database = st.text_input("Base de Datos")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    driver = st.text_input("Driver")

    if st.button("Probar Conexión"):
        try:
            conn = conectar(server, database, username, password, driver)
            st.session_state.credenciales = {
                "server": server,
                "database": database,
                "username": username,
                "password": password,
                "driver": driver,
            }
            st.session_state.conectado = True
            conn.close()
            st.rerun()
        except Exception as e:
            st.error(f"Error de conexión: {e}")

else:
    # pag principal
    if st.session_state.pagina == "menu":
        st.title("🗄️ Escoga la consultar a realizar")
        if st.button("⬅️ Desconectar"):
            st.session_state.conectado = False
            st.rerun()

        opciones = [
            "1. Listar tablas e índices",
            "2. Cantidad de tablas e índices",
            "3. Restricciones del esquema",
            "4. Info. detallada de índices",
            "5. Listado de Triggers",
            "6. Tamaño ocupado por tabla",
            "7. Tamaño estimado por registro",
            "8. Tamaño de columnas en bytes",
            "9. Cálculo de factor de bloqueo",
            "10. Análisis de costo de consulta",
        ]

        for i in range(0, 10, 2):
            cols = st.columns(2)
            for j in range(2):
                idx = i + j
                if idx < len(opciones):
                    with cols[j]:
                        with st.container(border=True):
                            st.write(f"**{opciones[idx]}**")
                            if st.button("Seleccionar", key=f"btn_{idx}"):
                                st.session_state.opcion_seleccionada = idx
                                st.session_state.pagina = "resultados"
                                st.rerun()

    # resultados
    elif st.session_state.pagina == "resultados":
        st.title("📊 Resultados")
        if st.button("⬅️ Volver al Menú"):
            st.session_state.pagina = "menu"
            st.rerun()

        if st.session_state.opcion_seleccionada == 0:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                mostrar_tabla_con_encabezados(
                    cursor,
                    "SELECT TABLE_SCHEMA AS Esquema, TABLE_NAME AS Tabla FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'",
                    "Tablas de la Base de Datos",
                )

                mostrar_tabla_con_encabezados(
                    cursor,
                    "SELECT t.name AS Tabla, i.name AS Indice, i.type_desc AS TipoIndice FROM sys.indexes AS i INNER JOIN sys.tables AS t ON i.object_id = t.object_id WHERE i.name IS NOT NULL ORDER BY Tabla, Indice;",
                    "Índices de la Base de Datos",
                )

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 1:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) AS TotalTablas FROM sys.tables")
                total_tablas = cursor.fetchone()[0]

                mostrar_tabla_con_encabezados(
                    cursor,
                    "SELECT COUNT(*) AS Total FROM sys.tables",
                    "Cantidad de Tablas en la Base de Datos",
                )

                mostrar_tabla_con_encabezados(
                    cursor,
                    """SELECT t.name AS Tabla, COUNT(i.index_id) AS CantidadIndices FROM sys.tables t LEFT JOIN sys.indexes i ON t.object_id = i.object_id AND i.name IS NOT NULL GROUP BY t.name ORDER BY CantidadIndices DESC""",
                    "Cantidad de Índices definidos por Tabla",
                )

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        # CONSULTAS DE GENESIS
        elif st.session_state.opcion_seleccionada == 2:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 3:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 4:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 5:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        # CONSULTAS DE JESUS
        elif st.session_state.opcion_seleccionada == 6:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 7:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 8:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 9:
            try:
                creds = st.session_state.credenciales
                conn = conectar(
                    creds["server"],
                    creds["database"],
                    creds["username"],
                    creds["password"],
                    creds["driver"],
                )
                cursor = conn.cursor()

                conn.close()
            except Exception as e:
                st.error(f"Error técnico: {e}")
