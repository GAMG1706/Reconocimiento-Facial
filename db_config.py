
import mysql.connector

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia según tu configuración
        password="1234567",  # Cambia según tu configuración
        database="datos",# Nombre de la base de datos
    )


def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia según tu configuración
        password="1234567",  # Cambia según tu configuración
        database="clase_ds3a",# Nombre de la base de datos
    )

