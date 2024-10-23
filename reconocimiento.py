import cv2
import face_recognition
import numpy as np
import os
import mysql.connector 
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import app

# Conexión a la base de datos
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia según tu configuración
        password="",  # Cambia según tu configuración
        database="clase_ds3a"  # Nombre de la base de datos
    )

conexion = conectar_db()  # Inicializar la conexión global

# Ruta de la carpeta que contiene las imágenes para la comparación
path = 'fotos'
images = []
classNames = []
myList = os.listdir(path)

# Cargar las imágenes y sus nombres
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    
    if curImg is not None:  # Verifica que la imagen se haya cargado correctamente
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])  # Nombre sin extensión
    else:
        print(f'No se pudo cargar la imagen: {cl}')

# Función para encontrar las codificaciones de las imágenes
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)
        
        if encodes:  # Verifica que se haya encontrado al menos una codificación
            encodeList.append(encodes[0])
        else:
            print('No se encontró un rostro en la imagen.')

    return encodeList

# Obtener las codificaciones de las imágenes conocidas
encodeListKnown = findEncodings(images)

# Iniciar la cámara
cap = cv2.VideoCapture(0)

# Función para mostrar el mensaje de éxito
def mostrar_mensaje_exito():
    ventana = tk.Tk()
    ventana.withdraw()  # Oculta la ventana principal
    messagebox.showinfo("Éxito", "Los datos se guardaron correctamente en la base de datos.")
    ventana.destroy()  # Cierra la ventana después de mostrar el mensaje

while True:
    success, img = cap.read()  # Leer la imagen de la cámara
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Redimensionar para acelerar el proceso
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # Convertir a RGB

    # Detectar los rostros en la imagen de la cámara
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        # Comparar los rostros de la cámara con las imágenes conocidas
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            # Obtener el nombre de la persona reconocida
            name = classNames[matchIndex].upper()

            # Obtener la fecha y hora actual
            now = datetime.now()
            fecha = now.strftime("%d/%m/%Y")
            hora = now.strftime("%H:%M")
            dia = now.strftime("%A")  # Obtener el día de la semana en inglés
            
            # Traducir el día al español
            dias_en_espanol = {
                "Monday": "Lunes",
                "Tuesday": "Martes",
                "Wednesday": "Miércoles",
                "Thursday": "Jueves",
                "Friday": "Viernes",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }
            dia_espanol = dias_en_espanol[dia]

            # Dibujar un cuadro en la cámara y mostrar el nombre y el mensaje
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Reescalar las coordenadas
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Cuadro azul
            cv2.putText(img, f'Alumno registrado: {name}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # Mostrar los datos en la esquina de la ventana
            cv2.putText(img, f'Nombre: {name}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f'Fecha: {fecha}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f'Día: {dia_espanol}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f'Hora: {hora}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Guardar la imagen del rostro recortado en la carpeta "fotos"
            rostro_img = img[y1:y2, x1:x2]
            img_path = f"fotos/{name}_{fecha.replace('/', '-')}_{hora.replace(':', '-')}.png"
            cv2.imwrite(img_path, rostro_img)

            # Leer la imagen guardada como binario
            with open(img_path, 'rb') as file:
                imagen_binaria = file.read()

            # Guardar los datos en la base de datos
            try:
                cursor = conexion.cursor()
                tabla_dia = dia_espanol.lower()  # Convertir el nombre del día al formato de la tabla
                sql = f"INSERT INTO {tabla_dia} (nombre, fecha, hora, imagen) VALUES (%s, %s, %s, %s)"
                valores = (name, fecha, hora, imagen_binaria)
                cursor.execute(sql, valores)
                conexion.commit()
                print("Los datos se guardaron correctamente en la base de datos.")
                mostrar_mensaje_exito()  # Mostrar mensaje de éxito
            except mysql.connector.Error as error:
                print(f"Error al guardar los datos: {error}")
                conexion.rollback()  # Revertir en caso de error

    # Mostrar la imagen en la ventana de la cámara
    cv2.imshow('Camara', img)

    # Presionar 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cerrar la conexión con la base de datos y liberar la cámara
conexion.close()
cap.release()
cv2.destroyAllWindows()

import tkinter as tk

def entrar():
    print("Entrar")

def escaneo():
    print("Escaneo")

def salir():
    root.quit()

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Reconocimiento")
root.geometry("300x200")
root.configure(bg="light blue")  # Fondo color celeste

# Crear los botones
btn_entrar = tk.Button(root, text="Entrar", width=15, command=entrar)
btn_entrar.pack(pady=10)  # Espaciado vertical

btn_escaneo = tk.Button(root, text="Escaneo", width=15, command=escaneo)
btn_escaneo.pack(pady=10)  # Espaciado vertical

btn_salir = tk.Button(root, text="Salir", width=15, command=salir)
btn_salir.pack(pady=10)  # Espaciado vertical

# Iniciar el bucle principal
root.mainloop()



import tkinter as tk
from tkinter import messagebox

def entrar():
    messagebox.showinfo("Información", "Has presionado el botón Entrar")

def escaneo():
    messagebox.showinfo("Información", "Has presionado el botón Escaneo")

def salir():
    root.quit()

# Ejecutar la aplicación
root.mainloop()
