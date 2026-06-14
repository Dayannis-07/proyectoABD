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
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes"
    # conn_str = f"DSN=MSSQLServerDatabase;SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)


# muestra las tablas con el nombre la de las columnas tipo sql
def mostrar_tabla_con_encabezados(cursor, query, titulo):
    cursor.execute(query)
    datos = cursor.fetchall()

    columnas = [column[0] for column in cursor.description]
    st.subheader(titulo)

    st.table([columnas] + [list(fila) for fila in datos])


def show_query_tables(*args):
    creds = st.session_state.credenciales
    try:
        conn = conectar(
            creds["server"],
            creds["database"],
            creds["username"],
            creds["password"],
            creds["driver"],
        )
        cursor = conn.cursor()

        for query in args:
            mostrar_tabla_con_encabezados(
                cursor,
                query[0],
                query[1],
            )
            pass

        conn.close()
    except Exception as e:
        st.error(f"Error técnico: {e}")


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
                show_query_tables(
                    (
                        "SELECT TABLE_SCHEMA AS Esquema, TABLE_NAME AS Tabla FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'",
                        "Tablas de la Base de Datos",
                    ),
                    (
                        "SELECT t.name AS Tabla, i.name AS Indice, i.type_desc AS TipoIndice FROM sys.indexes AS i INNER JOIN sys.tables AS t ON i.object_id = t.object_id WHERE i.name IS NOT NULL ORDER BY Tabla, Indice;",
                        "Índices de la Base de Datos",
                    ),
                )
            except Exception as e:
                st.error(f"Error técnico: {e}")

        elif st.session_state.opcion_seleccionada == 1:
            show_query_tables(
                (
                    "SELECT COUNT(*) AS Total FROM sys.tables",
                    "Cantidad de Tablas en la Base de Datos",
                ),
                (
                    """SELECT t.name AS Tabla, COUNT(i.index_id) AS CantidadIndices FROM sys.tables t LEFT JOIN sys.indexes i ON t.object_id = i.object_id AND i.name IS NOT NULL GROUP BY t.name ORDER BY CantidadIndices DESC""",
                    "Cantidad de Índices definidos por Tabla",
                ),
            )

        # CONSULTAS DE GENESIS
        elif st.session_state.opcion_seleccionada == 2:
            show_query_tables(
                (
                    """
            SELECT
                s.name AS Esquema,
                t.name AS Tabla,
                c.name AS NombreRestriccion,
                CASE c.type
                    WHEN 'PK' THEN 'PRIMARY KEY'
                    WHEN 'F' THEN 'FOREIGN KEY'
                    WHEN 'C' THEN 'CHECK'
                    WHEN 'UQ' THEN 'UNIQUE'
                    WHEN 'D' THEN 'DEFAULT'
                END AS TipoRestriccion
            FROM sys.objects c
            INNER JOIN sys.tables t
                ON c.parent_object_id = t.object_id
            INNER JOIN sys.schemas s
                ON t.schema_id = s.schema_id
            WHERE s.name = 'streaming'
                AND c.type IN ('PK','F','C','UQ','D')
            ORDER BY
                t.name,
                TipoRestriccion,
                c.name
            """,
                    "Restricciones del esquema",
                ),
            )

        elif st.session_state.opcion_seleccionada == 3:
            show_query_tables(
                (
                    """
            SELECT
            t.name AS Tabla,
            COUNT(i.index_id) AS CantidadIndices
            FROM sys.tables t
            INNER JOIN sys.schemas s
            ON t.schema_id = s.schema_id
            LEFT JOIN sys.indexes i
            ON t.object_id = i.object_id
            AND i.name IS NOT NULL
            WHERE s.name = 'streaming'
            GROUP BY t.name
            ORDER BY CantidadIndices DESC, t.name
            """,
                    "Cantidad de Índices por Tabla",
                ),
                (
                    """
                SELECT
                    t.name AS Tabla,
                    i.name AS NombreIndice,
                    STRING_AGG(c.name, ', ')
                        WITHIN GROUP (ORDER BY ic.key_ordinal) AS Columnas,
                    CASE
                        WHEN i.is_unique = 1 THEN 'Sí'
                        ELSE 'No'
                    END AS EsUnico,
                    i.type_desc AS TipoIndice,
                    CASE
                        WHEN i.is_primary_key = 1 THEN 'Sí'
                        ELSE 'No'
                    END AS EsPrimaryKey,
                    CASE
                        WHEN i.is_unique_constraint = 1 THEN 'Sí'
                        ELSE 'No'
                    END AS EsRestriccionUnique,
                    CASE
                        WHEN i.is_disabled = 1 THEN 'Sí'
                        ELSE 'No'
                    END AS EstaDeshabilitado
                FROM sys.indexes i
                INNER JOIN sys.tables t
                    ON i.object_id = t.object_id
                INNER JOIN sys.schemas s
                    ON t.schema_id = s.schema_id
                INNER JOIN sys.index_columns ic
                    ON i.object_id = ic.object_id
                    AND i.index_id = ic.index_id
                INNER JOIN sys.columns c
                    ON ic.object_id = c.object_id
                    AND ic.column_id = c.column_id
                WHERE s.name = 'streaming'
                    AND i.name IS NOT NULL
                GROUP BY
                    t.name,
                    i.name,
                    i.is_unique,
                    i.type_desc,
                    i.is_primary_key,
                    i.is_unique_constraint,
                    i.is_disabled
                ORDER BY
                    t.name,
                    i.name
                """,
                    "Detalle Índices del Esquema",
                ),
            )

        elif st.session_state.opcion_seleccionada == 4:
            show_query_tables(
                (
                    """
                SELECT
                    tr.name AS NombreTrigger,
                    tb.name AS Tabla,
                    CASE tr.type
                        WHEN 'TR' THEN 'SQL_TRIGGER'
                        ELSE tr.type_desc
                    END AS TipoTrigger,
                    CASE
                        WHEN tr.is_disabled = 1 THEN 'Deshabilitado'
                        ELSE 'Habilitado'
                    END AS Estado
                FROM sys.triggers tr
                INNER JOIN sys.tables tb
                    ON tr.parent_id = tb.object_id
                INNER JOIN sys.schemas s
                    ON tb.schema_id = s.schema_id
                WHERE s.name = 'streaming'
                ORDER BY tb.name, tr.name
                """,
                    "Info Triggers del Esquema",
                ),
            )

        elif st.session_state.opcion_seleccionada == 5:
            show_query_tables(
                (
                    """
                SELECT
                    t.name AS Tabla,
                    SUM(p.rows) AS Filas,
                    SUM(a.total_pages) * 8 AS TamañoKB,
                    CAST(SUM(a.total_pages) * 8.0 / 1024 AS DECIMAL(10,2)) AS TamañoMB
                FROM sys.tables t
                INNER JOIN sys.schemas s
                    ON t.schema_id = s.schema_id
                INNER JOIN sys.indexes i
                    ON t.object_id = i.object_id
                INNER JOIN sys.partitions p
                    ON i.object_id = p.object_id
                    AND i.index_id = p.index_id
                INNER JOIN sys.allocation_units a
                    ON p.partition_id = a.container_id
                WHERE s.name = 'streaming'
                GROUP BY t.name
                ORDER BY TamañoKB DESC
                """,
                    "Tamaño ocupado por cada tabla",
                )
            )

        # CONSULTAS DE JESUS
        elif st.session_state.opcion_seleccionada == 6:
            show_query_tables([])

        elif st.session_state.opcion_seleccionada == 7:
            show_query_tables([])

        elif st.session_state.opcion_seleccionada == 8:
            show_query_tables([])

        elif st.session_state.opcion_seleccionada == 9:
            show_query_tables([])
