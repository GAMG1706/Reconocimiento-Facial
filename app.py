import cv2
import os
import numpy as np
import mysql.connector
from mysql.connector import Error
from tkinter import Tk, Label, Entry, Button, messagebox
import face_recognition
import time

# Configura la conexión a la base de datos
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='datos'
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None 

# Captura la imagen después de esperar 4 segundos
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo acceder a la cámara.")
        return None

    cv2.namedWindow("Camera")
    for i in range(4):
        ret, frame = cap.read()
        if ret:
            cv2.putText(frame, f"Esperando... {4 - i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow("Camera", frame)
            cv2.waitKey(1000)
        else:
            break

    ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()
    return frame if ret else None

# Guarda la imagen y el nombre en la base de datos y en la carpeta
def save_data(image, name):
    connection = create_connection()
    if connection is None:
        return

    _, buffer = cv2.imencode('.jpg', image)
    img_blob = buffer.tobytes()

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO estudiantes(nombre, imagen) VALUES (%s, %s)", (name, img_blob))
        connection.commit()

        folder_name = "fotos"
        os.makedirs(folder_name, exist_ok=True)

        image_path = os.path.join(folder_name, f"{name}.jpg")
        cv2.imwrite(image_path, image)
        messagebox.showinfo("Información", "Los datos se guardaron correctamente.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Función para abrir la interfaz de ingreso de datos
def open_input_interface(captured_image):
    input_window = Tk()
    input_window.title("Ingrese su nombre")
    input_window.geometry("400x200")
    input_window.configure(bg='lightblue')  # Cambia el color de fondo a celeste

    label = Label(input_window, text="Nombre:", font=("Helvetica", 14), bg='lightblue')
    label.pack(pady=10)

    name_entry = Entry(input_window, font=("Helvetica", 14))
    name_entry.pack(pady=10)

    def on_save():
        name = name_entry.get().strip()
        if name:
            save_data(captured_image, name)
            input_window.destroy()
            open_camera_for_recognition()
        else:
            messagebox.showwarning("Advertencia", "Por favor ingrese un nombre.")

    save_button = Button(input_window, text="Guardar", command=on_save, font=("Helvetica", 14))
    save_button.pack(pady=10)

    input_window.mainloop()

# Función para abrir la cámara y mostrar el cuadro azul que sigue a la persona
def open_camera_for_recognition():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Camera for Recognition")

    known_face_encodings = []
    known_face_names = []

    folder_name = "fotos"
    for filename in os.listdir(folder_name):
        if filename.endswith(".jpg"):
            image_path = os.path.join(folder_name, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_face_encodings.append(encoding[0])
                known_face_names.append(filename[:-4])

    start_time = time.time()  # Tiempo inicial
    duration = 110  # Duración de 3 minutos en segundos

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        cv2.rectangle(frame, (width // 2 - 100, height // 2 - 100), (width // 2 + 100, height // 2 + 100), (255, 0, 0), 2)

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        name_detected = None
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Desconocido"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            name_detected = name

        if name_detected:
            cv2.putText(frame, f"Alumno registrado: {name_detected}", (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Alumno registrado", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Camera for Recognition", frame)

        # Cierra la cámara después de 3 minutos
        if time.time() - start_time > duration:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Permite salir con 'q'
            break

    cap.release()
    cv2.destroyAllWindows()

# Ejecuta el flujo del programa
if __name__ == "__main__":
    captured_image = capture_image()
    if captured_image is not None:
        open_input_interface(captured_image)

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










