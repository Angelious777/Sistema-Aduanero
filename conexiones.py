import psycopg2
import pyodbc

from config import LP_CONFIG, SCZ_CONFIG

# -----------------------------------
# CONEXION POSTGRESQL
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
# CONEXION SQL SERVER
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