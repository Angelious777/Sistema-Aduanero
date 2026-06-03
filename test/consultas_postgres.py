import psycopg2

print("Conectando a PostgreSQL...")

try:
    conn = psycopg2.connect(
        host="26.133.137.249",
        database="nodo_lp",
        user="postgres",
        password="postgres",
        port="5432",
        sslmode="disable"
    )

    print("Conexión exitosa")

    cur = conn.cursor()

    # ==================================
    # EJEMPLO 1: CONSULTA SIMPLE
    # ==================================
    cur.execute("SELECT * FROM cliente_publico;")

    filas = cur.fetchall()

    print("\nCLIENTES GLOBAL:\n")

    for fila in filas:
        print(fila)

    cur.close()
    conn.close()

    print("\nConexión cerrada")

except Exception as e:
    print("\nERROR:")
    print(e)