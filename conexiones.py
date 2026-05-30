import psycopg2
import pyodbc

from config import LP_CONFIG, SCZ_CONFIG


# -----------------------------------
# CENTRAL
# -----------------------------------

def conectar_central():

    return pyodbc.connect(

        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=nodo_central;'
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