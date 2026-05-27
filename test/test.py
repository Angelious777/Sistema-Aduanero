import psycopg2

print("Iniciando...")

conn = psycopg2.connect(
    host="26.133.137.249",
    database="lapaz_db",
    user="postgres",
    password="postgres",
    port="5432",
    sslmode="disable"
)

print("Conexion exitosa")