import psycopg2

print("Conectando a PostgreSQL...")

try:
    conn = psycopg2.connect(
        host="26.133.137.249",
        database="lapaz_db",
        user="postgres",
        password="postgres",
        port="5432",
        sslmode="disable"
    )

    print("Conexion exitosa")

    cur = conn.cursor()

    # =========================
    # BASE DE DATOS ACTUAL
    # =========================

    cur.execute("SELECT current_database();")

    db_actual = cur.fetchone()

    print("\nBASE DE DATOS ACTUAL:")
    print(db_actual[0])

    # =========================
    # SCHEMA ACTUAL
    # =========================

    cur.execute("SELECT current_schema();")

    schema_actual = cur.fetchone()

    print("\nSCHEMA ACTUAL:")
    print(schema_actual[0])

    # =========================
    # LISTAR TABLAS
    # =========================

    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name;
    """)

    tablas = cur.fetchall()

    print("\nTABLAS ENCONTRADAS:\n")

    for tabla in tablas:
        print(f"Schema: {tabla[0]} | Tabla: {tabla[1]}")

    # =========================
    # BUSCAR movimiento_lp
    # =========================

    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name ILIKE '%movimiento%';
    """)

    movimientos = cur.fetchall()

    print("\nTABLAS RELACIONADAS CON MOVIMIENTO:\n")

    if movimientos:
        for mov in movimientos:
            print(f"Schema: {mov[0]} | Tabla: {mov[1]}")
    else:
        print("No se encontraron tablas de movimiento")

    cur.close()
    conn.close()

    print("\nConexion cerrada")

except Exception as e:
    print("\nERROR:")
    print(e)