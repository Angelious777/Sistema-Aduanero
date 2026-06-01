import psycopg2
import pyodbc

from config import LP_CONFIG, SCZ_CONFIG


# -----------------------------------
# CENTRAL
# -----------------------------------

def conectar_central():

    return pyodbc.connect(

        'DRIVER={ODBC Driver 17 for SQL Server};'
<<<<<<< HEAD
        'SERVER=26.169.255.158;'
        'DATABASE=DB_CENTRAL;'
=======
        'SERVER=localhost;'
        'DATABASE=nodo_central;'
>>>>>>> b76c2513a37da4a3ad672f99ab597f81beb68953
        'UID=sa;'
        'PWD=1234'
    )

# -----------------------------------
# CONEXION LA PAZ
# -----------------------------------

def conectar_lp():

    return psycopg2.connect(
        host=LP_CONFIG['host'],
        database=LP_CONFIG['database'],
        user=LP_CONFIG['user'],
        password=LP_CONFIG['password'],
        port=LP_CONFIG['port']
    )

# -----------------------------------
# CONEXION SCZ
# -----------------------------------

def conectar_scz():

    conexion = pyodbc.connect(

        f"DRIVER={{{SCZ_CONFIG['driver']}}};"
        f"SERVER={SCZ_CONFIG['server']};"
        f"DATABASE={SCZ_CONFIG['database']};"
        f"UID={SCZ_CONFIG['user']};"
        f"PWD={SCZ_CONFIG['password']}"
    )

    return conexion