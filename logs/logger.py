from datetime import datetime
from conexiones import conectar_central

# -----------------------------------
# REGISTRAR EVENTO
# -----------------------------------

def registrar_log(nodo, evento):
    
    conn = conectar_central()
    
    cur = conn.cursor()
    cur.execute("""

        INSERT INTO logs_distribuidos
        (
            nodo,
            evento
        )

        VALUES (?, ?)

    """, (

        nodo,
        evento
    ))
    
    cur.commit()

    fecha = datetime.now()

    with open("logs.txt", "a") as archivo:

        archivo.write(
            f"[{fecha}] {evento}\n"
        )
   
        
def registrar_log(evento):
    
    fecha = datetime.now()
    
    with open("logs.txt", "a") as archivo:

        archivo.write(
            f"[{fecha}] {evento}\n"
        )