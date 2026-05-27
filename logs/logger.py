from datetime import datetime

# -----------------------------------
# REGISTRAR EVENTO
# -----------------------------------

def registrar_log(evento):

    fecha = datetime.now()

    with open("logs.txt", "a") as archivo:

        archivo.write(
            f"[{fecha}] {evento}\n"
        )